import json
from pathlib import Path


def test_gold_summary_exists():
    summary_file = Path("storage/gold/daily_summary.json")

    assert summary_file.exists()

    with open(summary_file, "r", encoding="utf-8") as file:
        summary = json.load(file)

    assert "total_transactions" in summary
    assert "total_quantity" in summary
    assert "total_revenue" in summary
    assert "average_order_value" in summary
    assert "unique_products" in summary