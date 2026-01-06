import argparse
import asyncio
import benchmark.dataset as dataset
import duckdb
import json
import os
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import threading

from benchmark.dataset import ALLOWED_FORMATS, create_dataset, Dataset
from benchmark.kafka_interface import KafkaInterface
from confluent_kafka import KafkaError, Consumer
from confluent_kafka.admin import AdminClient
from dotenv import load_dotenv
from time import sleep

# This needs to happens before we import pyiceberg, otherwise, it doesn't know about the variables in the .env file
load_dotenv()

from benchmark.arrow_interface.arrow_interface import ArrowInterface
from benchmark.arrow_interface.ducklake_interface import DuckLakeInterface
from benchmark.arrow_interface.iceberg_interface import IcebergInterface
from pyarrow.csv import read_csv, ReadOptions, ParseOptions, ConvertOptions

TABLE_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("vendor_id", pa.int32(), nullable=False),
    pa.field("passenger_count", pa.int32(), nullable=False),
    pa.field("trip_duration", pa.int32(), nullable=False),
    pa.field("pickup_datetime", pa.timestamp("s", tz="America/New_York"), nullable=False)
])


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", help="The path to a dataset")
    parser.add_argument("--format", choices=ALLOWED_FORMATS, required=False)
    parser.add_argument("--write-batch-size", type=int, default=1)
    # parser.add_argument("--scale-factor", type=int, help="The scale factor to generate data at.")
    parser.add_argument("--lakehouse", choices=["iceberg", "delta", "ducklake", "all"], default="all")
    parser.add_argument("--client", choices=["native", "duckdb"], default="native", help="The Python client used to interact with each table format.")
    return parser.parse_args()
        

async def run_experiment(
        lakehouses: list[ArrowInterface],
        kafka_interface: KafkaInterface,
        topic: str,
        dataset: Dataset,
        total_events: int, 
        write_batch_size: int = 1):
    
    for lakehouse in lakehouses:
        await kafka_interface.create_topic(topic)
        t1 = threading.Thread(target=kafka_interface.produce, args=[topic, dataset, total_events])
        t1.start()
        kafka_interface.consume_and_write(topic, lakehouse, total_events, dataset.schema, write_batch_size)
        t1.join()
        await kafka_interface.delete_topic(topic)
        # lakehouse.write_to_table(table)


async def main():
    total_events = 1_000_000
    args = get_args()
    dataset = create_dataset(args.dataset, args.format)
    # kafka_admin = AdminClient(conf={"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS")})
    kafka_interface = KafkaInterface(os.getenv("KAFKA_BOOTSTRAP_SERVERS"))
        
    if args.lakehouse == "all":
        lakehouses = [IcebergInterface(table_schema=dataset.schema), DuckLakeInterface(dataset.schema)]
    elif args.lakehouse == "iceberg":
        lakehouses = [IcebergInterface(table_schema=dataset.schema)]
    elif args.lakehouse == "ducklake":
        lakehouses = [DuckLakeInterface(table_schema=dataset.schema)]
    else:
        raise NotImplementedError
    await run_experiment(lakehouses, kafka_interface, os.getenv("KAFKA_TOPIC"), dataset, total_events, args.write_batch_size)


if __name__ == "__main__":
    asyncio.run(main())
