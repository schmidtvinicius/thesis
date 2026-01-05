from .arrow_interface import ArrowInterface

class DeltaInterface(ArrowInterface):
    """
    Currently, it is quite tricky to get delta-rs to work with a local OSS Unity Catalog.
    Although it is possible to read Delta tables with a few adjustments to the delta-rs
    source code, it is not possible to write to it, which defeats the whole purpose of our
    experiments. An issue was opened here: https://github.com/delta-io/delta-rs/issues/3966
    to try to improve compatibility between delta-rs and the OS version of UC. In addition,
    the only way to consistently write data to Delta+UC is by using Spark, which, again,
    deviates from the goal of our experiments, so for now Delta won't be considered in our
    experiments.
    """
    def __init__(self, **kwargs):
        super().__init__()
        # self.catalog_uri = kwargs["catalog_uri"]
        # arrow_table = pa.Table.from_pylist([{"id": "id1234567", "vendor_id": 2, "passenger_count": 3, "trip_duration": 123}], schema=kwargs["table_schema"])
        # table = deltalake.DeltaTable.create(table_uri="file:///var/tmp/delta/nyc_taxi", schema=kwargs["table_schema"])
        # table.alter.set_table_properties({"delta.minReaderVersion":"3", "delta.minWriterVersion": "7"})
        # deltalake.write_deltalake(table_or_uri=table, data=arrow_table, mode="append")
        # # table = deltalake.DeltaTable(table_uri="file:///var/tmp/delta/nyc_taxi")
        # deltalake.write_deltalake()
        # table.create_write_transaction(deltalake.transaction.AddAction())
        # table.alter.set_table_properties({"delta.minReaderVersion": "3", "delta.minWriterVersion": "7"})
        # deltalake.write_deltalake("uc://unity.default.nyc_taxi", arrow_table)


    def write_to_table(self, data):
        raise NotImplementedError
    

    def read_table(self):
        raise NotImplementedError
