"""
IceStream - Storage Manager

Routes validated transactions into:
    storage/good_data/
    storage/quarantine/

Good records are stored separately from invalid records.
"""

import json
import os
from datetime import datetime


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

GOOD_DATA_DIR = os.path.join(
    PROJECT_ROOT, "storage", "good_data"
)

QUARANTINE_DIR = os.path.join(
    PROJECT_ROOT, "storage", "quarantine"
)


def _ensure_directories():
    """Create storage directories if they do not exist."""
    os.makedirs(GOOD_DATA_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)


def _today_file(directory):
    """Return today's JSONL file path."""
    date_string = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(
        directory,
        f"transactions_{date_string}.jsonl"
    )


def save_good_record(record):
    """Save a valid transaction to good-data storage."""
    _ensure_directories()

    file_path = _today_file(GOOD_DATA_DIR)

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def save_quarantine_record(record, errors):
    """Save an invalid transaction with its validation errors."""

    _ensure_directories()

    quarantine_record = {
        "record": record,
        "errors": errors,
        "quarantined_at": datetime.now().isoformat(),
    }

    file_path = _today_file(QUARANTINE_DIR)

    with open(file_path, "a", encoding="utf-8") as file:
        file.write(json.dumps(quarantine_record) + "\n")


if __name__ == "__main__":

    test_good = {
        "transaction_id": "TEST-001",
        "price": 100
    }

    test_bad = {
        "transaction_id": "TEST-002",
        "price": -100
    }

    save_good_record(test_good)

    save_quarantine_record(
        test_bad,
        ["Invalid price: -100"]
    )

    print("Storage manager test completed.")