"""
IceStream - Transaction Schema Definition
Canonical schema for a valid e-commerce transaction.
"""

TRANSACTION_SCHEMA = {
    "transaction_id": str,
    "timestamp": str,
    "user_id": str,
    "product_id": str,
    "quantity": int,
    "price": float,
    "tax_amount": float,
    "payment_method": str,
    "country": str,
}

ALLOWED_PAYMENT_METHODS = [
    "credit_card", "debit_card", "upi", "net_banking", "wallet", "cod",
]

REQUIRED_FIELDS = list(TRANSACTION_SCHEMA.keys())


def get_sample_record():
    return {
        "transaction_id": "TXN-000001",
        "timestamp": "2026-08-16T10:15:00",
        "user_id": "USR-4521",
        "product_id": "PRD-8891",
        "quantity": 2,
        "price": 499.99,
        "tax_amount": 89.99,
        "payment_method": "upi",
        "country": "IN",
    }


if __name__ == "__main__":
    record = get_sample_record()
    print("Sample IceStream transaction record:")
    for key, value in record.items():
        print(f"  {key}: {value} ({type(value).__name__})")