1. Сгенерим сертификаты
``` bash
chmod +x scripts/generate-certs.sh
scripts/generate-certs.sh
```
2. Запустим docker compose
```bash
docker compose -f docker-compose.yml up -d
```
3. Создадим топики на кластере A (будут зеркалиться в B через MM2):
```bash
kafka-topics --bootstrap-server localhost:19092 --command-config client-a.properties \
  --create --topic shop.products.raw --partitions 3 --replication-factor 2

kafka-topics --bootstrap-server localhost:19092 --command-config client-a.properties \
  --create --topic shop.products.filtered --partitions 3 --replication-factor 2

kafka-topics --bootstrap-server localhost:19092 --command-config client-a.properties \
  --create --topic shop.banned --partitions 1 --replication-factor 2

kafka-topics --bootstrap-server localhost:19092 --command-config client-a.properties \
  --create --topic client.queries --partitions 3 --replication-factor 2

kafka-topics --bootstrap-server localhost:19092 --command-config client-a.properties \
  --create --topic client.recommendations --partitions 3 --replication-factor 2
```
4. Запускаем продюсер
```bash
python3.11 shop_api/publish_shop.py data/products.jsonl
```
5. Зальём товары в Postgres
```bash
python3.11 tools/load_products_to_pg.py data/products.jsonl
```
6. Проверяем API (имитация)
```bash
python3.11 shop_api/cli.py search "умные часы"
python3.11 shop_api/cli.py recs --user <user_id из поиска>
```
7. Products -> Postgres
```bash
curl -s -X POST http://localhost:8084/connectors -H 'Content-Type: application/json' -d '{
  "name": "sink-products-pg",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "topics": "shop.products.filtered",
    "connection.url": "jdbc:postgresql://pg:5432/marketplace",
    "connection.user": "pguser",
    "connection.password": "pgpass",
    "auto.create": "true",
    "auto.evolve": "true",
    "insert.mode": "upsert",
    "pk.mode": "record_value",
    "pk.fields": "product_id",
    "tasks.max": "1",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}'
```
Recommendations -> Postgres
```bash
curl -s -X POST http://localhost:8084/connectors -H 'Content-Type: application/json' -d '{
  "name": "sink-recos-pg",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "topics": "recommendations",
    "connection.url": "jdbc:postgresql://pg:5432/marketplace",
    "connection.user": "pguser",
    "connection.password": "pgpass",
    "auto.create": "true",
    "table.name.format": "recommendations",
    "insert.mode": "insert",
    "pk.mode": "record_key",
    "tasks.max": "1",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}'
```