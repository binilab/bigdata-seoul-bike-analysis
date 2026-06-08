-- 기존 외부 테이블 삭제
DROP TABLE IF EXISTS rental_2025_raw;

-- HDFS processed 경로의 UTF-8 CSV를 읽는 Hive 외부 테이블 생성
CREATE EXTERNAL TABLE rental_2025_raw (
    bike_no STRING,
    rent_datetime STRING,
    rent_station_no STRING,
    rent_station_name STRING,
    rent_rack_no STRING,
    return_datetime STRING,
    return_station_no STRING,
    return_station_name STRING,
    return_rack_no STRING,
    use_min STRING,
    use_distance_m STRING,
    birth_year STRING,
    gender STRING,
    user_type STRING,
    rent_station_id STRING,
    return_station_id STRING,
    bike_type STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    "separatorChar" = ",",
    "quoteChar" = "\"",
    "escapeChar" = "\\"
)
STORED AS TEXTFILE
LOCATION '/user/maria_dev/seoul_bike_2025/processed/'
TBLPROPERTIES (
    "skip.header.line.count" = "1"
);

-- 테이블 생성 확인용 샘플 조회
SELECT rent_datetime, rent_station_name, return_station_name, use_min, use_distance_m
FROM rental_2025_raw
LIMIT 10;

-- 전체 행 수 확인
SELECT COUNT(*) AS row_count
FROM rental_2025_raw;
