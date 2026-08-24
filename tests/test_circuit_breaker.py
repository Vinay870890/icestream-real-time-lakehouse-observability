from src.observability.circuit_breaker import check_circuit


def test_pipeline_continues_below_threshold():
    result = check_circuit(100, 1)

    assert result["status"] == "CLOSED"
    assert result["pipeline_action"] == "CONTINUE"


def test_pipeline_pauses_above_threshold():
    result = check_circuit(100, 3)

    assert result["status"] == "OPEN"
    assert result["pipeline_action"] == "PAUSE"


def test_exactly_two_percent_is_allowed():
    result = check_circuit(100, 2)

    assert result["status"] == "CLOSED"