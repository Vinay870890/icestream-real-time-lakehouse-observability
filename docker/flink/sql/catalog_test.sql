CREATE CATALOG icestream_catalog WITH (
  'type'='iceberg',
  'catalog-type'='rest',
  'uri'='http://iceberg-rest:8181',
  'warehouse'='s3://warehouse/',
  'io-impl'='org.apache.iceberg.aws.s3.S3FileIO',
  's3.endpoint'='http://minio:9000',
  's3.access-key-id'='admin',
  's3.secret-access-key'='icestreamadmin',
  's3.path-style-access'='true'
);

USE CATALOG icestream_catalog;

SHOW DATABASES;
