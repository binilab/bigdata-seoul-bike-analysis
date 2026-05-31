# 한글 주석과 문자열 처리를 위해 UTF-8 인코딩 사용

from pyspark.sql import SparkSession
from pyspark.sql import functions as F



INPUT_PATH = "hdfs:///user/maria_dev/seoul_bike/processed/seoul_bike_2017_utf8.csv"
# HDFS에 저장된 UTF-8 따릉이 CSV 경로

OUTPUT_BASE = "hdfs:///user/maria_dev/seoul_bike/results/csv"
# 분석 결과 CSV를 저장할 HDFS 기본 경로


def save_result(df, output_path):
    # 분석 결과 DataFrame을 CSV로 저장하는 함수

    df.coalesce(1) \
        .write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)



if __name__ == "__main__":

    spark = SparkSession.builder \
        .appName("SeoulBikeAnalysis") \
        .getOrCreate()
    # SparkSession 생성

    spark.sparkContext.setLogLevel("WARN")

    print("분석 시작")

    raw_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .option("quote", "\"") \
        .option("escape", "\"") \
        .csv(INPUT_PATH)
    # 처음에는 전부 문자열로 읽어서 타입 문제를 줄임

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
    # 한글 컬럼명을 코드에서 다루기 쉽게 영어 컬럼명으로 정리

    df = raw_df.toDF(*columns)
    df = df.withColumn("rent_ts", F.to_timestamp("rent_datetime", "yyyy-MM-dd HH:mm:ss"))
    df = df.withColumn("use_min_num", F.col("use_min").cast("double"))
    df = df.withColumn("use_distance_m_num", F.col("use_distance_m").cast("double"))
  
    clean_df = df.filter(F.col("rent_ts").isNotNull()) \
        .filter(F.col("use_min_num").isNotNull()) \
        .filter(F.col("use_distance_m_num").isNotNull()) \
        .filter(F.col("use_min_num") >= 0) \
        .filter(F.col("use_distance_m_num") >= 0)
    # 분석에 필요한 컬럼이 정상인 행만 남김

    print("정제 데이터 행 수:")
    # 정제 후 행 수 출력 제목

    print(clean_df.count())
 

    monthly_usage = clean_df.withColumn("month", F.date_format("rent_ts", "yyyy-MM")) \
        .groupBy("month") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("month")
    # 월별 이용량 집계

    hourly_usage = clean_df.withColumn("hour", F.hour("rent_ts")) \
        .groupBy("hour") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy("hour")
    # 시간대별 이용량 집계

    station_top10 = clean_df.groupBy("rent_station_no", "rent_station_name") \
        .agg(F.count("*").alias("rental_count")) \
        .orderBy(F.col("rental_count").desc()) \
        .limit(10)
    # 대여소별 이용량 상위 10개 집계

    usage_summary = clean_df.agg(
        F.count("*").alias("row_count"),
        F.avg("use_min_num").alias("avg_use_min"),
        F.min("use_min_num").alias("min_use_min"),
        F.max("use_min_num").alias("max_use_min"),
        F.avg("use_distance_m_num").alias("avg_distance_m"),
        F.min("use_distance_m_num").alias("min_distance_m"),
        F.max("use_distance_m_num").alias("max_distance_m"),
    )
    # 이용시간과 이동거리의 기본 통계 계산

    print("월별 이용량")
    # 월별 이용량 출력 제목

    monthly_usage.show(20, truncate=False)
    # 월별 이용량 미리보기

    print("시간대별 이용량")
    # 시간대별 이용량 출력 제목

    hourly_usage.show(24, truncate=False)
    # 시간대별 이용량 미리보기

    print("대여소별 이용량 Top 10")
    # 대여소 Top 10 출력 제목

    station_top10.show(10, truncate=False)
    # 대여소 Top 10 미리보기

    print("이용시간 및 이동거리 요약")
    # 요약 통계 출력 제목

    usage_summary.show(truncate=False)
    # 이용시간/이동거리 통계 미리보기

    save_result(monthly_usage, f"{OUTPUT_BASE}/monthly_usage")
    # 월별 이용량 결과 저장

    save_result(hourly_usage, f"{OUTPUT_BASE}/hourly_usage")
    # 시간대별 이용량 결과 저장

    save_result(station_top10, f"{OUTPUT_BASE}/station_top10")
    # 대여소 Top 10 결과 저장

    save_result(usage_summary, f"{OUTPUT_BASE}/usage_summary")
    # 이용시간/이동거리 요약 통계 저장

    print("분석 결과 저장 완료")
    # 분석 완료 출력

    spark.stop()

