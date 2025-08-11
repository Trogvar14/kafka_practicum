# consumer_avro.py
from confluent_kafka import DeserializingConsumer, OFFSET_BEGINNING
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

BOOTSTRAP = "rc1a-d0bkq4hc1n66j6ib.mdb.yandexcloud.net:9091,rc1b-9qjr2o7ijg4vfb7r.mdb.yandexcloud.net:9091,rc1d-ebsqkrdpmlvp14i7.mdb.yandexcloud.net:9091"
SSL_CA = "/Users/macbook/Desktop/kafka_lessons/kafka_practicum/practicum_7/secrets/CA.pem"
SR_URL = "http://localhost:8081"
TOPIC = "topic-1"

sr = SchemaRegistryClient({"url": SR_URL})

# schema_str можно опустить — десериалайзер возьмет writer’s schema по id из сообщения.
value_deserializer = AvroDeserializer(
    schema_registry_client=sr,
    schema_str=None,
    from_dict=lambda v, ctx: v
)

conf = {
    "bootstrap.servers": BOOTSTRAP,
    "security.protocol": "SASL_SSL",
    "sasl.mechanisms": "SCRAM-SHA-512",
    "sasl.username": "user_1",
    "sasl.password": "Kasper12",
    "ssl.ca.location": SSL_CA,
    "group.id": "demo-avro-1",
    "auto.offset.reset": "earliest",
    "value.deserializer": value_deserializer,
}

def on_assign(c, parts):
    for p in parts: p.offset = OFFSET_BEGINNING
    c.assign(parts)

c = DeserializingConsumer(conf)
c.subscribe([TOPIC], on_assign=on_assign)

from time import time
deadline = time() + 30
while time() < deadline:
    msg = c.poll(2.0)
    if not msg:
        continue
    print("Получено:", msg.value())
    break
c.close()
