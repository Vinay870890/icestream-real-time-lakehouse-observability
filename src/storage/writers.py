"""
IceStream - Data Storage Writers

Routes validated transactions into:
    - good_data/
    - quarantine/

JSON Lines format is used so every transaction is stored
as one independent JSON record.
"""

import json
import os
from datetime import datetime, timezone


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

GOOD_DATA_DIR = os.path.join(
    PROJECT_ROOT,
    "storage",
    "good_data"
)

QUARANTINE_DIR = os.path.join(
    PROJECT_ROOT,
    "storage",
    "quarantine"
)


def _ensure_directories():
    """Create storage directories if they don't exist."""

    os.makedirs(GOOD_DATA_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)


def _timestamp():
    """Return current UTC timestamp."""

    return datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )


def write_good_record(record):
    """
    Write a valid transaction to good_data.

    Returns:
        Path of the file written to.
    """

    _ensure_directories()

    filename = f"good_data_{_timestamp()}.jsonl"

    filepath = os.path.join(
        GOOD_DATA_DIR,
        filename
    )

    with open(filepath, "a", encoding="utf-8") as f:

        f.write(
            json.dumps(record) + "\n"
        )

    return filepath


def write_quarantine_record(record, errors):
    """
    Write an invalid transaction to quarantine.

    The original transaction is preserved together
    with the validation errors that caused quarantine.
    """

    _ensure_directories()

    filename = f"quarantine_{_timestamp()}.jsonl"

    filepath = os.path.join(
        QUARANTINE_DIR,
        filename
    )

    quarantine_record = {
        "quarantined_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "transaction": record,

        "validation_errors": errors,
    }

    with open(filepath, "a", encoding="utf-8") as f:

        f.write(
            json.dumps(quarantine_record) + "\n"
        )

    return filepath