import os

os.environ["AWS_ACCESS_KEY_ID"] = "admin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "icestreamadmin"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_S3_ENDPOINT"] = "http://localhost:9000"

from pyiceberg.catalog import load_catalog

catalog = load_catalog(
    "iceberg_rest",
    type="rest",
    uri="http://localhost:8181",
    warehouse="s3://warehouse/",
    **{
        "s3.endpoint": "http://localhost:9000",
        "s3.path-style-access": "true",
        "s3.access-key-id": "admin",
        "s3.secret-access-key": "icestreamadmin",
    }
)

main = catalog.load_table(("icestream", "transactions"))
dlq = catalog.load_table(("icestream", "transactions_dlq"))

print("--- MAIN: TEST-VALID-001 ---")
print(main.scan(
    row_filter="transaction_id = 'TEST-VALID-001'"
).to_arrow())

print("--- MAIN: TEST-INVALID-001 ---")
print(main.scan(
    row_filter="transaction_id = 'TEST-INVALID-001'"
).to_arrow())

print("--- DLQ: TEST-INVALID-001 ---")
print(dlq.scan(
    row_filter="transaction_id = 'TEST-INVALID-001'"
).to_arrow())
