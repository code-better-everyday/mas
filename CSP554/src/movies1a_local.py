import os
import sys


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
    raise SystemExit(1)


ensure_java_home()

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from pyspark.sql.functions import count

spark = SparkSession.builder.appName("MovieLensLocal").getOrCreate()
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

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path_movies = os.path.join(base_dir, "data", "movies.csv")
file_path_ratings = os.path.join(base_dir, "data", "ratings.csv")

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

# Exercise 1a
review_counts = ratings.groupBy("movieId").agg(count("userId").alias("review_count"))
review_counts.show(10)

# Exercise 1a
sorted_review_counts = review_counts.withColumnRenamed("review_count", "num_ratings").orderBy("num_ratings", ascending=False)
sorted_review_counts.show(10)

spark.stop()
