import duckdb
import json
import pyarrow as pa
import time

from datetime import datetime
from .arrow_interface import ArrowInterface
from .dataset import Dataset
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

class KafkaInterface:

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = AdminClient(conf={"bootstrap.servers": bootstrap_servers})
        

    def produce(self, topic: str, dataset: Dataset, total: int):
        
        producer = Producer({"bootstrap.servers": self.bootstrap_servers,})

        for _ in range(total):
            producer.produce(topic, json.dumps(dataset.get_next_event()))
            producer.flush(10000)

        print(f"Finished producing. In total, {total} events were produced")


    async def create_topic(self, topic: str):
        new_topic = NewTopic(topic)
        try:
            self.admin_client.create_topics([new_topic])
        except KafkaException as e:
            print(f"Error creating Kafka topic: {e}")

    
    async def delete_topic(self, topic: str):
        try:
            self.admin_client.delete_topics([topic])
        except KafkaException as e:
            print(f"Error deleting Kafka topic: {e}")


    def consume_and_write(self, topic: str, lakehouse: ArrowInterface, total_events: int, schema: pa.Schema, write_batch_size = 100):
        print(f"Schema {schema}")
        consumer = Consumer({"bootstrap.servers": self.bootstrap_servers, "group.id": lakehouse.__class__.__name__, "auto.offset.reset": "earliest"})
        consumer.subscribe([topic])
        table = schema.empty_table()
        processed = 0
        amimir = 0
        while processed < total_events:
            msg = consumer.poll(1.0)
            if msg is None:
                print("No message yet...")
                amimir += 1
                time.sleep(5)
                continue
            if error := msg.error():
                if error.code() == KafkaError._PARTITION_EOF:
                    print("Reached end of offset, sutting down")
                    break
                continue
            print(type(msg.value()))
            event: dict = json.loads(msg.value().decode("utf-8"))
            print(event)
            # event.pop("pickup_datetime")
            # event.pop("dropoff_datetime")
            table = pa.concat_tables([table, pa.Table.from_pylist([event], schema)])
            processed += 1
            if table.num_rows >= write_batch_size:
                lakehouse.write_to_table(table)
                table = schema.empty_table()
        print(f"Processed {processed} events in total. Slept {amimir} times in the process")


# class CustomJSONDecoder(json.JSONDecoder):

#     def decode(s: str) -> any:
#         if datetime.
