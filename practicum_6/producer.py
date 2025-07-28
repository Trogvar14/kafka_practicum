import logging
import os
import time
import uuid

from confluent_kafka import Producer


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    filename="kafka_producer.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    logger.info("До запуска 'producer': 60 сек.")
    time.sleep(60)
    logger.info("Конфигурация 'producer'...")

    producer_conf = {
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),

        "security.protocol": "SASL_SSL",
        "ssl.ca.location": "ca.crt",
        "ssl.certificate.location": "kafka-0-creds/kafka-0.crt",
        "ssl.key.location": "kafka-0-creds/kafka-0.key",

        "ssl.endpoint.identification.algorithm": "none",
        "sasl.mechanism": "PLAIN",
        "sasl.username": os.getenv("SASL_USERNAME"),
        "sasl.password": os.getenv("SASL_PASSWORD"),
    }

    try:
        producer = Producer(producer_conf)

        while True:
            key = f"key-{uuid.uuid4()}"
            value = "SASL/PLAIN"
            producer.produce(
                "topic-1",
                key=key,
                value=value,
            )
            producer.flush()
            logger.info(f"Отправлено сообщение: {key=}, {value=}")
            time.sleep(1)
    except Exception as e:
        logger.error(e)