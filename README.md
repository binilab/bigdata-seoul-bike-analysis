# Seoul Bike Rental Pattern Analysis

서울시 공공자전거 따릉이 대여이력 데이터를 이용해 Hadoop 기반 데이터 처리 파이프라인을 구축하고, 2025년 최신 이용 패턴을 분석한 빅데이터 프로그래밍 기말 프로젝트이다. 최종 해석은 공유 전동킥보드와 전기자전거 같은 개인형 이동수단(PM)이 확산되는 환경 속에서도 따릉이가 생활형 단거리 교통수단으로 성장했는지를 확인하는 데 초점을 둔다.

## 1. Project Overview

이 프로젝트는 최신 실시간 수요 예측보다는, 서울시 공공자전거 따릉이 대여이력 데이터를 이용해 Hadoop 기반 데이터 처리 파이프라인을 구축하고 최신 이용 패턴을 분석하는 데 초점을 둔다.

따릉이 수요는 계절, 시간대, 대여소 위치에 따라 달라질 수 있다. 최근에는 공유 전동킥보드와 공유 전기자전거 같은 개인형 이동수단도 함께 확산되고 있어, 따릉이가 이런 환경 속에서 대체되고 있는지 혹은 공공 단거리 교통수단으로 계속 성장하고 있는지 확인할 필요가 있다. 따라서 월별 이용량, 시간대별 대여 비중, 이용시간 및 이동거리 요약을 2017년과 2025년 비교 관점에서 분석하여 따릉이의 현재 역할을 해석한다.

먼저 2017년 1월~12월 데이터를 기준 데이터셋으로 사용해 HDFS 적재, Hive 테이블 생성, Spark 분석, 시각화까지 전체 파이프라인을 검증하였다. 이후 같은 파이프라인을 2025년 1월~12월 최신 데이터에 확장 적용하였다. 2025년 데이터는 37,372,654건으로 규모가 커서, HDP Sandbox 환경에서는 월별 파일 단위로 분할 실행한 뒤 결과를 결합하였다.

분석 질문은 다음과 같다.

1. 2017년과 비교했을 때 2025년 따릉이 전체 이용량은 감소했는가, 증가했는가?
2. 월별 이용량과 비성수기 이용량은 2017년 대비 어떻게 달라졌는가?
3. 시간대별 이용 비중은 2017년과 비교했을 때 생활 이동 성격을 유지하거나 강화했는가?
4. 평균 이용시간과 평균 이동거리는 2017년 대비 어떻게 변화했는가?
5. 공유 PM 확산 환경 속에서도 따릉이는 생활형 단거리 교통수단으로 성장했다고 볼 수 있는가?

## 2. Data

- 데이터 출처: 서울 열린데이터광장
- 데이터명: 서울특별시 공공자전거 대여이력 정보
- 분석 기간: 2017년 1월 ~ 12월, 2025년 1월 ~ 12월
- 원본 파일 형식: CSV
- 원본 인코딩: CP949
- 처리 후 인코딩: UTF-8
- 2017년 분석 행 수: 5,030,577건
- 2025년 분석 행 수: 37,372,654건

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
| 시각화 | Python, Pandas, Matplotlib | Spark 결과 CSV 시각화 |
| 버전 관리 | Git, GitHub | 코드 및 결과 관리 |

## 5. Repository Structure

- `README.md`: 프로젝트 개요, 실행 방법, 결과 요약
- `data/README.md`: 데이터 출처와 관리 방식 설명
- `data/sample/`: 샘플 데이터
- `src/ingest/`: 데이터 적재 관련 스크립트
  - `prepare_year_files.py`: 공식 월별 CSV 파일명을 파이프라인 규칙에 맞게 정리
  - `validate_year_data.py`: 연도별 CSV 헤더와 샘플 행 스키마 점검
- `src/pipeline/`: Hive, Spark 처리 코드
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

2025년 월별 분할 실행 결과를 결합하려면 다음 스크립트를 실행한다.

- 실행 파일: `src/analyze/summarize_2025_results.py`
- 실행 명령어: `python3 src/analyze/summarize_2025_results.py`

### 6.7 2025년 최신 데이터 분석

2017년 데이터로 전체 파이프라인을 검증한 뒤, 2025년 최신 데이터는 같은 컬럼 구조를 유지하므로 기존 파이프라인에 `YEAR` 환경 변수를 지정하여 별도 HDFS 경로에서 처리한다.

예를 들어 2025년 데이터를 사용할 경우, Mac 로컬에서 공식 월별 CSV 파일명을 먼저 정리한다.

