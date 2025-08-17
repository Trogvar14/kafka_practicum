import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, lit

# минимальные схемы
from pyspark.sql.types import (StructType, StructField, StringType, DoubleType,
    IntegerType, ArrayType, MapType)

product_schema = StructType([
    StructField("product_id", StringType()),
    StructField("name", StringType()),
    StructField("description", StringType()),
    StructField("price", StructType([
        StructField("amount", DoubleType()),
        StructField("currency", StringType())
    ])),
    StructField("category", StringType()),
    StructField("brand", StringType()),
    StructField("stock", StructType([
        StructField("available", IntegerType()),
        StructField("reserved", IntegerType())
    ])),
    StructField("sku", StringType()),
    StructField("tags", ArrayType(StringType())),
    StructField("images", ArrayType(StructType([
        StructField("url", StringType()),
        StructField("alt", StringType())
    ]))),
    StructField("specifications", MapType(StringType(), StringType())),
    StructField("created_at", StringType()),
    StructField("updated_at", StringType()),
    StructField("index", StringType()),
    StructField("store_id", StringType())
])

client_schema = StructType([
    StructField("client_id", StringType()),
    StructField("action", StringType()),     # search / recommend_request
    StructField("query", StringType()),
    StructField("ts", StringType())
])

spark = (SparkSession.builder
         .appName("ingest_to_hdfs")
         .config("spark.sql.streaming.checkpointLocation",
                 "hdfs://hdfs-namenode:9000/checkpoints/kafka_raw")
         .getOrCreate())

# читаем оба топика B кластерa
kafka_options = {
    "kafka.bootstrap.servers": "kafka-b-1:9092,kafka-b-2:9092",
    "subscribePattern": "^(products_filtered|client_requests)$",
    "startingOffsets": "latest",
    "kafka.security.protocol": "SSL",
    "kafka.ssl.truststore.location": "/opt/certs/kafka.truststore.jks",
    "kafka.ssl.truststore.password": "changeit",
    "kafka.ssl.truststore.type": "JKS",
    # Если SAN/hostname не совпадает, временно снимите проверку:
    # "kafka.ssl.endpoint.identification.algorithm": ""
}

df = (spark.readStream.format("kafka")
      .options(**kafka_options)
      .load()
      .selectExpr("topic",
                  "CAST(key AS STRING) as key",
                  "CAST(value AS STRING) as value",
                  "timestamp"))

# «мягкий» парс в два набора
products = (df.filter(col("topic") == "products_filtered")
              .withColumn("json", from_json(col("value"), product_schema))
              .select("topic", "key", "timestamp", "json.*")
              .withColumn("ingest_ts", col("timestamp"))
              .drop("timestamp"))

clients = (df.filter(col("topic") == "client_requests")
            .withColumn("json", from_json(col("value"), client_schema))
            .select("topic", "key", "timestamp", "json.*")
            .withColumn("ingest_ts", col("timestamp"))
            .drop("timestamp"))

# пишем раздельно в Parquet
products_q = (products.writeStream
              .format("parquet")
              .option("path", "hdfs://hdfs-namenode:9000/warehouse/products_filtered")
              .outputMode("append")
              .start())

clients_q = (clients.writeStream
             .format("parquet")
             .option("path", "hdfs://hdfs-namenode:9000/warehouse/client_requests")
             .outputMode("append")
             .start())

spark.streams.awaitAnyTermination()
