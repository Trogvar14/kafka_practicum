import faust
import os
import json

#===Модель заблокированных пользователей===
class Message(faust.Record, serializer='json'):
    sender_user_id: int
    recipient_user_id: int
    message: str

app = faust.App(
    "message-app",
    broker="localhost:9094",
    store=f"memory://",
)

#===Топик с сообщениями===
message_input_topic = app.topic(
    "message_input_topic",
    key_type=str,
    value_type=Message
)

#===Таблица с заблокированными пользователями===
blocked_table = app.Table(
    "blocked_user_table",
    partitions=1,
    default=int,
)

#===Агент который слушает и фильтрует сообщения===
@app.agent(message_input_topic)
async def iput_message(message_events):
    with open('./blocked_words.json', 'r') as words:
        blocked_words = json.load(words)
    async for event in message_events:
        for (sender_user_id, recipient_user_id) in blocked_table.items():
            if sender_user_id[0] == event.sender_user_id and sender_user_id[1] == event.recipient_user_id:
                print('Пользователь заблокирован! Невозможно отправить сообщение')
            else:
                for b_words in blocked_words['blocked_words']:
                    filtered_message = event.message.replace(b_words, "{blocked}")

                print(f"""Id отправителя: {event.sender_user_id}""")
                print(f"""Id получателя: {event.recipient_user_id}""")
                print(f"""Сообщение: {filtered_message}""")


if __name__ == '__main__':
    app.main()
