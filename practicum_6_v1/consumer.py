# consumer.py
from kafka import KafkaConsumer
import ssl
import os

cert_dir = "/app/client-creds"

print("🚀 Запуск консьюмера...")

# Читаем из topic-1 (разрешено)
print("✅ Попытка чтения из topic-1 (должно работать)...")
try:
    consumer1 = KafkaConsumer(
        'topic-1',
        bootstrap_servers=['kafka-0:9092', 'kafka-1:9092', 'kafka-2:9092'],
        security_protocol="SASL_SSL",
        ssl_cafile=os.path.join(cert_dir, 'ca.crt'),
        ssl_certfile=os.path.join(cert_dir, 'client.crt'),
        ssl_keyfile=os.path.join(cert_dir, 'client.key'),
        ssl_password='your-password',  # может не требоваться, если не зашифрован
        sasl_mechanism='PLAIN',
        sasl_plain_username='consumer',
        sasl_plain_password='your-password',
        value_serializer=lambda v: v.encode('utf-8'),
        acks='all',
        retries=5,
        retry_backoff_ms=1000
    )

    for msg in consumer1:
        print(f"📥 topic-1: {msg.value.decode('utf-8')}")
        break  # Прочитаем одно сообщение
    consumer1.close()
    print("✅ Чтение из topic-1 прошло успешно")
except Exception as e:
    print(f"❌ Ошибка чтения из topic-1: {e}")

# Читаем из topic-2 (запрещено)
print("\n🔒 Попытка чтения из topic-2 (должно быть запрещено)...")
try:
    consumer2 = KafkaConsumer(
        'topic-2',
        bootstrap_servers=['kafka-0:9092', 'kafka-1:9092', 'kafka-2:9092'],
        security_protocol="SASL_SSL",
        ssl_cafile=os.path.join(cert_dir, 'ca.crt'),
        ssl_certfile=os.path.join(cert_dir, 'client.crt'),
        ssl_keyfile=os.path.join(cert_dir, 'client.key'),
        ssl_password='your-password',  # может не требоваться, если не зашифрован
        sasl_mechanism='PLAIN',
        sasl_plain_username='consumer',
        sasl_plain_password='your-password',
        value_serializer=lambda v: v.encode('utf-8'),
        acks='all',
        retries=5,
        retry_backoff_ms=1000
    )

    for msg in consumer2:
        print(f"📥 topic-2: {msg.value.decode('utf-8')}")
        break
    consumer2.close()
    print("❌ Ожидалась ошибка, но чтение прошло!")
except Exception as e:
    print(f"✅ Успешно: не удалось читать из topic-2 — {type(e).__name__}: {e}")