import json
from pathlib import Path


GOLD_DIR = Path("storage/gold")
ANALYTICS_DIR = Path("storage/analytics")

ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)


def load_daily_summary():
    file_path = GOLD_DIR / "daily_summary.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_product_performance():
    file_path = GOLD_DIR / "product_performance.jsonl"

    products = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                products.append(json.loads(line))

    return products


def calculate_kpis(summary, products):
    total_transactions = summary["total_transactions"]
    total_quantity = summary["total_quantity"]
    total_revenue = summary["total_revenue"]

    average_quantity_per_transaction = (
        total_quantity / total_transactions
        if total_transactions > 0
        else 0
    )

    top_product = max(
        products,
        key=lambda product: product["total_revenue"],
        default=None
    )

    kpis = {
        "total_transactions": total_transactions,
        "total_quantity": total_quantity,
        "total_revenue": total_revenue,
        "average_order_value": summary["average_order_value"],
        "unique_products": summary["unique_products"],
        "average_quantity_per_transaction": round(
            average_quantity_per_transaction, 2
        ),
        "top_product": (
            top_product["product_id"]
            if top_product
            else None
        ),
        "top_product_revenue": (
            top_product["total_revenue"]
            if top_product
            else 0
        )
    }

    return kpis


def save_kpis(kpis):
    output_file = ANALYTICS_DIR / "kpi_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(kpis, file, indent=2)

    return output_file


def main():
    summary = load_daily_summary()
    products = load_product_performance()

    kpis = calculate_kpis(summary, products)
    output_file = save_kpis(kpis)

    print("=" * 50)
    print("          ICSTREAM KPI ANALYTICS")
    print("=" * 50)

    print(f"Total Transactions          : {kpis['total_transactions']}")
    print(f"Total Quantity              : {kpis['total_quantity']}")
    print(f"Total Revenue               : {kpis['total_revenue']}")
    print(f"Average Order Value         : {kpis['average_order_value']}")
    print(f"Unique Products             : {kpis['unique_products']}")
    print(
        f"Average Quantity/Transaction: "
        f"{kpis['average_quantity_per_transaction']}"
    )
    print(f"Top Product                 : {kpis['top_product']}")
    print(f"Top Product Revenue         : {kpis['top_product_revenue']}")

    print("=" * 50)
    print(f"KPI report saved to: {output_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()