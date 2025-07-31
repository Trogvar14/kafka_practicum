## Описание приложения

### Парметры
MacOs 15.3.2 \
Docker Desktop 4.22.0

### Алгоритм запуска

1. Создаем сертификат для брокеров
 - (Root CA) `ca.cnf`:
    ```
   [ policy_match ]
   countryName = match
   stateOrProvinceName = match
   organizationName = match
   organizationalUnitName = optional
   commonName = supplied
   emailAddress = optional
   
   [ req ]
   prompt = no
   distinguished_name = dn
   default_md = sha256
   default_bits = 4096
   x509_extensions = v3_ca
   
   [ dn ]
   countryName = RU
   organizationName = Yandex
   organizationalUnitName = Practice
   localityName = Moscow
   commonName = yandex-practice-kafka-ca
   
   [ v3_ca ]
   subjectKeyIdentifier = hash
   basicConstraints = critical,CA:true
   authorityKeyIdentifier = keyid:always,issuer:always
   keyUsage = critical,keyCertSign,cRLSign
   ```
   
   ```bash
   openssl req -new -nodes \
      -x509 \
      -days 365 \
      -newkey rsa:2048 \
      -keyout ca.key \
      -out ca.crt \
      -config ca.cnf
   ```
   
   - Файл для хранения сертификата безопасности `ca.pem`:
   
   ```bash
   cat ca.crt ca.key > ca.pem
   ```
   
   - Файлы конфигурации для каждого брокера:
   
         *  `kafka-0-creds/kafka-0.cnf`:
      
         ```bash
         [req]
         prompt = no
         distinguished_name = dn
         default_md = sha256
         default_bits = 4096
         req_extensions = v3_req
      
         [ dn ]
         countryName = RU
         organizationName = Yandex
         organizationalUnitName = Practice
         localityName = Moscow
         commonName = kafka-0
      
         [ v3_ca ]
         subjectKeyIdentifier = hash
         basicConstraints = critical,CA:true
         authorityKeyIdentifier = keyid:always,issuer:always
         keyUsage = critical,keyCertSign,cRLSign
      
         [ v3_req ]
         subjectKeyIdentifier = hash
         basicConstraints = CA:FALSE
         nsComment = "OpenSSL Generated Certificate"
         keyUsage = critical, digitalSignature, keyEncipherment
         extendedKeyUsage = serverAuth, clientAuth
         subjectAltName = @alt_names
      
         [ alt_names ]
         DNS.1 = kafka-0
         DNS.2 = kafka-0-external
         DNS.3 = localhost
         ```
      
         * `kafka-1-creds/kafka-1.cnf`:
      
         ```bash
         [req]
         prompt = no
         distinguished_name = dn
         default_md = sha256
         default_bits = 4096
         req_extensions = v3_req
      
         [ dn ]
         countryName = RU
         organizationName = Yandex
         organizationalUnitName = Practice
         localityName = Moscow
         commonName = kafka-1
      
         [ v3_ca ]
         subjectKeyIdentifier = hash
         basicConstraints = critical,CA:true
         authorityKeyIdentifier = keyid:always,issuer:always
         keyUsage = critical,keyCertSign,cRLSign
      
         [ v3_req ]
         subjectKeyIdentifier = hash
         basicConstraints = CA:FALSE
         nsComment = "OpenSSL Generated Certificate"
         keyUsage = critical, digitalSignature, keyEncipherment
         extendedKeyUsage = serverAuth, clientAuth
         subjectAltName = @alt_names
      
         [ alt_names ]
         DNS.1 = kafka-1
         DNS.2 = kafka-1-external
         DNS.3 = localhost
         ```
      
         * `kafka-2-creds/kafka-2.cnf`:
      
         ```bash
         [req]
         prompt = no
         distinguished_name = dn
         default_md = sha256
         default_bits = 4096
         req_extensions = v3_req
      
         [ dn ]
         countryName = RU
         organizationName = Yandex
         organizationalUnitName = Practice
         localityName = Moscow
         commonName = kafka-2
      
         [ v3_ca ]
         subjectKeyIdentifier = hash
         basicConstraints = critical,CA:true
         authorityKeyIdentifier = keyid:always,issuer:always
         keyUsage = critical,keyCertSign,cRLSign
      
         [ v3_req ]
         subjectKeyIdentifier = hash
         basicConstraints = CA:FALSE
         nsComment = "OpenSSL Generated Certificate"
         keyUsage = critical, digitalSignature, keyEncipherment
         extendedKeyUsage = serverAuth, clientAuth
         subjectAltName = @alt_names
      
         [ alt_names ]
         DNS.1 = kafka-2
         DNS.2 = kafka-2-external
         DNS.3 = localhost
         ```
   
     - приватные ключи и сертификат - CSR : 
   
        ```bash
        openssl req -new \
            -newkey rsa:2048 \
            -keyout kafka-0-creds/kafka-0.key \
            -out kafka-0-creds/kafka-0.csr \
            -config kafka-0-creds/kafka-0.cnf \
            -nodes
   
        openssl req -new \
            -newkey rsa:2048 \
            -keyout kafka-1-creds/kafka-1.key \
            -out kafka-1-creds/kafka-1.csr \
            -config kafka-1-creds/kafka-1.cnf \
            -nodes
   
        openssl req -new \
            -newkey rsa:2048 \
            -keyout kafka-2-creds/kafka-2.key \
            -out kafka-2-creds/kafka-2.csr \
            -config kafka-2-creds/kafka-2.cnf \
            -nodes
        ```
   
     - Сертификаты брокеров, подписанный CA:
   
        ```bash
        openssl x509 -req \
            -days 3650 \
            -in kafka-0-creds/kafka-0.csr \
            -CA ca.crt \
            -CAkey ca.key \
            -CAcreateserial \
            -out kafka-0-creds/kafka-0.crt \
            -extfile kafka-0-creds/kafka-0.cnf \
            -extensions v3_req
   
        openssl x509 -req \
            -days 3650 \
            -in kafka-1-creds/kafka-1.csr \
            -CA ca.crt \
            -CAkey ca.key \
            -CAcreateserial \
            -out kafka-1-creds/kafka-1.crt \
            -extfile kafka-1-creds/kafka-1.cnf \
            -extensions v3_req
   
        openssl x509 -req \
            -days 3650 \
            -in kafka-2-creds/kafka-2.csr \
            -CA ca.crt \
            -CAkey ca.key \
            -CAcreateserial \
            -out kafka-2-creds/kafka-2.crt \
            -extfile kafka-2-creds/kafka-2.cnf \
            -extensions v3_req
        ```
   
     - Создаем PKCS12-хранилища:
   
        ```bash
        openssl pkcs12 -export \
            -in kafka-0-creds/kafka-0.crt \
            -inkey kafka-0-creds/kafka-0.key \
            -chain \
            -CAfile ca.pem \
            -name kafka-0 \
            -out kafka-0-creds/kafka-0.p12 \
            -password pass:your-password
   
        openssl pkcs12 -export \
            -in kafka-1-creds/kafka-1.crt \
            -inkey kafka-1-creds/kafka-1.key \
            -chain \
            -CAfile ca.pem \
            -name kafka-1 \
            -out kafka-1-creds/kafka-1.p12 \
            -password pass:your-password
   
        openssl pkcs12 -export \
            -in kafka-2-creds/kafka-2.crt \
            -inkey kafka-2-creds/kafka-2.key \
            -chain \
            -CAfile ca.pem \
            -name kafka-2 \
            -out kafka-2-creds/kafka-2.p12 \
            -password pass:your-password
        ```


