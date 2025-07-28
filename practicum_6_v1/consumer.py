import logging
import os
import time

from confluent_kafka import Consumer


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    filename="kafka_consumer.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    logger.info("До запуска 'consumer': 60 сек.")
    time.sleep(60)
    logger.info("Конфигурация 'consumer'...")

    consumer_conf = {
        "bootstrap.servers": 'kafka-0:9092',
        "group.id": 'consumer-ssl-group',
        "auto.offset.reset": "earliest",

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-0-creds/kafka-0.crt",
        "ssl.key.location": "kafka-0-creds/kafka-0.key",

        "ssl.endpoint.identification.algorithm": "none",
        "sasl.mechanism": "PLAIN",
        "sasl.username": 'consumer',
        "sasl.password": 'your-password',
    }

    try:
        consumer = Consumer(consumer_conf)
        consumer.subscribe(["topic-1", "topic-2"])

        try:
            while True:
                message = consumer.poll(1)

                if message is None:
                    continue
                if message.error():
                    logger.error(f"Ошибка при получении сообщения: {message.error()}")
                    continue

                key = message.key().decode("utf-8")
                value = message.value().decode("utf-8")
                offset = message.offset()
                logger.info(f"Получено сообщение: key='{key}', value='{value}', {offset=}")
        finally:
            consumer.close()
    except Exception as e:
            logger.error(e)
