import faust
import os

rocksdb_path = os.path.abspath('./rocksdb-data')

#===Модель заблокированных пользователей===
class BockedUsers(faust.Record, serializer='json'):
    sender_user_id: int
    recipient_user_id: int

app = faust.App(
    "blocked-user-app",
    broker="localhost:9094",
    store=f"rocksdb://{rocksdb_path}", ### Данные храним в диске
)

#===Топик с заблокированными пользователями===
blocked_user_add_topic = app.topic(
    "blocked_users_topic",
    key_type=str,
    value_type=BockedUsers
)

#===Таблица с заблокированными пользователями===
blocked_table = app.Table(
    "blocked_user_table",
    partitions=1,
    default=int,
)

#===Агент который слушает и принимает блокировку пользователей===
@app.agent(blocked_user_add_topic)
async def add_process(block_events):
    async for event in block_events:
        key = (event.sender_user_id, event.recipient_user_id)
        blocked_table[key] = True
        print(f'Пользователь c user_id = {event.sender_user_id} заблокировал пользователя с user_id = {event.recipient_user_id}')

#===Периодик, ктороый каждые 30 сек. отображает список===
@app.timer(interval=30.0)
async def print_blocked():
    print('\nТекущий список заблокированных пользователей:')
    for (sender_user_id, recipient_user_id) in blocked_table.items():
        print(f'User list: {sender_user_id} → blocked = {recipient_user_id}')

if __name__ == '__main__':
    app.main()