- 원본 위치 예시: `data/raw/2025/extracted/`
- 정리 명령어: `python3 src/ingest/prepare_year_files.py --year 2025 --source-dir data/raw/2025/extracted --output-dir data/raw/2025/normalized --link-mode hardlink --overwrite`
- 스키마 점검 명령어: `python3 src/ingest/validate_year_data.py --input-dir data/raw/2025/normalized --glob 'seoul_bike_2025_*.csv' --encoding cp949 --sample-rows 1000`

HDP Sandbox에서는 2025년 파일을 `/home/maria_dev/seoul_bike_2025/raw/`에 둔 뒤 아래처럼 실행한다.

- raw 적재: `YEAR=2025 bash /home/maria_dev/upload_to_hdfs.sh`
- 인코딩 변환: `YEAR=2025 bash /home/maria_dev/convert_encoding.sh`
- Hive 테이블 생성: `sudo -u hive beeline -u jdbc:hive2://localhost:10000/default -n hive -f /home/maria_dev/create_hive_table_2025.sql`
- Spark 분석: `YEAR=2025 spark-submit --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=/bin/python3.6 /home/maria_dev/spark_analysis.py`

2025년 결과는 기존 2017년 검증 결과를 덮어쓰지 않도록 `/user/maria_dev/seoul_bike_2025/results/csv` 경로에 저장된다. HDP Sandbox에서 전체 12개월을 한 번에 처리하기 어려운 경우에는 월별 파일 단위로 분할 실행하고, 로컬에서 `summarize_2025_results.py`로 결과를 결합한다.

## 7. Analysis Results

### 7.1 Monthly Usage Comparison

2025년 전체 대여 건수는 37,372,654건으로 2017년 5,030,577건보다 약 7.43배 증가하였다. 월별로도 모든 달에서 2025년 이용량이 2017년보다 높았고, 겨울철 증가율은 약 14.31배로 나타났다.

### 7.2 Hourly Usage Comparison

시간대 분석은 2025년 단독 피크를 확인하는 용도가 아니라, 2017년과 비교해 생활 이동 성격이 유지되는지 확인하는 근거로 사용하였다. 두 연도 모두 최고 이용 시간은 18시였고, 18시 대여 건수는 약 7.20배 증가하였다.

- 2017년 8시·17~19시 이용 비중: 약 30.5%
- 2025년 8시·17~19시 이용 비중: 약 32.3%
- 변화: 약 +1.8%p

### 7.3 Duration and Distance Comparison

2017년보다 2025년의 평균 이용시간과 평균 이동거리는 모두 짧아졌다.

- 평균 이용시간: 28.59분 → 20.73분, 약 -27.5%
- 평균 이동거리: 3.62km → 2.30km, 약 -36.4%

이 결과는 2025년 따릉이 이용이 단순히 증가한 것에 그치지 않고, 생활권 안에서 짧게 이동하는 성격이 더 강해졌다는 해석으로 연결된다.

### 7.4 2017 Validation and Comparison

2017년 데이터는 파이프라인 자동화와 재현성 검증용으로 사용하였다. 2017년 전체 대여 건수는 5,030,577건이었고, 2025년 전체 대여 건수는 약 7.43배 증가하였다.

- 2017년 최고 이용 월: 9월, 889,888건
- 2025년 최고 이용 월: 6월, 4,024,309건
- 2017년 최고 이용 시간: 18시, 503,936건
- 2025년 최고 이용 시간: 18시, 3,627,270건

### 7.5 Interpretation: Shared PM Context

공유 전동킥보드와 전기자전거 같은 개인형 이동수단이 확산되는 환경에서도 따릉이 이용량은 감소하지 않았다. 2025년 전체 대여 건수는 2017년보다 약 7.43배 증가하였다. 또한 출퇴근 시간대 이용 비중은 소폭 증가했고, 평균 이용시간과 이동거리는 짧아졌다.

해석 보조 지표는 다음과 같다.

- 출퇴근 시간대 이용 비중 변화: 약 +1.8%p
- 평균 이용시간 변화: 약 -27.5%
- 평균 이동거리 변화: 약 -36.4%
- 겨울철 2017년 대비 증가율: 약 14.31배

이를 통해 따릉이는 공유 PM 확산 속에서도 장거리 여가용 이동수단보다는 출퇴근, 대중교통 연계, 생활권 이동에 쓰이는 공공 단거리 교통수단으로 성장한 것으로 해석할 수 있다.

### 7.6 Conclusion

