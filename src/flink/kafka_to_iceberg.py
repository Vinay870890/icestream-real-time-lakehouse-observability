from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common import WatermarkStrategy, Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors.kafka import KafkaSource
import json

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

source = KafkaSource.builder() \
    .set_bootstrap_servers("kafka:9092") \
    .set_topics("transactions") \
    .set_group_id("icestream-iceberg-writer") \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

stream = env.from_source(
    source,
    WatermarkStrategy.no_watermarks(),
    "Kafka Transactions"
)

def parse_record(value):
    r = json.loads(value)
    return (
        r.get("transaction_id"),
        r.get("product_id"),
        int(r.get("quantity", 0)),
        float(r.get("price", 0)),
        r.get("payment_method"),
        r.get("timestamp")
    )

stream.map(
    parse_record,
    output_type=Types.TUPLE([
        Types.STRING(),
        Types.STRING(),
        Types.INT(),
        Types.DOUBLE(),
        Types.STRING(),
        Types.STRING()
    ])
).print()

env.execute("IceStream Kafka Transaction Pipeline")
