import json
from pathlib import Path


def test_kpi_report():
    file_path = Path("storage/analytics/kpi_report.json")

    assert file_path.exists()

    with open(file_path, "r", encoding="utf-8") as file:
        kpis = json.load(file)

    assert kpis["total_transactions"] >= 0
    assert kpis["total_quantity"] >= 0
    assert kpis["total_revenue"] >= 0
    assert kpis["average_order_value"] >= 0
    assert kpis["unique_products"] >= 0