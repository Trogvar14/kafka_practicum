from confluent_kafka import Consumer
from helpers_serializer import SerializerClass

# Настройка консьюмера
conf = {
    "bootstrap.servers": "localhost:9094",  # Адрес брокера Kafka
    "auto.offset.reset": "earliest",  # Начало чтения с самого начала
    "session.timeout.ms": 6000,  # Время ожидания активности от консьюмера
    "group.id": "batch-consumer-2",
    "enable.auto.commit": False,

    "security.protocol": "SSL",
    "ssl.ca.location": "ca.crt",  # Сертификат центра сертификации
    "ssl.certificate.location": "kafka-1-creds/kafka-1.crt",  # Сертификат клиента Kafka
    "ssl.key.location": "kafka-1-creds/kafka-1.key",  # Приватный ключ для клиента Kafka
}

def BatchMessageConsumer():
    consumer = Consumer(conf)
    consumer.subscribe(["topic-1"])

    deserializer = SerializerClass()

    try:
        batch_size = 10  # Минимум сообщений за poll
        while True:
            msg_list = consumer.consume(num_messages=batch_size, timeout=1.0)

            if not msg_list:
                continue

            process_success = False
            for msg in msg_list:
                if msg is None or msg.error():
                    print(f"Ошибка: {msg.error() if msg else 'None'}")
                    continue
                try:
                    # Десериализация сообщения
                    deserializer_out = deserializer.deserialize(msg)

                    value = deserializer_out[1]
                    key = deserializer_out[0]

                    print(f"Получено сообщение: {key=}, {value=}, "
                          f"partition={msg.partition()}, offset={msg.offset()}")

                except Exception as e:
                    print(f"Ошибка: {e}")

            # Коммит смещения только если были успешно обработаны сообщения
            if process_success:
                consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()

if __name__ == "__main__":
    BatchMessageConsumer()