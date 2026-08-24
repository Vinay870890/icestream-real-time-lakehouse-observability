from src.observability.remediation import handle_pipeline_result


def test_bad_pipeline_is_quarantined():

    result = {
        "status": "OPEN",
        "pipeline_action": "PAUSE",
        "error_rate": 0.03,
        "threshold": 0.02,
        "reason": "Data quality error rate exceeded 2%"
    }

    output = handle_pipeline_result(result)

    assert output["action"] == "QUARANTINE"
    assert output["pipeline_status"] == "PAUSED"


def test_good_pipeline_continues():

    result = {
        "status": "CLOSED",
        "pipeline_action": "CONTINUE",
        "error_rate": 0.01,
        "threshold": 0.02,
        "reason": "Data quality within acceptable threshold"
    }

    output = handle_pipeline_result(result)

    assert output["action"] == "CONTINUE"
    assert output["pipeline_status"] == "RUNNING"