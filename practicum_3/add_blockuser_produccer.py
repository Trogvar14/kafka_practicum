import json
from confluent_kafka import Producer
import logging


conf = {
    "bootstrap.servers": "localhost:9094",
    "security.protocol": "PLAINTEXT",
}

producer = Producer(conf)
topic = "blocked_users_topic"

# Принимаем user_Id
print("Пожалуйста, введите ваш user_id")
sender_user_id = input()
print("Пожалуйста, введите user_id того, кого нужно заблокировать:")
recipient_user_id = input()

message_list = [
    {"sender_user_id": sender_user_id, "recipient_user_id": recipient_user_id},
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
