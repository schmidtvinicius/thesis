import duckdb
import os
import pyarrow as pa

from .arrow_interface import ArrowInterface

class DuckLakeInterface(ArrowInterface):

    def __init__(self, table_schema: pa.Schema):
        super().__init__()
        self.catalog_location = os.getenv("DUCKLAKE_CATALOG_LOCATION")
        self.data_location = os.getenv("DUCKLAKE_DATA_LOCATION")
        self.catalog_name = os.getenv("DUCKLAKE_CATALOG_NAME")
        self.table_name = os.getenv("TABLE_NAME")
        with duckdb.connect() as conn:
            conn.execute("INSTALL ducklake; LOAD ducklake;")
            conn.execute(f"ATTACH 'ducklake:{self.catalog_location}' AS {self.catalog_name} (DATA_PATH '{self.data_location}');")
            conn.execute(f"USE {self.catalog_name};")
            arrow_table = table_schema.empty_table()
            conn.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} AS FROM arrow_table;")
            # conn.execute(f"ALTER TABLE {self.table_name} SET PARTITIONED BY (month(pickup_datetime), day(pickup_datetime));")

    
    def write_to_table(self, data: pa.Table):
        with duckdb.connect() as conn:
            conn.execute(f"ATTACH 'ducklake:{self.catalog_location}' AS {self.catalog_name};")
            conn.execute(f"USE {self.catalog_name};")
            conn.execute(f"INSERT INTO {self.table_name} FROM data;")


    def read_table(self):
        return super().read_table() 
