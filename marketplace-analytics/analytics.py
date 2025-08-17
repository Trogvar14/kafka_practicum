import json, os
from kafka import KafkaProducer, KafkaConsumer

BOOTSTRAP_A = os.getenv("KAFKA_BOOTSTRAP_A", "localhost:19092")
BOOTSTRAP_B = os.getenv("KAFKA_BOOTSTRAP_B", "localhost:19094")
READ_FROM = os.getenv("ANALYTICS_READ_CLUSTER", "A")
BOOTSTRAP = BOOTSTRAP_A if READ_FROM == "A" else BOOTSTRAP_B

consumer = KafkaConsumer(
    "client_requests",
    bootstrap_servers=BOOTSTRAP,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    group_id="analytics-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_A,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

print(f"[ANALYTICS] Читает client_requests из кластера {READ_FROM} ({BOOTSTRAP})")
for msg in consumer:
    data = msg.value
    if data.get("type") == "recommend":
        user = data.get("value")
        recommendations = [{"product_id": "12345", "score": 0.9}, {"product_id": "23456", "score": 0.8}]
        producer.send("recommendations", {"user": user, "items": recommendations})
        print(f"[ANALYTICS] Рекомендации отправлены для user={user}: {recommendations}")
