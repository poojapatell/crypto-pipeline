from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, current_timestamp, to_timestamp,
    avg, stddev, lag, round as spark_round
)
from pyspark.sql.window import Window

# Create Spark Session
spark = SparkSession.builder \
    .appName("CryptoPipelineGoldLayer") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("[INFO] Reading Bronze layer Parquet files from S3...")

try:
    # Read all Parquet files from Bronze layer
    df = spark.read.parquet("s3a://pooja-crypto-pipeline-bronze/raw/*/")
    
    print(f"[INFO] Read {df.count()} records from Bronze layer")
    
    # Convert timestamp string to timestamp
    df = df.withColumn("ts", to_timestamp(col("timestamp")))
    
    # Sort by timestamp (required for window functions)
    df = df.sort("ts")
    
    # Define window for rolling metrics (last 100 rows = ~100 ticks)
    window_spec = Window.orderBy("ts").rowsBetween(-100, 0)
    
    # Compute rolling metrics
    gold_df = df.select(
        col("timestamp"),
        col("symbol"),
        col("price"),
        col("quantity"),
        spark_round(avg(col("price")).over(window_spec), 2).alias("price_ma_100ticks"),
        spark_round(stddev(col("price")).over(window_spec), 4).alias("price_volatility"),
        spark_round(col("price") - lag(col("price"), 1).over(Window.orderBy("ts")), 4).alias("price_change"),
        current_timestamp().alias("computed_at")
    ).filter(col("price_ma_100ticks").isNotNull())  # Drop early rows with nulls
    
    print(f"[INFO] Computed metrics for {gold_df.count()} records")
    
    # Write to Gold layer in S3
    output_path = "s3a://pooja-crypto-pipeline-bronze/gold/"
    print(f"[INFO] Writing Gold layer to {output_path}...")
    
    gold_df.coalesce(1).write \
        .format("parquet") \
        .mode("overwrite") \
        .save(output_path)
    
    print("[INFO] Gold layer written successfully!")
    
    # Show sample data
    print("\n[INFO] Sample Gold layer data:")
    gold_df.select("timestamp", "symbol", "price", "price_ma_100ticks", "price_volatility", "price_change").show(10)

except Exception as e:
    print(f"[ERROR] {str(e)}")
    raise

spark.stop()