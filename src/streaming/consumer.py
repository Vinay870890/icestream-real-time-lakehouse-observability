"""
IceStream - Kafka Consumer
Reads transactions from the Kafka topic and prints them.
This is a temporary verification consumer for Day 3;
Day 4 replaces this with the real streaming processor.
"""

import json
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"


def get_consumer():
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=10000,  # stop after 10s of no new messages
    )


if __name__ == "__main__":
    consumer = get_consumer()
    print(f"Listening on topic '{TOPIC}'... (will stop after 10s of silence)")
    count = 0
    for message in consumer:
        count += 1
        print(f"Received #{count}: {message.value}")
    print(f"Done. Total messages received: {count}")