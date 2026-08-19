"""
IceStream - Stream Processor
Consumes transactions from Kafka, performs basic structural validation,
and maintains running statistics for observability.
"""

import json
from kafka import KafkaConsumer

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

REQUIRED_FIELDS = [
    "transaction_id", "timestamp", "user_id", "product_id",
    "quantity", "price", "tax_amount", "payment_method", "country",
]


class PipelineStats:
    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid = 0

    def record(self, is_valid):
        self.total += 1
        if is_valid:
            self.valid += 1
        else:
            self.invalid += 1

    def error_rate(self):
        if self.total == 0:
            return 0.0
        return round((self.invalid / self.total) * 100, 2)

    def summary(self):
        return (
            f"Total: {self.total} | Valid: {self.valid} | "
            f"Invalid: {self.invalid} | Error rate: {self.error_rate()}%"
        )


def is_structurally_valid(record):
    """Day 4 check: are all required fields present (no missing keys)?
    Value-level checks (nulls, negative numbers, etc.) come in Day 5."""
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    return len(missing) == 0, missing


def get_consumer():
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=10000,
    )


if __name__ == "__main__":
    consumer = get_consumer()
    stats = PipelineStats()

    print(f"Processor listening on '{TOPIC}'... (stops after 10s of silence)\n")

    for message in consumer:
        record = message.value
        valid, missing = is_structurally_valid(record)
        stats.record(valid)

        txn_id = record.get("transaction_id", "UNKNOWN")
        if valid:
            print(f"[OK]      {txn_id}")
        else:
            print(f"[INVALID] {txn_id} - missing fields: {missing}")

    print("\n--- Pipeline Summary ---")
    print(stats.summary())