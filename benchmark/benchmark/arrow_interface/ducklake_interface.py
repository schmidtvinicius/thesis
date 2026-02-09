import duckdb
import os
import pyarrow as pa
import time

from .arrow_interface import ArrowInterface
from ..dataset import SCHEMA

class DuckLakeInterface(ArrowInterface):

    def __init__(self):
        super().__init__()
        self.client = "duckdb"
        self.inlining = bool(os.getenv("DUCKLAKE_INLINING"))
        self.catalog_location = os.getenv("DUCKLAKE_CATALOG_LOCATION")
        self.data_location = os.getenv("DUCKLAKE_DATA_LOCATION")
        self.catalog_name = os.getenv("DUCKLAKE_CATALOG_NAME")
        self.table_name = os.getenv("TABLE_NAME")
        self.connection = duckdb.connect(config={"threads": os.getenv("THREADS")})
        self.connection.execute("INSTALL ducklake; LOAD ducklake;")
        self.connection.execute(f"ATTACH 'ducklake:{self.catalog_location}' AS {self.catalog_name} (DATA_PATH '{self.data_location}');")
        self.connection.execute(f"USE {self.catalog_name};")

    
    def __str__(self) -> str:
        if self.inlining: return "ducklake-inlining"
        return "ducklake"
    

    def __del__(self):
        self.connection.close()


    def create_table(self):
        arrow_table = SCHEMA.empty_table()
        self.connection.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} AS FROM arrow_table;")
        self.connection.execute(f"CALL {self.catalog_name}.set_option('parquet_compression', '{os.getenv("PARQUET_COMPRESSION")}');")
        if self.inlining:
            self.connection.execute(f"CALL {self.catalog_name}.set_option('data_inlining_row_limit', 2);")

    
    def write_to_table(self, data: pa.Table) -> int:
        start = time.perf_counter_ns()
        self.connection.execute(f"INSERT INTO {self.table_name} FROM data;")
        end = time.perf_counter_ns()
        return end - start
    

    def flush_inlined_data(self) -> int|None:
        if not self.inlining:
            return
        start = time.perf_counter_ns()
        self.connection.execute(f"CALL ducklake_flush_inlined_data('{self.catalog_name}', table_name => '{self.table_name}');")
        end = time.perf_counter_ns()
        return end - start


    def read_table(self):
        return super().read_table()
    

    def delete_table(self):
        self.connection.execute(f"DROP TABLE {self.table_name};")
