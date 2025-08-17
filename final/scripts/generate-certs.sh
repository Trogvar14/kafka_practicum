#!/usr/bin/env bash
set -euo pipefail

# Генерим CA, подписываем брокерские ключи, формируем keystore/truststore.
# Требуются: openssl, keytool.

PASS=changeit
mkdir -p certs/a certs/b tmp

cat > tmp/openssl.cnf <<'EOF'
[ req ]
default_bits       = 2048
distinguished_name = req_distinguished_name
x509_extensions    = v3_ca
string_mask        = utf8only
prompt             = no

[ req_distinguished_name ]
C  = RU
ST = Demo
L  = Demo
O  = Demo
OU = Dev
CN = Demo-CA

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer
basicConstraints = critical, CA:true
keyUsage = critical, digitalSignature, cRLSign, keyCertSign

[ v3_server ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
basicConstraints = CA:false
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = localhost
DNS.2 = kafka-a-1
DNS.3 = kafka-a-2
DNS.4 = kafka-b-1
DNS.5 = kafka-b-2
EOF

echo "==> CA"
openssl req -x509 -nodes -new -newkey rsa:2048 -days 3650 \
  -keyout certs/ca.key -out certs/ca.crt -config tmp/openssl.cnf

sign_server () {
  local keystore=$1
  local alias=$2
  local outdir=$3

  # 1) приватный ключ и CSR (через keytool)
  keytool -genkeypair -alias $alias -keyalg RSA -keysize 2048 -validity 3650 \
    -keystore $outdir/$keystore -storepass $PASS -keypass $PASS \
    -dname "CN=$alias, OU=Dev, O=Demo, L=Demo, S=Demo, C=RU"

  keytool -certreq -alias $alias -keystore $outdir/$keystore -storepass $PASS \
    -file tmp/$alias.csr -dname "CN=$alias, OU=Dev, O=Demo, L=Demo, S=Demo, C=RU"

  # 2) выпускаем серверный сертификат от нашего CA c SAN
  openssl x509 -req -in tmp/$alias.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial \
    -out tmp/$alias.crt -days 3650 -extensions v3_server -extfile tmp/openssl.cnf

  # 3) импортируем CA и серверный сертификат в keystore
  keytool -import -noprompt -alias CARoot -file certs/ca.crt \
    -keystore $outdir/$keystore -storepass $PASS

  keytool -import -noprompt -alias $alias -file tmp/$alias.crt \
    -keystore $outdir/$keystore -storepass $PASS
}

echo "==> Серверные keystore для кластера A"
sign_server kafka-a-1.keystore.jks kafka-a-1 certs/a
sign_server kafka-a-2.keystore.jks kafka-a-2 certs/a

echo "==> Серверные keystore для кластера B"
sign_server kafka-b-1.keystore.jks kafka-b-1 certs/b
sign_server kafka-b-2.keystore.jks kafka-b-2 certs/b

echo "==> Truststore (CA)"
keytool -import -noprompt -alias CARoot -file certs/ca.crt \
  -keystore certs/a/kafka.truststore.jks -storepass $PASS
keytool -import -noprompt -alias CARoot -file certs/ca.crt \
  -keystore certs/b/kafka.truststore.jks -storepass $PASS

echo $PASS > certs/a/keystore_creds
echo $PASS > certs/a/key_creds
echo $PASS > certs/a/truststore_creds
echo $PASS > certs/b/keystore_creds
echo $PASS > certs/b/key_creds
echo $PASS > certs/b/truststore_creds

echo "Done"
