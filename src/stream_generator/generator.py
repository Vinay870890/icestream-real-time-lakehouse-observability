"""
IceStream - Transaction Generator

Generates realistic e-commerce transaction records using
real products from the BigBasket catalog.
"""

import random
import os
import uuid
from datetime import datetime, timezone

import pandas as pd


PAYMENT_METHODS = [
    "credit_card",
    "debit_card",
    "upi",
    "net_banking",
    "wallet",
    "cod",
]

COUNTRIES = ["IN"]


# Project root:
# icestream-real-time-lakehouse-observability/
#
# This file:
# src/stream_generator/generator.py
#
# Therefore:
# ..       = src
# ../..    = project root

_CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "raw",
    "BigBasket_Products.csv",
)


_product_pool = None


def _load_product_pool():
    """Load and cache valid products from the BigBasket catalog."""

    global _product_pool

    if _product_pool is not None:
        return _product_pool

    if not os.path.exists(_CSV_PATH):
        raise FileNotFoundError(
            f"BigBasket catalog not found at:\n{os.path.abspath(_CSV_PATH)}"
        )

    df = pd.read_csv(_CSV_PATH)

    df = df.dropna(subset=["product", "sale_price"])
    df = df[df["sale_price"] > 0]

    _product_pool = df[
        ["index", "product", "sale_price"]
    ].to_dict("records")

    return _product_pool


def _next_transaction_id():
    """Generate a globally unique transaction ID."""

    return f"TXN-{uuid.uuid4().hex[:12].upper()}"


def generate_transaction():
    """Generate one valid synthetic transaction."""

    pool = _load_product_pool()

    product = random.choice(pool)

    quantity = random.randint(1, 5)

    price = round(float(product["sale_price"]), 2)

    tax_amount = round(price * 0.18, 2)

    return {
        "transaction_id": _next_transaction_id(),

        "timestamp": datetime.now(timezone.utc).isoformat(),

        "user_id": f"USR-{random.randint(1000, 9999)}",

        "product_id": f"PRD-{int(product['index'])}",

        "quantity": quantity,

        "price": price,

        "tax_amount": tax_amount,

        "payment_method": random.choice(PAYMENT_METHODS),

        "country": "IN",
    }


def generate_batch(n=10):
    """Generate n valid transaction records."""

    return [
        generate_transaction()
        for _ in range(n)
    ]


if __name__ == "__main__":

    print("IceStream Transaction Generator")
    print("-" * 60)

    batch = generate_batch(5)

    for transaction in batch:
        print(transaction)