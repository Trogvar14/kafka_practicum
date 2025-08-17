import json, sys, time
from confluent_kafka import Producer

BOOTSTRAP = "localhost:19092"  # кластер A, EXTERNAL
CONF = {
    "bootstrap.servers": BOOTSTRAP,
    "security.protocol": "ssl",
    "ssl.ca.location": "certs/ca.crt",  # из твоего генератора
    "enable.idempotence": True,
    "linger.ms": 10,
    "batch.num.messages": 1000,
    "client.id": "shop-publisher",
}

def delivery(err, msg):
    if err:
        print(f"Delivery failed: {err}", file=sys.stderr)

def main(path):
    p = Producer(CONF)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            obj = json.loads(line)
            key = obj["product_id"].encode("utf-8")
            p.produce("shop.products.raw", value=line.encode("utf-8"), key=key, callback=delivery)
            p.poll(0)
    p.flush()
    print("DONE")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/products.jsonl")
