import adbc_driver_manager
import argparse
import lakehouse
import os
import pandas as pd
import pyarrow.parquet as pq

from dotenv import load_dotenv

# This needs to happens before we import pyiceberg, otherwise, it doesn't know about the variables in the .env file
# load_dotenv()

from pyiceberg.catalog import _ENV_CONFIG
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import IntegerType, StringType, NestedField

schema = Schema(
    NestedField(field_id=1, name="id", field_type=StringType()),
    NestedField(field_id=2, name="vendor_id", field_type=IntegerType()),
    NestedField(field_id=3, name="passenger_count", field_type=IntegerType()),
    NestedField(field_id=4, name="trip_duration", field_type=IntegerType()),
)


def main():
    print(_ENV_CONFIG.config)
    iceberg_catalog = load_catalog(**{
        "type": "rest",
        "header.X-Iceberg-Access-Delegation": "vended-credentials",
        "uri": "http://localhost:8181/api/catalog",
        "realm": "POLARIS",
        "credential": "root:s3cr3t",
        "warehouse": "iceberg_catalog",
        "scope": "PRINCIPAL_ROLE:ALL",
        "token-refresh-enabled": "true",
        "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO"
    })
    iceberg_catalog.create_namespace_if_not_exists("events")
    print(iceberg_catalog.list_namespaces())
    iceberg_catalog.create_table(("events","nyc_taxi"), schema=schema)
    print(iceberg_catalog.list_tables("events"))


def get_args():
    pass
    # pq.read_table()
    # adbc_driver_manager.AdbcConnection()


if __name__ == "__main__":
    main()
