import subprocess
import sys


def run_step(name, command):
    print("\n" + "=" * 60)
    print(f"  {name}")
    print("=" * 60)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"{name} failed.")

    print(f"✓ {name} completed successfully")


def main():
    python = sys.executable

    run_step(
        "SILVER PROCESSING",
        [python, "src/lakehouse/run_silver.py"]
    )

    run_step(
        "GOLD PROCESSING",
        [python, "src/lakehouse/gold_processor.py"]
    )

    print("\n" + "=" * 60)
    print("       ICSTREAM PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()