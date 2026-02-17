import argparse
import asyncio
import multiprocessing
import os
import threading
import time

# This needs to happens before we import pyiceberg, otherwise, it doesn't know about the variables in the .env file
from dotenv import load_dotenv
load_dotenv()

from benchmark.arrow_interface import ArrowInterface, DuckLakeInterface, IcebergInterface, IcebergDuckDBInterface
from benchmark.dataset import Dataset
from benchmark.kafka_interface import KafkaInterface
from benchmark.metrics import collect_hardware_metrics
from benchmark.results import setup_results_db, save_results


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch-write-size", default=1, type=int, help="The number of events to accumulate before writing them to the table")
    parser.add_argument("--minutes", type=int, default=5, help="The time in minutes each experiment should run for")
    parser.add_argument("--lakehouse", choices=["iceberg", "ducklake", "all"], default="ducklake")
    parser.add_argument("--client", choices=["native", "duckdb"], default="native", help="The Python client used to interact with each table format.")
    return parser.parse_args()
        

async def run_experiments(
        lakehouses: list[ArrowInterface],
        kafka_interface: KafkaInterface,
        dataset: Dataset,
        topic: str,
        total_minutes: int,
        batch_write_size: int):
            
    total_start_time = time.perf_counter()
    for lakehouse in lakehouses:
        for i in range(3):
            if isinstance(lakehouse, DuckLakeInterface):
                lakehouse.create_table(batch_write_size)
            else:
                lakehouse.create_table()
                
            await kafka_interface.create_topic(topic)
            stop_event_p = multiprocessing.Event()
            stop_event_t = threading.Event()
            events_produced = multiprocessing.Value("i", 0)
            cpu_percentage = []
            bytes_written = []
            write_times = []
            try:
                p1 = multiprocessing.Process(target=kafka_interface.produce, args=(topic, dataset, events_produced, stop_event_p))
                t1 = threading.Thread(target=collect_hardware_metrics, args=(cpu_percentage, bytes_written, write_times, stop_event_t))
                p1.start()
                t1.start()
                if batch_write_size > 1:
                    exp_duration_ns, waiting, flush_inlined_duration, event_stats = kafka_interface.consume_and_write_batches(topic, lakehouse, str(i), total_minutes, batch_write_size)
                else:
                    exp_duration_ns, waiting, flush_inlined_duration, event_stats = kafka_interface.consume_and_write(topic, lakehouse, str(i), total_minutes)
                stop_event_t.set()
                stop_event_p.set()
                # p1.join()
            finally:
                p1.join()
                t1.join()
            await kafka_interface.delete_topic(topic)
            results_start = time.perf_counter()
            save_results(
                str(lakehouse)+f"-{i}",
                lakehouse.client,
                exp_duration_ns,
                events_produced.value,
                flush_inlined_duration,
                waiting,
                event_stats,
                cpu_percentage,
                bytes_written,
                write_times,
                batch_write_size
            )
            results_end = time.perf_counter()
            print(f"took {results_end - results_start} to save results")
            lakehouse.delete_table()
    total_end_time = time.perf_counter()
    print(f"Finished all experiments! The total time was {total_end_time - total_start_time} seconds.")


async def main():
    import pyarrow as pa
    from benchmark.dataset import SCHEMA
    dataset = Dataset(os.getenv("DATASET_PATH"))
    iceberg = IcebergInterface()
    iceberg.create_table()

    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, SCHEMA) as writer:
        writer.write_batch(dataset.data.read_next_batch())

    with pa.ipc.open_stream(sink.getvalue()) as reader:
        event = reader.read_all()
    
    iceberg.write_to_table(event)

    return

    args = get_args()
    kafka_interface = KafkaInterface(os.getenv("KAFKA_BOOTSTRAP_SERVERS"))
    dataset = Dataset(os.getenv("DATASET_PATH"))
    setup_results_db(os.getenv("SQL_INIT_PATH"), os.getenv("RESULTS_PATH"))


    if args.lakehouse == "all":
        lakehouses = [IcebergInterface() if args.client == "native" else IcebergDuckDBInterface(), DuckLakeInterface()]
    elif args.lakehouse == "iceberg":
        lakehouses = [IcebergInterface() if args.client == "native" else IcebergDuckDBInterface()]
    elif args.lakehouse == "ducklake":
        lakehouses = [DuckLakeInterface()]
    else:
        raise NotImplementedError
    
    await run_experiments(lakehouses, kafka_interface, dataset, os.getenv("KAFKA_TOPIC"), args.minutes, args.batch_write_size)


if __name__ == "__main__":
    asyncio.run(main())
