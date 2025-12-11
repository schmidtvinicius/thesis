import adbc_driver_manager
import argparse
import duckdb
import lakehouse
import os
import pandas as pd
import pyarrow as pa
import pyarrow.csv as pa_csv
import pyarrow.parquet as pq
import requests
import asyncio

from dotenv import load_dotenv

# This needs to happens before we import pyiceberg, otherwise, it doesn't know about the variables in the .env file
load_dotenv()

from arrow_interface import DeltaInterface, IcebergInterface
from pyiceberg.catalog import _ENV_CONFIG
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import IntegerType, StringType, NestedField


def main():
    # args = get_args()

    schema = pa.schema([
        ("id", pa.string()),
        ("vendor_id", pa.int32()),
        ("passenger_count", pa.int32()),
        ("trip_duration", pa.int32()),
    ])
    table_data = pa_csv.read_csv("train.csv", 
                                    convert_options=pa_csv.ConvertOptions(
                                        include_columns=["id", "vendor_id", "passenger_count", "trip_duration"],
                                        column_types=schema))
    delta_interface = DeltaInterface(catalog_uri="uc://unity.default.nyc_taxi/", table_schema=schema)
    delta_interface.create_table('bla')

    # if args.lakehouse == "iceberg":
    #     iceberg_interface = IcebergInterface(namespace="events", table_name="nyc_taxi", table_schema=schema)
    #     iceberg_interface.write_to_table(table_data)
    #     arrow_table = iceberg_interface.read_table()
    #     conn = duckdb.connect()
    #     conn.sql("SELECT * FROM arrow_table LIMIT 100;").show()
    # elif args.lakehouse == "delta":
    #     delta_interface = DeltaInterface(catalog_uri="uc://unity.default.nyc_taxi/", table_schema=schema)
    # elif args.lakehouse == "ducklake":
    #     pass
    # else:
    #     raise NotImplementedError



def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lakehouse", choices=["iceberg", "delta", "ducklake", "all"], default="all")
    return parser.parse_args()
    # pq.read_table()
    # adbc_driver_manager.AdbcConnection()


if __name__ == "__main__":
    main()
