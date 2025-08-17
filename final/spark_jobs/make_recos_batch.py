from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, desc, row_number, max as smax
from pyspark.sql.window import Window
from pyspark.sql.functions import concat_ws, to_json, struct

spark = (SparkSession.builder
         .appName("make_recos_batch")
         .getOrCreate())

products = spark.read.parquet("hdfs://hdfs-namenode:9000/warehouse/products_filtered")
clients  = spark.read.parquet("hdfs://hdfs-namenode:9000/warehouse/client_requests")

# нормализуем
prod = (products
        .select("product_id","name","category","brand","stock.available")
        .withColumnRenamed("available","available"))

# последние запросы по клиенту
w = Window.partitionBy("client_id").orderBy(desc("ingest_ts"))
last_q = (clients
          .filter(col("action") == "search")
          .withColumn("rn", row_number().over(w))
          .filter(col("rn") == 1)
          .select("client_id", lower(col("query")).alias("q"))
         )

# «персонализация» — подстрока по названию/категории
cand = (last_q.join(prod,
        (lower(prod.name).contains(col("q"))) | (lower(prod.category).contains(col("q"))),
        how="left"))

# Топ-5 на клиента
win_client = Window.partitionBy("client_id").orderBy(desc(col("available")))
per_client_top = (cand
                  .withColumn("rn", row_number().over(win_client))
                  .filter(col("rn") <= 5)
                  .groupBy("client_id")
                  .agg(concat_ws(",", col("product_id")).alias("product_ids"))
                 )

# Фоллбек — общий топ-5
overall_top5 = (prod.orderBy(desc(col("available")))
                .limit(5)
                .select(concat_ws(",", col("product_id")).alias("product_ids"))
                .collect()[0]["product_ids"])

# Добавим фоллбек, где пусто
recs = (per_client_top
        .na.fill({"product_ids": overall_top5})
        .select(col("client_id").cast("string").alias("key"),
                to_json(struct("client_id","product_ids")).alias("value")))

# пишем в Kafka (cluster B)
(recs.write
 .format("kafka")
 .option("kafka.bootstrap.servers","kafka-b-1:9092,kafka-b-2:9092")
 .option("topic","recommendations")
 .option("kafka.security.protocol","SSL")
 .option("kafka.ssl.truststore.location","/opt/certs/kafka.truststore.jks")
 .option("kafka.ssl.truststore.password","changeit")
 .option("kafka.ssl.truststore.type","JKS")
 # .option("kafka.ssl.endpoint.identification.algorithm","")  # если нужно
 .save())
