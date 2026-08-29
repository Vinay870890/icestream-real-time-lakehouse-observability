"""
IceStream - Real-Time Stream Processor

Kafka
  ↓
Validator
  ↓
Bronze
  ↓
Silver
  ↓
Gold
  ↓
Observability Metrics

Invalid records are quarantined.
"""

import json
import os
import sys
from datetime import datetime, timezone

from kafka import KafkaConsumer


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from quality.validator import Validator
from lakehouse.bronze_writer import write_to_bronze
from storage.storage_manager import save_quarantine_record
from observability.metrics import save_metrics


KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"
CONSUMER_TIMEOUT_MS = 10000


class PipelineStats:
    """Maintain real-time pipeline statistics."""

    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.error_breakdown = {}

    def record(self, is_valid, errors):
        self.total += 1

        if is_valid:
            self.valid += 1
            return

        self.invalid += 1

        for error in errors:
            error_type = error.split(":")[0]

            self.error_breakdown[error_type] = (
                self.error_breakdown.get(error_type, 0) + 1
            )

    def error_rate(self):
        if self.total == 0:
            return 0.0

        return round(
            (self.invalid / self.total) * 100,
            2
        )

    def summary(self):
        return (
            f"Total: {self.total} | "
            f"Valid: {self.valid} | "
            f"Invalid: {self.invalid} | "
            f"Error rate: {self.error_rate()}%"
        )


def get_consumer():
    """Create Kafka consumer."""

    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset="earliest",
        value_deserializer=lambda value:
            json.loads(value.decode("utf-8")),
        consumer_timeout_ms=CONSUMER_TIMEOUT_MS,
        group_id="icestream-realtime-processor",
    )


def process_transaction(record, validator, stats):
    """Validate and route one streaming transaction."""

    is_valid, errors = validator.check(record)

    stats.record(is_valid, errors)

    transaction_id = record.get(
        "transaction_id",
        "UNKNOWN"
    )

    if is_valid:

        # Raw event enters Bronze layer.
        bronze_file = write_to_bronze(record)

        print(
            f"[OK] {transaction_id} "
            f"→ BRONZE "
            f"({bronze_file})"
        )

    else:

        save_quarantine_record(
            record,
            errors
        )

        print(
            f"[INVALID] {transaction_id} "
            f"→ QUARANTINE"
        )

        print(
            f"           Errors: {errors}"
        )


def main():

    print("=" * 60)
    print("        ICSTREAM REAL-TIME STREAM PROCESSOR")
    print("=" * 60)

    print(f"Kafka broker : {KAFKA_BROKER}")
    print(f"Kafka topic  : {TOPIC}")
    print()
    print("Kafka → Validation → Bronze → Observability")
    print("Invalid records → Quarantine")
    print()
    print(
        "Processor stops after "
        f"{CONSUMER_TIMEOUT_MS / 1000:.0f} seconds of silence."
    )
    print()

    try:
        consumer = get_consumer()

    except Exception as error:
        print("[ERROR] Could not connect to Kafka.")
        print(f"Reason: {error}")
        return

    validator = Validator()
    stats = PipelineStats()

    print(
        f"Listening for real-time events "
        f"on '{TOPIC}'..."
    )
    print()

    try:

        for message in consumer:

            record = message.value

            try:

                process_transaction(
                    record,
                    validator,
                    stats
                )

            except Exception as error:

                print(
                    f"[ERROR] Failed to process record: "
                    f"{error}"
                )

    except KeyboardInterrupt:

        print()
        print("Processor stopped by user.")

    finally:

        consumer.close()

    print()
    print("=" * 60)
    print("              PIPELINE SUMMARY")
    print("=" * 60)

    print(stats.summary())

    metric = save_metrics(stats)

    print()
    print("Metrics saved:")
    print(
        "storage/metrics/pipeline_metrics.jsonl"
    )

    print()
    print("Latest metric:")
    print(json.dumps(metric, indent=2))

    print()
    print("=" * 60)
    print("        REAL-TIME PROCESSING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()