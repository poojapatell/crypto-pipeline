from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType
import time

# Create Spark Session
spark = SparkSession.builder \
    .appName("CryptoPipelineConsumer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema
schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", DoubleType(), True),
    StructField("trade_id", LongType(), True)
])

print("[INFO] Connecting to Kafka broker at kafka:29092...")

try:
    # Read from Kafka in batch mode
    df = spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "price-ticks") \
        .option("startingOffsets", "earliest") \
        .option("endingOffsets", "latest") \
        .load()

    print(f"[INFO] Read {df.count()} records from Kafka")

    # Parse JSON
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    # Write to S3 Bronze layer
    output_path = f"s3a://pooja-crypto-pipeline-bronze/raw/{int(time.time())}"
    print(f"[INFO] Writing to {output_path}...")

    parsed_df.select(
        col("timestamp"),
        col("symbol"),
        col("price"),
        col("quantity"),
        col("trade_id"),
        current_timestamp().alias("ingestion_time")
    ).coalesce(1).write \
        .format("parquet") \
        .mode("append") \
        .save(output_path)

    print("[INFO] Data written successfully to S3 Bronze layer!")
    print(f"[INFO] Output location: {output_path}")

except Exception as e:
    print(f"[ERROR] {str(e)}")
    raise

spark.stop()