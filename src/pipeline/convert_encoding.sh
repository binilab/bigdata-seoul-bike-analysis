#!/usr/bin/env bash

set -e

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

YEAR="${YEAR:-2017}"

if [ "${YEAR}" = "2017" ]; then
    DEFAULT_LOCAL_BASE_DIR="/home/maria_dev/seoul_bike"
    DEFAULT_HDFS_BASE_DIR="/user/maria_dev/seoul_bike"
else
    DEFAULT_LOCAL_BASE_DIR="/home/maria_dev/seoul_bike_${YEAR}"
    DEFAULT_HDFS_BASE_DIR="/user/maria_dev/seoul_bike_${YEAR}"
fi

LOCAL_BASE_DIR="${LOCAL_BASE_DIR:-${DEFAULT_LOCAL_BASE_DIR}}"
RAW_DIR="${LOCAL_BASE_DIR}/raw"
PROCESSED_DIR="${LOCAL_BASE_DIR}/processed"
HDFS_PROCESSED_DIR="${HDFS_PROCESSED_DIR:-${DEFAULT_HDFS_BASE_DIR}/processed}"
FILE_GLOB="${FILE_GLOB:-seoul_bike_${YEAR}_*.csv}"
PROCESSED_GLOB="${PROCESSED_GLOB:-seoul_bike_${YEAR}_*_utf8.csv}"

echo "서울시 따릉이 데이터 전처리 및 HDFS 적재 시작"
echo "분석 연도: ${YEAR}"
echo "로컬 raw 경로: ${RAW_DIR}"
echo "로컬 processed 경로: ${PROCESSED_DIR}"
echo "HDFS processed 경로: ${HDFS_PROCESSED_DIR}"
echo "파일 패턴: ${FILE_GLOB}"

echo "------------------------------------------"
echo "[1] 권한 및 디렉토리 준비"

sudo chown -R maria_dev "${LOCAL_BASE_DIR}"
chmod -R u+rwX "${LOCAL_BASE_DIR}"
rm -rf "${PROCESSED_DIR}"
mkdir -p "${PROCESSED_DIR}"

raw_files=("${RAW_DIR}"/${FILE_GLOB})

if [ ! -e "${raw_files[0]}" ]; then
    echo "변환할 CSV 파일을 찾지 못함: ${RAW_DIR}/${FILE_GLOB}"
    exit 1
fi

ls -lh "${raw_files[@]}"

echo "------------------------------------------"
echo "[2] 월별 CSV 인코딩 변환"

for raw_file in "${raw_files[@]}"; do
    raw_name=$(basename "${raw_file}" .csv)
    processed_file="${PROCESSED_DIR}/${raw_name}_utf8.csv"

    echo "변환 파일: ${raw_name}.csv"
    iconv -f CP949 -t UTF-8 -c "${raw_file}" > "${processed_file}"
    ls -lh "${processed_file}"
done

echo "------------------------------------------"
echo "[3] 변환 데이터 검증"

first_processed_file=$(ls "${PROCESSED_DIR}"/${PROCESSED_GLOB} | head -n 1)

echo "검증 파일: ${first_processed_file}"
echo "상위 3줄:"
head -n 3 "${first_processed_file}"

echo ""
echo "BOM 확인:"
head -c 3 "${first_processed_file}" | xxd

echo "------------------------------------------"
echo "[4] HDFS processed 재적재"

hdfs dfs -rm -r -f "${HDFS_PROCESSED_DIR}"
hdfs dfs -mkdir -p "${HDFS_PROCESSED_DIR}"

processed_files=("${PROCESSED_DIR}"/${PROCESSED_GLOB})

for processed_file in "${processed_files[@]}"; do
    file_name=$(basename "${processed_file}")
    echo "HDFS 업로드 파일: ${file_name}"
    hdfs dfs -put "${processed_file}" "${HDFS_PROCESSED_DIR}/"
done

echo "------------------------------------------"
echo "[5] HDFS processed 적재 결과"

hdfs dfs -ls -h "${HDFS_PROCESSED_DIR}"
hdfs dfs -du -h "${HDFS_PROCESSED_DIR}"

echo "전처리 스크립트 완료"
