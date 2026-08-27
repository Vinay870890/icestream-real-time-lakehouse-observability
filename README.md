# \# IceStream – Real-Time Lakehouse Observability

# 

# \## Overview

# 

# IceStream is a real-time data engineering and lakehouse observability

# pipeline designed to detect bad streaming data before it reaches

# downstream analytics systems.

# 

# The project simulates an e-commerce transaction platform where streaming

# events are generated, deliberately exposed to data-quality failures,

# validated, processed through Bronze/Silver/Gold layers, monitored through

# observability metrics, and automatically quarantined when the error rate

# exceeds a defined threshold.

# 

# \## Problem Statement

# 

# Traditional batch pipelines can allow bad data to remain undetected until

# downstream reports or dashboards are affected.

# 

# IceStream addresses this problem by introducing:

# 

# \- Real-time transaction generation

# \- Streaming ingestion through Apache Kafka

# \- Data-quality validation

# \- Bronze/Silver/Gold data layers

# \- Invalid-record quarantine

# \- Data-quality metrics

# \- KPI analytics

# \- Circuit-breaker protection

# \- Automated pipeline guard logic

# \- Incident logging

# \- Automated testing

# 

# \## Architecture

# 

# ```text

# E-Commerce Transactions

# &#x20;         |

# &#x20;         v

# Transaction Generator

# &#x20;         |

# &#x20;         v

# Bad Data Injection

# &#x20;         |

# &#x20;         v

# &#x20;     Apache Kafka

# &#x20;         |

# &#x20;         v

# &#x20;       Bronze

# &#x20;         |

# &#x20;         v

# &#x20;     Validation

# &#x20;      /       \\

# &#x20;     /         \\

# &#x20;  Valid       Invalid

# &#x20;    |             |

# &#x20;    v             v

# &#x20;  Silver      Quarantine

# &#x20;    |

# &#x20;    v

# &#x20;   Gold

# &#x20;    |

# &#x20;    v

# KPI Analytics

# &#x20;    |

# &#x20;    v

# Observability

# &#x20;    |

# &#x20;    v

# Circuit Breaker

# &#x20;    |

# &#x20;    +----------------+

# &#x20;    |                |

# &#x20;  <= 2%             > 2%

# &#x20;    |                |

# &#x20; CONTINUE           PAUSE

# &#x20;                     |

# &#x20;                     v

# &#x20;               Incident Log

# &#x20;                     |

# &#x20;                     v

# &#x20;               React Dashboard

# ```

# 

# \## Data Flow

# 

# \### 1. Transaction Generation

# 

# The transaction generator creates simulated e-commerce transaction

# events.

# 

# The generated transactions contain fields such as:

# 

# \- Transaction ID

# \- Product ID

# \- Quantity

# \- Price

# \- Payment information

# \- Transaction metadata

# 

# \### 2. Bad Data Injection

# 

# The pipeline deliberately introduces invalid records to simulate

# real-world data-quality problems.

# 

# Examples include:

# 

# \- Missing values

# \- Invalid values

# \- Incorrect quantities

# \- Invalid transaction fields

# \- Malformed records

# 

# This allows the observability and remediation components to be tested

# against realistic pipeline failures.

# 

# \### 3. Apache Kafka Streaming

# 

# Apache Kafka acts as the streaming layer between transaction generation

# and downstream processing.

# 

# ```text

# Transaction Producer

# &#x20;       |

# &#x20;       v

# &#x20;   Kafka Topic

# &#x20;       |

# &#x20;       v

# Stream Consumer / Processor

# ```

# 

# Kafka allows the project to simulate continuous event-driven data

# processing rather than relying only on traditional batch ingestion.

# 

# \### 4. Bronze Layer

# 

# The Bronze layer stores incoming transaction data in its raw form.

# 

# The purpose of the Bronze layer is to preserve incoming records before

# downstream validation and transformation.

# 

# ```text

# Kafka

# &#x20; |

# &#x20; v

# Bronze

# ```

# 

# \### 5. Silver Layer

# 

# The Silver layer contains validated and cleaned transaction records.

# 

# The Bronze data is processed and separated into valid and invalid records.

# 

# ```text

# &#x20;            Bronze

# &#x20;               |

# &#x20;               v

# &#x20;          Validation

# &#x20;          /        \\

# &#x20;         /          \\

# &#x20;      Valid        Invalid

# &#x20;        |              |

# &#x20;        v              v

# &#x20;     Silver       Quarantine

# ```

# 

# Only valid records continue toward the analytical Gold layer.

# 

# \### 6. Gold Layer

# 

# The Gold layer contains business-level aggregated information generated

# from the Silver transaction data.

# 

# Current Gold metrics include:

# 

# \- Total transactions

# \- Total quantity

# \- Total revenue

# \- Average order value

# \- Unique products

