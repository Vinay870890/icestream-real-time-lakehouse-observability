"""
IceStream - Bad Data Injector

Intentionally corrupts valid transaction records to simulate
real-world data quality problems.
"""

import copy
import random


def inject_null_tax(record):
    """Set tax_amount to NULL."""
    r = copy.deepcopy(record)
    r["tax_amount"] = None
    return r


def inject_invalid_quantity(record):
    """Set quantity to an invalid value."""
    r = copy.deepcopy(record)
    r["quantity"] = random.choice([0, -1, -5])
    return r


def inject_invalid_payment_method(record):
    """Use a payment method outside the allowed list."""
    r = copy.deepcopy(record)
    r["payment_method"] = "bitcoin"
    return r


def inject_missing_field(record):
    """Remove a required field to simulate schema problems."""
    r = copy.deepcopy(record)

    field_to_drop = random.choice([
        "user_id",
        "product_id",
        "country",
    ])

    del r[field_to_drop]

    return r


def inject_negative_price(record):
    """Set price to a negative value."""
    r = copy.deepcopy(record)
    r["price"] = -abs(r["price"])
    return r


CORRUPTION_SCENARIOS = {
    "null_tax": inject_null_tax,
    "invalid_quantity": inject_invalid_quantity,
    "invalid_payment_method": inject_invalid_payment_method,
    "missing_field": inject_missing_field,
    "negative_price": inject_negative_price,
}


def corrupt_batch(records, error_rate=0.10, scenario=None):
    """
    Corrupt a percentage of records.

    Args:
        records: List of valid transaction dictionaries.
        error_rate: Probability that each record is corrupted.
        scenario: Specific corruption scenario or None for random selection.

    Returns:
        List containing clean and corrupted records.
    """

    if not 0 <= error_rate <= 1:
        raise ValueError("error_rate must be between 0 and 1")

    if scenario is not None and scenario not in CORRUPTION_SCENARIOS:
        raise ValueError(
            f"Unknown scenario: {scenario}. "
            f"Available: {list(CORRUPTION_SCENARIOS.keys())}"
        )

    result = []

    for record in records:

        if random.random() < error_rate:

            if scenario:
                corruption_function = CORRUPTION_SCENARIOS[scenario]
            else:
                corruption_function = random.choice(
                    list(CORRUPTION_SCENARIOS.values())
                )

            result.append(
                corruption_function(record)
            )

        else:
            result.append(
                copy.deepcopy(record)
            )

    return result


if __name__ == "__main__":

    # Import generator from the same directory
    from generator import generate_batch

    print("IceStream Bad Data Injector")
    print("-" * 60)

    clean_records = generate_batch(20)

    dirty_records = corrupt_batch(
        clean_records,
        error_rate=0.30
    )

    for record in dirty_records:
        print(record)