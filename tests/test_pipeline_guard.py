from src.observability.pipeline_guard import evaluate_pipeline


def test_guard_pauses_bad_pipeline():
    result = evaluate_pipeline(100, 97, 3)

    assert result["status"] == "OPEN"
    assert result["pipeline_action"] == "PAUSE"


def test_guard_allows_good_pipeline():
    result = evaluate_pipeline(100, 99, 1)

    assert result["status"] == "CLOSED"
    assert result["pipeline_action"] == "CONTINUE"