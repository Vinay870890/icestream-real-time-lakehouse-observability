from src.observability.incident_logger import log_incident


def handle_pipeline_result(result):

    if result["status"] == "OPEN":

        incident = log_incident(result)

        return {
            "action": "QUARANTINE",
            "pipeline_status": "PAUSED",
            "incident": incident
        }

    return {
        "action": "CONTINUE",
        "pipeline_status": "RUNNING",
        "incident": None
    }


if __name__ == "__main__":

    bad_result = {
        "status": "OPEN",
        "pipeline_action": "PAUSE",
        "error_rate": 0.03,
        "threshold": 0.02,
        "reason": "Data quality error rate exceeded 2%"
    }

    result = handle_pipeline_result(bad_result)

    print("=" * 60)
    print("       ICSTREAM AUTOMATED REMEDIATION")
    print("=" * 60)
    print(f"Action          : {result['action']}")
    print(f"Pipeline Status : {result['pipeline_status']}")
    print("=" * 60)