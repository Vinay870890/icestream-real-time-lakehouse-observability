from src.observability.circuit_breaker import check_circuit


def evaluate_pipeline(processed, valid, invalid):
    result = check_circuit(processed, invalid)

    print("=" * 60)
    print("          ICSTREAM PIPELINE GUARD")
    print("=" * 60)
    print(f"Processed       : {processed}")
    print(f"Valid           : {valid}")
    print(f"Invalid         : {invalid}")
    print(f"Error Rate      : {result['error_rate'] * 100:.2f}%")
    print(f"Threshold       : {result['threshold'] * 100:.2f}%")
    print(f"Circuit Status  : {result['status']}")
    print(f"Pipeline Action : {result['pipeline_action']}")
    print(f"Reason          : {result['reason']}")
    print("=" * 60)

    return result


if __name__ == "__main__":
    evaluate_pipeline(
        processed=100,
        valid=97,
        invalid=3
    )