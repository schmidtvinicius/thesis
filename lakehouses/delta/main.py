import pandas as pd

import argparse
import functools
import threading

from config import CONFIG
from kafka_producer import produce, consume
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, to_timestamp, count, max as max_
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType


PROPERTIES = {
    "driver": "org.duckdb.DuckDBDriver",
}

def test_deletion_vectors(spark: SparkSession, data_path: str) -> None:
    """
    Here we test how deletion vectors are used by Delta to avoid rewriting entire data files
    if a single or few rows are updated/deleted. In cases where the table is small, e.g. 6 rows,
    it seems like Delta adds a deletion vector but still rewrites the parquet files, since the
    table is so small. In this case, the delta log doesn't show any deletion vectors were added. 
    However, if auto-compaction is enabled, it will first rewrite the small data files into a 
    single parquet file and after the MERGE operation it will just create a deletion vector.
    """
    spark.sql(f"""CREATE TABLE IF NOT EXISTS
              default.nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER)
              USING DELTA LOCATION '{data_path}'
              TBLPROPERTIES ('delta.enableDeletionVectors' = true);
                """)
    
    # df = spark.createDataFrame(pd.read_csv('train.csv', usecols=["id", "vendor_id", "passenger_count", "trip_duration"]), schema=StructType([
    #     StructField("id", StringType(), True),
    #     StructField("vendor_id", IntegerType(), True),
    #     StructField("passenger_count", IntegerType(), True),
    #     StructField("trip_duration", IntegerType(), True),
    # ]))
    
    df = spark.createDataFrame([
        {"id": "id2875421", "vendor_id": 2, "passenger_count": 1, "trip_duration": 455},
        {"id": "id2377394", "vendor_id": 1, "passenger_count": 1, "trip_duration": 663},
        {"id": "id3858529", "vendor_id": 2, "passenger_count": 1, "trip_duration": 2124},
        {"id": "id3504673", "vendor_id": 2, "passenger_count": 1, "trip_duration": 429},
        {"id": "id2181028", "vendor_id": 2, "passenger_count": 1, "trip_duration": 435},
        {"id": "id0801584", "vendor_id": 2, "passenger_count": 6, "trip_duration": 443},
    ], schema=StructType([
        StructField("id", StringType(), True),
        StructField("vendor_id", IntegerType(), True),
        StructField("passenger_count", IntegerType(), True),
        StructField("trip_duration", IntegerType(), True),
    ]))

    df.createOrReplaceTempView("updates")

    spark.sql("""INSERT INTO default.nyc_taxi
              FROM updates;
                """)
    
    new_df = spark.createDataFrame([
        {"id": "id2875421", "vendor_id": 2, "passenger_count": 2, "trip_duration": 123},
        # {"id": "id2377394", "vendor_id": 1, "passenger_count": 2, "trip_duration": 234},
        # {"id": "id3858529", "vendor_id": 2, "passenger_count": 2, "trip_duration": 345},
        # {"id": "id3504673", "vendor_id": 2, "passenger_count": 2, "trip_duration": 456},
        # {"id": "id2181028", "vendor_id": 2, "passenger_count": 2, "trip_duration": 567},
        # {"id": "id0801584", "vendor_id": 2, "passenger_count": 2, "trip_duration": 678},
    ], schema=StructType([
        StructField("id", StringType(), True),
        StructField("vendor_id", IntegerType(), True),
        StructField("passenger_count", IntegerType(), True),
        StructField("trip_duration", IntegerType(), True),
    ]))

    new_df.createOrReplaceTempView("updates")

    spark.sql("""MERGE INTO default.nyc_taxi AS dest 
              USING updates AS src
              ON src.id = dest.id
              WHEN MATCHED THEN UPDATE SET
                passenger_count = src.passenger_count,
                trip_duration = dest.trip_duration + src.trip_duration
              WHEN NOT MATCHED THEN
                INSERT (id, vendor_id, passenger_count, trip_duration)
                VALUES (src.id, src.vendor_id, src.passenger_count, src.trip_duration);""")

    
