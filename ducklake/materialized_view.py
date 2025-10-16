import argparse
import duckdb
import json
import numpy as np
import os
import random
import threading
import time

from confluent_kafka import Consumer, Producer
from datetime import datetime
from dotenv import load_dotenv
from kafka_producer import produce

load_dotenv()

RAW_TABLE = "raw_events"
DEST_TABLE = "user_clicks"

# Set up DuckDB schema
def init_db(con: duckdb.DuckDBPyConnection):
    with con.cursor() as cursor:
        cursor.execute("USE events;")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
                timestamp TIMESTAMP,
                user_id VARCHAR,
                user_name VARCHAR,
                event_type VARCHAR
            )
        """)
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {DEST_TABLE} (
                user_id VARCHAR,
                user_name VARCHAR,
                count BIGINT,
                last_snapshot INT,        
            )
        """)


def consume_and_insert(bootstrap_servers: str, topic: str, con: duckdb.DuckDBPyConnection, duration_seconds: int, group_id: str ="duckdb-consumer"):
    consumer = Consumer({
        "bootstrap.servers": bootstrap_servers,
        "group.id": group_id,
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe([topic])

    print(f"Consuming from topic {topic}...")
    start_time = time.time()
    raw_files = 0

    with con.cursor() as cursor:
        cursor.execute("USE events;")
        try:
            while time.time() - start_time < duration_seconds:
                msgs = []
                window_length = random.choice([i for i in range(5, 16)])
                if window_length > 10:
                    raw_files += 1
                while len(msgs) < window_length:
                    msg = consumer.poll(1.0)
                    if msg is None:
                        print("No new messages found, sleeping for 5 seconds...")
                        time.sleep(5)
                        continue
                    if msg.error():
                        print("Consumer error:", msg.error())
                        continue
                    msgs.append(msg)

                try:
                    values = []
                    for msg in msgs:
                        event = json.loads(msg.value().decode("utf-8"))
                        values.append(datetime.fromisoformat(event.pop("timestamp")))
                        values.append(event['user_id'])
                        values.append(event['user_name'])
                        values.append(event['event_type'])
                    cursor.execute(
                        f"INSERT INTO {RAW_TABLE} VALUES {'(?, ?, ?, ?),'*((len(values)-4)//4)}(?,?,?,?)",
                        values
                    )
                except Exception as e:
                    print("Error inserting:", e)

        except KeyboardInterrupt:
            print("Stopping consumer...")
        finally:
            print("Closing consumer...")
            consumer.close()
    print(f'Produced {raw_files} raw files')


def aggregate_loop(con: duckdb.DuckDBPyConnection, duration_seconds: int):    
    start_time = time.time()
    with con.cursor() as cursor:
        cursor.execute("USE events;")
        while time.time() - start_time < duration_seconds:
            try:
                # Determine the latest last_snapshot in the destination table
                last_snapshot_update = cursor.execute(f"SELECT max(last_snapshot) FROM {DEST_TABLE};").fetchone()[0] or 0
                max_snapshot = cursor.execute(f"SELECT max(snapshot_id) FROM events.snapshots();").fetchone()[0]

                # Aggregate only new raw data
                aggregate_sql = f"""
                    MERGE INTO {DEST_TABLE} AS dest
                    USING (
                        SELECT 
                            user_id,
                            user_name,
                            COUNT(*) AS count,
                            ? AS last_snapshot,
                        FROM events.table_changes('{RAW_TABLE}', ?, ?)
                        WHERE event_type = 'CLICK'
                        GROUP BY user_id, user_name
                    ) AS src
                    ON dest.user_id = src.user_id
                    WHEN MATCHED THEN 
                        UPDATE SET 
                            count = dest.count + src.count,
                            last_snapshot = src.last_snapshot
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, user_name, count, last_snapshot)
                        VALUES (src.user_id, src.user_name, src.count, src.last_snapshot);
                """
                cursor.execute(aggregate_sql, [max_snapshot, last_snapshot_update, max_snapshot])

                print(f"Aggregation executed at {datetime.now()} from {last_snapshot_update} to {max_snapshot}")
                # time.sleep(2)
                print(f"Current files for {DEST_TABLE}:")
                print(cursor.execute(f"CALL ducklake_list_files('events', '{DEST_TABLE}');").fetchall())

            except Exception as e:
                print("Aggregation error:", e)
                # print('an error occurred')


def main():
    parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default="my-topic", help="Kafka topic to consume from")
    parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    parser.add_argument("--catalog", default='duckdb', choices=["duckdb", "postgres"])
    args = parser.parse_args()

    con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")

    if args.catalog == 'duckdb':
        con.execute("ATTACH 'ducklake:catalog/events.ducklake' AS events (DATA_INLINING_ROW_LIMIT 10, DATA_PATH 'data_files/');")
    else:
        con.execute(f"""ATTACH 'ducklake:postgres:dbname={os.environ.get('POSTGRES_DB')} 
                    host=localhost
                    port=5432
                    user={os.environ.get('POSTGRES_USER')}
                    password={os.environ.get('POSTGRES_PASSWORD')}'
                    AS events (DATA_PATH 'data_files/');""")

    init_db(con)

    t1 = threading.Thread(target=consume_and_insert, args=(args.bootstrap_servers, args.topic, con, args.duration_seconds))
    t2 = threading.Thread(target=aggregate_loop, args=(con, args.duration_seconds), daemon=True)
    t3 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t3.start()
    t1.start()
    t2.start()
    
    t3.join()
    t1.join()
    t2.join()

    # Final flush to ensure all inlined data is persisted to Parquet files
    if args.catalog == 'duckdb':
        print("Flushing inlined data to Parquet files...")
        con.execute(f"CALL ducklake_flush_inlined_data('events', table_name => '{RAW_TABLE}');")

    con.execute(f"CALL ducklake_merge_adjacent_files('events', '{RAW_TABLE}');")
    # con.execute("CALL ducklake_cleanup_old_files('events', cleanup_all => true);")

    print("Compacting files...")
    # con.execute(f"CALL ducklake_rewrite_data_files('events', '{DEST_TABLE}');")
    # con.execute(f"CALL ducklake_merge_adjacent_files('events', '{DEST_TABLE}');")
    # con.execute("CALL ducklake_cleanup_old_files('events', cleanup_all => true);")
    con.close()


if __name__ == "__main__":
    main()
