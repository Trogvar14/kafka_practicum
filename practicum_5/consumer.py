import faust
import os
import json

rocksdb_path = os.path.abspath('./rocksdb-data')

app = faust.App(
    "user-app",
    broker="kafka://localhost:9094",
    web_port=7070,
    store=f"rocksdb://{rocksdb_path}", ### Данные храним в диске
)

users_topic = app.topic(
    "customers.public.users",
    key_type=str,
    value_type=bytes,  # Принимаем сырые данные
    value_serializer="json",
)

orders_topic = app.topic(
    "customers.public.orders",
    key_type=str,
    value_type=bytes,  # Принимаем сырые данные
    value_serializer="json",
)

@app.agent(users_topic)
async def user_process_message(events):
    async for event in events:
        try:
            print(f"Получены данные из Users: {event}")
        except UnicodeDecodeError:
            print(f"Бинарные данные (не UTF-8): {event.value}")

@app.agent(orders_topic)
async def order_process_message(events):
    async for event in events:
        try:
            print(f"Получены данные из Orders: {event}")
        except UnicodeDecodeError:
            print(f"Бинарные данные (не UTF-8): {event.value}")




if __name__ == '__main__':
    app.main()
