"""
IceStream - Data Quality Rules Engine
Configurable, reusable validation rules for transaction records.
"""

from datetime import datetime

REQUIRED_FIELDS = [
    "transaction_id", "timestamp", "user_id", "product_id",
    "quantity", "price", "tax_amount", "payment_method", "country",
]

ALLOWED_PAYMENT_METHODS = [
    "credit_card", "debit_card", "upi", "net_banking", "wallet", "cod",
]


def check_required_fields(record):
    """Rule: all required fields must be present."""
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        return False, f"Missing fields: {missing}"
    return True, None


def check_nulls(record):
    """Rule: no required field may be None."""
    nulls = [f for f in REQUIRED_FIELDS if record.get(f, "MISSING") is None]
    if nulls:
        return False, f"NULL values in: {nulls}"
    return True, None


def check_quantity(record):
    """Rule: quantity must be > 0."""
    qty = record.get("quantity")
    if qty is None:
        return True, None  # caught by check_nulls
    if not isinstance(qty, (int, float)) or qty <= 0:
        return False, f"Invalid quantity: {qty}"
    return True, None


def check_price(record):
    """Rule: price must be >= 0."""
    price = record.get("price")
    if price is None:
        return True, None
    if not isinstance(price, (int, float)) or price < 0:
        return False, f"Invalid price: {price}"
    return True, None


def check_tax_amount(record):
    """Rule: tax_amount must be >= 0."""
    tax = record.get("tax_amount")
    if tax is None:
        return True, None  # caught by check_nulls
    if not isinstance(tax, (int, float)) or tax < 0:
        return False, f"Invalid tax_amount: {tax}"
    return True, None


def check_payment_method(record):
    """Rule: payment_method must be in the allowed list."""
    method = record.get("payment_method")
    if method is None:
        return True, None
    if method not in ALLOWED_PAYMENT_METHODS:
        return False, f"Invalid payment_method: {method}"
    return True, None


def check_timestamp(record):
    """Rule: timestamp must be a valid ISO 8601 string."""
    ts = record.get("timestamp")
    if ts is None:
        return True, None
    try:
        datetime.fromisoformat(ts)
        return True, None
    except (ValueError, TypeError):
        return False, f"Invalid timestamp: {ts}"


def check_transaction_id_present(record):
    """Rule: transaction_id must exist and be non-empty (uniqueness handled by caller)."""
    txn_id = record.get("transaction_id")
    if not txn_id:
        return False, "Missing or empty transaction_id"
    return True, None


# The full set of rules, run in order. Each returns (is_valid, error_message).
RULES = [
    check_required_fields,
    check_nulls,
    check_transaction_id_present,
    check_quantity,
    check_price,
    check_tax_amount,
    check_payment_method,
    check_timestamp,
]


def validate_record(record, seen_transaction_ids=None):
    """
    Runs all rules against a record. Stops at the first failure
    (fail-fast) and returns (is_valid, list_of_errors).
    Pass seen_transaction_ids (a set) to also check for duplicates.
    """
    errors = []

    for rule in RULES:
        is_valid, message = rule(record)
        if not is_valid:
            errors.append(message)

    if seen_transaction_ids is not None:
        txn_id = record.get("transaction_id")
        if txn_id in seen_transaction_ids:
            errors.append(f"Duplicate transaction_id: {txn_id}")
        elif txn_id:
            seen_transaction_ids.add(txn_id)

    return len(errors) == 0, errors