import os
import pyarrow as pa

from .arrow_interface import ArrowInterface
from pyiceberg.catalog import load_catalog


class IcebergInterface(ArrowInterface):
    """A class for interacting with Iceberg tables through a catalog. Configuration 
    for the catalog should be in a `.env` file in the root directory, as described
    here: https://py.iceberg.apache.org/configuration/
    """
    def __init__(self, table_schema: pa.Schema):
        super().__init__()
        self.catalog = load_catalog()
        self.catalog_namespace = os.getenv("ICEBERG_CATALOG_NAMESPACE")
        self.catalog.create_namespace_if_not_exists(self.catalog_namespace)
        self.table = self.catalog.create_table_if_not_exists((self.catalog_namespace,os.getenv("TABLE_NAME")), schema=table_schema)


    def write_to_table(self, data):
        self.table.append(data)

    
    def read_table(self):
        return self.table.scan().to_arrow()
