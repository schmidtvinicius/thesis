import json
import numpy as np
import random
import time

from confluent_kafka import Producer, Consumer
from datetime import datetime

def produce(bootstrap_servers: str, topic: str, duration_seconds: int):
    producer = Producer({"bootstrap.servers": bootstrap_servers,})
    user_names = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
    
    print(f"Producing to topic {topic}...")
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        user_id = np.random.randint(0,10)
        event = {
            "timestamp": datetime.isoformat(datetime.now()),
            "user_id": user_id,
            "user_name": user_names[user_id],
            "event_type": random.choice(['CLICK', 'SCROLL', 'SWIPE'])
        }
        producer.produce(topic, json.dumps(event))
        producer.flush(10000)


def consume(topic: str) -> None:
    consumer = Consumer({
        "bootstrap.servers": 'localhost:9092',
        "group.id": 'test-consumer',
        "auto.offset.reset": "earliest"
    })
    consumer.subscribe([topic])
    msg = consumer.poll(15)
    total = 0
    while msg is not None and not msg.error():
        total += 1
        print(json.loads(msg.value().decode("utf-8")))
        msg = consumer.poll(15)
    print(f'finished consuming messages, in total {total} messages were consumed')
    # if msg.error():
    #     print(f"Kafka error: {msg.error()}")    


if __name__ == '__main__':
    # produce('localhost:9092', 'my-topic', 5)
    consume('my-topic')