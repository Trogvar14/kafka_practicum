## Описание приложения

### Парметры
MacOs 15.3.2 \
Docker Desktop 4.22.0
venv python3.9

### Алгоритм запуска
1. Нужно инициализировать вирутальное окружение - ```python3.9 -m venv venv_faust```
2. Активируем виртуальное окружение - ```source venv_faust/bin/activate```
3. Обновляем pip -```pip install --upgrade pip```
4. Устанавливаем нужные библиотеки - ```pip install -r requirements.txt```
5. Запускаем docker контейнер с приложением.\
Для этого нужно в консоли выполнить команду ```docker-compose up --build```
6. Проверяем с помощью команды ```docker ps``` контейнеры.
Должно запуститься 5 контейнеров:
- kafka-ui
- ksqldb-cli 
- ksqldb-server
- schema-registry
- kafka1
- kafka2
- zookeeper
7. Создаем топик c тремя партициями и с двумя репликациями
```docker exec -it kafka1 kafka-topics --create --topic blocked_users_topic --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1```\
```docker exec -it kafka1 kafka-topics --create --topic message_input_topic --bootstrap-server kafka1:9092 --partitions 1 --replication-factor 1```\
Обязательно убедитесь что вы активировали виртуальное окружение (пункт 2)
8. Проверяем топики с помощью команды ```docker exec -it kafka1 kafka-topics --describe --topic blocked_users_topic --bootstrap-server kafka1:9092```
9. Запускаем Faust приложение - ```python faust_user.py worker -l info```\
Обязательно убедитесь что вы активировали виртуальное окружение (пункт 2)
10. Запускаем ```python3 add_blockuser_produccer.py```\
Далее нужно:
- Указать ваш id = 1
- Указать id пользователя которого нужно заблокировать id = 2
Обязательно убедитесь что вы активировали виртуальное окружение (пункт 2)
11. В отдельной консоли запускаем - ```python faust_message.py worker -l info```\
Обязательно убедитесь что вы активировали виртуальное окружение (пункт 2)
12. В отдельной консоли запускаем - ```python3 input_message_produccer.py```\
Далее нужно воспроизвести два сценария:
- Сценарий 1:
  - Указываем ваш id = 1
  - Указываем id получателя = 2
  - Отправляем любое сообщение. К примеру - тест
  - Консоль с faust_message.py должен вывести ```Пользователь заблокирован! Невозможно отправить сообщение```

- Сценарий 2:
  - Указываем ваш id = 1
  - Указываем id получателя = 2
  - Отправляем сообщение с указанием запрещенных слов. К примеру, ```Альтушка сказала бы что это сообщение полнейший кринж```
  - Консоль с faust_message.py должен вывести отфильтрованное сообщение ```{blocked} сказала бы что это сообщение полнейший {blocked}```
  - Список с запрещенными словами можно дополнить в ```blocked_words.json```

