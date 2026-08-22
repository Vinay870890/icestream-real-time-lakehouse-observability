"""
IceStream - Observability Report

Reads pipeline metrics and generates a summary report.
"""

import json
import os


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

METRICS_FILE = os.path.join(
    PROJECT_ROOT,
    "storage",
    "metrics",
    "pipeline_metrics.jsonl"
)

REPORT_DIR = os.path.join(
    PROJECT_ROOT,
    "storage",
    "metrics"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "pipeline_report.txt"
)


def load_metrics():
    """Load all metric snapshots."""

    if not os.path.exists(METRICS_FILE):
        return []

    metrics = []

    with open(
        METRICS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            metrics.append(json.loads(line))

    return metrics


def generate_report():

    metrics = load_metrics()

    if not metrics:
        print("No metrics available.")
        return

    latest = metrics[-1]

    total = latest.get("total_records", 0)
    valid = latest.get("valid_records", 0)
    invalid = latest.get("invalid_records", 0)
    error_rate = latest.get("error_rate", 0)

    breakdown = latest.get(
        "error_breakdown",
        {}
    )

    lines = []

    lines.append(
        "========================================"
    )

    lines.append(
        "        ICESTREAM PIPELINE REPORT"
    )

    lines.append(
        "========================================"
    )

    lines.append("")

    lines.append(
        f"Timestamp       : {latest.get('timestamp')}"
    )

    lines.append(
        f"Total Records   : {total}"
    )

    lines.append(
        f"Valid Records   : {valid}"
    )

    lines.append(
        f"Invalid Records : {invalid}"
    )

    lines.append(
        f"Error Rate      : {error_rate}%"
    )

    lines.append("")

    lines.append(
        "Error Breakdown"
    )

    lines.append(
        "----------------"
    )

    if breakdown:

        for error_type, count in sorted(
            breakdown.items(),
            key=lambda x: -x[1]
        ):

            lines.append(
                f"{error_type}: {count}"
            )

    else:

        lines.append(
            "No validation errors."
        )

    lines.append("")

    lines.append(
        "Metric Snapshots"
    )

    lines.append(
        "----------------"
    )

    lines.append(
        f"Total snapshots: {len(metrics)}"
    )

    report = "\n".join(lines)

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(report)

    print(report)

    print()
    print(
        f"Report saved: {os.path.relpath(REPORT_FILE, PROJECT_ROOT)}"
    )


if __name__ == "__main__":
    generate_report()
    