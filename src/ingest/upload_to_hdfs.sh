#!/usr/bin/evn bash 

set -e 

LOCAL_FILE="/home/maria_dev/seoul_bike/raw/seoul_bike_2017.csv"
HDFS_DIR="/user/maria_dev/seoul_bike/raw"
HDFS_FILE="${HDFS_DIR}/seoul_bike_2017.csv"

echo "로컬 원본 파일:"
echo "${LOCAL_FILE}"
echo "HDFS 저장 경로:"
echo "${HDFS_FILE}"
ls -lh "${LOCAL_FILE}"

hdfs dfs -mkdir -p "${HDFS_DIR}"
hdfs dfs -rm -f "${HDFS_FILE}"
hdfs dfs -put "${LOCAL_FILE}" "${HDFS_FILE}"

echo "HDFS 파일 목록:"
hdfs dfs -ls -h "${HDFS_DIR}"

echo "HDFS 파일 앞부분:"
hdfs dfs -cat "${HDFS_FILE}" | head -n 3