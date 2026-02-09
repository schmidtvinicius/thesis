import duckdb
import pyarrow as pa

from datetime import datetime


SCHEMA = pa.schema([
    ("VendorID", pa.int32()),
    ("tpep_pickup_datetime", pa.timestamp("us")),
    ("tpep_dropoff_datetime", pa.timestamp("us")),
    ("passenger_count", pa.int64()),
    ("trip_distance", pa.float64()),
    ("RatecodeID", pa.int64()),
    ("store_and_fwd_flag", pa.string()),
    ("PULocationID", pa.int32()),
    ("DOLocationID", pa.int32()),
    ("payment_type", pa.int64()),
    ("fare_amount", pa.float64()),
    ("extra", pa.float64()),
    ("mta_tax", pa.float64()),
    ("tip_amount", pa.float64()),
    ("tolls_amount", pa.float64()),
    ("improvement_surcharge", pa.float64()),
    ("total_amount", pa.float64()),
    ("congestion_surcharge", pa.float64()),
    ("Airport_fee", pa.float64()),
    ("cbd_congestion_fee", pa.float64()),
    ("trip_id", pa.int64())
])


class Dataset():

    def __init__(self, path):
        self.data = duckdb.read_parquet(path).arrow(1)

    
    def __del__(self):
        self.data.close()


    # def get_next_event(self) -> dict:
    #     return {k:(datetime.isoformat(v, sep=" ") if isinstance(v, datetime) else v)  for k,v in zip(self.data.columns, self.data.fetchone())}
    

    def get_next_batch(self):
        sink = pa.BufferOutputStream()
        with pa.ipc.new_stream(sink, SCHEMA) as writer:
            writer.write_batch(self.data.read_next_batch())
        return sink.getvalue()
