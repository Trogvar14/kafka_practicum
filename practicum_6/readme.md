## Описание приложения

### Парметры
MacOs 15.3.2 \
Docker Desktop 4.22.0

### Алгоритм запуска
1. Необходимо запустить docker контейнеры - ``docker compose up``
2. Входим в docker контейнер - ``docker exec -it kafka1 bash``
3. Создаем topic-1 и topic-2
    - ``kafka-topics --create --topic topic-1 --bootstrap-server kafka1:9092 --partitions 3 --replication-factor 2``
    - ``kafka-topics --create --topic topic-2 --bootstrap-server kafka1:9092 --partitions 3 --replication-factor 2``
4. Внутри контейнера нужно выполнить команду - ``kafka-acls --bootstrap-server kafka1:9092 --add --allow-principal User:* --operation Read --topic topic-1`` 
    Команда дает разрешение на чтение topic-1
5. Далее внутри контейнера нужно выполнить команду - ``kafka-acls --bootstrap-server kafka1:9092 --add --allow-principal User:* --operation Write --topic topic-1``
    Команда дает разрешение на запись в topic-1
6. Далее выполняем команду - ``kafka-acls --bootstrap-server kafka1:9092 --add --deny-principal User:user_consumer_user --operation Read --topic topic-2``
7. И также команду - ``kafka-acls --bootstrap-server kafka1:9092 --add --allow-principal User:user_producer_user --operation Write --topic topic-2``
