"""
IceStream - Kafka Consumer

Reads real-time transactions from the Kafka topic.
"""

import json

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable


KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"


def get_consumer():
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda value:
            json.loads(value.decode("utf-8")),
        consumer_timeout_ms=10000,
        group_id="icestream-verification-consumer",
    )


def main():

    print("=" * 50)
    print("       ICSTREAM KAFKA CONSUMER")
    print("=" * 50)

    try:
        consumer = get_consumer()

    except NoBrokersAvailable:
        print("[ERROR] Kafka broker is not available.")
        return

    count = 0

    try:

        for message in consumer:

            count += 1

            print(
                f"Received #{count}: "
                f"{message.value}"
            )

    except KeyboardInterrupt:

        print()
        print("Consumer stopped.")

    finally:

        consumer.close()

    print()
    print(f"Total messages received: {count}")


if __name__ == "__main__":
    main()