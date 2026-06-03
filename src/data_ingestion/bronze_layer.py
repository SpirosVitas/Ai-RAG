"""
Μην τον δοκιμασετε δεν τρεχει σε τοπικο περιβαλλον, μονο σε Databricks με Delta Lake
γιατι θελει pyspark + java + delta lake dependencies που δεν ειναι απλα να ρυθμιστουν τοπικα.
"""
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

# Define the explicit schema for the Bronze Ingestion Table
BRONZE_TABLE_SCHEMA = StructType([
    StructField("celex_id", StringType(), False),
    StructField("file_name", StringType(), False),
    StructField("file_path", StringType(), False),
    StructField("source_api", StringType(), False),
    StructField("status", StringType(), False),
    StructField("ingestion_timestamp", TimestampType(), False)
])

def ingest_metadata_to_bronze(spark: SparkSession, downloaded_files: list, catalog: str = "main", schema: str = "regulatory_project"):
    """
    Ingests metadata of downloaded PDF documents into the Bronze Delta Table using the PySpark Dataframe API.
    """
    table_name = f"{catalog}.{schema}.bronze_regulatory_log"
    
    # Create the database schema if it does not exist
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
    
    # Create the Bronze Delta Table if it does not exist using SQL definition
    spark.sql(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            celex_id STRING,
            file_name STRING,
            file_path STRING,
            source_api STRING,
            status STRING,
            ingestion_timestamp TIMESTAMP
        ) USING DELTA
    """)
    
    # Prepare local Python records from the input list
    records = []
    for file_info in downloaded_files:
        records.append((
            file_info["celex_id"],
            file_info["file_name"],
            file_info["file_path"],
            "EUR-Lex",
            "RAW_DOWNLOADED",
            datetime.utcnow()
        ))
        
    if not records:
        print("No new records to ingest into the Bronze layer.")
        return

    # Create a base PySpark DataFrame from the Python records using the explicit schema
    input_df = spark.createDataFrame(records, schema=BRONZE_TABLE_SCHEMA)
    
    # PySpark Dataframe API transformation to enforce exact column selection and auditing
    final_bronze_df = input_df.select(
        input_df["celex_id"],
        input_df["file_name"],
        input_df["file_path"],
        input_df["source_api"],
        input_df["status"],
        current_timestamp().alias("ingestion_timestamp")
    )
    
    # Append the transformed DataFrame directly into the Delta Table via the PySpark Writer API
    final_bronze_df.write \
        .format("delta") \
        .mode("append") \
        .saveAsTable(table_name)
        
    print(f"Successfully appended {len(records)} metadata records to {table_name} using PySpark Dataframe API.")


if __name__ == "__main__":
    print("Initializing local SparkSession for smoke testing...")
    local_spark = SparkSession.builder \
        .appName("LocalBronzeTesting") \
        .master("local[*]") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()
        
    sample_downloads = [
        {
            "celex_id": "32022R2554", 
            "file_name": "32022R2554_EN.pdf", 
            "file_path": "abfss://regulatory-data@storage.dfs.core.windows.net/raw/32022R2554_EN.pdf"
        }
    ]
    
    try:
        ingest_metadata_to_bronze(local_spark, sample_downloads, catalog="local_test", schema="bronze")
    except Exception as e:
        print(f"Environment log variation handled: {e}")
    finally:
        local_spark.stop()