2. **Truststore и Keystore для каждого брокера.**

   - Keystore:
   
   ```bash
   keytool -importkeystore \
       -deststorepass your-password \
       -destkeystore kafka-0-creds/kafka.kafka-0.keystore.pkcs12 \
       -srckeystore kafka-0-creds/kafka-0.p12 \
       -deststoretype PKCS12  \
       -srcstoretype PKCS12 \
       -noprompt \
       -srcstorepass your-password
   
   keytool -importkeystore \
       -deststorepass your-password \
       -destkeystore kafka-1-creds/kafka.kafka-1.keystore.pkcs12 \
       -srckeystore kafka-1-creds/kafka-1.p12 \
       -deststoretype PKCS12  \
       -srcstoretype PKCS12 \
       -noprompt \
       -srcstorepass your-password
   
   keytool -importkeystore \
       -deststorepass your-password \
       -destkeystore kafka-2-creds/kafka.kafka-2.keystore.pkcs12 \
       -srckeystore kafka-2-creds/kafka-2.p12 \
       -deststoretype PKCS12  \
       -srcstoretype PKCS12 \
       -noprompt \
       -srcstorepass your-password
   ```
   
   - Truststore:
   
   ```bash
   keytool -import \
       -file ca.crt \
       -alias ca \
       -keystore kafka-0-creds/kafka.kafka-0.truststore.jks \
       -storepass your-password \
       -noprompt
   
   keytool -import \
       -file ca.crt \
       -alias ca \
       -keystore kafka-1-creds/kafka.kafka-1.truststore.jks \
       -storepass your-password \
       -noprompt
   
   keytool -import \
       -file ca.crt \
       -alias ca \
       -keystore kafka-2-creds/kafka.kafka-2.truststore.jks \
       -storepass your-password \
       -noprompt
   ```
   
   - Файлы с паролями:
   
   ```bash
   echo "your-password" > kafka-0-creds/kafka-0_sslkey_creds
   echo "your-password" > kafka-0-creds/kafka-0_keystore_creds
   echo "your-password" > kafka-0-creds/kafka-0_truststore_creds
   
   echo "your-password" > kafka-1-creds/kafka-1_sslkey_creds
   echo "your-password" > kafka-1-creds/kafka-1_keystore_creds
   echo "your-password" > kafka-1-creds/kafka-1_truststore_creds
   
   echo "your-password" > kafka-2-creds/kafka-2_sslkey_creds
   echo "your-password" > kafka-2-creds/kafka-2_keystore_creds
   echo "your-password" > kafka-2-creds/kafka-2_truststore_creds
   ```
   
   - PKCS12 в JKS:
   
   ```bash
   keytool -importkeystore \
       -srckeystore kafka-0-creds/kafka-0.p12 \
       -srcstoretype PKCS12 \
       -destkeystore kafka-0-creds/kafka-0.keystore.jks \
       -deststoretype JKS \
       -deststorepass your-password
   
   keytool -importkeystore \
       -srckeystore kafka-1-creds/kafka-1.p12 \
       -srcstoretype PKCS12 \
       -destkeystore kafka-1-creds/kafka-1.keystore.jks \
       -deststoretype JKS \
       -deststorepass your-password
   
   keytool -importkeystore \
       -srckeystore kafka-2-creds/kafka-2.p12 \
       -srcstoretype PKCS12 \
       -destkeystore kafka-2-creds/kafka-2.keystore.jks \
       -deststoretype JKS \
       -deststorepass your-password
   ```
   
   - Импортируем CA в Truststore:
   
   ```bash
   keytool -import -trustcacerts -file ca.crt \
       -keystore kafka-0-creds/kafka-0.truststore.jks \
       -storepass your-password -noprompt -alias ca
   
   keytool -import -trustcacerts -file ca.crt \
       -keystore kafka-1-creds/kafka-1.truststore.jks \
       -storepass your-password -noprompt -alias ca
   
   keytool -import -trustcacerts -file ca.crt \
       -keystore kafka-2-creds/kafka-2.truststore.jks \
       -storepass your-password -noprompt -alias ca
   ```
   
   - Конфигурация для ZooKeeper (для аутентификации через SASL/PLAIN) в 
   файле `zookeeper.sasl.jaas.conf`:
   
   ```
   Server {
     org.apache.zookeeper.server.auth.DigestLoginModule required
     user_admin="your-password";
   };
   ```
   
   - Конфигурация Kafka для авторизации в ZooKeeper в файле 
   `kafka_server_jaas.conf`:
   
   ```
   KafkaServer {
      org.apache.kafka.common.security.plain.PlainLoginModule required
      username="admin"
      password="your-password"
      user_admin="your-password"
      user_kafka="your-password"
      user_producer="your-password"
      user_consumer="your-password";
   };
   
   Client {
      org.apache.kafka.common.security.plain.PlainLoginModule required
      username="admin"
      password="your-password";
   };
   ```
   
   - Учетные записи клиента `admin.properties`:
   
   ```
   security.protocol=SASL_SSL
   ssl.truststore.location=/etc/kafka/secrets/kafka.kafka-0.truststore.jks
   ssl.truststore.password=your-password
   sasl.mechanism=PLAIN
   sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="admin" password="your-password";
   ```
