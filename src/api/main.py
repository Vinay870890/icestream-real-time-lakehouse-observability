from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parents[2]
STORAGE_DIR = BASE_DIR / "storage"

METRICS_FILE = STORAGE_DIR / "metrics" / "pipeline_metrics.jsonl"
STATUS_FILE = STORAGE_DIR / "metrics" / "pipeline_status.json"
KPI_FILE = STORAGE_DIR / "analytics" / "kpi_report.json"
INCIDENT_FILE = STORAGE_DIR / "metrics" / "incident_log.jsonl"


app = FastAPI(
    title="IceStream API",
    description="Real-Time Lakehouse Observability Backend",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_json_file(path: Path):
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {}


def read_jsonl_file(path: Path):
    if not path.exists():
        return []

    records = []

    try:
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    except OSError:
        return []

    return records


@app.get("/")
def root():
    return {
        "service": "IceStream API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/status")
def get_status():
    status = read_json_file(STATUS_FILE)

    if not status:
        return {
            "status": "UNKNOWN",
            "action": "UNKNOWN",
            "error_rate": 0,
            "threshold": 0.02,
            "reason": "No pipeline status available",
        }

    return status


@app.get("/api/metrics")
def get_metrics():
    metrics = read_jsonl_file(METRICS_FILE)

    if not metrics:
        return {
            "total_records": 0,
            "valid_records": 0,
            "invalid_records": 0,
            "error_rate": 0,
            "error_breakdown": {},
        }

    return metrics[-1]


@app.get("/api/kpis")
def get_kpis():
    kpis = read_json_file(KPI_FILE)

    if not kpis:
        return {
            "total_transactions": 0,
            "total_quantity": 0,
            "total_revenue": 0,
            "average_order_value": 0,
            "unique_products": 0,
            "average_quantity_per_transaction": 0,
            "top_product": None,
            "top_product_revenue": 0,
        }

    return kpis


@app.get("/api/incidents")
def get_incidents():
    incidents = read_jsonl_file(INCIDENT_FILE)

    return {
        "count": len(incidents),
        "incidents": incidents[-20:][::-1],
    }