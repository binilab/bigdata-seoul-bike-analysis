# Data

## 1. 데이터 출처

본 프로젝트는 서울 열린데이터광장에서 제공하는 **서울시 공공자전거 따릉이 대여이력 정보**를 사용한다.

- 데이터명: 서울시 공공자전거 따릉이 대여이력 정보
- 제공처: 서울 열린데이터광장
- 주요 내용: 년도별, 대여소별, 자전거별 대여이력 원천 데이터
- 활용 목적: 월별 이용량, 시간대별 이용량, 대여소별 이용량, 이용 시간 및 이동 거리 분포 분석

## 2. 데이터 관리 방식

대용량 원본 데이터는 GitHub에 업로드하지 않는다.

원본 CSV 파일은 로컬 환경 또는 HDP Sandbox 내부에 저장한 뒤, HDFS에 적재하여 분석한다.

예상 HDFS 경로는 다음과 같다.

- HDFS raw data path: `/user/maria_dev/seoul_bike/raw/`

## 3. GitHub 업로드 범위

GitHub에는 다음 파일만 업로드한다.

- `data/README.md`
- `data/sample/seoul_bike_sample.csv`

단, `data/sample/seoul_bike_sample.csv`는 원본 데이터 중 100~1000줄 정도만 추출한 샘플 파일로 사용한다.

## 4. GitHub에 업로드하지 않는 파일

다음 파일은 `.gitignore`를 통해 GitHub 업로드 대상에서 제외한다.

- `data/raw/`
- `*.zip`
- `*.csv.gz`
- `*.tar.gz`

## 5. 데이터 수집 계획

데이터 수집은 `src/ingest/download_data.py` 또는 Bash 스크립트로 재실행 가능하게 작성할 예정이다.

수집한 데이터는 누적 100MB 이상을 확보하고, 이후 HDFS에 저장하여 Hive와 Spark 분석에 사용한다.