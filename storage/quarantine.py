"""
IceStream - Quarantine Storage

Stores invalid transactions separately from valid records.
Each quarantined record is written as one JSON object per line.
"""

import json
import os
from datetime import datetime, timezone


QUARANTINE_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "storage",
    "quarantine"
)

QUARANTINE_FILE = os.path.join(
    QUARANTINE_DIR,
    "invalid_transactions.jsonl"
)


def quarantine_record(record, errors):
    """
    Store an invalid transaction in quarantine.

    Parameters
    ----------
    record : dict
        Original transaction.
    errors : list
        Validation errors.
    """

    os.makedirs(QUARANTINE_DIR, exist_ok=True)

    payload = {
        "quarantined_at": datetime.now(timezone.utc).isoformat(),
        "transaction": record,
        "validation_errors": errors
    }

    with open(QUARANTINE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")


def get_quarantine_file():
    """Return the quarantine file path."""
    return QUARANTINE_FILE