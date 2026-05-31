#!/usr/bin/env bash
set -e

export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# 경로 설정
LOCAL_BASE_DIR="/home/maria_dev/seoul_bike"
RAW_FILE="${LOCAL_BASE_DIR}/raw/seoul_bike_2017.csv"
PROCESSED_DIR="${LOCAL_BASE_DIR}/processed"
PROCESSED_FILE="${PROCESSED_DIR}/seoul_bike_2017_utf8.csv"
HDFS_PROCESSED_DIR="/user/maria_dev/seoul_bike/processed"
HDFS_PROCESSED_FILE="${HDFS_PROCESSED_DIR}/seoul_bike_2017_utf8.csv"

echo "  서울시 따릉이 데이터 전처리 및 HDFS 적재 시작"


# 1. 권한 및 디렉토리 준비
sudo chown -R maria_dev "${LOCAL_BASE_DIR}"
chmod -R u+rwX "${LOCAL_BASE_DIR}"
mkdir -p "${PROCESSED_DIR}"

# 2. 인코딩 변환 (CP949 -> UTF-8)
echo "로컬 파일 인코딩 변환 중"
iconv -f CP949 -t UTF-8 -c "${RAW_FILE}" > "${PROCESSED_FILE}"

# 3. 데이터 검증 (BOM 및 한글 깨짐 확인 내용을 로그처럼 출력)
echo "------------------------------------------"
echo "변환된 파일 상위 3줄 출력"
head -n 3 "${PROCESSED_FILE}"
echo ""
echo "변환된 파일 BOM(Byte Order Mark) 확인"
head -c 3 "${PROCESSED_FILE}" | xxd
echo "------------------------------------------"

# 4. HDFS 적재
echo "HDFS 구버전 데이터 삭제 및 신규 데이터 업로드 중"
hdfs dfs -mkdir -p "${HDFS_PROCESSED_DIR}"
hdfs dfs -rm -f "${HDFS_PROCESSED_FILE}"
hdfs dfs -put "${PROCESSED_FILE}" "${HDFS_PROCESSED_DIR}/"

# 5. 최종 결과 확인
echo "HDFS 적재 완료 상태 확인"
hdfs dfs -ls -h "${HDFS_PROCESSED_FILE}"


echo "자동화 스크립트 성공"
