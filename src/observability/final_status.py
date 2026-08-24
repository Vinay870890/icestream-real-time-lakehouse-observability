import json
from pathlib import Path
from datetime import datetime


STATUS_FILE = Path("storage/metrics/pipeline_status.json")

STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)


def write_pipeline_status(
    status,
    action,
    error_rate,
    threshold=0.02,
    reason=""
):
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "pipeline": "IceStream",
        "status": status,
        "action": action,
        "error_rate": error_rate,
        "threshold": threshold,
        "reason": reason
    }

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return data


if __name__ == "__main__":

    result = write_pipeline_status(
        status="HEALTHY",
        action="CONTINUE",
        error_rate=0.01,
        threshold=0.02,
        reason="Data quality within acceptable threshold"
    )

    print("=" * 60)
    print("       ICSTREAM PIPELINE STATUS")
    print("=" * 60)
    print(f"Status      : {result['status']}")
    print(f"Action      : {result['action']}")
    print(f"Error Rate  : {result['error_rate'] * 100:.2f}%")
    print(f"Threshold   : {result['threshold'] * 100:.2f}%")
    print(f"Reason      : {result['reason']}")
    print("=" * 60)