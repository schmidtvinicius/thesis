import os
import pyarrow as pa
import time

from benchmark.arrow_interface import DuckLakeInterface
from benchmark.dataset import Dataset, SCHEMA

def main():

    dataset = Dataset(os.getenv("DATASET_PATH"))
    ducklake = DuckLakeInterface()

    merge_times = []

    for _ in range(3):
        ducklake.create_table(1)
        for _ in range(30_000):
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, SCHEMA) as writer:
                writer.write_batch(dataset.data.read_next_batch())

            with pa.ipc.open_stream(sink.getvalue()) as reader:
                event = reader.read_all()

            ducklake.write_to_table(event)
        merge_start = time.perf_counter_ns()
        ducklake.connection.execute(f"CALL ducklake_merge_adjacent_files('{ducklake.catalog_name}');")
        merge_end = time.perf_counter_ns()
        merge_times.append((merge_end - merge_start)/1e9)
        ducklake.delete_table()

    print(f"Time taken to merge 30,000 files for three different runs: {merge_times}")


if __name__ == "__main__":
    main()