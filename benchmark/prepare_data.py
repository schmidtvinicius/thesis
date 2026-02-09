import duckdb
import os

last_id = 0
RAW_DIR = "raw_data"
DATA_DIR = "data"

for data_file in sorted(os.listdir(RAW_DIR)):
    table = duckdb.sql(f"SELECT *, (row_number() OVER ()) + {last_id} AS trip_id FROM '{os.path.join(RAW_DIR,data_file)}'")
    last_id += table.shape[0]
    table.write_parquet(os.path.join(DATA_DIR, data_file))
