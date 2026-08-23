from src.lakehouse.bronze_writer import write_to_bronze


def test_bronze_writer():
    transaction = {
        "transaction_id": "TEST-001",
        "product_id": "PRD-001",
        "quantity": 2,
        "price": 500
    }

    output_file = write_to_bronze(transaction)

    assert output_file.exists()