# Seoul Bike Rental Pattern Analysis

서울시 공공자전거 따릉이 대여이력 데이터를 이용해 Hadoop 기반 데이터 처리 파이프라인을 구축하고, 2017년 1년치 이용 패턴을 분석한 빅데이터 프로그래밍 기말 프로젝트이다.

## 1. Project Overview

이 프로젝트는 최신 실시간 수요 예측보다는, 공개된 2017년 1년치 서울시 공공자전거 따릉이 대여이력 데이터를 이용해 Hadoop 기반 데이터 처리 파이프라인을 구축하고 이용 패턴을 분석하는 데 초점을 둔다.

따릉이 수요는 계절, 시간대, 대여소 위치에 따라 달라질 수 있다. 따라서 월별 이용량, 시간대별 대여량, 대여소별 이용량 Top 10, 이용시간 및 이동거리 분포를 분석하여 수요가 집중되는 시기와 장소를 확인한다.

최신 연도 데이터는 파일 규모가 크기 때문에, 본 프로젝트에서는 먼저 2017년 1월~12월 데이터를 기준 데이터셋으로 사용해 전체 파이프라인을 검증하였다. 동일한 파이프라인에 최신 연도 데이터를 적용하면 최근 이용 패턴 분석으로 확장할 수 있다.

분석 질문은 다음과 같다.

1. 월별 따릉이 이용량은 어떻게 변화하는가?
2. 시간대별 따릉이 대여량은 언제 가장 많은가?
3. 대여소별 이용량 Top 10은 어디인가?
4. 이용시간과 이동거리는 어떤 분포를 보이는가?

## 2. Data

- 데이터 출처: 서울 열린데이터광장
- 데이터명: 서울특별시 공공자전거 대여이력 정보
- 분석 기간: 2017년 1월 ~ 2017년 12월
- 원본 파일 형식: CSV
- 원본 인코딩: CP949
- 처리 후 인코딩: UTF-8
- 분석 대상 행 수: 5,030,577건

대용량 원본 데이터는 GitHub에 업로드하지 않고, `data/raw/`는 `.gitignore`로 제외하였다.  
필요한 경우 `data/sample/`에 샘플 데이터만 저장한다.

## 3. System Architecture

데이터 처리 흐름은 다음과 같다.

1. 서울 열린데이터광장 CSV 다운로드
2. Mac 로컬에서 월별 파일 정리
3. HDP Sandbox 로컬 디렉토리로 전송
4. HDFS raw 경로에 원본 CSV 적재
5. CP949 인코딩을 UTF-8로 변환
6. HDFS processed 경로에 변환 CSV 적재
7. Hive External Table 생성
8. Spark DataFrame으로 집계 분석
9. HDFS results 경로에 분석 결과 저장
10. Mac 로컬로 결과 CSV 복사
11. Matplotlib으로 시각화

주요 HDFS 경로는 다음과 같다.

- raw 데이터: `/user/maria_dev/seoul_bike/raw`
- processed 데이터: `/user/maria_dev/seoul_bike/processed`
- 분석 결과: `/user/maria_dev/seoul_bike/results/csv`

## 4. Tech Stack

| 구분 | 사용 기술 | 역할 |
|---|---|---|
| 데이터 수집/정리 | Bash, Python | 공개 데이터 다운로드 및 파일 정리 |
| 저장 | HDFS | raw, processed, result 데이터 저장 |
| 데이터 관리 | Hive | HDFS CSV에 테이블 구조 부여 |
| 분석 | Spark DataFrame | 월별, 시간대별, 대여소별, 분포 집계 |
| 보조 처리 | Pig | Hadoop 기반 보조 집계 |
| 시각화 | Python, Pandas, Matplotlib | Spark 결과 CSV 시각화 |
| 버전 관리 | Git, GitHub | 코드 및 결과 관리 |

## 5. Repository Structure

- `README.md`: 프로젝트 개요, 실행 방법, 결과 요약
- `data/README.md`: 데이터 출처와 관리 방식 설명
- `data/sample/`: 샘플 데이터
- `src/ingest/`: 데이터 적재 관련 스크립트
- `src/pipeline/`: Hive, Spark, Pig 처리 코드
- `src/analyze/`: EDA 노트북과 시각화 코드
- `results/csv/`: Spark 분석 결과 CSV
- `results/figures/`: 시각화 결과 이미지

## 6. How to Run

### 6.1 HDP Sandbox 접속

GCP VM에서 HDP Sandbox 컨테이너로 접속한다.

- 명령어: `ssh maria_dev@localhost -p 2222`
- 비밀번호: `maria_dev`

### 6.2 HDFS raw 데이터 적재

HDP Sandbox 안에서 실행한다.

- 실행 파일: `/home/maria_dev/upload_to_hdfs.sh`
- 실행 명령어: `bash /home/maria_dev/upload_to_hdfs.sh`

확인 명령어:

- `hdfs dfs -ls -h /user/maria_dev/seoul_bike/raw`
- `hdfs dfs -du -h /user/maria_dev/seoul_bike/raw`

### 6.3 인코딩 변환 및 processed 데이터 적재

원본 CSV는 CP949 인코딩이므로 UTF-8로 변환한 뒤 HDFS processed 경로에 적재한다.

