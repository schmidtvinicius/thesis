import json
import numpy as np
import random
import time

from confluent_kafka import Producer
from datetime import datetime

def produce(bootstrap_servers: str, topic: str, duration_seconds: int):
    producer = Producer({"bootstrap.servers": bootstrap_servers,})
    user_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    
    print(f"Producing to topic {topic}...")
    start_time = time.time()
    while time.time() - start_time < duration_seconds:
        user_id = np.random.randint(0, 10)
        event = {
            "timestamp": datetime.isoformat(datetime.now()),
            "user_id": user_id,
            "user_name": user_names[user_id],
            "event_type": random.choice(['CLICK', 'SCROLL', 'SWIPE'])
        }
        producer.produce(topic, json.dumps(event))
        producer.flush(10000)