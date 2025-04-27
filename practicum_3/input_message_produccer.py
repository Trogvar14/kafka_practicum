import json
from confluent_kafka import Producer
import logging


conf = {
    "bootstrap.servers": "localhost:9094",
    "security.protocol": "PLAINTEXT",
}

producer = Producer(conf)

topic = "message_input_topic"

# Принимаем сообщение
print("Пожалуйста, введите ваш user_id")
sender_user_id = str(input())
print("Пожалуйста, введите user_id того, кому адресовано сообщение:")
recipient_user_id = str(input())
print("Пожалуйста, введите сообщение:")
message = str(input())

message_list = [
    {"sender_user_id": sender_user_id, "recipient_user_id": recipient_user_id, "message":message},
]

def delivery_report(err, msg):
    if err:
        logging.error(f"Ошибка отправки: {err}")
    else:
        print(f"Сообщение отправлено в топик - {msg.topic()} [{msg.partition()}]")

for message in message_list:
    producer.produce(
        topic=topic,
        key="user_key".encode('utf-8'),
        value=json.dumps(message).encode('utf-8'),
        on_delivery=delivery_report,
    )

producer.flush()