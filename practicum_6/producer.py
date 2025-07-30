# producer.py
from kafka import KafkaProducer
import ssl
import os
import time

cert_dir = "/app/client-creds"

print("Запуск продюсера...")

producer = KafkaProducer(
    bootstrap_servers=['kafka1:9093', 'kafka2:9095'],
    security_protocol="SSL",
    ssl_cafile=os.path.join(cert_dir, 'ca.crt'),
    ssl_certfile=os.path.join(cert_dir, 'client.crt'),
    ssl_keyfile=os.path.join(cert_dir, 'client.key'),
    ssl_password='changeit',
    value_serializer=lambda v: v.encode('utf-8'),
    acks='all',
    retries=5,
    retry_backoff_ms=1000
)

try:
    for i in range(10):
        msg1 = f"Hello to topic-1: {i}"
        msg2 = f"Hello to topic-2: {i}"
        producer.send('topic-1', msg1)
        producer.send('topic-2', msg2)
        print(f"Отправлено: {msg1}")
        print(f"Отправлено: {msg2}")
        time.sleep(1)
    producer.flush()
    print("✅ Все сообщения отправлены!")
except Exception as e:
    print(f"❌ Ошибка продюсера: {e}")
finally:
    producer.close()