"""
IceStream - Transaction Generator
Produces realistic e-commerce transaction records by sampling real
products from the BigBasket catalog and wrapping them in a live,
synthetic transaction (timestamp, user, quantity, payment method).
"""

import random
import os
from datetime import datetime
import pandas as pd

PAYMENT_METHODS = ["credit_card", "debit_card", "upi", "net_banking", "wallet", "cod"]
COUNTRIES = ["IN"]  # BigBasket is India-only; keep this realistic

_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "raw", "BigBasket_Products.csv"
)

_transaction_counter = 0
_product_pool = None


def _load_product_pool():
    """Loads and cleans the BigBasket catalog once, caches it in memory."""
    global _product_pool
    if _product_pool is not None:
        return _product_pool

    df = pd.read_csv(_CSV_PATH)
    df = df.dropna(subset=["product", "sale_price"])
    df = df[df["sale_price"] > 0]

    _product_pool = df[["index", "product", "sale_price"]].to_dict("records")
    return _product_pool


def _next_transaction_id():
    global _transaction_counter
    _transaction_counter += 1
    return f"TXN-{_transaction_counter:06d}"


def generate_transaction():
    """Generates a single, fully valid transaction record from a real product."""
    pool = _load_product_pool()
    product = random.choice(pool)

    quantity = random.randint(1, 5)
    price = round(float(product["sale_price"]), 2)
    tax_amount = round(price * 0.18, 2)  # 18% GST-style tax

    return {
        "transaction_id": _next_transaction_id(),
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": f"USR-{random.randint(1000, 9999)}",
        "product_id": f"PRD-{int(product['index'])}",
        "quantity": quantity,
        "price": price,
        "tax_amount": tax_amount,
        "payment_method": random.choice(PAYMENT_METHODS),
        "country": random.choice(COUNTRIES),
    }


def generate_batch(n=10):
    """Generates n valid transaction records."""
    return [generate_transaction() for _ in range(n)]


if __name__ == "__main__":
    batch = generate_batch(5)
    for txn in batch:
        print(txn)