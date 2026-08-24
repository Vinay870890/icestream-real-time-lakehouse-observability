import json
from pathlib import Path
from datetime import datetime


STATUS_FILE = Path("storage/metrics/pipeline_status.json")

STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)


def write_status(status):
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        **status
    }

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


if __name__ == "__main__":
    write_status({
        "status": "CLOSED",
        "pipeline_action": "CONTINUE",
        "error_rate": 0.01,
        "threshold": 0.02,
        "reason": "Data quality within acceptable threshold"
    })

    print(f"Pipeline status written to {STATUS_FILE}")