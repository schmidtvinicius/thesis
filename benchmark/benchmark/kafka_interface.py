import duckdb
import json
import pyarrow as pa
import time

from datetime import datetime
from .arrow_interface import ArrowInterface, DuckLakeInterface
from .dataset import Dataset, SCHEMA
from confluent_kafka import Consumer, Producer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from io import BytesIO


class KafkaInterface:

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = AdminClient(conf={"bootstrap.servers": bootstrap_servers})
        

    def produce(self, topic: str, dataset: Dataset, events_produced, stop_event):
        producer = Producer({"bootstrap.servers": self.bootstrap_servers})
        while not stop_event.is_set():
            producer.produce(topic, dataset.get_next_batch())
            producer.flush(10000)
            events_produced.value += 1


    async def create_topic(self, topic: str):
        try:
            self.admin_client.create_topics([NewTopic(topic)])
        except KafkaException as e:
            print(f"Error creating Kafka topic: {e}")

    
    async def delete_topic(self, topic: str):
        try:
            self.admin_client.delete_topics([topic])
        except KafkaException as e:
            print(f"Error deleting Kafka topic: {e}")


    def consume_and_write(self, topic: str, lakehouse: ArrowInterface, run_number: str, total_minutes: int):
        consumer = Consumer({"bootstrap.servers": self.bootstrap_servers, "group.id": lakehouse.__class__.__name__+run_number, "auto.offset.reset": "earliest"})
        consumer.subscribe([topic])
        waiting = 0
        total_ns = int(total_minutes * 60 * 1e9)
        event_stats = []
        start_time = time.perf_counter_ns()
        while (time.perf_counter_ns() - start_time) < total_ns:
            msg = consumer.poll(1.0)
            if msg is None:
                print("No message yet...")
                waiting += 1
                time.sleep(5)
                continue
            # if error := msg.error():
            #     if error.code() == KafkaError._PARTITION_EOF:
            #         print("Reached end of offset, sutting down")
            #         break
            #     continue

            read_start = time.perf_counter_ns()
            # event = duckdb.read_json(BytesIO(msg.value())).to_arrow_table()
            with pa.ipc.open_stream(msg.value()) as reader:
                event = reader.read_all()
            read_end = time.perf_counter_ns()

            write_duration = lakehouse.write_to_table(event)
            event_stats.append((event["trip_id"][0].as_py(), read_end - read_start, write_duration))
        
        flush_inlined_duration = None
        if isinstance(lakehouse, DuckLakeInterface) and lakehouse.inlining:
            flush_inlined_duration = lakehouse.flush_inlined_data()
        
        end_time = time.perf_counter_ns()
        return (end_time - start_time, waiting*5, flush_inlined_duration, event_stats)
    

    def consume_and_write_batches(self, topic: str, lakehouse: ArrowInterface, run_number: str, total_minutes: int, batch_size: int):
        consumer = Consumer({"bootstrap.servers": self.bootstrap_servers, "group.id": lakehouse.__class__.__name__+run_number, "auto.offset.reset": "earliest"})
        consumer.subscribe([topic])
        waiting = 0
        total_ns = int(total_minutes * 60 * 1e9)
        batch_table = SCHEMA.empty_table()
        last_event_id = None
        event_stats = []

        start_time = time.perf_counter_ns()
        while (time.perf_counter_ns() - start_time) < total_ns:
            msg = consumer.poll(1.0)
            if msg is None:
                print("No message yet...")
                waiting += 1
                time.sleep(5)
                continue

            read_start = time.perf_counter_ns()
            with pa.ipc.open_stream(msg.value()) as reader:
                event = reader.read_all()
            read_end = time.perf_counter_ns()
            batch_table = pa.concat_tables([batch_table, event])
            last_event_id = event["trip_id"][0].as_py()

            write_duration = None
            if batch_table.num_rows >= batch_size:
                write_duration = lakehouse.write_to_table(batch_table)
                batch_table = SCHEMA.empty_table()

            event_stats.append((last_event_id, read_end - read_start, write_duration))
        
        if batch_table.num_rows > 0:
            write_duration = lakehouse.write_to_table(batch_table)
            event_stats.append((last_event_id, None, write_duration))
        
        flush_inlined_duration = None
        if isinstance(lakehouse, DuckLakeInterface) and lakehouse.inlining:
            flush_inlined_duration = lakehouse.flush_inlined_data()
        
        end_time = time.perf_counter_ns()
        return (end_time - start_time, waiting*5, flush_inlined_duration, event_stats) 
