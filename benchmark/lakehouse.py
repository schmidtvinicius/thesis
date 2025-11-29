import os

from pyspark.sql import SparkSession

class DuckLake():

    def __init__(self) -> SparkSession:
        self.spark = SparkSession.builder \
                .appName(self.__class__.__name__) \
                .config("spark.jars.packages", "org.duckdb:duckdb_jdbc:1.4.2.0") \
                .config('spark.driver.defaultJavaOptions', '-Djava.security.manager=allow') \
                .getOrCreate()


class Delta():

    def __new__(cls):
        pass

    def __init__(self, data_path: str):
        self.spark = SparkSession.builder \
                    .appName(self.__class__.__name__) \
                    .config("spark.jars.packages", "io.delta:delta-spark_2.13:4.0.0,io.unitycatalog:unitycatalog-spark_2.13:0.3.0") \
                    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
                    .config("spark.sql.catalog.spark_catalog", "io.unitycatalog.spark.UCSingleCatalog") \
                    .config("spark.sql.catalog.unity", "io.unitycatalog.spark.UCSingleCatalog") \
                    .config("spark.sql.catalog.unity.token", "") \
                    .config("spark.sql.defaultCatalog", "unity") \
                    .config("spark.sql.catalog.unity.uri", os.environ.get('DELTA_CATALOG_URI')) \
                    .getOrCreate()

        
    def setup_table(self):
        self.spark.sql(f"""CREATE TABLE IF NOT EXISTS
                default.nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER)
                USING DELTA LOCATION '{self.data_path}'
                TBLPROPERTIES ('delta.enableDeletionVectors' = true);
                    """)


class Iceberg():

    def __init__(self, catalog_name: str):
        self.spark = SparkSession.builder \
                    .appName(self.__class__.__name__) \
                    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-4.0_2.13:1.10.0") \
                    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
                    .config(f"spark.sql.catalog.polaris", "org.apache.iceberg.spark.SparkCatalog") \
                    .config(f"spark.sql.catalog.polaris.type", "rest") \
                    .config(f"spark.sql.catalog.polaris.warehouse", 'polaris') \
                    .config(f"spark.sql.catalog.polaris.uri", os.environ.get('ICEBERG_CATALOG_URI')) \
                    .config(f"spark.sql.catalog.polaris.credential", f"{os.environ.get('POLARIS_CLIENT_ID')}:{os.environ.get('POLARIS_SECRET')}") \
                    .config(f"spark.sql.catalog.polaris.scope", "PRINCIPAL_ROLE:ALL") \
                    .config("spark.sql.defaultCatalog", "polaris") \
                    .config("spark.sql.catalog.polaris.metrics-reporter-impl", "org.apache.iceberg.metrics.LoggingMetricsReporter") \
                    .getOrCreate()
        self.catalog_name = catalog_name

    
    def setup_table(self):
        self.spark.sql(f"USE {self.catalog_name};")
        self.spark.sql("CREATE NAMESPACE IF NOT EXISTS events;")
        self.spark.sql("USE events;")
        self.spark.sql("CREATE TABLE IF NOT EXISTS nyc_taxi (id STRING, vendor_id INTEGER, passenger_count INTEGER, trip_duration INTEGER);")
        