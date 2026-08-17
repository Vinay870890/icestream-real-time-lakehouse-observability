"""
IceStream - Bad Data Injector
Takes a clean transaction record and corrupts it in a controlled,
labeled way. Used to simulate real-world data quality problems.
"""

import random
import copy


def inject_null_tax(record):
    """Scenario: NULL tax_amount."""
    r = copy.deepcopy(record)
    r["tax_amount"] = None
    return r


def inject_invalid_quantity(record):
    """Scenario: negative or zero quantity."""
    r = copy.deepcopy(record)
    r["quantity"] = random.choice([-1, 0, -5])
    return r


def inject_invalid_payment_method(record):
    """Scenario: payment_method outside the allowed list."""
    r = copy.deepcopy(record)
    r["payment_method"] = "bitcoin"
    return r


def inject_missing_field(record):
    """Scenario: schema change - a required field is dropped entirely."""
    r = copy.deepcopy(record)
    field_to_drop = random.choice(["user_id", "product_id", "country"])
    del r[field_to_drop]
    return r


def inject_negative_price(record):
    """Scenario: invalid negative price."""
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


def corrupt_batch(records, error_rate=0.1, scenario=None):
    result = []
    for record in records:
        if random.random() < error_rate:
            fn = (
                CORRUPTION_SCENARIOS[scenario]
                if scenario
                else random.choice(list(CORRUPTION_SCENARIOS.values()))
            )
            result.append(fn(record))
        else:
            result.append(record)
    return result


if __name__ == "__main__":
    from generator import generate_batch

    clean_batch = generate_batch(20)
    dirty_batch = corrupt_batch(clean_batch, error_rate=0.3)

    for txn in dirty_batch:
        print(txn)
