from pathlib import Path
from silver_processor import process_bronze_file


BRONZE_DIR = Path("storage/bronze/transactions")


def main():
    files = list(BRONZE_DIR.glob("*.jsonl"))

    if not files:
        print("No Bronze files found.")
        return

    for bronze_file in files:
        result = process_bronze_file(bronze_file)

        print("=" * 40)
        print(f"File: {bronze_file.name}")
        print(f"Processed: {result['processed']}")
        print(f"Valid: {result['valid']}")
        print(f"Invalid: {result['invalid']}")
        print("=" * 40)


if __name__ == "__main__":
    main()