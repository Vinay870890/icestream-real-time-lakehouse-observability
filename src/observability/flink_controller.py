from pathlib import Path
import json
import urllib.request
import urllib.error

FLINK_API = "http://localhost:8081"
STATUS_FILE = Path("storage/metrics/pipeline_status.json")


def get_pipeline_status():
    if not STATUS_FILE.exists():
        print("[ERROR] pipeline_status.json not found.")
        return None

    with open(STATUS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_running_jobs():
    url = f"{FLINK_API}/jobs/overview"

    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode("utf-8"))

    return [
        job for job in data.get("jobs", [])
        if job.get("state") == "RUNNING"
    ]


def cancel_job(job_id):
    url = f"{FLINK_API}/jobs/{job_id}?mode=cancel"

    request = urllib.request.Request(
        url,
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as error:
        print(f"[ERROR] Failed to cancel Flink job: HTTP {error.code}")
        return None


def main():
    print("=" * 60)
    print("       ICSTREAM FLINK CIRCUIT CONTROLLER")
    print("=" * 60)

    status = get_pipeline_status()

    if status is None:
        return

    print(f"Pipeline status : {status.get('status')}")
    print(f"Pipeline action : {status.get('action')}")
    print(f"Error rate      : {status.get('error_rate', 0) * 100:.2f}%")
    print(f"Threshold       : {status.get('threshold', 0) * 100:.2f}%")

    try:
        jobs = get_running_jobs()
    except Exception as error:
        print(f"[ERROR] Could not connect to Flink: {error}")
        return

    print(f"Running jobs    : {len(jobs)}")

    if status.get("status") != "OPEN":
        print()
        print("[OK] Circuit is CLOSED.")
        print("[OK] No Flink action required.")
        return

    if not jobs:
        print()
        print("[INFO] Circuit is OPEN.")
        print("[INFO] No running Flink job to stop.")
        return

    print()
    print("[ALERT] Circuit breaker is OPEN.")
    print("[ACTION] Cancelling running Flink job(s)...")

    for job in jobs:
        job_id = job.get("jid") or job.get("id")
        job_name = job.get("name", "UNKNOWN")

        print()
        print(f"Job : {job_name}")
        print(f"ID  : {job_id}")

        result = cancel_job(job_id)

        if result:
            print(f"[OK] Flink job cancellation accepted: HTTP {result}")
        else:
            print("[ERROR] Flink job cancellation failed.")

    print()
    print("=" * 60)
    print("       FLINK CIRCUIT ACTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