- 실행 파일: `/home/maria_dev/convert_encoding.sh`
- 실행 명령어: `bash /home/maria_dev/convert_encoding.sh`

확인 명령어:

- `hdfs dfs -ls -h /user/maria_dev/seoul_bike/processed`
- `hdfs dfs -du -h /user/maria_dev/seoul_bike/processed`

### 6.4 Hive External Table 생성

Hive에서는 HDFS processed 경로의 CSV 파일을 External Table로 연결한다.

- SQL 파일: `src/pipeline/create_hive_table.sql`
- HDP 실행 위치 예시: `/home/maria_dev/create_hive_table.sql`

실행 명령어:

- `sudo -u hive beeline -u jdbc:hive2://localhost:10000/default -n hive -f /home/maria_dev/create_hive_table.sql`

확인 쿼리:

- `SELECT COUNT(*) FROM rental_2017_raw;`

### 6.5 Spark 분석 실행

Spark 분석은 HDP Sandbox에서 실행한다.

- 실행 파일: `/home/maria_dev/spark_analysis.py`

실행 전 환경 변수:

- `unset LC_ALL`
- `export LANG=en_US.UTF-8`
- `export PYSPARK_PYTHON=/bin/python3.6`

실행 명령어:

- `spark-submit --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 /home/maria_dev/spark_analysis.py`

분석 결과는 HDFS의 `/user/maria_dev/seoul_bike/results/csv` 경로에 저장된다.

### 6.6 시각화 실행

Spark 결과 CSV를 Mac 로컬의 `results/csv/`로 복사한 뒤 실행한다.

- 실행 파일: `src/analyze/visualize.py`
- 실행 명령어: `python3 src/analyze/visualize.py`

생성되는 시각화 파일:

- `results/figures/monthly_usage.png`
- `results/figures/hourly_usage.png`
- `results/figures/station_top10.png`
- `results/figures/duration_distribution.png`
- `results/figures/distance_distribution.png`

## 7. Analysis Results

### 7.1 Monthly Usage

2017년 월별 이용량은 겨울철에 낮고, 봄 이후 증가하다가 9월에 가장 높게 나타났다.

- 2017년 1월: 84,148건
- 2017년 9월: 889,888건
- 2017년 10월: 863,113건

### 7.2 Hourly Usage

시간대별로는 18시 이용량이 가장 높았다.  
8시에도 이용량이 증가하여 출근 시간대 수요도 확인되었다.

- 18시: 503,936건
- 19시: 387,540건
- 17시: 343,836건

### 7.3 Top 10 Rental Stations

대여소별 이용량은 여의나루역 1번출구 앞이 가장 높게 나타났다.  
상위 대여소에는 한강공원 접근 지점, 지하철역 주변, 유동인구가 많은 지역이 포함되었다.

### 7.4 Duration and Distance

이용시간은 10~20분 구간과 30~60분 구간이 많았고, 이동거리는 2~5km 구간이 가장 많았다.

- 전체 분석 행 수: 5,030,577건
- 평균 이용시간: 약 28.59분
- 평균 이동거리: 약 3.62km

## 8. Outputs

분석 결과 CSV:

- `results/csv/monthly_usage.csv`
- `results/csv/hourly_usage.csv`
- `results/csv/station_top10.csv`
- `results/csv/usage_summary.csv`
- `results/csv/duration_distribution.csv`
- `results/csv/distance_distribution.csv`

시각화 결과:

- `results/figures/monthly_usage.png`
- `results/figures/hourly_usage.png`
- `results/figures/station_top10.png`
- `results/figures/duration_distribution.png`
- `results/figures/distance_distribution.png`

## 9. Limitations

- 본 분석은 2017년 데이터만 사용했기 때문에 현재 따릉이 이용 현황을 직접 설명하지는 못한다.
- 최신 연도 데이터는 파일 규모가 더 크기 때문에, 이번 프로젝트에서는 먼저 2017년 1년치 데이터로 파이프라인을 구축하고 검증하였다.
- 향후 동일한 수집, HDFS 적재, 인코딩 변환, Hive 테이블 생성, Spark 분석 파이프라인에 최신 연도 데이터를 적용하면 최근 이용 패턴과 연도별 변화를 비교할 수 있다.
- 날씨, 공휴일, 지하철역 위치 등 외부 변수를 결합하지 않아 이용량 변화의 원인을 완전히 설명하기는 어렵다.
- 이용시간과 이동거리에는 일부 이상치가 포함되어 있으며, 추가적인 이상치 처리 기준을 적용하면 더 안정적인 분석이 가능하다.

## 10. AI Tool Usage

- ChatGPT: HDP Sandbox 실행 과정에서 발생한 인코딩/권한 오류 디버깅 보조
- ChatGPT: Spark 집계 흐름 점검 및 시각화 구성 아이디어 참고
- 최종 코드와 결과 해석은 프로젝트 데이터와 실행 결과를 기준으로 직접 확인함

## 11. References

- 서울 열린데이터광장, 서울특별시 공공자전거 대여이력 정보
- Apache Hadoop Documentation
- Apache Hive Documentation
- Apache Spark Documentation
- Apache Pig Documentation
- Matplotlib Documentation
