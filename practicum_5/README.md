## Описание приложения

### Парметры
MacOs 15.3.2 \
Docker Desktop 4.22.0

### Алгоритм запуска
1. Нужно запустить проект используя команду ``docker up -d``
2. Убедиться что запущены все контейнеры ``docker ps``
3. Запускаем Faust приложение - ``python consumer.py worker -l info``
4. Grafana доступна по ссылке ``http://localhost:3000/`` логин и пароль - admin
5. -- Добавление пользователей
INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');
INSERT INTO users (name, email) VALUES ('Jane Smith', 'jane@example.com');
INSERT INTO users (name, email) VALUES ('Alice Johnson', 'alice@example.com');
INSERT INTO users (name, email) VALUES ('Bob Brown', 'bob@example.com');


6. -- Добавление заказов
INSERT INTO orders (user_id, product_name, quantity) VALUES (1, 'Product A', 2);
INSERT INTO orders (user_id, product_name, quantity) VALUES (1, 'Product B', 1);
INSERT INTO orders (user_id, product_name, quantity) VALUES (2, 'Product C', 5);
INSERT INTO orders (user_id, product_name, quantity) VALUES (3, 'Product D', 3);
INSERT INTO orders (user_id, product_name, quantity) VALUES (4, 'Product E', 4);
7. После выполнения команд ``python consumer.py worker -l info`` должен отобразить данные