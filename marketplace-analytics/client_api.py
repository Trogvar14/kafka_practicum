import json, os, psycopg2
from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:19092")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
)

def save_to_db(query_type, query_value):
    conn = psycopg2.connect(dbname="marketplace", user="postgres", password="postgres", host="localhost", port=5432)
    cur = conn.cursor()
    cur.execute("INSERT INTO client_requests (type, value) VALUES (%s, %s)", (query_type, query_value))
    conn.commit()
    cur.close()
    conn.close()

def main():
    while True:
        cmd = input("Введите команду (search/recommend/exit): ").strip()
        if cmd == "exit":
            break
        elif cmd == "search":
            name = input("Введите название товара: ").strip()
            producer.send("client_requests", {"type": "search", "value": name})
            save_to_db("search", name)
            print(f"[CLIENT API] Поиск отправлен: {name}")
        elif cmd == "recommend":
            user = input("Введите ID пользователя: ").strip()
            producer.send("client_requests", {"type": "recommend", "value": user})
            save_to_db("recommend", user)
            print(f"[CLIENT API] Запрос рекомендаций отправлен: {user}")
        else:
            print("Неизвестная команда. Используйте: search / recommend / exit")

if __name__ == "__main__":
    main()
