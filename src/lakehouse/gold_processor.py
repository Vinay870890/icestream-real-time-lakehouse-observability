import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime


SILVER_DIR = Path("storage/silver/transactions")
GOLD_DIR = Path("storage/gold")

GOLD_DIR.mkdir(parents=True, exist_ok=True)


def load_silver_records():
    records = []

    for file in SILVER_DIR.glob("*.jsonl"):
        with open(file, "r", encoding="utf-8") as source:
            for line in source:
                line = line.strip()

                if not line:
                    continue

                records.append(json.loads(line))

    return records


def create_daily_summary(records):
    total_transactions = len(records)
    total_quantity = sum(record["quantity"] for record in records)
    total_revenue = sum(record["total_amount"] for record in records)

    unique_products = len(
        set(record["product_id"] for record in records)
    )

    average_order_value = (
        total_revenue / total_transactions
        if total_transactions > 0
        else 0
    )

    summary = {
        "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "total_transactions": total_transactions,
        "total_quantity": total_quantity,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(average_order_value, 2),
        "unique_products": unique_products
    }

    output_file = GOLD_DIR / "daily_summary.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    return summary


def create_product_performance(records):
    products = defaultdict(
        lambda: {
            "quantity": 0,
            "revenue": 0.0,
            "transactions": 0
        }
    )

    for record in records:
        product_id = record["product_id"]

        products[product_id]["quantity"] += record["quantity"]
        products[product_id]["revenue"] += record["total_amount"]
        products[product_id]["transactions"] += 1

    output_file = GOLD_DIR / "product_performance.jsonl"

    with open(output_file, "w", encoding="utf-8") as file:
        for product_id, data in products.items():

            result = {
                "product_id": product_id,
                "total_quantity": data["quantity"],
                "total_revenue": round(data["revenue"], 2),
                "transaction_count": data["transactions"]
            }

            file.write(json.dumps(result) + "\n")

    return products


def main():
    records = load_silver_records()

    if not records:
        print("No Silver records found.")
        return

    summary = create_daily_summary(records)
    create_product_performance(records)

    print("=" * 45)
    print("          ICSTREAM GOLD LAYER")
    print("=" * 45)

    print(f"Total Transactions : {summary['total_transactions']}")
    print(f"Total Quantity     : {summary['total_quantity']}")
    print(f"Total Revenue      : {summary['total_revenue']}")
    print(f"Average Order Value: {summary['average_order_value']}")
    print(f"Unique Products    : {summary['unique_products']}")

    print("=" * 45)
    print("Gold layer generated successfully.")
    print("=" * 45)


if __name__ == "__main__":
    main()