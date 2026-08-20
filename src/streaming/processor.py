"""
IceStream - Stream Processor

Consumes transactions from Kafka, runs full data-quality validation,
maintains pipeline statistics, and routes records to:

    VALID   -> storage/good_data/
    INVALID -> storage/quarantine/

Day 7: Good Data / Quarantine Separation
"""

import json
import sys
import os


# ---------------------------------------------------------
# Add src/ to Python path
# ---------------------------------------------------------

SRC_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

sys.path.insert(0, SRC_DIR)


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from kafka import KafkaConsumer

from quality.validator import Validator

from storage.writers import (
    write_good_record,
    write_quarantine_record
)


# ---------------------------------------------------------
# Kafka Configuration
# ---------------------------------------------------------

KAFKA_BROKER = "localhost:9092"
TOPIC = "transactions"


# ---------------------------------------------------------
# Pipeline Statistics
# ---------------------------------------------------------

class PipelineStats:

    def __init__(self):

        self.total = 0

        self.valid = 0

        self.invalid = 0

        self.error_breakdown = {}


    def record(self, is_valid, errors):

        self.total += 1

        if is_valid:

            self.valid += 1

        else:

            self.invalid += 1

            for err in errors:

                key = err.split(":")[0]

                self.error_breakdown[key] = (
                    self.error_breakdown.get(key, 0) + 1
                )


    def error_rate(self):

        if self.total == 0:

            return 0.0

        return round(
            (self.invalid / self.total) * 100,
            2
        )


    def summary(self):

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

            for err_type, count in sorted(
                self.error_breakdown.items(),
                key=lambda x: -x[1]
            ):

                lines.append(
                    f"  - {err_type}: {count}"
                )


        return "\n".join(lines)


# ---------------------------------------------------------
# Kafka Consumer
# ---------------------------------------------------------

def get_consumer():

    return KafkaConsumer(

        TOPIC,

        bootstrap_servers=KAFKA_BROKER,

        auto_offset_reset="earliest",

        value_deserializer=lambda v:
            json.loads(v.decode("utf-8")),

        consumer_timeout_ms=10000
    )


# ---------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------

if __name__ == "__main__":

    consumer = get_consumer()

    validator = Validator()

    stats = PipelineStats()


    print(
        f"Processor listening on '{TOPIC}'..."
    )

    print(
        "Valid records → storage/good_data/"
    )

    print(
        "Invalid records → storage/quarantine/"
    )

    print(
        "(stops after 10s of silence)\n"
    )


    # -----------------------------------------------------
    # Process Kafka Messages
    # -----------------------------------------------------

    for message in consumer:

        record = message.value


        # ---------------------------------------------
        # Run Data Quality Validation
        # ---------------------------------------------

        is_valid, errors = validator.check(record)


        # ---------------------------------------------
        # Update Statistics
        # ---------------------------------------------

        stats.record(
            is_valid,
            errors
        )


        txn_id = record.get(
            "transaction_id",
            "UNKNOWN"
        )


        # ---------------------------------------------
        # VALID RECORD
        # ---------------------------------------------

        if is_valid:

            filepath = write_good_record(
                record
            )


            print(
                f"[OK]      {txn_id} "
                f"→ GOOD DATA"
            )


        # ---------------------------------------------
        # INVALID RECORD
        # ---------------------------------------------

        else:

            filepath = write_quarantine_record(
                record,
                errors
            )


            print(
                f"[INVALID] {txn_id} "
                f"→ QUARANTINE - {errors}"
            )


    # -----------------------------------------------------
    # Pipeline Summary
    # -----------------------------------------------------

    print(
        "\n--- Pipeline Summary ---"
    )

    print(
        stats.summary()
    )


    # -----------------------------------------------------
    # Storage Summary
    # -----------------------------------------------------

    print(
        "\n--- Storage Routing ---"
    )

    print(
        f"Valid records stored in: "
        f"storage/good_data/"
    )

    print(
        f"Invalid records stored in: "
        f"storage/quarantine/"
    )