3. Запускаем docker контейнеры - ``docker compose up -d``
4. Создаем 2 топика:
     ```bash
   docker exec -it kafka-0 kafka-topics \
     --bootstrap-server kafka-0:9092 \
     --command-config /etc/kafka/secrets/admin.properties \
     --create --topic topic-1 \
     --partitions 3 \
     --replication-factor 3
   
   docker exec -it kafka-0 kafka-topics \
     --bootstrap-server kafka-0:9092 \
     --command-config /etc/kafka/secrets/admin.properties \
     --create --topic topic-2 \
     --partitions 3 \
     --replication-factor 3
   ```
5. Настраиваем права доступа
  
 ```bash
   docker exec -it kafka-0 kafka-acls \
     --bootstrap-server kafka-0:9092 \
     --command-config /etc/kafka/secrets/admin.properties \
     --add \
     --allow-principal User:producer \
     --operation Write \
     --topic topic-1
   ```

```bash
   docker exec -it kafka-0 kafka-acls \
     --bootstrap-server kafka-0:9092 \
     --command-config /etc/kafka/secrets/admin.properties \
     --add \
     --allow-principal User:consumer \
     --operation Read \
     --topic topic-1 \
     --group consumer-ssl-group
   ```

```bash
   docker exec -it kafka-0 kafka-acls \
     --bootstrap-server kafka-0:9092 \
     --command-config /etc/kafka/secrets/admin.properties \
     --add \
     --allow-principal User:producer \
     --operation Write \
     --topic topic-2
   ```
6. Генерируем клиентский сертификат
```bash
  mkdir client-creds
  
  openssl genrsa -out client.key 2048
  
  openssl req -new -key client.key -out client.csr -subj "/CN=client"
  
  openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365
  
  ls -l client.key client.crt
```

```bash
  cp ca.crt client-creds/
  cp client.crt client-creds/
  cp client.key client-creds/
```

7. Запускаем Docker.client
```docker build -f Dockerfile.client -t kafka-client .```
8. Запускаем продюссера
```docker run --rm --network kafka-connect-network kafka-client python producer.py```
9. Запускаем консюмеров
```docker run --rm --network kafka-connect-network kafka-client python consumer.py```
10. В консоли должны увидеть:
- ✅ Чтение из topic-1 прошло успешно
- ✅ Успешно: не удалось читать из topic-2 