# \- Product-level performance

# 

# Example:

# 

# ```text

# Silver Transactions

# &#x20;       |

# &#x20;       v

# &#x20;  Aggregation

# &#x20;       |

# &#x20;       v

# &#x20;     Gold

# &#x20;       |

# &#x20;  +----+----------------+

# &#x20;  |                     |

# Daily Summary      Product Performance

# ```

# 

# \### 7. KPI Analytics

# 

# The analytics layer generates business KPIs from processed transaction

# data.

# 

# Current KPIs include:

# 

# ```text

# Total Transactions

# Total Quantity

# Total Revenue

# Average Order Value

# Unique Products

# Average Quantity / Transaction

# Top Product

# Top Product Revenue

# ```

# 

# The resulting KPI report is stored in:

# 

# ```text

# storage/analytics/kpi\_report.json

# ```

# 

# \### 8. Observability

# 

# IceStream monitors the health and quality of the data pipeline.

# 

# The observability layer records information such as:

# 

# \- Processed records

# \- Valid records

# \- Invalid records

# \- Error rate

# \- Pipeline status

# \- Incident information

# 

# This allows pipeline failures to be identified instead of allowing bad

# data to silently flow into downstream analytics.

# 

# \### 9. Circuit Breaker

# 

# The circuit breaker protects downstream processing from excessive

# data-quality failures.

# 

# The configured error-rate threshold is:

# 

# ```text

# 2%

# ```

# 

# The behavior is:

# 

# ```text

# Error Rate <= 2%

# &#x20;       |

# &#x20;       v

# &#x20;   CONTINUE

# ```

# 

# ```text

# Error Rate > 2%

# &#x20;       |

# &#x20;       v

# &#x20;     PAUSE

# ```

# 

# The implementation also explicitly allows an error rate of exactly 2%.

# 

# For example:

# 

# ```text

# Processed : 1000

# Invalid   : 20

# Error Rate: 2.00%

# Status    : CLOSED

# Action    : CONTINUE

# ```

# 

# But:

# 

# ```text

# Processed : 1000

# Invalid   : 21

# Error Rate: 2.10%

# Status    : OPEN

# Action    : PAUSE

# ```

# 

# \### 10. Pipeline Guard

# 

# The Pipeline Guard evaluates the circuit-breaker decision and determines

# whether the pipeline should continue or pause.

# 

# ```text

# Data Quality Metrics

# &#x20;       |

# &#x20;       v

# &#x20; Circuit Breaker

# &#x20;       |

# &#x20;  +----+----+

# &#x20;  |         |

# &#x20;  v         v

# CONTINUE    PAUSE

# ```

# 

# This provides a protection mechanism between data-quality monitoring and

# downstream processing.

# 

# \### 11. Quarantine

# 

# Invalid records are separated from valid records and stored in

# quarantine storage.

# 

# ```text

# Invalid Transaction

# &#x20;       |

# &#x20;       v

# &#x20;  Quarantine

# ```

# 

# This prevents bad records from entering the normal analytical flow while

# preserving them for investigation.

# 

# \### 12. Incident Logging

# 

# When data-quality problems cause the pipeline to exceed the configured

# threshold, the system records incident information.

# 

# The incident log can be used to understand:

# 

# \- When the problem occurred

# \- The observed error rate

# \- The pipeline status

# \- Why processing was paused

# 

# \## Project Structure

# 

# ```text

# icestream-real-time-lakehouse-observability/

# |

# +-- src/

# |   |

# |   +-- generator/

# |   |

# |   +-- streaming/

# |   |

# |   +-- lakehouse/

# |   |   |

# |   |   +-- run\_pipeline.py

# |   |   +-- run\_silver.py

# |   |   +-- silver\_processor.py

# |   |   +-- gold\_processor.py

# |   |

# |   +-- analytics/

# |   |   |

# |   |   +-- kpi\_analyzer.py

# |   |

# |   +-- observability/

# |       |

# |       +-- circuit\_breaker.py

# |       +-- pipeline\_guard.py

# |       +-- remediation.py

# |

# +-- tests/

# |   |

# |   +-- test\_bronze.py

# |   +-- test\_circuit\_breaker.py

# |   +-- test\_kpis.py

# |   +-- test\_lakehouse\_pipeline.py

# |   +-- test\_pipeline\_guard.py

# |   +-- test\_remediation.py

# |

# +-- frontend/

# |

# +-- storage/

# |   |

# |   +-- bronze/

# |   +-- silver/

# |   +-- gold/

# |   +-- quarantine/

# |   +-- metrics/

# |   +-- analytics/

# |

# +-- README.md

# +-- requirements.txt

# +-- docker-compose.yml

# +-- .gitignore

# ```

# 

# \## Storage Layers

# 

# The project follows a layered data architecture.

# 

