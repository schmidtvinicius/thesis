import argparse
import asyncio
import os
from types import LambdaType
import pyarrow as pa
import threading
import time

from benchmark.dataset import Dataset
from benchmark.kafka_interface import KafkaInterface
from dotenv import load_dotenv
from multiprocessing import Process

# This needs to happens before we import pyiceberg, otherwise, it doesn't know about the variables in the .env file
load_dotenv()

from benchmark.arrow_interface.arrow_interface import ArrowInterface
from benchmark.arrow_interface.ducklake_interface import DuckLakeInterface
from benchmark.arrow_interface.iceberg_interface import IcebergInterface

TABLE_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("vendor_id", pa.int32(), nullable=False),
    pa.field("passenger_count", pa.int32(), nullable=False),
    pa.field("trip_duration", pa.int32(), nullable=False),
    pa.field("pickup_datetime", pa.timestamp("s", tz="America/New_York"), nullable=False)
])


def get_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("--dataset", help="The path to a dataset")
    # parser.add_argument("--format", choices=ALLOWED_FORMATS, required=False,)
    parser.add_argument("--write-batch-size", type=int, default=1)
    # parser.add_argument("--total-events", type=int, help="The number of events to generate")
    parser.add_argument("--lakehouse", choices=["iceberg", "delta", "ducklake", "all"], default="ducklake")
    parser.add_argument("--client", choices=["native", "duckdb"], default="native", help="The Python client used to interact with each table format.")
    return parser.parse_args()
        

async def run_experiment(
        lakehouses: list[ArrowInterface],
        kafka_interface: KafkaInterface,
        topic: str,
        dataset: Dataset,
        total_events: int, 
        write_batch_size: int = 1):
            
    experiments = {"experiment": [], "dataset": []}
    total_start_time = time.perf_counter()
    for i, lakehouse in enumerate(lakehouses):
        experiments["experiment"].append(f"Experiment_{i}")
        await kafka_interface.create_topic(topic)
        stop_event = threading.Event()
        p1 = Process(target=kafka_interface.produce, args=(topic, dataset, total_events))
        p1.start()
        kafka_interface.consume_and_write(topic, lakehouse, total_events, dataset.schema, write_batch_size)
        p1.join()
        await kafka_interface.delete_topic(topic)
        # lakehouse.write_to_table(table)
    total_end_time = time.perf_counter()


async def main():
    from confluent_kafka import Producer
    from datetime import datetime
    import json
    total_events = 100_000
    args = get_args()
    dataset = Dataset()
    kafka_interface = KafkaInterface(os.getenv("KAFKA_BOOTSTRAP_SERVERS"))

    # start_time = datetime.now()
    # kafka_interface.produce(os.getenv("KAFKA_TOPIC"), dataset, total_events, threading.Event())
    # end_time = datetime.now()
    # print(f"Took {(end_time - start_time).total_seconds()} seconds to produce {total_events} events")
    # return
        
    if args.lakehouse == "all":
        lakehouses = [IcebergInterface(table_schema=dataset.schema), DuckLakeInterface(dataset.schema)]
    elif args.lakehouse == "iceberg":
        lakehouses = [IcebergInterface(table_schema=dataset.schema)]
    elif args.lakehouse == "ducklake":
        lakehouses = [DuckLakeInterface(table_schema=dataset.schema)]
    else:
        raise NotImplementedError
    experiment_stats = vars(args)
    await run_experiment(lakehouses, kafka_interface, os.getenv("KAFKA_TOPIC"), dataset, total_events, args.write_batch_size)


if __name__ == "__main__":
    asyncio.run(main())
