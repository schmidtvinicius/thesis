import argparse
import duckdb
import functools
import pyarrow.csv as arrow_csv
import threading

from config import CONFIG
from kafka_producer import produce, consume
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, count, max as max_
from pyspark.sql.types import StructType, StructField, StringType


PROPERTIES = {
    "driver": "org.duckdb.DuckDBDriver",
}

def setup_spark():
    spark = SparkSession.builder \
        .appName("SparkKafkaToDuckDB") \
        .config("spark.jars.packages", "org.duckdb:duckdb_jdbc:1.4.2.0") \
        .config('spark.driver.defaultJavaOptions', '-Djava.security.manager=allow') \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    return spark

    
def spark_process_kafka(jdbc_url: str, duration_seconds: int = 20, bootstrap_servers: str = "localhost:9092", topic: str = "my-topic"):
    """
    Stream data from Kafka, aggregate CLICK events, and store results in DuckDB using Spark Structured Streaming.
    """

    # Initialize Spark session"jdbc:duckdb:./events.duckdb"
    spark = SparkSession.builder \
        .appName("SparkKafkaToDuckDB") \
        .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,"
            "org.duckdb:duckdb_jdbc:1.4.2.0") \
        .config("spark.driver.memory", "2g") \
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
        .outputMode("update") \
        .start()

    # Stop it manually after the specified duration
    terminated = query.awaitTermination(duration_seconds)
    if not terminated:
        query.stop()


def overwrite_to_sink(batch_df: DataFrame, batch_id: int, *args, **kwargs):
    """Simple overwrite of the entire table each micro-batch"""
    # batch_df.write.jdbc(
    #     url=kwargs["jdbc_url"],
    #     table="user_clicks",
    #     mode="overwrite",
    #     properties=PROPERTIES,
    # )
    # batch_df.createOrReplaceTempView("updates")
    updates = batch_df.toArrow()
    con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")
    con.execute("ATTACH 'ducklake:catalog/events.ducklake' AS events;")
    with con.cursor() as cursor:
        cursor.execute("""MERGE INTO events.user_clicks dest 
                    USING updates src
                    ON dest.user_id = src.user_id
                    WHEN MATCHED THEN
                    UPDATE SET
                        count_of_clicks = src.count_of_clicks,
                        updated_at = src.updated_at
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, user_name, count_of_clicks, updated_at)
                        VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at);
                        """)
        # cursor.execute("""MERGE INTO events.user_clicks dest 
        #             USING (SELECT user_id, user_name, MAX(timestamp) AS updated_at, COUNT(*) AS count_of_clicks
        #                     FROM updates
        #                     WHERE event_type = 'CLICK'
        #                     GROUP BY user_id, user_name) src
        #             ON dest.user_id = src.user_id
        #             WHEN MATCHED THEN
        #             UPDATE SET
        #                 count_of_clicks = dest.count_of_clicks + src.count_of_clicks,
        #                 updated_at = src.updated_at
        #             WHEN NOT MATCHED THEN
        #                 INSERT (user_id, user_name, count_of_clicks, updated_at)
        #                 VALUES (src.user_id, src.user_name, src.count_of_clicks, src.updated_at);
        #                 """)
    con.close()

    
def setup_catalog(url: str, data_path: str, **kwargs):
    con = duckdb.connect(config = {"allow_unsigned_extensions": "true"})
    con.execute("FORCE INSTALL ducklake; LOAD ducklake;")
    # con.execute(f"ATTACH '{url}' AS events ({",".join(map(lambda i: f"{i[0]} {i[1]}", options.items()))});")
    con.execute(f"ATTACH '{url}' AS events (DATA_PATH '{data_path}');")
    with con.cursor() as cursor:
        cursor.execute("USE events;")
        for option_name, option_value in kwargs.items():
            cursor.execute(f"CALL events.set_option('{option_name}', '{option_value}');")
        # cursor.execute("CREATE TABLE IF NOT EXISTS user_clicks (user_id INTEGER, user_name STRING, updated_at TIMESTAMP, count_of_clicks INTEGER);")


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
            setup_catalog(url=CONFIG["DUCKLAKE"]["DUCKDB_URL"],
                          data_path=CONFIG["DUCKLAKE"]["DATA_PATH"])
            jdbc_url = f"jdbc:duckdb:{CONFIG["DUCKLAKE"]["DUCKDB_URL"]}"
        elif args.catalog == "postgres":
            setup_catalog(url=CONFIG["DUCKLAKE"]["POSTGRES_URL"], 
                          data_path=CONFIG["DUCKLAKE"]["DATA_PATH"])
            jdbc_url = f"jdbc:duckdb:{CONFIG["DUCKLAKE"]["POSTGRES_URL"]}"

    # with duckdb.connect() as con:
    #     df = arrow_csv.read_csv('train.csv', convert_options=arrow_csv.ConvertOptions(include_columns=['id', 'vendor_id', 'passenger_count', 'trip_duration']))
    #     con.execute("ATTACH 'ducklake:catalog/events.ducklake' AS events; USE events;")
    #     con.execute("CREATE TABLE IF NOT EXISTS nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER);")
    #     con.execute("INSERT INTO nyc_taxi FROM df;")

    # return

    # spark = setup_spark()

    # spark.sql(f"""
    #     CREATE OR REPLACE TEMPORARY VIEW ducklake_tables
    #     USING jdbc
    #     OPTIONS (
    #         url "{jdbc_url}",
    #         driver "org.duckdb.DuckDBDriver",
    #         dbtable "information_schema.tables"
    #     )
    # """)

    # spark.sql(f"""
    #     CREATE TABLE nyc_taxi
    #     USING jdbc
    #     OPTIONS (
    #         url "{jdbc_url}",
    #         driver "org.duckdb.DuckDBDriver",
    #         dbtable "nyc_taxi"
    #     )
    # """)

    # spark.sql("SELECT * FROM nyc_taxi;").show(truncate=False)

    # while True:
    #     continue

    
    t1 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t2 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t3 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))
    t4 = threading.Thread(target=produce, args=(args.bootstrap_servers, args.topic, args.duration_seconds))

    t1.start()

    spark_process_kafka(
        jdbc_url=jdbc_url,
        duration_seconds=60,
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic
    )

    t1.join()


if __name__ == "__main__":
    main()
    # consume('my-topic')