def setup_spark(catalog_uri: str, auto_compaction: bool) -> SparkSession:
    """
    Setup a spark session using the given catalog URI (Unity Catalog) and path to store the data files
    """ 
    spark = SparkSession.builder \
        .appName("SparkKafkaToDelta") \
        .config("spark.jars.packages",
            "io.delta:delta-spark_2.13:4.0.0," \
            "io.unitycatalog:unitycatalog-spark_2.13:0.3.0," \
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "io.unitycatalog.spark.UCSingleCatalog") \
        .config("spark.sql.catalog.unity", "io.unitycatalog.spark.UCSingleCatalog") \
        .config("spark.sql.catalog.unity.token", "") \
        .config("spark.sql.defaultCatalog", "unity") \
        .config("spark.sql.catalog.unity.uri", catalog_uri) \
        .config("spark.databricks.delta.autoCompact.enabled", auto_compaction) \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("INFO")
    
    return spark


def spark_process_kafka(spark: SparkSession, data_path: str, duration_seconds: int = 20, bootstrap_servers: str = "localhost:9092", topic: str = "my-topic"):

    spark.sql(f"""CREATE TABLE IF NOT EXISTS 
                default.user_clicks (user_id INTEGER, user_name STRING, count_of_clicks LONG, updated_at TIMESTAMP)
                USING DELTA LOCATION '{data_path}'
                TBLPROPERTIES ('delta.enableDeletionVectors' = true);""")

    # Define Kafka source schema
    schema = StructType([
        StructField("timestamp", TimestampType(), True),
        StructField("user_id", IntegerType(), True),
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
    
    
    # Start streaming query in micro-batch mode
    query = agg_df.writeStream \
        .foreachBatch(functools.partial(overwrite_to_sink, data_path=data_path)) \
        .outputMode("complete") \
        .start()
    
    # Start streaming query in continuous processing mode (experimental)
    # query = agg_df.writeStream \
    #     .foreach(functools.partial(overwrite_to_sink_continuous, data_path=data_path)) \
    #     .outputMode("complete") \
    #     .start()
    

    # Stop it manually after the specified duration
    # query.processAllAvailable()
    # query.stop()
    # print(query.isActive)
    terminated = query.awaitTermination(duration_seconds)
    if not terminated:
        query.stop()


def overwrite_to_sink(batch_df: DataFrame, batch_id: int, *args, **kwargs):
    """
    Simple overwrite of the entire table each micro-batch. If we use the `batch_df.write.save method,
    the operation doesn't trigger the use of deletion vectors, since it simply rewrites the whole
    table. Therefore, we need to create a view of the updated micro-batch and use a MERGE INTO to
    update our table.
    """
    # batch_df.createOrReplaceTempView("updates")
    # batch_df.sparkSession.sql("""MERGE INTO default.user_clicks dest
    #                             USING (SELECT user_id, user_name, count(*) AS count_of_clicks, MAX(timestamp) AS updated_at
    #                                     FROM updates 
    #                                     WHERE event_type = 'CLICK' 
    #                                     GROUP BY user_id, user_name) src
    #                             ON dest.user_id = src.user_id
    #                             WHEN MATCHED THEN 
    #                                 UPDATE SET 
    #                                     count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
    #                                     updated_at = src.updated_at
    #                             WHEN NOT MATCHED THEN
    #                                 INSERT (user_id, user_name, count_of_clicks, updated_at)
    #                                 VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at);
    #                             """)
    # batch_df.sparkSession.sql("""MERGE INTO default.user_clicks dest
    #                             USING updates src
    #                             ON dest.user_id = src.user_id
    #                             WHEN MATCHED THEN 
    #                                 UPDATE SET 
    #                                     count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
    #                                     updated_at = src.updated_at
    #                             WHEN NOT MATCHED THEN
    #                                 INSERT (user_id, user_name, count_of_clicks, updated_at)
    #                                 VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at);
    #                             """)
    batch_df.write.save(path=kwargs["data_path"],
                    format="delta",
                    mode="overwrite",
                    )


def main():    
    parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default="my-topic", help="Kafka topic to consume from")
    parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    args = parser.parse_args()

    spark = setup_spark(catalog_uri=CONFIG["UNITY"]["URI"], auto_compaction=False)
        
    t1 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t1.start()

    spark_process_kafka(spark=spark, data_path=CONFIG["UNITY"]["USER_CLICKS_PATH"], duration_seconds=60)
    
    t1.join()
    spark.sql("SELECT * FROM default.user_clicks ORDER BY user_id;").show()


if __name__ == "__main__":
    main()
    # consume("my-topic")
