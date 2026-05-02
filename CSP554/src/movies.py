import sys
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col

if len(sys.argv) != 3:
   print("Usage: movies <moviespath> <ratingspath>  ", file=sys.stderr)
   exit(-1)

spark = SparkSession.builder.appName('MovieLens').getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema_movies = StructType(
    [
        StructField("id", StringType(), False),
        StructField("title", StringType(), False),
        StructField("genres", StringType(), True),
    ]
)

schema_ratings = StructType(
    [
        StructField("userId", StringType(), False),
        StructField("movieId", StringType(), False),
        StructField("rating", FloatType(), True),
        StructField("timestamp", StringType(), True),
    ]
)

file_path_movies = sys.argv[1]
file_path_ratings = sys.argv[2]

movies = (
    spark.read.format("csv")
    .option("encoding", "UTF-8")
    .option("header", True)
    .option("sep", ",")
    .option("escape", '"')
    .schema(schema_movies)
    .load(file_path_movies)
)

movies.show(10)

ratings = (
    spark.read.format("csv")
    .option("encoding", "UTF-8")
    .option("header", True)
    .option("sep", ",")
    .option("escape", '"')
    .schema(schema_ratings)
    .load(file_path_ratings)
)

ratings.show(10)

# Add your code here


