import argparse
import duckdb
import functools
import threading

from config import CONFIG
from kafka_producer import produce
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, to_timestamp, count, max as max_
from pyspark.sql.types import StructType, StructField, StringType


PROPERTIES = {
    "driver": "org.duckdb.DuckDBDriver"
}

    
def spark_process_kafka(jdbc_url: str, duration_seconds: int = 20, bootstrap_servers: str = "localhost:9092", topic: str = "my-topic"):
    """
    Stream data from Kafka, aggregate CLICK events, and store results in DuckDB using Spark Structured Streaming.
    """

    # Initialize Spark session"jdbc:duckdb:./events.duckdb"
    spark = SparkSession.builder \
        .appName("SparkKafkaToDuckDB") \
        .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,"
            "org.duckdb:duckdb_jdbc:1.4.0.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("INFO")

    # Define Kafka source schema
    schema = StructType([
        StructField("timestamp", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("user_name", StringType(), True),
        StructField("event_type", StringType(), True)
    ])

    # Read from Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrap_servers) \
        .option("subscribe", topic) \
        .option("startingOffsets", "earliest") \
        .load()

    # Decode Kafka value and parse JSON
    value_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str")
    parsed_df = value_df.select(from_json(col("json_str"), schema).alias("data")).select("data.*")

    # Filter CLICK events and aggregate
    clicks_df = parsed_df.filter(col("event_type") == "CLICK") \
        .withColumn("timestamp", to_timestamp("timestamp"))

    agg_df = clicks_df.groupBy("user_id", "user_name") \
        .agg(
            count("*").alias("count_of_clicks"),
            max_("timestamp").alias("updated_at")
        )
    
    
    # Start streaming query
    query = agg_df.writeStream \
        .foreachBatch(functools.partial(overwrite_to_sink, jdbc_url=jdbc_url)) \
        .outputMode("complete") \
        .start()

    # Stop it manually after the specified duration
    query.awaitTermination(duration_seconds)
    if query.isActive:
        query.stop()


def overwrite_to_sink(batch_df: DataFrame, batch_id: int, *args, **kwargs):
    """Simple overwrite of the entire table each micro-batch"""
    print(batch_df.show())
    batch_df.write.jdbc(
        url=kwargs["jdbc_url"],
        table="user_clicks",
        mode="overwrite",
        properties=PROPERTIES,
    )

    
def setup_catalog(uri: str, options: dict):
    con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")
    con.execute(f"ATTACH '{uri}' AS events ({",".join(map(lambda i: f"{i[0]} '{i[1]}'", options.items()))});")
    with con.cursor() as cursor:
        cursor.execute("USE events;")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS user_clicks (
                user_id VARCHAR,
                user_name VARCHAR,
                count BIGINT,
                last_snapshot INT,
            )
        """)


def insert_overwrite_duckdb(batch_df: DataFrame, batch_id: int, *args, **kwargs):
    """
    This method is an example of how you can do funky stuff within the spark streaming runtime.
    """
    batch_df.write.jdbc(
        url=kwargs["jdbc_url"],
        table="user_clicks_unaggregated",
        mode="append",  # Use "overwrite" if you want to replace existing data
        properties=PROPERTIES
    )
    create_table = """
    CREATE TABLE IF NOT EXISTS user_clicks (
        user_id VARCHAR,
        user_name VARCHAR,
        count_of_clicks BIGINT,
        updated_at TIMESTAMP
    );
    """
    agg_sql = """
        DELETE FROM user_clicks;
        INSERT INTO user_clicks
        SELECT user_id, user_name, sum(count_of_clicks), max(updated_at)
        FROM user_clicks_unaggregated
        GROUP BY user_id, user_name;
    """
    
    # Execute the SQL using DuckDB Python API
    con = duckdb.connect("events.duckdb")
    con.execute(create_table)
    con.begin()
    con.execute(agg_sql)
    con.commit()
    con.close()


def main():    
    parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default="my-topic", help="Kafka topic to consume from")
    parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    parser.add_argument("--sink", choices=["duckdb", "ducklake"], default="duckdb")
    parser.add_argument("--catalog", choices=["duckdb", "postgres"], default="duckdb")
    args = parser.parse_args()
    
    jdbc_url = "jdbc:duckdb:./events.duckdb"
    if args.sink == "ducklake":
        if args.catalog == "duckdb":
            setup_catalog(CONFIG["DUCKLAKE"]["DUCKDB_URL"], {"DATA_INLINING_ROW_LIMIT": 10, "DATA_PATH": CONFIG["DUCKLAKE"]["DATA_PATH"]})
            jdbc_url = f"jdbc:duckdb:{CONFIG["DUCKLAKE"]["DUCKDB_URL"]}"
        elif args.catalog == "postgres":
            setup_catalog(CONFIG["DUCKLAKE"]["POSTGRES_URL"], {"DATA_PATH": CONFIG["DUCKLAKE"]["DATA_PATH"]})
            jdbc_url = f"jdbc:duckdb:{CONFIG["DUCKLAKE"]["POSTGRES_URL"]}"
        

    t1 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t1.start()

    spark_process_kafka(
        jdbc_url=jdbc_url,
        duration_seconds=args.duration_seconds,
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic
    )

    t1.join()


if __name__ == "__main__":
    main()
