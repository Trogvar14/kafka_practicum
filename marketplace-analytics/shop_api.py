import json, time, os
from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:19092")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
    linger_ms=50
)

with open("products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

for product in products:
    producer.send("products", product)
    print(f"[SHOP API] Отправлен товар: {product['name']}")
    time.sleep(0.2)

producer.flush()
print("[SHOP API] Готово.")
