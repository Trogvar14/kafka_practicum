# producer_avro.py
import os, json
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "rc1a-d0bkq4hc1n66j6ib.mdb.yandexcloud.net:9091,rc1b-9qjr2o7ijg4vfb7r.mdb.yandexcloud.net:9091,rc1d-ebsqkrdpmlvp14i7.mdb.yandexcloud.net:9091")
KAFKA_USERNAME = os.getenv("KAFKA_USERNAME", "user_1")
KAFKA_PASSWORD = os.getenv("KAFKA_PASSWORD", "Kasper12")
SSL_CA = os.getenv("SSL_CA", "/Users/macbook/Desktop/kafka_lessons/kafka_practicum/practicum_7/secrets/CA.pem")

SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
TOPIC = os.getenv("TOPIC", "topic-1")
SCHEMA_PATH = os.getenv("SCHEMA_PATH", "schema.json")

SR_AUTO_REGISTER = os.getenv("SR_AUTO_REGISTER", "true").lower() == "true"

if os.path.exists(SCHEMA_PATH):
    schema_str = open(SCHEMA_PATH, "r", encoding="utf-8").read()
else:
    # fallback — ваша схема из сообщения
    schema_str = json.dumps({
        "type": "record",
        "name": "User",
        "namespace": "com.example",
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
            {"name": "email", "type": ["string", "null"], "default": None},
            {"name": "age", "type": "int"}
        ]
    })

sr = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
value_serializer = AvroSerializer(
    schema_registry_client=sr,
    schema_str=schema_str,
    to_dict=lambda v, ctx: v,
    conf={"auto.register.schemas": SR_AUTO_REGISTER}
)

producer_conf = {
    "bootstrap.servers": BOOTSTRAP,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "SCRAM-SHA-512",
    "sasl.username": KAFKA_USERNAME,
    "sasl.password": KAFKA_PASSWORD,
    "ssl.ca.location": SSL_CA,
    "acks": "1",
    "compression.type": "none",
    "value.serializer": value_serializer,
}

producer = SerializingProducer(producer_conf)

def dr(err, msg):
    print("DELIVERY:", "OK" if err is None else err)

# пример сообщения
value = {"id": "1", "name": "Alice", "email": None, "age": 30}
producer.produce(TOPIC, value=value, on_delivery=dr)
producer.flush(10)
