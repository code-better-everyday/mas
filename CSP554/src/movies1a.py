import os
import sys
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import col, count


def ensure_java_home():
    if os.environ.get("JAVA_HOME"):
        return

    candidate_roots = [
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Java",
        r"C:\Program Files (x86)\Java",
    ]

    for root in candidate_roots:
        if not os.path.isdir(root):
            continue

        for entry in sorted(os.listdir(root), reverse=True):
            candidate = os.path.join(root, entry)
            if os.path.isdir(candidate) and os.path.isfile(os.path.join(candidate, "bin", "java.exe")):
                os.environ["JAVA_HOME"] = candidate
                os.environ["PATH"] = candidate + r"\bin;" + os.environ.get("PATH", "")
                return

    print("Java not found and JAVA_HOME environment variable is not set.", file=sys.stderr)
    print("Install Java and set JAVA_HOME to point to the Java installation directory.", file=sys.stderr)
    exit(-1)


ensure_java_home()

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

# ratings.show(10)
# exercise 1a
print("*" * 50)
print("Exercise 1a")
review_counts = ratings.groupBy("movieId").agg(count("userId").alias("review_count"))
review_counts.show(10)
print("*" * 50)

# exercise 1b
print("*" * 50)
print("Exercise 1b")
sorted_review_counts = review_counts.withColumnRenamed("review_count", "num_ratings").orderBy("num_ratings", ascending=False)
sorted_review_counts.show(10)
print("*" * 50)
