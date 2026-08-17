"""
IceStream - Kafka Producer
Sends generated transactions (clean + corrupted) into the Kafka topic.
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "stream_generator"))

from kafka import KafkaProducer
from generator import generate_batch
from bad_data import corrupt_batch

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"


def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )


def send_batch(producer, n=20, error_rate=0.2):
    clean = generate_batch(n)
    dirty = corrupt_batch(clean, error_rate=error_rate)

    for record in dirty:
        producer.send(TOPIC, value=record)
        print(f"Sent: {record.get('transaction_id')}")
        time.sleep(0.1)  # small delay to simulate real-time streaming

    producer.flush()


if __name__ == "__main__":
    producer = get_producer()
    print(f"Connected to Kafka at {KAFKA_BROKER}, sending to topic '{TOPIC}'...")
    send_batch(producer, n=20, error_rate=0.2)
    print("Done sending batch.")