import json
from datetime import datetime
from pathlib import Path


BRONZE_DIR = Path("storage/bronze/transactions")
BRONZE_DIR.mkdir(parents=True, exist_ok=True)


def write_to_bronze(transaction):
    """
    Store the raw transaction in the Bronze layer.
    """

    record = {
        "ingestion_timestamp": datetime.utcnow().isoformat(),
        "raw_transaction": transaction
    }

    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    output_file = BRONZE_DIR / f"transactions_{date_str}.jsonl"

    with open(output_file, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    return output_file