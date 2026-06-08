# Analyze

이 폴더는 따릉이 데이터 분석 흐름을 확인하기 위한 탐색용 노트북을 저장한다.

## 파일 설명

- `seoul_bike_eda.ipynb`
  - Spark DataFrame으로 데이터 구조를 확인하고, 월별/시간대별/대여소별 집계 방향을 탐색한 노트북
  - 최종 실행용 코드는 `src/pipeline/spark_analysis.py`에 정리함
- `visualize.py`
  - 2017년 Spark 결과 CSV를 읽어 기본 시각화 파일을 생성하는 스크립트
- `summarize_2025_results.py`
  - 2025년 월별 분할 실행 결과를 결합하고, 2017년 결과와 비교 가능한 CSV 및 그래프를 생성하는 스크립트
  - 공유 PM 확산 환경 속 따릉이의 역할을 해석하기 위한 출퇴근 시간대 비중 변화, 평균 이용시간/거리 변화, 계절별 증가율 지표도 함께 생성

## 실행 환경

이 노트북은 Mac 로컬 Python 커널이 아니라, HDP Sandbox의 PySpark 환경에서 실행하는 것을 기준으로 작성하였다.

입력 데이터 경로는 다음 HDFS 경로를 사용한다.

- `hdfs:///user/maria_dev/seoul_bike/processed/seoul_bike_2017_utf8.csv`

따라서 Mac 로컬 Jupyter Notebook에서 바로 실행하면 HDFS 경로를 읽지 못할 수 있다.

## 역할 구분

- `seoul_bike_eda.ipynb`: 분석 과정 확인용
- `src/pipeline/spark_analysis.py`: 최종 재현용 Spark 실행 스크립트

최종 결과 CSV는 `spark_analysis.py`를 `spark-submit`으로 실행하여 생성한다.

## 2025년 결과 결합

2025년 데이터는 HDP Sandbox 자원 한계로 전체 12개월을 한 번에 집계하지 않고 월별 파일 단위로 분할 실행하였다. Mac 로컬로 복사한 월별 결과는 `results/csv/2025_summary_text/`에 저장한 뒤 다음 명령어로 결합한다. 결합된 2025년 결과는 최종 분석 해석에 사용한다.

- `python3 src/analyze/summarize_2025_results.py`

생성되는 주요 파일은 다음과 같다.

- `results/csv/2025_monthly_usage.csv`
- `results/csv/2025_hourly_usage.csv`
- `results/csv/2025_usage_summary_by_month.csv`
- `results/csv/2025_usage_summary_total.csv`
- `results/csv/2017_2025_monthly_comparison.csv`
- `results/csv/2017_2025_hourly_share_comparison.csv`
- `results/csv/2017_2025_role_comparison.csv`
- `results/csv/2025_season_usage.csv`
- `results/csv/2017_2025_season_growth.csv`
- `results/csv/2025_interpretation_metrics.csv`
- `results/figures/2017_2025_monthly_usage_compare.png`
- `results/figures/2017_2025_hourly_share_compare.png`

`2025_interpretation_metrics.csv`는 최종 해석을 위한 보조 지표이다. 이 파일에는 2017년 대비 2025년 전체 대여 증가 배수, 출퇴근 시간대 비중 변화, 평균 이용시간 변화, 평균 이동거리 변화, 겨울철 증가율 등이 저장된다. 이를 통해 따릉이가 공유 PM 확산 속에서도 생활형 단거리 교통수단으로 성장했는지 해석한다.
