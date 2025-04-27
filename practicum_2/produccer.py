from confluent_kafka import Producer
from helpers_serializer import SerializerClass

# Конфигурация продюсера – адрес сервера
conf = {
    "bootstrap.servers": "localhost:9094",
    "security.protocol": "PLAINTEXT",
}

# Создание продюсера
producer = Producer(conf)

# Сообщение для отправки
message_list = []

i = 1
while i <= 20:
    message_list.append({"id": i, "message": f"Тут должно быть сообщение - {i}"})
    i += 1

print(f"""Сгенерированный list с сообщениями: {message_list}""")


# Функция обратного вызова для подтверждения доставки
def delivery_report(err, msg):
   if err is not None:
       print(f"Message delivery failed: {err}")
   else:
       print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Тема Kafka
topic = 'first_topic'

serializer = SerializerClass()

# Отправка сообщения
for message_value in message_list:
    serializer_out = serializer.serialize(message_value, topic=topic)

    producer.produce(
       topic=topic,
       key=serializer_out[0],
       value=serializer_out[1],
       on_delivery=delivery_report
    )

# Ожидание завершения отправки всех сообщений
producer.flush()
