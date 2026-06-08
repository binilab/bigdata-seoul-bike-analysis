# Data

## 1. 데이터 출처

본 프로젝트는 서울 열린데이터광장에서 제공하는 **서울시 공공자전거 따릉이 대여이력 정보**를 사용한다.

- 데이터명: 서울시 공공자전거 따릉이 대여이력 정보
- 제공처: 서울 열린데이터광장
- 데이터 URL: https://data.seoul.go.kr/dataList/datasetView.do?infId=OA-15182&serviceKind=1&srvType=A
- 주요 내용: 년도별, 대여소별, 자전거별 대여이력 원천 데이터
- 활용 목적: 월별 이용량, 시간대별 이용량, 대여소별 이용량, 이용 시간 및 이동 거리 분포 분석

공유 전동킥보드와 공유 전기자전거 같은 개인형 이동수단(PM) 확산은 최종 해석의 배경으로만 활용한다. 이번 핵심 분석에는 따릉이 대여이력 데이터를 사용하며, 공유 전동킥보드 실제 대여이력은 결합하지 않았다.

향후 확장에 사용할 수 있는 관련 공개 데이터는 다음과 같다.

- 서울시 공유 전동킥보드 운영 현황: https://data.seoul.go.kr/dataList/OA-22199/F/1/datasetView.do
- 서울시 전동킥보드 견인 현황: https://data.seoul.go.kr/dataList/OA-21304/S/1/datasetView.do?tab=A
- 서울시 전동킥보드 주차구역현황: https://data.seoul.go.kr/dataList/OA-21710/S/1/datasetView.do?tab=A

## 2. 데이터 관리 방식

대용량 원본 데이터는 GitHub에 업로드하지 않는다.

원본 CSV 파일은 로컬 환경 또는 HDP Sandbox 내부에 저장한 뒤, HDFS에 적재하여 분석한다.

주요 HDFS 경로는 다음과 같다.

- 2017 검증용 HDFS raw data path: `/user/maria_dev/seoul_bike/raw/`
- 2017 검증용 HDFS processed data path: `/user/maria_dev/seoul_bike/processed/`
- 2017 검증용 HDFS result data path: `/user/maria_dev/seoul_bike/results/csv/`
- 2025 분석용 HDFS path: `/user/maria_dev/seoul_bike_2025/`

## 3. GitHub 업로드 범위

GitHub에는 다음 파일만 업로드한다.

- `data/README.md`
- `data/sample/seoul_bike_sample.csv`

단, `data/sample/seoul_bike_sample.csv`는 원본 데이터 중 1000줄 이하만 추출한 샘플 파일로 사용한다.

## 4. GitHub에 업로드하지 않는 파일

다음 파일은 `.gitignore`를 통해 GitHub 업로드 대상에서 제외한다.

- `data/raw/`
- `*.zip`
- `*.csv.gz`
- `*.tar.gz`

## 5. 데이터 수집 및 적재 방식

원본 데이터는 서울 열린데이터광장에서 2017년 및 2025년 대여이력 CSV 파일을 내려받은 뒤, 1월부터 12월까지 월별 분석이 가능하도록 정리하였다. 2017년 데이터는 전체 파이프라인 검증용으로 사용하고, 2025년 데이터는 최종 분석용으로 사용한다.

HDP Sandbox 내부에서는 `src/ingest/upload_to_hdfs.sh`를 사용하여 원본 CSV를 HDFS raw 경로에 적재한다. 이후 `src/pipeline/convert_encoding.sh`를 사용하여 CP949 인코딩을 UTF-8로 변환하고, 변환된 CSV를 HDFS processed 경로에 다시 적재한다.

샘플 데이터는 `src/ingest/create_sample.py`로 원본 CSV에서 일부 행만 추출하여 생성한다. 전체 원본 데이터는 누적 100MB 이상이며, GitHub에는 대용량 원본 대신 샘플 데이터와 분석 결과만 저장한다.

최신 연도 데이터는 공식 파일명이 연도/월 suffix 형태로 제공될 수 있으므로, `src/ingest/prepare_year_files.py`로 `seoul_bike_YYYY_MM.csv` 형식에 맞춘 뒤 같은 파이프라인에 투입한다. 2025년 데이터는 `data/raw/2025/normalized/seoul_bike_2025_01.csv`부터 `seoul_bike_2025_12.csv`까지 정리한 뒤 사용하였다.

최신 연도 데이터는 대용량 원본이므로 2017년 원본과 마찬가지로 GitHub에 업로드하지 않는다.
