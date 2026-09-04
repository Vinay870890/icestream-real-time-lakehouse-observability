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
);

CREATE TABLE IF NOT EXISTS default_catalog.default_database.kafka_transactions (
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
  'properties.group.id' = 'icestream-iceberg-sink',
  'scan.startup.mode' = 'earliest-offset',
  'format' = 'json'
);

USE CATALOG iceberg_catalog;

CREATE TABLE IF NOT EXISTS icestream.transactions (
  transaction_id STRING,
  product_id STRING,
  quantity INT,
  price DOUBLE,
  payment_method STRING,
  `timestamp` TIMESTAMP_LTZ(3)
);

INSERT INTO icestream.transactions
SELECT
  transaction_id,
  product_id,
  quantity,
  price,
  payment_method,
  CAST(`timestamp` AS TIMESTAMP_LTZ(3))
FROM default_catalog.default_database.kafka_transactions;
