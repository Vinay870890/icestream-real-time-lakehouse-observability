# 🧊 IceStream — Real-Time Lakehouse Observability

> A real-time data engineering and lakehouse observability pipeline that detects bad streaming data **before** it reaches downstream analytics systems.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Kafka](https://img.shields.io/badge/Streaming-Apache%20Kafka-black)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688)
![React](https://img.shields.io/badge/Frontend-React-61DAFB)
![Tests](https://img.shields.io/badge/Tests-10%20passed-brightgreen)

---

## Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Architecture](#-architecture)
- [Data Flow](#-data-flow)
- [REST API](#-rest-api)
- [React Monitoring Dashboard](#-react-monitoring-dashboard)
- [Project Structure](#-project-structure)
- [Storage Architecture](#-storage-architecture)
- [Testing](#-testing)
- [Running the Project](#-running-the-project)
- [Example Outputs](#-example-outputs)
- [Technology Stack](#-technology-stack)
- [Key Engineering Concepts](#-key-engineering-concepts)
- [Reliability Design](#-reliability-design)
- [Current Project Validation](#-current-project-validation)
- [Project Status](#-project-status)
- [Future Enhancements](#-future-enhancements)
- [Resume Description](#-resume-description)
- [Key Project Achievement](#-key-project-achievement)
- [Author](#-author)

---

## 📖 Overview

**IceStream** is a real-time data engineering and lakehouse observability pipeline designed to detect bad streaming data before it reaches downstream analytics systems.

The project simulates an e-commerce transaction platform where streaming events are generated, deliberately exposed to data-quality failures, validated, processed through **Bronze / Silver / Gold** layers, monitored through observability metrics, and automatically quarantined when the error rate exceeds a defined threshold.

It combines data ingestion, data-quality validation, lakehouse-style processing, KPI analytics, pipeline observability, circuit-breaker protection, automated remediation, incident logging, REST API integration, and a React-based monitoring dashboard.

---

## 🎯 Problem Statement

Traditional batch pipelines can allow bad data to remain undetected until downstream reports or dashboards are affected.

IceStream addresses this problem by introducing:

- Real-time transaction generation
- Streaming ingestion through Apache Kafka
- Data-quality validation
- Bronze/Silver/Gold architecture
- Invalid-record quarantine
- Data-quality metrics
- KPI analytics
- Circuit-breaker protection
- Pipeline Guard logic
- Automated remediation
- Incident logging
- REST API for observability data
- React-based monitoring dashboard
- Automated testing

---

## 🏗️ Architecture

```
                    E-Commerce Transactions
                              |
                              v
                    Transaction Generator
                              |
                              v
                       Bad Data Injection
                              |
                              v
                         Apache Kafka
                              |
                              v
                            Bronze
                              |
                              v
                         Validation
                         /        \
                        /          \
                     Valid        Invalid
                       |             |
                       v             v
                    Silver      Quarantine
                       |
                       v
                      Gold
                       |
                       v
                 KPI Analytics
                       |
                       v
                  Observability
                       |
                       v
                 Circuit Breaker
                  /           \
             <= 2%             > 2%
                |                |
                v                v
             CONTINUE          PAUSE
                                  |
                                  v
                         Automated Remediation
                                  |
                                  v
                           Incident Logging
                                  |
                                  v
                           FastAPI Backend
                                  |
                                  v
                         React / React Flow
                            Dashboard
```

---

## 🔄 Data Flow

### 1. Transaction Generation

The transaction generator creates simulated e-commerce transaction events.

Generated transactions contain fields such as:

- Transaction ID
- Product ID
- Quantity
- Price
- Payment information
- Transaction metadata

**Implementation:**
```
src/stream_generator/
├── bad_data.py
├── generator.py
└── schema.py
```

### 2. Bad Data Injection

The pipeline deliberately introduces invalid records to simulate real-world data-quality problems, including:

- Missing values
- Invalid values
- Incorrect quantities
- Invalid transaction fields
- Malformed records

This allows the observability and remediation components to be tested against controlled pipeline failures.

**Implementation:** `src/stream_generator/bad_data.py`

### 3. Apache Kafka Streaming

Apache Kafka acts as the streaming layer between transaction generation and downstream processing.

```
Transaction Producer
        |
        v
    Kafka Topic
        |
        v
Stream Consumer / Processor
```

Kafka allows the project to simulate continuous event-driven data processing rather than relying only on traditional batch ingestion.

**Implementation:**
```
src/streaming/
├── producer.py
├── consumer.py
└── processor.py
```

### 4. Bronze Layer

The Bronze layer stores incoming transaction data in its raw form, preserving records before downstream validation and transformation.

```
Kafka
  |
  v
Bronze
```

**Implementation:** `src/lakehouse/bronze_writer.py`
**Storage:** `storage/bronze/`

### 5. Silver Layer

The Silver layer contains validated and cleaned transaction records. Bronze data is processed and separated into valid and invalid records.

```
             Bronze
                |
                v
            Validation
            /        \
           /          \
        Valid        Invalid
          |             |
          v             v
       Silver       Quarantine
```

Only valid records continue toward the analytical Gold layer.

**Implementation:**
```
src/lakehouse/
├── silver_processor.py
└── run_silver.py
```

### 6. Gold Layer

The Gold layer contains business-level aggregated information generated from processed Silver data.

Current Gold metrics include:

- Total transactions
- Total quantity
- Total revenue
- Average order value
- Unique products
- Product-level performance

```
Silver Transactions
        |
        v
   Aggregation
        |
        v
       Gold
```

**Implementation:** `src/lakehouse/gold_processor.py`

### 7. KPI Analytics

The analytics layer generates business KPIs from processed transaction data.

Current KPIs include:

- Total Transactions
- Total Quantity
- Total Revenue
- Average Order Value
- Unique Products
- Average Quantity / Transaction
- Top Product
- Top Product Revenue

**Implementation:** `src/analytics/kpi_analyzer.py`
**Output:** `storage/analytics/kpi_report.json`

### 8. Observability

IceStream monitors the health and quality of the data pipeline. The observability layer tracks:

- Processed records
- Valid records
- Invalid records
- Error rate
- Pipeline status
- Pipeline actions
- Incident information

**Implementation:** `src/observability/`
**Metrics:** `storage/metrics/pipeline_metrics.jsonl`
**Status:** `storage/metrics/pipeline_status.json`

### 9. Circuit Breaker

The circuit breaker protects downstream processing from excessive data-quality failures.

**Configured error-rate threshold:** `2%`

**Decision rule:**

```
Error Rate <= 2%          Error Rate > 2%
        |                          |
        v                          v
     CLOSED                       OPEN
        |                          |
        v                          v
    CONTINUE                     PAUSE
```

An error rate of exactly 2% is allowed.

**Boundary condition:**
```
Processed : 1000
Invalid   : 20
Error Rate: 2.00%
Threshold : 2.00%
Status    : CLOSED
Action    : CONTINUE
```

**Pipeline pauses:**
```
Processed : 1000
Invalid   : 21
Error Rate: 2.10%
Threshold : 2.00%
Status    : OPEN
Action    : PAUSE
```

**Implementation:** `src/observability/circuit_breaker.py`

> The circuit-breaker behavior is covered by automated tests, including the exact 2% boundary condition.

### 10. Pipeline Guard

The Pipeline Guard evaluates the circuit-breaker decision and determines whether the pipeline should continue or pause.

```
Data Quality Metrics
        |
        v
 Circuit Breaker
        |
   +----+----+
   |         |
   v         v
CONTINUE    PAUSE
```

**Implementation:** `src/observability/pipeline_guard.py`

The Pipeline Guard provides a protection layer between data-quality monitoring and downstream processing.

### 11. Automated Remediation

When the circuit breaker opens, the remediation layer handles the failed pipeline state.

```
Circuit Breaker
      |
      v
     OPEN
      |
      v
  QUARANTINE
      |
      v
 Pipeline PAUSED
      |
      v
 Incident Logged
```

**Implementation:** `src/observability/remediation.py`

The remediation component separates failure handling from the circuit-breaker decision itself.

### 12. Quarantine

Invalid records are separated from valid records and stored in quarantine storage.

```
Invalid Transaction
        |
        v
    Quarantine
```

This prevents invalid records from entering the normal analytical flow while preserving them for investigation.

**Storage:** `storage/quarantine/`

### 13. Incident Logging

When data-quality problems cause the pipeline to exceed the configured threshold, IceStream records an incident.

The incident log records information such as:

- Timestamp
- Pipeline status
- Error rate
- Threshold
- Pipeline action
- Reason for the incident

**Implementation:** `src/observability/incident_logger.py`
**Storage:** `storage/metrics/incident_log.jsonl`

---

## 🌐 REST API

IceStream includes a FastAPI backend that exposes pipeline observability and analytics data to the dashboard.

**Implementation:** `src/api/main.py`

**Start the API** (from the project root):

```bash
python -m uvicorn src.api.main:app --reload
```

The API runs locally on: `http://127.0.0.1:8000`

### Available Endpoints

| Endpoint | Purpose |
|---|---|
| `/` | API service information |
| `/api/status` | Current pipeline status |
| `/api/metrics` | Latest pipeline metrics |
| `/api/kpis` | Business KPI report |
| `/api/incidents` | Recent incident history |

FastAPI interactive documentation: `http://127.0.0.1:8000/docs`

---

## 💻 React Monitoring Dashboard

IceStream includes a React dashboard for visualizing pipeline health, business KPIs, data-quality metrics, incidents, and pipeline architecture. The dashboard uses **React Flow** to visualize the pipeline architecture.

**Directory:** `dashboard/`

**Start the dashboard** (in another terminal):

```bash
cd dashboard
npm install
npm run dev
```

The dashboard is available at: `http://localhost:5173`

### Dashboard Features

- Pipeline health status
- Error-rate monitoring
- Valid and invalid record counts
- Business KPI analytics
- Product analytics
- Circuit-breaker state
- Pipeline protection status
- Recent incident history
- React Flow pipeline architecture visualization
- Automatic dashboard refresh
- FastAPI backend integration

---

## 📁 Project Structure

```
icestream-real-time-lakehouse-observability/
|
├── src/
│   |
│   ├── analytics/
│   │   └── kpi_analyzer.py
│   |
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   |
│   ├── lakehouse/
│   │   ├── bronze_writer.py
│   │   ├── gold_processor.py
│   │   ├── run_pipeline.py
│   │   ├── run_silver.py
│   │   ├── silver_processor.py
│   │   └── flink/
│   │
│   ├── observability/
│   │   ├── circuit_breaker.py
│   │   ├── final_status.py
│   │   ├── incident_logger.py
│   │   ├── metrics.py
│   │   ├── pipeline_guard.py
│   │   ├── remediation.py
│   │   ├── report.py
│   │   └── run_observability.py
│   │
│   ├── quality/
│   │   ├── rules.py
│   │   └── validator.py
│   │
│   ├── storage/
│   │   ├── storage_manager.py
│   │   └── writers.py
│   │
│   ├── streaming/
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   └── processor.py
│   │
│   └── stream_generator/
│       ├── bad_data.py
│       ├── generator.py
│       └── schema.py
│
├── dashboard/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── tests/
│   ├── test_bronze.py
│   ├── test_circuit_breaker.py
│   ├── test_kpis.py
│   ├── test_lakehouse_pipeline.py
│   ├── test_pipeline_guard.py
│   └── test_remediation.py
│
├── storage/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── quarantine/
│   ├── metrics/
│   └── analytics/
│
├── requirements.txt
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🗄️ Storage Architecture

IceStream follows a layered data architecture:

```
                  Raw Data
                     |
                     v
                  BRONZE
                     |
                     v
                 Validation
                  /       \
                 /         \
                v           v
             SILVER     QUARANTINE
                |
                v
               GOLD
                |
                v
             ANALYTICS
```

| Layer | Description | Path |
|---|---|---|
| **Bronze** | Stores incoming transaction records in raw form | `storage/bronze/` |
| **Silver** | Stores validated and cleaned transaction records | `storage/silver/` |
| **Gold** | Stores business-level aggregated data | `storage/gold/` |
| **Quarantine** | Stores invalid records that fail validation | `storage/quarantine/` |
| **Metrics** | Stores pipeline observability and incident information | `storage/metrics/` |
| **Analytics** | Stores generated KPI reports | `storage/analytics/` |

> Generated runtime data is excluded from version control through `.gitignore`.

---

## 🧪 Testing

The project uses **pytest** for automated testing. The test suite covers:

- Bronze writer
- Circuit-breaker behavior
- Exact 2% threshold boundary
- Pipeline Guard
- KPI analytics
- Lakehouse pipeline
- Remediation
- Quarantine behavior

**Run the complete test suite:**

```bash
python -m pytest tests -v
```

**Current validated result:**
```
10 passed in 0.32s
```

---

## 🚀 Running the Project

### 1. Install Python Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### 2. Run the Lakehouse Pipeline

```bash
python src\lakehouse\run_pipeline.py
```

This executes the Silver and Gold processing stages.

### 3. Generate KPI Analytics

```bash
python src\analytics\kpi_analyzer.py
```

This generates `storage/analytics/kpi_report.json`.

### 4. Run Pipeline Guard

```bash
python -m src.observability.pipeline_guard
```

Example output:
```
Processed       : 100
Valid           : 97
Invalid         : 3
Error Rate      : 3.00%
Threshold       : 2.00%
Circuit Status  : OPEN
Pipeline Action : PAUSE
Reason          : Data quality error rate exceeded 2%
```

### 5. Run Observability

```bash
python -m src.observability.run_observability
```

This evaluates the latest pipeline metrics and updates pipeline status and incident information.

### 6. Start FastAPI

```bash
python -m uvicorn src.api.main:app --reload
```

### 7. Start React Dashboard

In another terminal:

```bash
cd dashboard
npm install
npm run dev
```

---

## 📊 Example Outputs

### Pipeline Output

A successful pipeline execution produces output similar to:

```
SILVER PROCESSING

transactions_2026-08-23.jsonl: Processed 1 Valid 1 Invalid 0
transactions_2026-08-24.jsonl: Processed 1 Valid 1 Invalid 0
transactions_2026-08-27.jsonl: Processed 3 Valid 3 Invalid 0

SILVER completed

GOLD PROCESSING

Total Transactions : 5
Total Quantity     : 10
Total Revenue      : 5000
Average Order Value: 1000.0
Unique Products    : 1

GOLD completed

PIPELINE COMPLETED
```

### KPI Output

```
Total Transactions          : 5
Total Quantity              : 10
Total Revenue               : 5000
Average Order Value         : 1000.0
Unique Products             : 1
Average Quantity/Transaction: 2.0
Top Product                 : PRD-001
Top Product Revenue         : 5000.0
```

The KPI report is written to `storage/analytics/kpi_report.json`.

### Circuit Breaker Examples

**Healthy pipeline:**
```
Processed       : 100
Valid           : 99
Invalid         : 1
Error Rate      : 1.00%
Threshold       : 2.00%
Circuit Status  : CLOSED
Pipeline Action : CONTINUE
```

**Failed pipeline:**
```
Processed       : 100
Valid           : 97
Invalid         : 3
Error Rate      : 3.00%
Threshold       : 2.00%
Circuit Status  : OPEN
Pipeline Action : PAUSE
```

---

## 🛠️ Technology Stack

| Category | Tools / Technologies |
|---|---|
| Programming | Python 3.11 |
| Streaming | Apache Kafka |
| Data Processing | Pandas, JSON, JSONL |
| Data Generation | Faker |
| Configuration | python-dotenv |
| Data Quality | Python validation rules, automated data-quality checks |
| Lakehouse / Processing | Apache Flink (integration/infrastructure), Apache Iceberg (integration/infrastructure), Bronze/Silver/Gold architecture |
| Backend | FastAPI, Uvicorn |
| Frontend | React, React Flow, Vite |
| Testing | Pytest |
| Infrastructure | Docker, Docker Compose |
| Version Control | Git, GitHub |

---

## 🧠 Key Engineering Concepts

IceStream demonstrates practical data-engineering and reliability-engineering concepts, including:

- Real-time event streaming
- Kafka-based ingestion
- Data-quality validation
- Bronze/Silver/Gold architecture
- Lakehouse concepts
- Data quarantine
- Pipeline observability
- KPI analytics
- Error-rate monitoring
- Circuit-breaker patterns
- Pipeline protection
- Automated remediation
- Incident logging
- Failure handling
- REST API integration
- React Flow architecture visualization
- Automated testing

---

## 🛡️ Reliability Design

The main reliability principle of IceStream is:

```
                 Detect
                    |
                    v
                 Validate
                    |
                    v
                  Measure
                    |
                    v
              Check Threshold
                    |
              +-----+-----+
              |           |
              v           v
           Healthy      Failure
              |           |
              v           v
          Continue       Pause
                            |
                            v
                       Quarantine
                            |
                            v
                      Incident Log
```

This prevents known data-quality failures from silently propagating into downstream analytical systems.

The design separates:

- Data generation
- Data validation
- Data processing
- Data-quality measurement
- Failure detection
- Pipeline protection
- Remediation
- Incident tracking
- Analytics
- Visualization

---

## ✅ Current Project Validation

The automated test suite has been validated with:

```
10 passed
0 failed
```

The implementation has been tested across:

- Data ingestion
- Bronze processing
- Silver processing
- Gold processing
- KPI generation
- Circuit-breaker decisions
- Exact 2% threshold behavior
- Pipeline Guard behavior
- Quarantine/remediation behavior
- Incident logging

The FastAPI backend has been validated with the following routes:

- `/`
- `/api/status`
- `/api/metrics`
- `/api/kpis`
- `/api/incidents`

The React dashboard provides a visual interface for pipeline and analytics states.

---

## 📌 Project Status

### Current Implementation

The current project provides a working data engineering and observability workflow:

```
Transaction Generation
        |
        v
Bad Data Injection
        |
        v
Apache Kafka
        |
        v
Bronze
        |
        v
Validation
        |
   +----+----+
   |         |
   v         v
Silver   Quarantine
   |
   v
Gold
   |
   v
KPI Analytics
   |
   v
Observability
   |
   v
Circuit Breaker
   |
   v
Pipeline Guard
   |
   v
Remediation
   |
   v
Incident Logging
   |
   v
FastAPI
   |
   v
React Dashboard
```

The core reliability workflow is implemented and covered by automated tests.

---

## 🔮 Future Enhancements

The project can be extended toward a more production-oriented lakehouse architecture with:

- Deeper Apache Flink stream-processing integration
- Production Apache Iceberg table workflows
- Great Expectations for advanced data-quality validation
- WebSocket-based live observability updates
- Cloud object storage such as Amazon S3
- Advanced React Flow lineage visualization
- Automated data re-fetching
- Time-travel data recovery workflows
- Production deployment
- Distributed processing
- Advanced anomaly detection
- More comprehensive alerting
- Cloud-native observability

These represent potential extensions beyond the current core implementation.

---

## 📝 Resume Description

> **IceStream – Real-Time Lakehouse Observability:** Built a Python and Apache Kafka-based real-time e-commerce transaction pipeline with Bronze/Silver/Gold data layers, automated data-quality validation, quarantine handling, KPI analytics, pipeline observability, incident logging, and a 2% circuit-breaker mechanism to protect downstream processing.

---

## 🏆 Key Project Achievement

The project demonstrates how a streaming data pipeline can move from:

```
Raw Events
    |
    v
Streaming
    |
    v
Validation
    |
    v
Data Quality
    |
    v
Quarantine
    |
    v
Observability
    |
    v
Automated Protection
    |
    v
Analytics
    |
    v
Visualization
```

**The central reliability principle of IceStream is:**

> Detect bad data early, isolate it automatically, and prevent it from propagating into downstream analytics.

---

## 👤 Author

Built as a real-time data engineering, lakehouse, and observability project.