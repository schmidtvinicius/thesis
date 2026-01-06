import duckdb

from datetime import datetime

ALLOWED_FORMATS = ["csv", "parquet"]

class Dataset():

    def get_next_event(self) -> dict:
        return {k:(datetime.isoformat(v) if isinstance(v, datetime) else v)  for k,v in zip(self.data.columns, self.data.fetchone())}
    

class CSVDataset(Dataset):
    
    def __init__(self, source: str, sf: int|None = None):
        super().__init__()
        self.data = duckdb.read_csv(source)
        self.schema = self.data.arrow().schema


class ParquetDataset(Dataset):

    def __init__(self, soruce: str, sf: int|None = None):
        super().__init__()
        self.data = duckdb.read_parquet(soruce)
        self.schema = self.data.arrow().schema


class TPCHDataset(Dataset):

    def __init__(self, sf: int = 1):
        raise NotImplementedError()


    def get_next_event(self) -> dict:
        pass


def create_dataset(source: str, format: str) -> Dataset:
    if source.lower() == "tpch":
        return TPCHDataset()
    if format.lower() is None or format.lower() not in ALLOWED_FORMATS:
        raise ValueError(f"When `source` is not 'tpch', `format` must be specified to one of {ALLOWED_FORMATS}")
    if format.lower() == "csv":
        return CSVDataset(source=source)
    if format.lower() == "parquet":
        return ParquetDataset(source=source)