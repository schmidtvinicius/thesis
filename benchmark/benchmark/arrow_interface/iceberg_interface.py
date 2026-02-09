import duckdb
import os
import pyarrow as pa
import time

from .arrow_interface import ArrowInterface
from ..dataset import SCHEMA
from pyiceberg.catalog import load_catalog


class IcebergInterface(ArrowInterface):
    """A class for interacting with Iceberg tables through a catalog. Configuration 
    for the catalog should be in a `.env` file in the root directory, as described
    here: https://py.iceberg.apache.org/configuration/
    """
    def __init__(self):
        super().__init__()
        self.client = "pyiceberg"
        self.catalog = load_catalog()
        self.catalog_namespace = os.getenv("ICEBERG_CATALOG_NAMESPACE")
        self.table_name = os.getenv("TABLE_NAME")
        self.catalog.create_namespace_if_not_exists(self.catalog_namespace)

    
    def __str__(self):
        return "iceberg"


    def write_to_table(self, data: pa.Table) -> int:
        start = time.perf_counter_ns()
        self.table.append(data)
        end = time.perf_counter_ns()
        return end - start

    
    def read_table(self):
        return self.table.scan().to_arrow()
    

    def create_table(self):
        self.table = self.catalog.create_table_if_not_exists((self.catalog_namespace,os.getenv("TABLE_NAME")), schema=SCHEMA, properties={"write.parquet.compression-codec": os.getenv("PARQUET_COMPRESSION")})
    

    def delete_table(self):
        self.catalog.drop_table(f"{self.catalog_namespace}.{self.table_name}")
    

class IcebergDuckDBInterface(ArrowInterface):
    
    def __init__(self):
        super().__init__()
        self.client = "duckdb"
        self.catalog = load_catalog()
        self.catalog_name = os.getenv("ICEBERG_CATALOG_NAME")
        self.catalog_namespace = os.getenv("ICEBERG_CATALOG_NAMESPACE")
        self.table_name = os.getenv("TABLE_NAME")
        self.full_table_name = ".".join([self.catalog_name, self.catalog_namespace, self.table_name])
        self.catalog.create_namespace_if_not_exists(self.catalog_namespace)
        self.connection = duckdb.connect(config={"threads": os.getenv("THREADS")})
        self.connection.execute(f"""CREATE SECRET iceberg_secret (
                                    TYPE iceberg,
                                    CLIENT_ID '{os.getenv("POLARIS_CLIENT_ID")}',
                                    CLIENT_SECRET '{os.getenv("POLARIS_SECRET")}',
                                    OAUTH2_SERVER_URI '{os.getenv("POLARIS_OAUTH2_URI")}');""")
        self.connection.execute(f"""ATTACH '{self.catalog_name}' AS {self.catalog_name} (
                                    TYPE iceberg,
                                    SECRET iceberg_secret,
                                    ENDPOINT '{os.getenv("ICEBERG_CATALOG_URI")}');""")

    
    def __del__(self):
        self.connection.close()

    
    def __str__(self):
        return "iceberg"
    

    def create_table(self):
        arrow_table = SCHEMA.empty_table()
        self.connection.execute(f"CREATE TABLE IF NOT EXISTS {self.full_table_name} AS FROM arrow_table;")
        self.connection.execute(f"""CALL set_iceberg_table_properties({self.full_table_name}, {{
                                    'write.parquet.compression-codec': '{os.getenv("PARQUET_COMPRESSION")}',
                                    'write.metadata.path': '{os.path.join(os.getenv("ICEBERG_STORAGE_LOCATION"), self.catalog_namespace, self.table_name, "metadata")}'}});""")


    def write_to_table(self, data: pa.Table) -> int:
        start = time.perf_counter_ns()
        self.connection.execute(f"INSERT INTO {self.full_table_name} FROM data;")
        end = time.perf_counter_ns()
        return end - start
    

    def read_table(self):
        return super().read_table()
    

    def delete_table(self):
        self.connection.execute(f"DROP TABLE {self.full_table_name};")
