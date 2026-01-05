import duckdb

from datetime import datetime

class Dataset():
    ALLOWED_FORMATS = ["csv", "parquet"]

    def __init__(self, source: str, format: str, sf: int|None = None):
        if format not in Dataset.ALLOWED_FORMATS:
            raise AssertionError(f"`format` '{format}' not supported, must be one of {Dataset.ALLOWED_FORMATS}")
        
        if format.lower() == "csv":
            self.data = duckdb.read_csv(source)
        elif format.lower() == "parquet":
            self.data = duckdb.read_parquet(source)
            
        self.schema = self.data.arrow().schema


    def get_next_event(self) -> dict:
        return {k:(datetime.isoformat(v) if isinstance(v, datetime) else v)  for k,v in zip(self.data.columns, self.data.fetchone())}
