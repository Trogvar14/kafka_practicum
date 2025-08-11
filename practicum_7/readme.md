Задание 1
2. Зашел в yandex cloud
2. Создал кластер с kafka c 3 брокерами
3. Я прошел аутентефикацию в в Yandex Cloud CLI
3. Создаем топик
```bash
   yc managed-kafka topic create topic-1 \
  --cluster-name kafka_practicum \
  --partitions 3 \
  --replication-factor 3 \
  --cleanup-policy UNSPECIFIED \
  --retention-ms 604800000 \
  --segment-bytes 1073741824
```
- cleanup-policy - compact_and_delete (будем использовать и сжатие и удаление)
- retention-ms - 604800000 (установил как 7 дней)
- segment-bytes - 1073741824 (установил как 1 Гб)
4. Создаем схему в формате .json и регистрируем
Запуск rjyntqythf: 
```bash
docker compose -f docker-compose.schema-registry.yml up -d
docker logs -f schema-registry
```
```bash
jq -Rs '{schema: .}' schema.json | \
curl -X POST \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data @- \
  http://localhost:8081/subjects/topic-1-value/versions

```
5. Запускаем produccer.py
    Если нет ошибки видим - DELIVERY: OK
6. Запускаем consumer.py
    Если нет ошибки видим - Получено: {'id': '1', 'name': 'Alice', 'email': None, 'age': 30}
Скрины в /screen/1.png

Задание 2
1. Запускаем контейнер с Nifi
2. Преобразуем CA.pem в truststore JKS 
```bash
mkdir -p security
keytool -importcert -alias yandex-ca \
  -file /Users/macbook/Desktop/kafka_lessons/kafka_practicum/practicum_7/secrets/CA.pem \
  -keystore ./security/truststore.jks \
  -storepass changeit -noprompt
```
Логи в /screen/2.png
3. Настроил NiFi (смотри скрины) /screen/nifi-1.png ... nifi-6.png
4. Проверить логи можно командой:
```bash
kcat -b rc1a-d0bkq4hc1n66j6ib.mdb.yandexcloud.net:9091,rc1b-9qjr2o7ijg4vfb7r.mdb.yandexcloud.net:9091,rc1d-ebsqkrdpmlvp14i7.mdb.yandexcloud.net:9091 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-512 \
  -X sasl.username=user_1 \
  -X sasl.password='Kasper12' \
  -X ssl.ca.location="/Users/macbook/Desktop/kafka_lessons/kafka_practicum/practicum_7/secrets/CA.pem" \
  -t nifi-test -C -o beginning -c 5
```
Вывод: {"source":"nifi","ts":"1754948527258","msg":"hello from nifi"}

logs.png