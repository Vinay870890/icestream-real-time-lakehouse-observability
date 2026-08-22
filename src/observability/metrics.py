"""
IceStream - Pipeline Metrics

Persists pipeline quality metrics for observability.
"""

import json
import os
from datetime import datetime, timezone


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

METRICS_DIR = os.path.join(
    PROJECT_ROOT,
    "storage",
    "metrics"
)

METRICS_FILE = os.path.join(
    METRICS_DIR,
    "pipeline_metrics.jsonl"
)


def save_metrics(stats):
    """Save current pipeline statistics as one JSON record."""

    os.makedirs(METRICS_DIR, exist_ok=True)

    metric = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_records": stats.total,
        "valid_records": stats.valid,
        "invalid_records": stats.invalid,
        "error_rate": stats.error_rate(),
        "error_breakdown": stats.error_breakdown,
    }

    with open(
        METRICS_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(metric) + "\n"
        )

    return metric