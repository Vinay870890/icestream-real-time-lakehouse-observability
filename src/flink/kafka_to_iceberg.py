from pyflink.table import EnvironmentSettings, TableEnvironment


def main():
    # ============================================================
    # FLINK TABLE ENVIRONMENT
    # ============================================================
    settings = EnvironmentSettings.in_streaming_mode()
    table_env = TableEnvironment.create(settings)

    # ============================================================
    # CHECKPOINTING
    # IMPORTANT:
    # Configure this on TableEnvironment because this is a
    # Table API job.
    # ============================================================
    table_env.get_config().set(
        "execution.checkpointing.interval",
        "10s"
    )

    table_env.get_config().set(
        "execution.checkpointing.timeout",
        "60s"
    )

    # ============================================================
    # ICEBERG REST CATALOG
    # ============================================================
    table_env.execute_sql("""
        CREATE CATALOG iceberg_catalog WITH (
            'type' = 'iceberg',
            'catalog-type' = 'rest',
            'uri' = 'http://iceberg-rest:8181',
            'warehouse' = 's3://warehouse/',
            'io-impl' = 'org.apache.iceberg.aws.s3.S3FileIO',
            's3.endpoint' = 'http://minio:9000',
            's3.access-key-id' = 'admin',
            's3.secret-access-key' = 'icestreamadmin',
            's3.path-style-access' = 'true'
        )
    """)

    # ============================================================
    # KAFKA SOURCE
    #
    # Keep Kafka in Flink's default catalog.
    # Do NOT create this table inside iceberg_catalog.
    # ============================================================
    table_env.execute_sql("""
        CREATE TABLE default_catalog.default_database.kafka_transactions (
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
            'properties.group.id' = 'icestream-flink-iceberg',
            'scan.startup.mode' = 'earliest-offset',
            'format' = 'json'
        )
    """)

    # ============================================================
    # SWITCH TO ICEBERG CATALOG
    # ============================================================
    table_env.execute_sql("""
        USE CATALOG iceberg_catalog
    """)

    # ============================================================
    # ICEBERG VALID TRANSACTIONS TABLE
    # ============================================================
    table_env.execute_sql("""
        CREATE TABLE IF NOT EXISTS icestream.transactions (
            transaction_id STRING,
            product_id STRING,
            quantity INT,
            price DOUBLE,
            payment_method STRING,
            `timestamp` TIMESTAMP_LTZ(3)
        )
    """)

    # ============================================================
    # ICEBERG DLQ TABLE
    #
    # This table will be used later for bad records.
    # ============================================================
    table_env.execute_sql("""
        CREATE TABLE IF NOT EXISTS icestream.transactions_dlq (
            transaction_id STRING,
            raw_record STRING,
            validation_errors STRING,
            quarantined_at TIMESTAMP_LTZ(3)
        )
    """)

    # ============================================================
    # VALID DATA → ICEBERG
    #
    # Only records satisfying the validation rules are written
    # to the Iceberg transactions table.
    # ============================================================
    table_env.execute_sql("""
        INSERT INTO icestream.transactions
        SELECT
            transaction_id,
            product_id,
            quantity,
            price,
            payment_method,
            CAST(`timestamp` AS TIMESTAMP_LTZ(3))
        FROM default_catalog.default_database.kafka_transactions
        WHERE transaction_id IS NOT NULL
          AND product_id IS NOT NULL
          AND quantity > 0
          AND price >= 0
          AND payment_method IS NOT NULL
          AND TRY_CAST(`timestamp` AS TIMESTAMP_LTZ(3)) IS NOT NULL
    """).wait()


if __name__ == "__main__":
    main()