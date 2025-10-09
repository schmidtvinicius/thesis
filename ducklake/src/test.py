import duckdb
import numpy as np
import random
import time

from datetime import datetime

def main():
    start = time.time()
    con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")
    con.execute("ATTACH 'ducklake:catalog/events_ducklake.ducklake' AS events_ducklake (DATA_INLINING_ROW_LIMIT 10, DATA_PATH 'data_files/');")
    # con.execute("ATTACH 'ducklake:catalog/events_ducklake.ducklake' AS events_ducklake (DATA_PATH 'data_files/');")

    with con.cursor() as cursor:
        cursor.execute('USE events_ducklake;')
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS raw_events (
                timestamp TIMESTAMP,
                user_id VARCHAR,
                user_name VARCHAR,
                event_type VARCHAR
            )
        """)
        user_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        for _ in range(1500):
            user_id = np.random.randint(0, 10)
            event = {
                "timestamp": datetime.isoformat(datetime.now()),
                "user_id": user_id,
                "user_name": user_names[user_id],
                "event_type": random.choice(['CLICK', 'SCROLL', 'SWIPE'])
            }
            try:
                cursor.execute(
                            f"INSERT INTO raw_events VALUES (?, ?, ?, ?)",
                            [event["timestamp"], event["user_id"], event["user_name"], event["event_type"]]
                        )
            except Exception as e:
                print(f'Error inserting: {e}')
    con.execute(f"CALL ducklake_flush_inlined_data('events_ducklake', table_name => 'raw_events');")
    con.close()
    print(f'Elapsed time: {time.time() - start} seconds')


if __name__ == '__main__':
    main()