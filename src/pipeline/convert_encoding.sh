#!/usr/bin/env bash

set -e

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

LOCAL_BASE_DIR="/home/maria_dev/seoul_bike"
RAW_DIR="${LOCAL_BASE_DIR}/raw"
PROCESSED_DIR="${LOCAL_BASE_DIR}/processed"
HDFS_PROCESSED_DIR="/user/maria_dev/seoul_bike/processed"

echo "따릉이 데이터 전처리 시작"
echo "raw 경로: ${RAW_DIR}"
echo "processed 경로: ${PROCESSED_DIR}"
echo "HDFS processed 경로: ${HDFS_PROCESSED_DIR}"

echo "------------------------------------------"
echo "[1] 로컬 권한 및 폴더 정리"

sudo chown -R maria_dev "${LOCAL_BASE_DIR}"
chmod -R u+rwX "${LOCAL_BASE_DIR}"

rm -rf "${PROCESSED_DIR}"
mkdir -p "${PROCESSED_DIR}"

echo "변환 대상:"
ls -lh "${RAW_DIR}"/seoul_bike_2017_*.csv

echo "------------------------------------------"
echo "[2] CP949 -> UTF-8 변환"

for raw_file in "${RAW_DIR}"/seoul_bike_2017_*.csv; do
    raw_name=$(basename "${raw_file}" .csv)
    processed_file="${PROCESSED_DIR}/${raw_name}_utf8.csv"

    echo "변환 파일: ${raw_name}.csv"
    iconv -f CP949 -t UTF-8 -c "${raw_file}" > "${processed_file}"

    ls -lh "${processed_file}"
done

echo "------------------------------------------"
echo "[3] 변환 결과 확인"

first_file=$(ls "${PROCESSED_DIR}"/seoul_bike_2017_*_utf8.csv | head -n 1)

echo "검증 파일: ${first_file}"
echo "상위 3줄:"
head -n 3 "${first_file}"

echo ""
echo "BOM 확인:"
head -c 3 "${first_file}" | xxd

echo "------------------------------------------"
echo "[4] HDFS processed 적재"

hdfs dfs -rm -r -f "${HDFS_PROCESSED_DIR}"
hdfs dfs -mkdir -p "${HDFS_PROCESSED_DIR}"

for processed_file in "${PROCESSED_DIR}"/seoul_bike_2017_*_utf8.csv; do
    file_name=$(basename "${processed_file}")

    echo "업로드 파일: ${file_name}"
    hdfs dfs -put "${processed_file}" "${HDFS_PROCESSED_DIR}/"
done

echo "------------------------------------------"
echo "[5] HDFS 적재 결과"

hdfs dfs -ls -h "${HDFS_PROCESSED_DIR}"
hdfs dfs -du -h "${HDFS_PROCESSED_DIR}"

echo "전처리 완료"
