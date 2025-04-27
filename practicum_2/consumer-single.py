from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from helpers_serializer import SerializerClass


# Настройка консьюмера
conf = {
    "bootstrap.servers": "localhost:9094",  # Адрес брокера Kafka
    "auto.offset.reset": "earliest",  # Начало чтения с самого начала
    "session.timeout.ms": 6000,  # Время ожидания активности от консьюмера
    "group.id": "single-consumer-1",
    "enable.auto.commit": True,  # Автоматический коммит смещений
}


def SingleMessageConsumer():

    consumer = Consumer(conf)
    consumer.subscribe(["first_topic"])

    deserializer = SerializerClass()

    try:
        print('Захожу в цикл')
        while True:
            msg = consumer.poll(0.1)

            if msg is None:
                continue
            if msg.error():
                print(f"Ошибка: {msg.error()}")
                continue

            deserializer_out = deserializer.deserialize(msg)

            value = deserializer_out[1]
            key = deserializer_out[0]


            print(
                f"Получено сообщение: {key=}, {value=}, "
                f"partition={msg.partition()}, offset={msg.offset()}"
            )

    finally:
        consumer.close()


if __name__ == "__main__":
    SingleMessageConsumer()