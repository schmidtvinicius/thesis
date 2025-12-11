from dotenv import load_dotenv
# load_dotenv()

import deltalake
import os
import pyarrow as pa
import pyiceberg

from abc import ABC, abstractmethod

class ArrowInterface(ABC):
    
    @abstractmethod
    def write_to_table(self, data) -> None: ...

    @abstractmethod
    def create_table(self, table_name: str) -> None: ...

    @abstractmethod
    def read_table(self): ...


class IcebergInterface(ArrowInterface):
    """A class for interacting with Iceberg tables through a catalog. Configuration 
    for the catalog should be in a `.env` file in the root directory, as described
    here: https://py.iceberg.apache.org/configuration/
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        self.catalog = pyiceberg.catalog.load_catalog()
        self.catalog.create_namespace_if_not_exists(kwargs["namespace"])
        self.table = self.catalog.create_table_if_not_exists((kwargs["namespace"],kwargs["table_name"]), schema=kwargs["table_schema"])


    def create_table(self, table_name: str, schema: pa.Schema):
        self.catalog.create_table_if_not_exists((self.namespace, table_name), schema=schema)


    def write_to_table(self, data):
        self.table.append(data)

    
    def read_table(self):
        return self.table.scan().to_arrow()
    

class DuckLakeInterface(ArrowInterface):

    def __init__(self):
        super().__init__()

    
    def write_to_table(self, data):
        return super().write_to_table(data)
    

    def read_table(self):
        return super().read_table()
    

    def create_table(self, table_name):
        return super().create_table(table_name)
    

class DeltaInterface(ArrowInterface):
    """
    Currently, it is quite tricky to get delta-rs to work with a local OSS Unity Catalog.
    Although it is possible to read Delta tables with a few adjustments to the delta-rs
    source code, it is not possible to write to it, which defeats the whole purpose of our
    experiments. An issue was opened here: https://github.com/delta-io/delta-rs/issues/3966
    to try to improve compatibility between delta-rs and the OS version of UC. In addition,
    the only way to consistently write data to Delta+UC is by using Spark, which, again,
    deviates from the goal of our experiments, so for now Delta won't be considered in our
    experiments.
    """
    def __init__(self, **kwargs):
        super().__init__()
        # self.catalog_uri = kwargs["catalog_uri"]
        # arrow_table = pa.Table.from_pylist([{"id": "id1234567", "vendor_id": 2, "passenger_count": 3, "trip_duration": 123}], schema=kwargs["table_schema"])
        # table = deltalake.DeltaTable.create(table_uri="file:///var/tmp/delta/nyc_taxi", schema=kwargs["table_schema"])
        # table.alter.set_table_properties({"delta.minReaderVersion":"3", "delta.minWriterVersion": "7"})
        # deltalake.write_deltalake(table_or_uri=table, data=arrow_table, mode="append")
        # # table = deltalake.DeltaTable(table_uri="file:///var/tmp/delta/nyc_taxi")
        # deltalake.write_deltalake()
        # table.create_write_transaction(deltalake.transaction.AddAction())
        # table.alter.set_table_properties({"delta.minReaderVersion": "3", "delta.minWriterVersion": "7"})
        # deltalake.write_deltalake("uc://unity.default.nyc_taxi", arrow_table)


    def write_to_table(self, data):
        raise NotImplementedError
    

    def read_table(self):
        raise NotImplementedError
    

    def create_table(self, table_name):
        raise NotImplementedError
