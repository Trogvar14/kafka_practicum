#!/usr/bin/env bash
set -euo pipefail

ADMIN_PASS="admin-secret"
APP_PASS="app-secret"

echo "== Cluster A users =="
docker compose exec -T kafka-a-1 kafka-configs --zookeeper zookeeper-a:2181 \
  --alter --add-config "SCRAM-SHA-512=[password=${ADMIN_PASS}]" \
  --entity-type users --entity-name admin

docker compose exec -T kafka-a-1 kafka-configs --zookeeper zookeeper-a:2181 \
  --alter --add-config "SCRAM-SHA-512=[password=${APP_PASS}]" \
  --entity-type users --entity-name app

echo "== Cluster B users =="
docker compose exec -T kafka-b-1 kafka-configs --zookeeper zookeeper-b:2181 \
  --alter --add-config "SCRAM-SHA-512=[password=${ADMIN_PASS}]" \
  --entity-type users --entity-name admin

docker compose exec -T kafka-b-1 kafka-configs --zookeeper zookeeper-b:2181 \
  --alter --add-config "SCRAM-SHA-512=[password=${APP_PASS}]" \
  --entity-type users --entity-name app

echo "Users admin/app created on both clusters."
