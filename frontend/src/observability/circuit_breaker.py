ERROR_THRESHOLD = 0.02


def calculate_error_rate(processed, invalid):
    if processed == 0:
        return 0.0

    return invalid / processed


def check_circuit(processed, invalid):
    error_rate = calculate_error_rate(processed, invalid)

    if error_rate > ERROR_THRESHOLD:
        return {
            "status": "OPEN",
            "pipeline_action": "PAUSE",
            "error_rate": round(error_rate, 4),
            "threshold": ERROR_THRESHOLD,
            "reason": "Data quality error rate exceeded 2%"
        }

    return {
        "status": "CLOSED",
        "pipeline_action": "CONTINUE",
        "error_rate": round(error_rate, 4),
        "threshold": ERROR_THRESHOLD,
        "reason": "Data quality within acceptable threshold"
    }


if __name__ == "__main__":
    tests = [
        (100, 1),
        (100, 3),
        (1000, 20),
        (1000, 21),
    ]

    for processed, invalid in tests:
        result = check_circuit(processed, invalid)

        print("=" * 50)
        print(f"Processed   : {processed}")
        print(f"Invalid     : {invalid}")
        print(f"Error Rate  : {result['error_rate'] * 100:.2f}%")
        print(f"Threshold   : {result['threshold'] * 100:.2f}%")
        print(f"Status      : {result['status']}")
        print(f"Action      : {result['pipeline_action']}")
        print(f"Reason      : {result['reason']}")