from pyflink.table import EnvironmentSettings, TableEnvironment


# ============================================================
# FLINK STREAMING ENVIRONMENT
# ============================================================

settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(settings)

t_env.get_config().set(
    "execution.checkpointing.interval",
    "10s"
)

t_env.get_config().set(
    "execution.checkpointing.timeout",
    "60s"
)


# ============================================================
# ICEBERG REST CATALOG
# ============================================================

t_env.execute_sql("""
CREATE CATALOG iceberg_catalog WITH (
    'type' = 'iceberg',
    'catalog-type' = 'rest',
    'uri' = 'http://iceberg-rest:8181',
    'warehouse' = 's3://warehouse/',
    'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
    's3.endpoint' = 'http://minio:9000',
    's3.path-style-access' = 'true',
    's3.access-key-id' = 'admin',
    's3.secret-access-key' = 'icestreamadmin',
    'client.region' = 'us-east-1'
)
""")


# ============================================================
# ICEBERG DATABASE
# ============================================================

t_env.execute_sql("""
CREATE DATABASE IF NOT EXISTS iceberg_catalog.icestream
""")


# ============================================================
# MAIN ICEBERG TABLE
# ============================================================

t_env.execute_sql("""
CREATE TABLE IF NOT EXISTS iceberg_catalog.icestream.transactions (
    transaction_id STRING,
    product_id STRING,
    quantity INT,
    price DOUBLE,
    payment_method STRING,
    `timestamp` TIMESTAMP_LTZ(6)
)
""")


# ============================================================
# DLQ ICEBERG TABLE
# ============================================================

t_env.execute_sql("""
CREATE TABLE IF NOT EXISTS iceberg_catalog.icestream.transactions_dlq (
    transaction_id STRING,
    raw_record STRING,
    validation_errors STRING,
    quarantined_at TIMESTAMP_LTZ(6)
)
""")


# ============================================================
# KAFKA SOURCE
# ============================================================

t_env.execute_sql("""
CREATE TABLE kafka_transactions (
    transaction_id STRING,
    product_id STRING,
    quantity INT,
    price DOUBLE,
    payment_method STRING,
    `timestamp` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'transactions',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'icestream-flink-single-job',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.ignore-parse-errors' = 'true'
)
""")


# ============================================================
# DATA QUALITY CLASSIFICATION
# ============================================================

t_env.execute_sql("""
CREATE TEMPORARY VIEW classified_transactions AS
SELECT
    transaction_id,
    product_id,
    quantity,
    price,
    payment_method,
    `timestamp`,

    CASE
        WHEN transaction_id IS NULL
            THEN 'transaction_id is null'

        WHEN product_id IS NULL
            THEN 'product_id is null'

        WHEN quantity IS NULL OR quantity <= 0
            THEN 'quantity must be greater than 0'

        WHEN price IS NULL OR price < 0
            THEN 'price must be greater than or equal to 0'

        WHEN payment_method IS NULL
            THEN 'payment_method is null'

        WHEN UPPER(payment_method) NOT IN (
            'CREDIT_CARD',
            'DEBIT_CARD',
            'WALLET',
            'NET_BANKING',
            'COD',
            'UPI'
        )
            THEN 'invalid payment_method'

        WHEN `timestamp` IS NULL
            THEN 'timestamp is null'

        ELSE NULL
    END AS validation_error

FROM kafka_transactions
""")


# ============================================================
# STATEMENT SET
# ============================================================

statement_set = t_env.create_statement_set()


# ============================================================
# VALID RECORDS → MAIN ICEBERG TABLE
# ============================================================

statement_set.add_insert_sql("""
INSERT INTO iceberg_catalog.icestream.transactions
SELECT
    transaction_id,
    product_id,
    quantity,
    price,
    payment_method,

    CAST(
        REPLACE(
            SUBSTRING(`timestamp`, 1, 19),
            'T',
            ' '
        )
        AS TIMESTAMP_LTZ(6)
    ) AS `timestamp`

FROM classified_transactions

WHERE validation_error IS NULL
  AND `timestamp` IS NOT NULL
""")


# ============================================================
# INVALID RECORDS → DLQ ICEBERG TABLE
# ============================================================

statement_set.add_insert_sql("""
INSERT INTO iceberg_catalog.icestream.transactions_dlq
SELECT
    transaction_id,

    CONCAT(
        '{',
        '"transaction_id":"',
        COALESCE(transaction_id, ''),
        '","product_id":"',
        COALESCE(product_id, ''),
        '","quantity":',
        COALESCE(CAST(quantity AS STRING), 'null'),
        ',"price":',
        COALESCE(CAST(price AS STRING), 'null'),
        ',"payment_method":"',
        COALESCE(payment_method, ''),
        '","timestamp":"',
        COALESCE(`timestamp`, ''),
        '"}'
    ) AS raw_record,

    validation_error AS validation_errors,

    CURRENT_TIMESTAMP AS quarantined_at

FROM classified_transactions

WHERE validation_error IS NOT NULL
""")


# ============================================================
# START STREAMING JOB
# ============================================================

result = statement_set.execute()

print("STREAMING JOB SUBMITTED", flush=True)
print(result, flush=True)