#!/bin/bash
sleep 30  # дать Kafka запуститься

kafka-topics --bootstrap-server kafka1:9092 --create --topic topic-1 --partitions 3 --replication-factor 2
kafka-topics --bootstrap-server kafka1:9092 --create --topic topic-2 --partitions 3 --replication-factor 2

kafka-acls --bootstrap-server kafka1:9092 \
  --add --allow-principal User:CN=kafka-client \
  --operation Read,Write,Describe --topic topic-1

kafka-acls --bootstrap-server kafka1:9092 \
  --add --allow-principal User:CN=kafka-client \
  --operation Write,Describe --topic topic-2