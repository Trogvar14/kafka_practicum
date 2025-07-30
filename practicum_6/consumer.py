# consumer.py
from confluent_kafka import Consumer, KafkaException, KafkaError
import signal
import sys

# Для graceful shutdown
def sigterm_handler(signum, frame):
    print("\n🛑 Завершаем работу потребителя...")
    c.close()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
signal.signal(signal.SIGINT, sigterm_handler)

def create_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9093,localhost:9095',
        'security.protocol': 'ssl',
        'ssl.key.location': './ssl-client/client.key',
        'ssl.certificate.location': './ssl-client/client.crt',
        'ssl.ca.location': './ssl-client/ca.crt',
        'ssl.key.password': 'changeit',
        'group.id': 'python-test-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
        'session.timeout.ms': 60000,
    }
    return Consumer(conf)

def main():
    c = create_consumer()
    try:
        c.subscribe(['topic-2'])
        print("✅ Потребитель запущен. Ожидание сообщений из topic-2...")
        print("Нажмите Ctrl+C для остановки.")
    except KafkaException as e:
        print(f"❌ Ошибка подписки: {e}")
        sys.exit(1)

    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                elif msg.error().code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
                    print(f"❌ Нет доступа к топику: {msg.topic()}")
                    continue
                else:
                    print(f"❌ Ошибка Kafka: {msg.error()}")
                    break

            print(f"📨 Получено: {msg.value().decode('utf-8')} "
                  f"из {msg.topic()}[{msg.partition()}] @ {msg.offset()} "
                  f"(timestamp: {msg.timestamp()})")

    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем.")
    finally:
        c.close()
        print("✅ Потребитель остановлен.")

if __name__ == "__main__":
    main()