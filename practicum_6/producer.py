from confluent_kafka import Producer
import socket
import time
import sys

def create_producer():
    conf = {
        'bootstrap.servers': 'localhost:9093,localhost:9095',  # SSL порты Kafka1 и Kafka2
        'security.protocol': 'ssl',
        'ssl.key.location': './ssl-client/client.key',
        'ssl.certificate.location': './ssl-client/client.crt',
        'ssl.ca.location': './ssl-client/ca.crt',
        'ssl.key.password': 'changeit',  # пароль от ключа (если был)
        'client.id': socket.gethostname(),
        'enable.idempotence': True,
        'acks': 'all',
    }
    return Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Ошибка доставки: {err} в топик {msg.topic()}")
    else:
        print(f"✅ Сообщение доставлено: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

def main():
    try:
        p = create_producer()
    except Exception as e:
        print(f"❌ Ошибка создания продюсера: {e}")
        sys.exit(1)

    topics = ['topic-1', 'topic-2']
    print("Запуск продюсера. Отправка 5 сообщений в каждый топик...")

    for i in range(5):
        for topic in topics:
            message = f"Hello from Python producer! Topic: {topic}, message #{i}"
            try:
                p.produce(
                    topic,
                    message.encode('utf-8'),
                    callback=delivery_report
                )
            except BufferError:
                print("❗ Очередь заполнена, ждём...")
                p.poll(1.0)
                p.produce(topic, message.encode('utf-8'), callback=delivery_report)
            p.poll(0)  # Обработка колбэков

        time.sleep(1)

    print("Ожидание доставки всех сообщений...")
    p.flush(timeout=10)
    print("✅ Все сообщения отправлены.")

if __name__ == "__main__":
    main()