import argparse
import os
import pandas as pd
import psutil
import threading

from dotenv import load_dotenv
from kafka_producer import produce, consume
from py4j.protocol import Py4JError, Py4JJavaError
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, count, max as max_, sum as sum_
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, TimestampType

load_dotenv('.env')

def setup_spark(catalog_uri: str, catalog_name: str, client_id: str, client_secret: str) -> SparkSession:
    spark: SparkSession = SparkSession.builder \
            .appName("SparkKafkaToIceberg") \
            .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7") \
            .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
            .config(f"spark.sql.catalog.{catalog_name}", "org.apache.iceberg.spark.SparkCatalog") \
            .config(f"spark.sql.catalog.{catalog_name}.type", "rest") \
            .config(f"spark.sql.catalog.{catalog_name}.warehouse", catalog_name) \
            .config(f"spark.sql.catalog.{catalog_name}.uri", catalog_uri) \
            .config(f"spark.sql.catalog.{catalog_name}.credential", f"{client_id}:{client_secret}") \
            .config(f"spark.sql.catalog.{catalog_name}.scope", "PRINCIPAL_ROLE:ALL") \
            .getOrCreate()
    spark.sql(f"USE {catalog_name};")
    spark.sql("CREATE NAMESPACE IF NOT EXISTS events;")


    return spark


def spark_process_kafka(spark: SparkSession, duration_in_seconds:int = 20, bootstrap_servers: str = "localhost:9092", topic: str = "my-topic"):
    spark.sql("USE events;") 
    spark.sql("CREATE TABLE IF NOT EXISTS user_clicks (user_id INTEGER, user_name STRING, updated_at TIMESTAMP, total_event_id INTEGER, count_of_clicks LONG);") 
    
    # Define Kafka source schema
    schema = StructType([
        StructField("timestamp", TimestampType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("user_name", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("event_id", IntegerType(), True)
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
    # clicks_df = parsed_df.filter("event_type = 'CLICK'") \
    #     .withColumn("timestamp", to_timestamp("timestamp"))

    # agg_df = clicks_df.groupBy("user_id", "user_name") \
    #     .agg(
    #         count("*").alias("count_of_clicks"),
    #         max_("timestamp").alias("updated_at"),
    #         sum_("event_id").alias("total_event_id")
    #     )

    # Start streaming query in micro-batch mode
    query = parsed_df.writeStream \
        .foreachBatch(overwrite_to_sink) \
        .outputMode("append") \
        .start()

    # Stop it manually after the specified duration
    # query.processAllAvailable()
    terminated = query.awaitTermination(duration_in_seconds)
    if not terminated:
        query.stop()


def overwrite_to_sink(batch_df: DataFrame, batch_id: int, *args, **kwargs):
    """
    Simple overwrite of the entire table each micro-batch. If we use the `batch_df.write.save method,
    the operation doesn't trigger the use of deletion vectors, since it simply rewrites the whole
    table. Therefore, we need to create a view of the updated micro-batch and use a MERGE INTO to
    update our table.
    """
    try:
        batch_df.createOrReplaceTempView("updates")
        batch_df.sparkSession.sql(f"""MERGE INTO iceberg_catalog.events.user_clicks dest
                                    USING (SELECT user_id, user_name, count(*) AS count_of_clicks, MAX(timestamp) AS updated_at, SUM(event_id) AS total_event_id
                                            FROM updates 
                                            WHERE event_type = 'CLICK' 
                                            GROUP BY user_id, user_name) src
                                    ON dest.user_id = src.user_id
                                    WHEN MATCHED THEN 
                                        UPDATE SET 
                                            count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
                                            updated_at = src.updated_at,
                                            total_event_id = dest.total_event_id + src.total_event_id
                                    WHEN NOT MATCHED THEN
                                        INSERT (user_id, user_name, count_of_clicks, updated_at, total_event_id)
                                        VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at, src.total_event_id);
                                    """)
        # batch_df.sparkSession.sql(f"""MERGE INTO iceberg_catalog.events.user_clicks dest
        #                             USING updates src
        #                             ON dest.user_id = src.user_id
        #                             WHEN MATCHED THEN 
        #                                 UPDATE SET 
        #                                     count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
        #                                     updated_at = src.updated_at,
        #                                     total_event_id = dest.total_event_id + src.total_event_id
        #                             WHEN NOT MATCHED THEN
        #                                 INSERT (user_id, user_name, count_of_clicks, updated_at, total_event_id)
        #                                 VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at, src.total_event_id);
        #                             """)
        # batch_df.write.saveAsTable("iceberg_catalog.events.user_clicks", mode="overwrite")
        # batch_df.sparkSession.sql(f"INSERT INTO iceberg_catalog.events.user_clicks SELECT user_id, user_name, timestamp, event_id FROM updates;")
    except Exception as e:
        print(e)


def main():
    spark = setup_spark(
        catalog_uri=os.environ.get("CATALOG_URI"),
        catalog_name=os.environ.get("CATALOG_NAME"),
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET")
    )

    # spark.sql("USE events;")
    # spark.sql("CREATE TABLE IF NOT EXISTS nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER);")

    # schema = StructType([
    #     StructField("id", StringType(), True),
    #     StructField("vendor_id", IntegerType(), True),
    #     StructField("passenger_count", IntegerType(), True),
    #     StructField("trip_duration", IntegerType(), True),
    # ])
    
    # df = spark.createDataFrame(pd.read_csv('train.csv', usecols=["id", "vendor_id", "passenger_count", "trip_duration"]), schema=schema)

    # df.createOrReplaceTempView("updates")

    # spark.sql("INSERT INTO nyc_taxi SELECT * FROM updates;")
    # return
    spark.sql("SELECT * FROM events.nyc_taxi;").show()

    while True:
        continue

    parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default="my-topic", help="Kafka topic to consume from")
    parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    args = parser.parse_args()
        
    t1 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t1.start()

    spark_process_kafka(spark=spark, duration_in_seconds=60)
    
    t1.join()

    # spark.sql(f"USE {os.environ.get("CATALOG_NAME")};")
    # spark.sql("USE NAMESPACE events;")
    spark.sql("SELECT * FROM iceberg_catalog.events.user_clicks ORDER BY user_id;").show(truncate=False)
    # spark.sql("SELECT COUNT(*) FROM (SELECT DISTINCT event_id FROM iceberg_catalog.events.user_clicks);").show()
    spark.sql("SELECT AVG(count_of_clicks) AS mean_clicks FROM iceberg_catalog.events.user_clicks;").show()
    spark.sql("EXPLAIN SELECT * FROM iceberg_catalog.events.user_clicks;").show(truncate=False)


if __name__ == "__main__": 
    main()
    # print(psutil.disk_io_counters(perdisk=True))
    # consume('my-topic')