2025년 분석 결과, 따릉이 이용량은 2017년 대비 크게 증가했으며 모든 달에서 2017년보다 높은 이용량을 보였다. 시간대별로는 18시 피크가 유지되었고, 8시와 17~19시를 합친 출퇴근 시간대 비중은 2017년보다 소폭 증가하였다. 평균 이용시간과 이동거리는 줄어들어 생활형 단거리 이동 성격이 더 강해졌다고 해석할 수 있다.

따라서 본 프로젝트의 최종 결론은 다음과 같다. 따릉이는 공유 PM 확산 속에서도 이용량이 감소하지 않았고, 시간대와 이동 특성까지 고려했을 때 서울의 생활형 단거리 교통수단으로 성장하였다. 운영 측면에서는 성수기 월과 출퇴근 시간대의 자전거 재배치 및 반납 공간 관리를 강화할 필요가 있다.

## 8. Outputs

분석 결과 CSV:

- `results/csv/monthly_usage.csv`
- `results/csv/hourly_usage.csv`
- `results/csv/station_top10.csv`
- `results/csv/usage_summary.csv`
- `results/csv/duration_distribution.csv`
- `results/csv/distance_distribution.csv`
- `results/csv/2025_monthly_usage.csv`
- `results/csv/2025_hourly_usage.csv`
- `results/csv/2025_hourly_usage_by_month.csv`
- `results/csv/2025_usage_summary_by_month.csv`
- `results/csv/2025_usage_summary_total.csv`
- `results/csv/2017_2025_monthly_comparison.csv`
- `results/csv/2017_2025_hourly_share_comparison.csv`
- `results/csv/2017_2025_role_comparison.csv`
- `results/csv/2025_season_usage.csv`
- `results/csv/2017_2025_season_growth.csv`
- `results/csv/2025_interpretation_metrics.csv`

시각화 결과:

- `results/figures/monthly_usage.png`
- `results/figures/hourly_usage.png`
- `results/figures/station_top10.png`
- `results/figures/duration_distribution.png`
- `results/figures/distance_distribution.png`
- `results/figures/2025_monthly_usage.png`
- `results/figures/2025_hourly_usage.png`
- `results/figures/2017_2025_monthly_usage_compare.png`
- `results/figures/2017_2025_hourly_share_compare.png`
- `results/figures/2025_avg_duration_by_month.png`

## 9. Limitations

- 본 분석의 최종 해석은 2025년 데이터를 중심으로 한다.
- 2017년 데이터는 전체 파이프라인 자동화와 재현성 검증용으로 사용하였다.
- 2025년 데이터는 HDP Sandbox 자원 한계로 전체 12개월을 한 번에 처리하지 않고 월별 파일 단위로 분할 실행하였다.
- 2025년 월별 이용량, 시간대별 이용량, 이용시간/거리 요약은 결합하였지만, 월별 Top 10 대여소를 단순 합산하여 2025년 연간 Top 10으로 해석하지는 않았다.
- 향후 더 큰 Spark 실행 환경을 사용하면 2025년 전체 연간 대여소 Top 10, 요일별 패턴, 지역별 패턴까지 확장할 수 있다.
- 날씨, 공휴일, 지하철역 위치 등 외부 변수를 결합하지 않아 이용량 변화의 원인을 완전히 설명하기는 어렵다.
- 공유 전동킥보드나 공유 전기자전거의 실제 대여이력 데이터를 함께 분석하지 않았으므로, 공유 PM 확산이 따릉이 이용량에 미친 직접적인 인과효과를 주장하지는 않는다.
- 이용시간과 이동거리에는 일부 이상치가 포함되어 있으며, 추가적인 이상치 처리 기준을 적용하면 더 안정적인 분석이 가능하다.

## 10. References

- 서울 열린데이터광장, 서울특별시 공공자전거 대여이력 정보: https://data.seoul.go.kr/dataList/datasetView.do?infId=OA-15182&serviceKind=1&srvType=A
- 서울 열린데이터광장, 서울시 공유 전동킥보드 운영 현황: https://data.seoul.go.kr/dataList/OA-22199/F/1/datasetView.do
- 서울 열린데이터광장, 서울시 전동킥보드 견인 현황: https://data.seoul.go.kr/dataList/OA-21304/S/1/datasetView.do?tab=A
- 서울 열린데이터광장, 서울시 전동킥보드 주차구역현황: https://data.seoul.go.kr/dataList/OA-21710/S/1/datasetView.do?tab=A
- Apache Hadoop Documentation
- Apache Hive Documentation
- Apache Spark Documentation
- Matplotlib Documentation
