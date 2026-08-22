"""
IceStream - Stream Processor

Pipeline:

Kafka
  ↓
Validator
  ↓
Good Data / Quarantine
  ↓
Pipeline Metrics

Valid transactions are written to:
    storage/good_data/

Invalid transactions are written to:
    storage/quarantine/
"""

import json
import sys
import os

# Allow imports from src/
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

SRC_DIR = os.path.join(PROJECT_ROOT, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from kafka import KafkaConsumer

from quality.validator import Validator

from storage.storage_manager import (
    save_good_record,
    save_quarantine_record,
)

from observability.metrics import save_metrics

# ============================================================
# CONFIGURATION
# ============================================================

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"

# Stop after 10 seconds without receiving a message.
CONSUMER_TIMEOUT_MS = 10000


# ============================================================
# PIPELINE STATISTICS
# ============================================================

class PipelineStats:
    """Maintains running data-quality statistics."""

    def __init__(self):
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.error_breakdown = {}

    def record(self, is_valid, errors):
        """Record the result of validating one transaction."""

        self.total += 1

        if is_valid:
            self.valid += 1
            return

        self.invalid += 1

        for error in errors:

            # Example:
            # "Invalid price: -100"
            #
            # becomes:
            # "Invalid price"

            error_type = error.split(":")[0]

            self.error_breakdown[error_type] = (
                self.error_breakdown.get(error_type, 0) + 1
            )

    def error_rate(self):
        """Return invalid-record percentage."""

        if self.total == 0:
            return 0.0

        return round(
            (self.invalid / self.total) * 100,
            2
        )

    def summary(self):
        """Return formatted pipeline summary."""

        lines = [
            (
                f"Total: {self.total} | "
                f"Valid: {self.valid} | "
                f"Invalid: {self.invalid} | "
                f"Error rate: {self.error_rate()}%"
            )
        ]

        if self.error_breakdown:

            lines.append("Error breakdown:")

            for error_type, count in sorted(
                self.error_breakdown.items(),
                key=lambda x: -x[1]
            ):

                lines.append(
                    f"  - {error_type}: {count}"
                )

        return "\n".join(lines)


# ============================================================
# KAFKA CONSUMER
# ============================================================

def get_consumer():
    """Create and return the Kafka consumer."""

    return KafkaConsumer(

        TOPIC,

        bootstrap_servers=KAFKA_BROKER,

        auto_offset_reset="earliest",

        value_deserializer=lambda value:
            json.loads(value.decode("utf-8")),

        consumer_timeout_ms=CONSUMER_TIMEOUT_MS,

        # Each processor instance uses its own group.
        # This is useful for local testing.
        group_id="icestream-processor",

    )


# ============================================================
# MAIN PROCESSING PIPELINE
# ============================================================

def main():

    print("=" * 50)
    print("        IceStream Stream Processor")
    print("=" * 50)

    print()
    print(f"Kafka broker : {KAFKA_BROKER}")
    print(f"Kafka topic  : {TOPIC}")
    print()

    print("Valid records   → storage/good_data/")
    print("Invalid records → storage/quarantine/")
    print()

    # --------------------------------------------------------
    # Connect to Kafka
    # --------------------------------------------------------

    try:

        consumer = get_consumer()

    except NoBrokersAvailable:

        print("[ERROR] Kafka broker is not available.")
        print()
        print("Make sure Docker Desktop is running and Kafka is started:")
        print()
        print("    docker ps")
        print("    docker start icestream-kafka")
        print()

        return

    # --------------------------------------------------------
    # Initialize validator and statistics
    # --------------------------------------------------------

    validator = Validator()
    stats = PipelineStats()

    print(
        f"Processor listening on '{TOPIC}'..."
    )

    print(
        "(Stops after 10 seconds of silence)"
    )

    print()

    # --------------------------------------------------------
    # Consume Kafka messages
    # --------------------------------------------------------

    try:

        for message in consumer:

            record = message.value

            try:

                # --------------------------------------------
                # Validate transaction
                # --------------------------------------------

                is_valid, errors = validator.check(record)

                # --------------------------------------------
                # Update statistics
                # --------------------------------------------

                stats.record(
                    is_valid,
                    errors
                )

                transaction_id = record.get(
                    "transaction_id",
                    "UNKNOWN"
                )

                # --------------------------------------------
                # GOOD DATA
                # --------------------------------------------

                if is_valid:

                    save_good_record(record)

                    print(
                        f"[OK]        {transaction_id} → GOOD"
                    )

                # --------------------------------------------
                # BAD DATA
                # --------------------------------------------

                else:

                    save_quarantine_record(
                        record,
                        errors
                    )

                    print(
                        f"[INVALID]   "
                        f"{transaction_id} → QUARANTINE"
                    )

                    print(
                        f"            {errors}"
                    )

            except Exception as error:

                print(
                    f"[ERROR] Failed to process record: {error}"
                )

    except KeyboardInterrupt:

        print()
        print("Processor stopped by user.")

    finally:

        consumer.close()

    # ========================================================
    # PIPELINE SUMMARY
    # ========================================================

    print()
    print("=" * 50)
    print("        PIPELINE SUMMARY")
    print("=" * 50)

    print(
        stats.summary()
    )
    metric = save_metrics(stats)

    print()
    print("Metrics saved:")
    print("storage/metrics/pipeline_metrics.jsonl")

    print()

    # ========================================================
    # STORAGE LOCATIONS
    # ========================================================

    print("Storage:")
    print()

    print(
        "Good data  : storage/good_data/"
    )

    print(
        "Quarantine : storage/quarantine/"
    )

    print()

    print("=" * 50)
    print("        PROCESSING COMPLETE")
    print("=" * 50)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()