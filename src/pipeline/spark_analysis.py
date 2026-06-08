# -*- coding: utf-8 -*-

import os

from pyspark import StorageLevel
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


# HDFS 입력/출력 경로
YEAR = os.environ.get("YEAR", "2017")

if YEAR == "2017":
    DEFAULT_HDFS_BASE = "hdfs:///user/maria_dev/seoul_bike"
else:
    DEFAULT_HDFS_BASE = f"hdfs:///user/maria_dev/seoul_bike_{YEAR}"

INPUT_PATH = os.environ.get(
    "INPUT_PATH",
    f"{DEFAULT_HDFS_BASE}/processed/seoul_bike_{YEAR}_*_utf8.csv",
)
OUTPUT_BASE = os.environ.get(
    "OUTPUT_BASE",
    f"{DEFAULT_HDFS_BASE}/results/csv",
)


def save_result(df, output_path):
    # Spark 결과는 기본적으로 여러 part 파일로 저장되므로, 작은 집계 결과는 1개 파일로 줄여 저장
    df.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)


if __name__ == "__main__":
    # Spark 실행 시작
    spark = SparkSession.builder \
        .appName("SeoulBikeAnalysis") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    spark.conf.set(
        "spark.sql.shuffle.partitions",
        os.environ.get("SPARK_SQL_SHUFFLE_PARTITIONS", "48"),
    )

    print("analysis_start")
    print("analysis_year")
    print(YEAR)
    print("input_path")
    print(INPUT_PATH)
    print("output_base")
    print(OUTPUT_BASE)
    print("shuffle_partitions")
    print(spark.conf.get("spark.sql.shuffle.partitions"))

    # CSV 로드
    raw_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .option("quote", "\"") \
        .option("escape", "\"") \
        .csv(INPUT_PATH)

    # 원본 한글 컬럼명을 분석용 영어 컬럼명으로 변경
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

    if len(raw_df.columns) != len(columns):
        raise ValueError(
            "unexpected_column_count: expected={}, actual={}".format(
                len(columns),
                len(raw_df.columns),
            )
        )

    df = raw_df.toDF(*columns)

    # 분석에 필요한 날짜/숫자 컬럼 변환
    df = df.withColumn("rent_ts", F.to_timestamp("rent_datetime", "yyyy-MM-dd HH:mm:ss"))
    df = df.withColumn("use_min_num", F.col("use_min").cast("double"))
    df = df.withColumn("use_distance_m_num", F.col("use_distance_m").cast("double"))

    # 날짜와 숫자값이 정상인 데이터만 사용
    clean_df = df.filter(F.col("rent_ts").isNotNull()) \
        .filter(F.col("use_min_num").isNotNull()) \
        .filter(F.col("use_distance_m_num").isNotNull()) \
        .filter(F.col("use_min_num") >= 0) \
        .filter(F.col("use_distance_m_num") >= 0)

    # 2025년 전체 데이터처럼 큰 입력에서는 여러 집계가 같은 정제 결과를 반복해서 읽지 않도록 저장한다.
    clean_df = clean_df.persist(StorageLevel.MEMORY_AND_DISK)

    print("clean_row_count")
    print(clean_df.count())

    # 1. 월별 이용량
    monthly_usage = clean_df.withColumn("month", F.date_format("rent_ts", "yyyy-MM")) \
        .groupBy("month") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("month")

    # 2. 시간대별 이용량
    hourly_usage = clean_df.withColumn("hour", F.hour("rent_ts")) \
        .groupBy("hour") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("hour")

    # 3. 대여소별 이용량 Top 10
    station_top10 = clean_df.groupBy("rent_station_no", "rent_station_name") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy(F.col("rental_count").desc()) \
        .limit(10)

    # 4. 이용시간과 이동거리 요약 통계
    usage_summary = clean_df.agg(
        F.count("*").alias("row_count"),
        F.avg("use_min_num").alias("avg_use_min"),
        F.min("use_min_num").alias("min_use_min"),
        F.max("use_min_num").alias("max_use_min"),
        F.avg("use_distance_m_num").alias("avg_distance_m"),
        F.min("use_distance_m_num").alias("min_distance_m"),
        F.max("use_distance_m_num").alias("max_distance_m"),
    )

    # 5. 이용시간 구간별 분포
    duration_distribution = clean_df.withColumn(
        "duration_group",
        F.when(F.col("use_min_num") < 5, "00_0_5min")
         .when(F.col("use_min_num") < 10, "01_5_10min")
         .when(F.col("use_min_num") < 20, "02_10_20min")
         .when(F.col("use_min_num") < 30, "03_20_30min")
         .when(F.col("use_min_num") < 60, "04_30_60min")
         .otherwise("05_60min_over")
    ).groupBy("duration_group") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("duration_group")

    # 6. 이동거리 구간별 분포
    distance_distribution = clean_df.withColumn(
        "distance_group",
        F.when(F.col("use_distance_m_num") < 500, "00_0_500m")
         .when(F.col("use_distance_m_num") < 1000, "01_500_1000m")
         .when(F.col("use_distance_m_num") < 2000, "02_1000_2000m")
         .when(F.col("use_distance_m_num") < 5000, "03_2000_5000m")
         .otherwise("04_5000m_over")
    ).groupBy("distance_group") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("distance_group")

    # 결과 저장
    print("save_monthly_usage")
    save_result(monthly_usage, f"{OUTPUT_BASE}/monthly_usage")
    print("save_hourly_usage")
    save_result(hourly_usage, f"{OUTPUT_BASE}/hourly_usage")
    print("save_station_top10")
    save_result(station_top10, f"{OUTPUT_BASE}/station_top10")
    print("save_usage_summary")
    save_result(usage_summary, f"{OUTPUT_BASE}/usage_summary")
    print("save_duration_distribution")
    save_result(duration_distribution, f"{OUTPUT_BASE}/duration_distribution")
    print("save_distance_distribution")
    save_result(distance_distribution, f"{OUTPUT_BASE}/distance_distribution")

    # 저장 후 간단히 확인
    monthly_usage.show(20, truncate=False)
    duration_distribution.show(truncate=False)
    distance_distribution.show(truncate=False)

    print("analysis_done")

    clean_df.unpersist()

    spark.stop()
