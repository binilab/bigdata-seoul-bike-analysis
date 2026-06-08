#!/usr/bin/env bash

set -e

YEAR="${YEAR:-2017}"

if [ "${YEAR}" = "2017" ]; then
    DEFAULT_LOCAL_BASE_DIR="/home/maria_dev/seoul_bike"
    DEFAULT_HDFS_BASE_DIR="/user/maria_dev/seoul_bike"
else
    DEFAULT_LOCAL_BASE_DIR="/home/maria_dev/seoul_bike_${YEAR}"
    DEFAULT_HDFS_BASE_DIR="/user/maria_dev/seoul_bike_${YEAR}"
fi

LOCAL_RAW_DIR="${LOCAL_RAW_DIR:-${DEFAULT_LOCAL_BASE_DIR}/raw}"
HDFS_RAW_DIR="${HDFS_RAW_DIR:-${DEFAULT_HDFS_BASE_DIR}/raw}"
FILE_GLOB="${FILE_GLOB:-seoul_bike_${YEAR}_*.csv}"

echo "HDFS raw 적재 시작"
echo "분석 연도: ${YEAR}"
echo "로컬 raw 경로: ${LOCAL_RAW_DIR}"
echo "HDFS raw 경로: ${HDFS_RAW_DIR}"
echo "파일 패턴: ${FILE_GLOB}"

echo "업로드 대상:"
raw_files=("${LOCAL_RAW_DIR}"/${FILE_GLOB})

if [ ! -e "${raw_files[0]}" ]; then
    echo "업로드할 CSV 파일을 찾지 못함: ${LOCAL_RAW_DIR}/${FILE_GLOB}"
    exit 1
fi

ls -lh "${raw_files[@]}"

hdfs dfs -rm -r -f "${HDFS_RAW_DIR}"
hdfs dfs -mkdir -p "${HDFS_RAW_DIR}"

for raw_file in "${raw_files[@]}"; do
    file_name=$(basename "${raw_file}")

    echo "업로드 파일: ${file_name}"
    hdfs dfs -put "${raw_file}" "${HDFS_RAW_DIR}/"
done

echo "HDFS raw 적재 결과:"
hdfs dfs -ls -h "${HDFS_RAW_DIR}"

echo "HDFS raw 적재 완료"
