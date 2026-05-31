create database if not exists seoul_bike;

use seoul_bike; 

drop table if exists rental_2017_raw; 

create external table rental_2017_raw(
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

row format serde 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
with serdeproperties (
    "separatorChar" = ",",
    "quoteChar"     = "\"",
    "escapeChar"    = "\\"
)
stored as textfile
location '/user/maria_dev/seoul_bike/processed/'
tblproperties ("skip.header.line.count"="1");

-- 테이블 생성 확인용 샘플 조회
SELECT *
FROM rental_2017_raw
LIMIT 5;

-- 전체 행 수 확인
SELECT COUNT(*) AS row_count
FROM rental_2017_raw;