# ```text

# &#x20;             Raw Data

# &#x20;                |

# &#x20;                v

# &#x20;             BRONZE

# &#x20;                |

# &#x20;                v

# &#x20;            Validation

# &#x20;                |

# &#x20;         +------+------+

# &#x20;         |             |

# &#x20;         v             v

# &#x20;      SILVER       QUARANTINE

# &#x20;         |

# &#x20;         v

# &#x20;        GOLD

# &#x20;         |

# &#x20;         v

# &#x20;      ANALYTICS

# ```

# 

# \### Bronze

# 

# Stores incoming transaction records.

# 

# \### Silver

# 

# Stores validated and cleaned transaction records.

# 

# \### Gold

# 

# Stores business-level aggregated data.

# 

# \### Quarantine

# 

# Stores invalid records that fail validation.

# 

# \### Metrics

# 

# Stores pipeline observability and incident information.

# 

# \### Analytics

# 

# Stores generated KPI reports.

# 

# \## Testing

# 

# The project uses `pytest` for automated testing.

# 

# The test suite covers:

# 

# \- Bronze writer

# \- Circuit breaker behavior

# \- Pipeline guard

# \- KPI analytics

# \- Lakehouse pipeline

# \- Remediation

# \- Quarantine behavior

# 

# Run the complete test suite:

# 

# ```powershell

# python -m pytest tests -v

# ```

# 

# Current test status:

# 

# ```text

# 10 tests collected

# 10 tests passed

# 0 tests failed

# ```

# 

# \## Running the Project

# 

# \### Run the Lakehouse Pipeline

# 

# ```powershell

# python src\\lakehouse\\run\_pipeline.py

# ```

# 

# This executes the Silver and Gold processing stages.

# 

# \### Run KPI Analytics

# 

# ```powershell

# python src\\analytics\\kpi\_analyzer.py

# ```

# 

# This generates the KPI report.

# 

# \### Run Circuit Breaker

# 

# Use module execution:

# 

# ```powershell

# python -m src.observability.circuit\_breaker

# ```

# 

# \### Run Pipeline Guard

# 

# ```powershell

# python -m src.observability.pipeline\_guard

# ```

# 

# \### Run All Tests

# 

# ```powershell

# python -m pytest tests -v

# ```

# 

# \## Example Pipeline Output

# 

# A successful pipeline execution looks like:

# 

# ```text

# ============================================================

# &#x20; SILVER PROCESSING

# ============================================================

# 

# File: transactions\_2026-08-23.jsonl

# Processed: 1

# Valid: 1

# Invalid: 0

# 

# File: transactions\_2026-08-24.jsonl

# Processed: 1

# Valid: 1

# Invalid: 0

# 

# ✓ SILVER PROCESSING completed successfully

# 

# ============================================================

# &#x20; GOLD PROCESSING

# ============================================================

# 

# Total Transactions : 2

# Total Quantity     : 4

# Total Revenue      : 2000

# Average Order Value: 1000.0

# Unique Products    : 1

# 

# ✓ GOLD PROCESSING completed successfully

# 

# ============================================================

# &#x20;      ICSTREAM PIPELINE COMPLETED

# ============================================================

# ```

# 

# \## Example KPI Output

# 

# ```text

# ==================================================

# &#x20;         ICSTREAM KPI ANALYTICS

# ==================================================

# Total Transactions          : 2

# Total Quantity              : 4

# Total Revenue               : 2000

# Average Order Value         : 1000.0

# Unique Products             : 1

# Average Quantity/Transaction: 2.0

# Top Product                 : PRD-001

# Top Product Revenue         : 2000.0

# ==================================================

# ```

# 

# \## Circuit Breaker Example

# 

# \### Pipeline Continues

# 

# ```text

# Processed   : 100

# Invalid     : 1

# Error Rate  : 1.00%

# Threshold   : 2.00%

# Status      : CLOSED

# Action      : CONTINUE

# Reason      : Data quality within acceptable threshold

# ```

# 

# \### Pipeline Pauses

# 

# ```text

# Processed   : 100

# Invalid     : 3

# Error Rate  : 3.00%

# Threshold   : 2.00%

# Status      : OPEN

# Action      : PAUSE

# Reason      : Data quality error rate exceeded 2%

# ```

# 

# \## Technology Stack

# 

# \### Programming

# 

# \- Python 3.11

# 

# \### Streaming

# 

# \- Apache Kafka

# 

# \### Data Processing

# 

# \- Pandas

# \- JSON / JSONL

# 

# \### Data Generation

# 

# \- Faker

# 

# \### Configuration

# 

# \- Python-dotenv

# 

# \### Testing

# 

# \- Pytest

# 

# \### Frontend

# 

# \- React

# \- React Flow

# 

# \### Infrastructure

# 

# \- Docker

# 

