## Описание приложения

### Парметры
MacOs 15.3.2 \
Docker Desktop 4.22.0

### Алгоритм запуска
python3.9 -m venv venv_faust
source venv_faust/bin/activate
1. pip install -r requirements.txt
2. pip install --upgrade pip
1. Запускаем docker контейнер с приложением.\
Для этого нужно в консоли выполнить команду ```docker-compose up -- build```
2. Проверяем с помощью команды ```docker ps``` контейнеры.
Должно запуститься 5 контейнеров:
- kafka-ui
- schema-registry
- kafka1
- kafka2
- zookeeper

3. Создаем топик c тремя партициями и с двумя репликациями
```docker exec -it kafka1 kafka-topics --create --topic blocked_users_topic --bootstrap-server kafka1:9092 --partitions 3 --replication-factor 2```
4. Проверяем топики с пмощью команды ```docker exec -it kafka1 kafka-topics --describe --topic blocked_users_topic --bootstrap-server kafka1:9092```
5. faust -A faust_user worker -l info    
6. ```
    CREATE STREAM blocked_users_stream (
        user_id STRING,
        blocked_user_id STRING
    ) WITH (
        KAFKA_TOPIC='blocked_users_topic',  -- Имя топика Kafka
        VALUE_FORMAT='JSON',      -- Формат данных (JSON, AVRO, DELIMITED, и т.д.)
        PARTITIONS=3              -- Число партиций потока (по умолчанию 1)
    );
```
6. 
7. Запускаем косюмер с автокоммитом и ручным коммитом
- consumer-single.py - консюмер должен считывать по одному сообщению, обрабатывать его и коммитить оффсет автоматически.
Запускается с помощью команды ```python3 consumer-single.py```
- consumer-batch.py - консюмер должен считывать минимум по 10 сообщений за один poll, обрабатывать сообщения в цикле и один раз коммитить оффсет после обработки пачки.
Запускается с помощью команды ```python3 consumer-batch.py```
6. Запускаем продюссер с помощью команды ```python3 produccer.py```
7. Можем проверить consumer-single.py и consumer-batch.py сообщения который высылает продюссер produccer.py

### Краткое описание основных файлов
***serializer.py***\
В py файле содержится класс ```SerializerClass``` позволяющий сериализацировать и десериализировать сообщения.\
При создании класса конфигурация regestry и json схема.\
Функция ```serialize``` на вход принимает message_value (сообщение) и topic (название топика)\
Функция ```deserialize``` на вход принимает msg (сообщение)\
На выходе получаем сериализованный/десериализованный key и value\

***produccer.py***\
py файл помогает создать и отправить сообщение в топик.\
Мы задаем конфигурацию для продюссера в переменной ```conf```.\
Далее генерируем сообщения (message_list).\
```delivery_report``` - Функция обратного вызова для подтверждения доставки\
Далее, предварительно сериализовав функцией ```SerializerClass.serialize```, в цикле мы по одному сообщению отправляем в топик.\

***consumer-single.py*** \
В данном файле реализуем функионал автокоммита.\
Консюмер должен считывать по одному сообщению, обрабатывать его и коммитить оффсет автоматически.\
В переменной ```conf``` передаем конфигурацию для консюмера.\
По условию задания задаем id группы, отличный от других консюмеров ```"group.id": "single-consumer-1"```.\
Также добавляем флажок ```True``` для ```enable.auto.commit``` - ```"enable.auto.commit": True```\
Функция ```SingleMessageConsumer``` запускает цикл, который проверяет сообщения в топике. И если есть новое сообщение десериализует его и выводит на консоль.\
В случае ошибки, мы тоже увидим ошибку в консоли.\
Не забываем закрыть консюмер ```consumer.close()```

***consumer-batch.py*** \
В данном файле реализуем функионал ручного подверждения.\
Также обработка сообщений по батчам\
Консюмер должен считывать минимум по 10 сообщений за один poll, обрабатывать сообщения в цикле и один раз коммитить оффсет после обработки пачки.\
В переменной ```conf``` передаем конфигурацию для консюмера.\
По условию задания задаем id группы, отличный от других консюмеров ```"group.id": "batch-consumer-2"```.\
Также добавляем флажок ```False``` для ```enable.auto.commit``` - ```"enable.auto.commit": True```\
В этом случае нам самим придется коммитить сообщения.\
Функция ```BatchMessageConsumer``` запускает цикл, который проверяет сообщения в топике. \
Вместо ```pool()``` использум ```consumer.consume(num_messages=batch_size, timeout=1.0)```, где num_messages это кол-во сообщений в batch.\
Далее мы:
- Забираем по 10 сообщений. 
- Выводим на консоль через цикл.
- Если сообщения были успешно обработаны, комитим. - ```consumer.commit(asynchronous=False)```

Не забываем закрыть консюмер ```consumer.close()```