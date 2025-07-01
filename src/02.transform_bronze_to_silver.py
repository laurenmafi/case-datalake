# Databricks notebook source
from pyspark.sql import functions as F

# COMMAND ----------

# DBTITLE 1,Widgets
dbutils.widgets.text("processing_date", "2023-01", "Processing date (YYYY-MM)")
processing_date = dbutils.widgets.get("processing_date")

# COMMAND ----------

# DBTITLE 1,Buckets
project_name = "datalake-template-project"  
bronze_base = f"s3://{project_name}-bronze-zone/nyc_tlc"
silver_base = f"s3://{project_name}-silver-zone/nyc_tlc"

print(f"Using project name: {project_name}")
print(f"Bronze path: {bronze_base}")
print(f"Silver path: {silver_base}")

# COMMAND ----------

# DBTITLE 1,Path Read/Write
def get_bronze_path(source): return f"{bronze_base}/{source}/partition_year_month={processing_date}/"

# COMMAND ----------

# DBTITLE 1,Create Table
spark.sql(f"""
CREATE EXTERNAL TABLE IF NOT EXISTS `silver`.`nyc_tlc` (
    `vendor_id` integer,
    `vendor_name` string,
    `pickup_datetime` timestamp,
    `dropoff_datetime` timestamp,
    `total_amount` double,
    `payment_type` string,
    `passenger_count` integer,
    `source` string,
    `dt` string
)
PARTITIONED BY (dt)
LOCATION "{silver_base}"
""")

# COMMAND ----------

# DBTITLE 1,Format Colunms origem green
df_green = spark.read.parquet(
    get_bronze_path("green_tripdata")
)
df_green_clean = df_green.select(
    F.col("VendorID").cast("integer").alias("vendor_id"),
    F.when(F.col("VendorID") == 1, F.lit("Creative Mobile Technologies, LLC"))
        .when(F.col("VendorID") == 2, F.lit("Curb Mobility, LLC"))
        .when(F.col("VendorID") == 6, F.lit("Myle Technologies Inc"))
        .otherwise(F.lit("Other"))
        .alias("vendor_name"),
    F.col("lpep_pickup_datetime").cast("timestamp").alias("pickup_datetime"),
    F.col("lpep_dropoff_datetime").cast("timestamp").alias("dropoff_datetime"),
    F.col("total_amount").cast("double"),
    F.when(F.col("payment_type") == 0, F.lit("Flex Fare trip"))
        .when(F.col("payment_type") == 1, F.lit("Credit card"))
        .when(F.col("payment_type") == 2, F.lit("Cash"))
        .when(F.col("payment_type") == 3, F.lit("No charge"))
        .when(F.col("payment_type") == 4, F.lit("Dispute"))
        .when(F.col("payment_type") == 5, F.lit("Unknown"))
        .when(F.col("payment_type") == 6, F.lit("Voided trip"))
        .otherwise(F.lit("Other"))
        .alias("payment_type"),
    F.col("passenger_count").cast("integer"),
    F.lit("green").alias("source"),
    F.lit(processing_date).alias("dt")
)

# COMMAND ----------

# DBTITLE 1,Format Columns origem yellow
df_yellow = spark.read.parquet(
    get_bronze_path("yellow_tripdata")
)
df_yellow_clean = df_yellow.select(
    F.col("VendorID").cast("integer").alias("vendor_id"),
    F.when(F.col("VendorID") == 1, F.lit("Creative Mobile Technologies, LLC"))
        .when(F.col("VendorID") == 2, F.lit("Curb Mobility, LLC"))
        .when(F.col("VendorID") == 6, F.lit("Myle Technologies Inc"))
        .when(F.col("VendorID") == 7, F.lit("Helix"))
        .otherwise(F.lit("Other"))
        .alias("vendor_name"),
    F.col("tpep_pickup_datetime").cast("timestamp").alias("pickup_datetime"),
    F.col("tpep_dropoff_datetime").cast("timestamp").alias("dropoff_datetime"),
    F.col("total_amount").cast("double"),
    F.when(F.col("payment_type") == 0, F.lit("Flex Fare trip"))
        .when(F.col("payment_type") == 1, F.lit("Credit card"))
        .when(F.col("payment_type") == 2, F.lit("Cash"))
        .when(F.col("payment_type") == 3, F.lit("No charge"))
        .when(F.col("payment_type") == 4, F.lit("Dispute"))
        .when(F.col("payment_type") == 5, F.lit("Unknown"))
        .when(F.col("payment_type") == 6, F.lit("Voided trip"))
        .otherwise(F.lit("Other"))
        .alias("payment_type"),
    F.col("passenger_count").cast("integer"),
    F.lit("yellow").alias("source"),
    F.lit(processing_date).alias("dt")
)

# COMMAND ----------

# DBTITLE 1
df_final = df_yellow_clean.union(df_green_clean)

# COMMAND ----------

# DBTITLE 1,Union and Write Delta Table
(
    df_final.write
        .option("replaceWhere", f"dt = '{processing_date}'")
        .option("path", silver_base)
        .mode("overwrite")
        .saveAsTable("silver.nyc_tlc", partitionBy=["dt"])
)