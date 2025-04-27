from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg, sum, first, last
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, TimestampType

def create_spark_session():
    return (SparkSession.builder
            .appName("FinTech Streaming")
            .config("spark.cassandra.connection.host", "cassandra")
            .config("spark.cassandra.connection.port", "9042")
            .config("spark.cassandra.output.consistency.level", "ONE")
            .getOrCreate())

def main():
    try:
        # Initialize Spark session
        spark = create_spark_session()
        spark.sparkContext.setLogLevel("WARN")
        
        # Define the schema for incoming Kafka data
        schema = StructType([
            StructField("symbol", StringType(), True),
            StructField("price", DoubleType(), True),
            StructField("volume", LongType(), True),
            StructField("timestamp", LongType(), True)
        ])
        
        # Read stream from Kafka
        kafka_df = (spark
                    .readStream
                    .format("kafka")
                    .option("kafka.bootstrap.servers", "kafka:9092")
                    .option("subscribe", "raw-financial-data")
                    .option("startingOffsets", "latest")
                    .load())
        
        # Parse JSON data
        parsed_df = kafka_df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        # Convert timestamp to proper format
        parsed_df = parsed_df.withColumn(
            "event_time", 
            (col("timestamp") / 1000).cast(TimestampType())
        )
        
        # Write raw data to Cassandra (excluding event_time)
        raw_query = (parsed_df.drop("event_time")
                     .writeStream
                     .format("org.apache.spark.sql.cassandra")
                     .option("checkpointLocation", "/tmp/checkpoint/raw_data")
                     .option("keyspace", "fintech")
                     .option("table", "raw_financial_data")
                     .start())
        
        print("Raw data streaming query started successfully")
        
        # Perform aggregations with 5-second windows
        agg_df = (parsed_df
                  .withWatermark("event_time", "10 seconds")
                  .groupBy(col("symbol"), window(col("event_time"), "5 seconds"))
                  .agg(
                      avg("price").alias("avg_price"),
                      sum("volume").alias("total_volume"),
                      first("price").alias("first_price"),
                      last("price").alias("last_price")
                  )
                  .withColumn("price_change", col("last_price") - col("first_price"))
                  .select(
                      col("symbol"),
                      col("window.start").alias("window_start"),
                      col("window.end").alias("window_end"),
                      col("avg_price"),
                      col("total_volume"),
                      col("price_change")
                  ))
        
        # Write aggregated data to Cassandra
        agg_query = (agg_df
                     .writeStream
                     .format("org.apache.spark.sql.cassandra")
                     .option("checkpointLocation", "/tmp/checkpoint/aggregated_data")
                     .option("keyspace", "fintech")
                     .option("table", "aggregated_financial_data")
                     .start())
        
        print("Aggregation streaming query started successfully")
        
        # Wait for termination
        spark.streams.awaitAnyTermination()
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()