import argparse
import functools
import pandas as pd
import os
import threading

from dotenv import load_dotenv
from kafka_producer import produce
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, count, max as max_
from pyspark.sql.types import StructField, StructType, IntegerType, StringType, TimestampType

load_dotenv('.env')

def setup_spark(catalog_uri: str, catalog_name: str, client_id: str, client_secret: str) -> SparkSession:
    SparkSession.builder
    spark: SparkSession = SparkSession.builder \
            .appName("SparkKafkaToIceberg") \
            .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.7") \
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


def spark_process_kafka(spark: SparkSession, duration_seconds: int = 20, bootstrap_servers: str = "localhost:9092", topic: str = "my-topic"):
    # spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {os.environ.get("CATALOG_NAME")}.ns1")
    # spark.sql(f"USE {os.environ.get("CATALOG_NAME")}.ns1")
    # spark.sql(f"""CREATE TABLE IF NOT EXISTS
    #           nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER);
    #             """)
    # spark.sql("INSERT INTO nyc_taxi (id, vendor_id, passenger_count, trip_duration) VALUES ('abcd123', 1234564, 4, 559);")
    
    # df = spark.createDataFrame(pd.read_csv('train.csv', usecols=["id", "vendor_id", "passenger_count", "trip_duration"]), schema=StructType([
    #     StructField("id", StringType(), True),
    #     StructField("vendor_id", IntegerType(), True),
    #     StructField("passenger_count", IntegerType(), True),
    #     StructField("trip_duration", IntegerType(), True),
    # ]))
    # df.createOrReplaceTempView("updates")
    # spark.sql("SELECT * FROM updates LIMIT 10").show()

    # spark.sql(f"MERGE INTO nyc_taxi dest USING updates src ON dest.id = src.id WHEN NOT MATCHED THEN INSERT *;")
    # # spark.sql(f"INSERT INTO nyc_taxi USING (SELECT * FROM updates);")
    # spark.sql("SELECT * FROM nyc_taxi;").show()

    spark.sql("USE events;") 
    spark.sql("CREATE TABLE IF NOT EXISTS user_clicks (user_id INTEGER, user_name STRING, updated_at TIMESTAMP, count_of_clicks LONG);") 
    

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
        .foreachBatch(overwrite_to_sink) \
        .outputMode("update") \
        .start()
    
    # Start streaming query in continuous processing mode (experimental)
    # query = agg_df.writeStream \
    #     .foreach(functools.partial(overwrite_to_sink_continuous, data_path=data_path)) \
    #     .outputMode("complete") \
    #     .start()
    

    # Stop it manually after the specified duration
    query.processAllAvailable()
    # query.stop()
    print(query.isActive)
    # query.awaitTermination(duration_seconds)
    # if query.isActive:
    #     query.stop()


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
                                    USING updates src
                                    ON dest.user_id = src.user_id
                                    WHEN MATCHED THEN 
                                        UPDATE SET 
                                            count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
                                            updated_at = src.updated_at
                                    WHEN NOT MATCHED THEN
                                        INSERT (user_id, user_name, count_of_clicks, updated_at)
                                        VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at);
                                    """)
        # batch_df.write.save(path=kwargs["data_path"],
        #                 format="delta",
        #                 mode="overwrite",
        #                 )
    except Exception as e:
        print(e)


def main():
    spark = setup_spark(
        catalog_uri=os.environ.get("CATALOG_URI"),
        catalog_name=os.environ.get("CATALOG_NAME"),
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET")
    )

    parser = argparse.ArgumentParser(description="Kafka to DuckDB streaming pipeline")
    parser.add_argument("--bootstrap-servers", type=str, default="localhost:9092", help="Kafka bootstrap servers")
    parser.add_argument("--topic", type=str, default="my-topic", help="Kafka topic to consume from")
    parser.add_argument("--duration-seconds", type=int, default=20, help="Duration to run the pipeline (seconds)")
    args = parser.parse_args()
        
    t1 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t2 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t3 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t4 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t1.start()
    # t2.start()
    # t3.start()
    # t4.start()

    spark_process_kafka(spark=spark)
    
    t1.join()
    # t2.join()
    # t3.join()
    # t4.join()


if __name__ == "__main__": 
    main()
