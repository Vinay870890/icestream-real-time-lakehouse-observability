import json
from datetime import datetime
from pathlib import Path


SILVER_DIR = Path("storage/silver/transactions")
QUARANTINE_DIR = Path("storage/quarantine")

SILVER_DIR.mkdir(parents=True, exist_ok=True)
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)


def process_bronze_file(bronze_file):
    silver_file = SILVER_DIR / bronze_file.name
    quarantine_file = (
        QUARANTINE_DIR / f"silver_quarantine_{bronze_file.stem}.jsonl"
    )

    processed = 0
    valid = 0
    invalid = 0

    with open(bronze_file, "r", encoding="utf-8") as source, \
         open(silver_file, "w", encoding="utf-8") as silver, \
         open(quarantine_file, "w", encoding="utf-8") as quarantine:

        for line in source:
            processed += 1

            try:
                record = json.loads(line)
                transaction = record["raw_transaction"]

                transaction_id = transaction.get("transaction_id")
                product_id = transaction.get("product_id")
                quantity = transaction.get("quantity")
                price = transaction.get("price")

                if not transaction_id:
                    raise ValueError("Missing transaction_id")

                if not product_id:
                    raise ValueError("Missing product_id")

                if not isinstance(quantity, int) or quantity <= 0:
                    raise ValueError("Invalid quantity")

                if not isinstance(price, (int, float)) or price <= 0:
                    raise ValueError("Invalid price")

                clean_record = {
                    "transaction_id": transaction_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": float(price),
                    "total_amount": round(quantity * price, 2),
                    "processed_timestamp": datetime.utcnow().isoformat()
                }

                silver.write(json.dumps(clean_record) + "\n")
                valid += 1

            except Exception as error:
                quarantine.write(json.dumps({
                    "error": str(error),
                    "original_record": line.strip()
                }) + "\n")

                invalid += 1

    return {
        "processed": processed,
        "valid": valid,
        "invalid": invalid
    }