import json
from pathlib import Path
from datetime import datetime


INCIDENT_FILE = Path("storage/metrics/incident_log.jsonl")

INCIDENT_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_incident(result):
    incident = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": result["status"],
        "pipeline_action": result["pipeline_action"],
        "error_rate": result["error_rate"],
        "threshold": result["threshold"],
        "reason": result["reason"]
    }

    with open(INCIDENT_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(incident) + "\n")

    return incident


if __name__ == "__main__":
    sample_result = {
        "status": "OPEN",
        "pipeline_action": "PAUSE",
        "error_rate": 0.03,
        "threshold": 0.02,
        "reason": "Data quality error rate exceeded 2%"
    }

    incident = log_incident(sample_result)

    print("=" * 60)
    print("       ICSTREAM INCIDENT LOGGER")
    print("=" * 60)
    print(f"Timestamp       : {incident['timestamp']}")
    print(f"Status          : {incident['status']}")
    print(f"Pipeline Action : {incident['pipeline_action']}")
    print(f"Error Rate      : {incident['error_rate'] * 100:.2f}%")
    print(f"Threshold       : {incident['threshold'] * 100:.2f}%")
    print(f"Reason          : {incident['reason']}")
    print("=" * 60)