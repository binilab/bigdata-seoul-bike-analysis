#!/usr/bin/env bash

set -e

LOCAL_RAW_DIR="/home/maria_dev/seoul_bike/raw"
HDFS_RAW_DIR="/user/maria_dev/seoul_bike/raw"

echo "HDFS raw 적재 시작"
echo "로컬 raw 경로: ${LOCAL_RAW_DIR}"
echo "HDFS raw 경로: ${HDFS_RAW_DIR}"

echo "업로드 대상:"
ls -lh "${LOCAL_RAW_DIR}"/seoul_bike_2017_*.csv

hdfs dfs -rm -r -f "${HDFS_RAW_DIR}"
hdfs dfs -mkdir -p "${HDFS_RAW_DIR}"

for raw_file in "${LOCAL_RAW_DIR}"/seoul_bike_2017_*.csv; do
    file_name=$(basename "${raw_file}")

    echo "업로드 파일: ${file_name}"
    hdfs dfs -put "${raw_file}" "${HDFS_RAW_DIR}/"
done

echo "HDFS raw 적재 결과:"
hdfs dfs -ls -h "${HDFS_RAW_DIR}"

echo "HDFS raw 적재 완료"