# \### Version Control

# 

# \- Git

# \- GitHub

# 

# \## Key Engineering Concepts

# 

# IceStream demonstrates practical data-engineering and reliability

# engineering concepts including:

# 

# \- Real-time event streaming

# \- Data-quality validation

# \- Bronze/Silver/Gold architecture

# \- Data lakehouse concepts

# \- Data quarantine

# \- Pipeline observability

# \- KPI analytics

# \- Error-rate monitoring

# \- Circuit-breaker patterns

# \- Pipeline protection

# \- Automated remediation

# \- Incident logging

# \- Automated testing

# \- Failure handling

# 

# \## Reliability Design

# 

# The main reliability principle of IceStream is:

# 

# ```text

# &#x20;             Detect

# &#x20;               |

# &#x20;               v

# &#x20;            Validate

# &#x20;               |

# &#x20;               v

# &#x20;            Measure

# &#x20;               |

# &#x20;               v

# &#x20;         Check Threshold

# &#x20;               |

# &#x20;         +-----+-----+

# &#x20;         |           |

# &#x20;         v           v

# &#x20;      Healthy      Failure

# &#x20;         |           |

# &#x20;         v           v

# &#x20;     Continue       Pause

# &#x20;                     |

# &#x20;                     v

# &#x20;                 Quarantine

# &#x20;                     |

# &#x20;                     v

# &#x20;               Incident Log

# ```

# 

# This prevents known data-quality failures from silently propagating into

# downstream analytical systems.

# 

# \## Current Project Validation

# 

# The complete automated test suite currently reports:

# 

# ```text

# ============================== test session starts ==============================

# 

# 10 tests collected

# 

# 10 passed

# 0 failed

# 

# ============================== 10 passed ==============================

# ```

# 

# The pipeline has been verified across:

# 

# \- Data ingestion

# \- Bronze processing

# \- Silver processing

# \- Gold processing

# \- KPI generation

# \- Circuit-breaker decisions

# \- Pipeline guard behavior

# \- Quarantine/remediation behavior

# 

# \## Project Status

# 

# \*\*Core project completed.\*\*

# 

# The current implementation provides a working real-time data engineering

# and observability pipeline with:

# 

# ```text

# Transaction Generation

# &#x20;       |

# &#x20;       v

# Bad Data Injection

# &#x20;       |

# &#x20;       v

# Apache Kafka

# &#x20;       |

# &#x20;       v

# Bronze

# &#x20;       |

# &#x20;       v

# Validation

# &#x20;       |

# &#x20;  +----+----+

# &#x20;  |         |

# &#x20;  v         v

# Silver   Quarantine

# &#x20;  |

# &#x20;  v

# Gold

# &#x20;  |

# &#x20;  v

# KPI Analytics

# &#x20;  |

# &#x20;  v

# Observability

# &#x20;  |

# &#x20;  v

# Circuit Breaker

# &#x20;  |

# &#x20;  v

# Pipeline Guard

# ```

# 

# \## Future Enhancements

# 

# The project can be extended toward a more production-oriented lakehouse

# architecture with:

# 

# \- Apache Flink for continuous stream processing

# \- Apache Iceberg for ACID lakehouse tables

# \- Great Expectations for advanced data-quality validation

# \- WebSocket-based live observability updates

# \- Cloud object storage such as S3

# \- Advanced React Flow lineage visualization

# \- Automated data re-fetching

# \- Time-travel data recovery

# \- Production deployment

# \- Distributed processing

# \- Advanced anomaly detection

# 

# These are future extensions and are not represented as currently

# implemented components.

# 

# \## Resume Description

# 

# > \*\*IceStream – Real-Time Lakehouse Observability:\*\* Built a Python and

# > Apache Kafka-based real-time e-commerce transaction pipeline with

# > Bronze/Silver/Gold data layers, automated data-quality validation,

# > quarantine handling, KPI analytics, observability metrics, and a

# > 2% circuit-breaker mechanism to protect downstream processing.

# 

# \## Key Project Achievement

# 

# The project demonstrates how a streaming data pipeline can move from:

# 

# ```text

# Raw Events

# &#x20;   |

# &#x20;   v

# Streaming

# &#x20;   |

# &#x20;   v

# Validation

# &#x20;   |

# &#x20;   v

# Data Quality

# &#x20;   |

# &#x20;   v

# Quarantine

# &#x20;   |

# &#x20;   v

# Observability

# &#x20;   |

# &#x20;   v

# Automated Protection

# &#x20;   |

# &#x20;   v

# Analytics

# ```

# 

# The central principle of IceStream is:

# 

# > \*\*Detect bad data early, isolate it automatically, and prevent it from

# > propagating into downstream analytics.\*\*

# 

# \## Author

# 

# Built as a real-time data engineering, lakehouse, and observability

# project.

