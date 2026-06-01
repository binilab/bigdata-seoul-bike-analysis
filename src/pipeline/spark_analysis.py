# -*- coding: utf-8 -*-

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

INPUT_PATH = "hdfs:///user/maria_dev/seoul_bike/processed/seoul_bike_2017_*_utf8.csv"
OUTPUT_BASE = "hdfs:///user/maria_dev/seoul_bike/results/csv"


def save_result(df, output_path):
    df.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("SeoulBikeAnalysis") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print("analysis_start")

    raw_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .option("quote", "\"") \
        .option("escape", "\"") \
        .csv(INPUT_PATH)

    columns = [
        "bike_no",
        "rent_datetime",
        "rent_station_no",
        "rent_station_name",
        "rent_rack_no",
        "return_datetime",
        "return_station_no",
        "return_station_name",
        "return_rack_no",
        "use_min",
        "use_distance_m",
        "birth_year",
        "gender",
        "user_type",
        "rent_station_id",
        "return_station_id",
        "bike_type",
    ]

    df = raw_df.toDF(*columns)

    df = df.withColumn("rent_ts", F.to_timestamp("rent_datetime", "yyyy-MM-dd HH:mm:ss"))
    df = df.withColumn("use_min_num", F.col("use_min").cast("double"))
    df = df.withColumn("use_distance_m_num", F.col("use_distance_m").cast("double"))

    clean_df = df.filter(F.col("rent_ts").isNotNull()) \
        .filter(F.col("use_min_num").isNotNull()) \
        .filter(F.col("use_distance_m_num").isNotNull()) \
        .filter(F.col("use_min_num") >= 0) \
        .filter(F.col("use_distance_m_num") >= 0)

    print("clean_row_count")
    print(clean_df.count())

    monthly_usage = clean_df.withColumn("month", F.date_format("rent_ts", "yyyy-MM")) \
        .groupBy("month") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("month")

    hourly_usage = clean_df.withColumn("hour", F.hour("rent_ts")) \
        .groupBy("hour") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("hour")

    station_top10 = clean_df.groupBy("rent_station_no", "rent_station_name") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy(F.col("rental_count").desc()) \
        .limit(10)

    usage_summary = clean_df.agg(
        F.count("*").alias("row_count"),
        F.avg("use_min_num").alias("avg_use_min"),
        F.min("use_min_num").alias("min_use_min"),
        F.max("use_min_num").alias("max_use_min"),
        F.avg("use_distance_m_num").alias("avg_distance_m"),
        F.min("use_distance_m_num").alias("min_distance_m"),
        F.max("use_distance_m_num").alias("max_distance_m"),
    )

    print("monthly_usage")
    monthly_usage.show(20, truncate=False)

    print("hourly_usage")
    hourly_usage.show(24, truncate=False)

    print("station_top10")
    station_top10.show(10, truncate=False)

    print("usage_summary")
    usage_summary.show(truncate=False)

    save_result(monthly_usage, f"{OUTPUT_BASE}/monthly_usage")
    save_result(hourly_usage, f"{OUTPUT_BASE}/hourly_usage")
    save_result(station_top10, f"{OUTPUT_BASE}/station_top10")
    save_result(usage_summary, f"{OUTPUT_BASE}/usage_summary")

    print("analysis_done")

    spark.stop()
