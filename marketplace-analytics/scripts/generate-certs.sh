#!/usr/bin/env bash
set -euo pipefail
# Самоподписанные сертификаты для демонстрации TLS (не для продакшена).
# Требует keytool и openssl.

mkdir -p certs/a certs/b certs/clients
PASS=changeit

create_keystore() {
  local keystore=$1
  local cn=$2
  keytool -genkey -noprompt \
    -alias $cn \
    -dname "CN=$cn, OU=Dev, O=Demo, L=City, S=State, C=RU" \
    -keystore $keystore \
    -storepass $PASS -keypass $PASS -keyalg RSA -keysize 2048 -validity 3650
}

create_truststore() {
  local truststore=$1
  local cert=$2
  keytool -import -noprompt -alias CARoot -file $cert -keystore $truststore -storepass $PASS
}

# CA
openssl req -new -x509 -keyout certs/ca.key -out certs/ca.crt -days 3650 -nodes -subj "/CN=Demo-CA"

# Cluster A
create_keystore certs/a/kafka-a-1.keystore.jks kafka-a-1
create_keystore certs/a/kafka-a-2.keystore.jks kafka-a-2

# Cluster B
create_keystore certs/b/kafka-b-1.keystore.jks kafka-b-1
create_keystore certs/b/kafka-b-2.keystore.jks kafka-b-2

# Truststores
create_truststore certs/a/kafka.truststore.jks certs/ca.crt
create_truststore certs/b/kafka.truststore.jks certs/ca.crt

# Credential files for Confluent images
echo $PASS > certs/a/keystore_creds
echo $PASS > certs/a/key_creds
echo $PASS > certs/a/truststore_creds

echo $PASS > certs/b/keystore_creds
echo $PASS > certs/b/key_creds
echo $PASS > certs/b/truststore_creds

echo "Certs generated."
