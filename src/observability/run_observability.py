import json
import os

from src.observability.circuit_breaker import check_circuit
from src.observability.remediation import handle_pipeline_result
from src.observability.final_status import write_pipeline_status


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

METRICS_FILE = os.path.join(
    PROJECT_ROOT,
    "storage",
    "metrics",
    "pipeline_metrics.jsonl"
)


def load_latest_metrics():
    """Load the latest pipeline metric snapshot."""

    if not os.path.exists(METRICS_FILE):
        raise FileNotFoundError(
            f"Metrics file not found: {METRICS_FILE}"
        )

    latest = None

    with open(
        METRICS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:
            line = line.strip()

            if not line:
                continue

            latest = json.loads(line)

    if latest is None:
        raise ValueError("No metrics available.")

    return latest


def run_observability():

    metrics = load_latest_metrics()

    processed = metrics.get("total_records", 0)
    invalid = metrics.get("invalid_records", 0)

    # pipeline_metrics stores error_rate as a percentage.
    # circuit_breaker expects a fraction.
    circuit = check_circuit(
        processed,
        invalid
    )

    remediation = handle_pipeline_result(circuit)

    status = write_pipeline_status(
        status=circuit["status"],
        action=remediation["action"],
        error_rate=circuit["error_rate"],
        threshold=circuit["threshold"],
        reason=circuit["reason"]
    )

    print("=" * 60)
    print("          ICSTREAM OBSERVABILITY")
    print("=" * 60)

    print(f"Processed       : {processed}")
    print(f"Valid           : {metrics.get('valid_records', 0)}")
    print(f"Invalid         : {invalid}")
    print(f"Error Rate      : {circuit['error_rate'] * 100:.2f}%")
    print(f"Threshold       : {circuit['threshold'] * 100:.2f}%")
    print(f"Circuit Status  : {circuit['status']}")
    print(f"Pipeline Action : {circuit['pipeline_action']}")
    print(f"Remediation     : {remediation['action']}")
    print(f"Pipeline Status : {remediation['pipeline_status']}")
    print(f"Reason          : {circuit['reason']}")

    print("=" * 60)

    return {
        "metrics": metrics,
        "circuit": circuit,
        "remediation": remediation,
        "status": status
    }


if __name__ == "__main__":
    run_observability()