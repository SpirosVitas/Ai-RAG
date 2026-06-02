import os
import sys

# Αυτό λέει στο PySpark να χρησιμοποιήσει ακριβώς την Python του .venv σου
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local[*]").appName("test").getOrCreate()

df = spark.createDataFrame([(1,"A"),(2,"B")],["id","name"])
df.show()

spark.stop()