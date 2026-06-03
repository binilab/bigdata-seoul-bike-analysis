#!/usr/bin/env bash
# Bash 스크립트로 실행할 파일임을 표시

set -e
# 중간에 에러가 발생하면 즉시 스크립트 중단

export LANG=en_US.UTF-8
# 실행 환경의 기본 문자 인코딩을 UTF-8로 설정

export LC_ALL=en_US.UTF-8
# 전체 locale 범주를 UTF-8로 설정

LOCAL_BASE_DIR="/home/maria_dev/seoul_bike"
# HDP 컨테이너 내부 따릉이 데이터 기본 경로

RAW_DIR="${LOCAL_BASE_DIR}/raw"
# CP949 원본 CSV들이 들어 있는 로컬 raw 폴더

PROCESSED_DIR="${LOCAL_BASE_DIR}/processed"
# UTF-8 변환본을 저장할 로컬 processed 폴더

HDFS_PROCESSED_DIR="/user/maria_dev/seoul_bike/processed"
# UTF-8 변환본을 저장할 HDFS processed 폴더

echo "서울시 따릉이 데이터 전처리 및 HDFS 적재 시작"
echo "로컬 raw 경로: ${RAW_DIR}"
# 원본 CSV 경로 출력

echo "로컬 processed 경로: ${PROCESSED_DIR}"
# 변환본 저장 경로 출력

echo "HDFS processed 경로: ${HDFS_PROCESSED_DIR}"
# HDFS processed 저장 경로 출력

echo "------------------------------------------"

echo "[1] 권한 및 디렉토리 준비"
# 1단계 작업 로그 출력

sudo chown -R maria_dev "${LOCAL_BASE_DIR}"
# docker cp 과정에서 바뀐 파일 소유자를 maria_dev로 변경

chmod -R u+rwX "${LOCAL_BASE_DIR}"
# maria_dev 계정에 읽기/쓰기 권한 부여

rm -rf "${PROCESSED_DIR}"



mkdir -p "${PROCESSED_DIR}"

ls -lh "${RAW_DIR}"/seoul_bike_2017_*.csv


echo "------------------------------------------"


echo "[2] 월별 CSV 인코딩 변환"


for raw_file in "${RAW_DIR}"/seoul_bike_2017_*.csv; do
    raw_name=$(basename "${raw_file}" .csv)
    processed_file="${PROCESSED_DIR}/${raw_name}_utf8.csv"
    echo "변환 파일: ${raw_name}.csv"
    # 현재 변환 중인 파일 출력

    iconv -f CP949 -t UTF-8 -c "${raw_file}" > "${processed_file}"


    ls -lh "${processed_file}"
    # 변환된 파일 용량 확인
done
# 월별 CSV 변환 반복 종료

echo "------------------------------------------"
# 로그 구분선 출력

echo "[3] 변환 데이터 검증"
# 3단계 작업 로그 출력

first_processed_file=$(ls "${PROCESSED_DIR}"/seoul_bike_2017_*_utf8.csv | head -n 1)
# 변환된 파일 중 첫 번째 파일을 검증용으로 선택

echo "검증 파일: ${first_processed_file}"
# 검증 대상 파일 경로 출력

echo "상위 3줄:"
# 파일 미리보기 제목 출력

head -n 3 "${first_processed_file}"

echo ""


echo "BOM 확인:"


head -c 3 "${first_processed_file}" | xxd

echo "------------------------------------------"
# 로그 구분선 출력

echo "[4] HDFS processed 재적재"
# 4단계 작업 로그 출력

hdfs dfs -rm -r -f "${HDFS_PROCESSED_DIR}"
# 기존 HDFS processed 폴더 삭제


hdfs dfs -mkdir -p "${HDFS_PROCESSED_DIR}"
# HDFS processed 폴더 새로 생성

for processed_file in "${PROCESSED_DIR}"/seoul_bike_2017_*_utf8.csv; do
    # 로컬 processed 폴더의 UTF-8 CSV를 하나씩 처리

    file_name=$(basename "${processed_file}")
    # 파일명만 추출

    echo "HDFS 업로드 파일: ${file_name}"
    # 현재 HDFS 업로드 중인 파일명 출력

    hdfs dfs -put "${processed_file}" "${HDFS_PROCESSED_DIR}/"
    # UTF-8 변환본을 HDFS processed 경로에 업로드
done
# HDFS 업로드 반복 종료

echo "------------------------------------------"
# 로그 구분선 출력

echo "[5] HDFS processed 적재 결과"
# 5단계 작업 로그 출력

hdfs dfs -ls -h "${HDFS_PROCESSED_DIR}"
# HDFS processed 폴더의 파일 목록과 용량 확인

hdfs dfs -du -h "${HDFS_PROCESSED_DIR}"
# HDFS processed 폴더의 전체 용량 확인

echo "자동화 스크립트 성공"
# 전체 스크립트 완료 로그 출력
