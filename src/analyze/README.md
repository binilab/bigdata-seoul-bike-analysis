# Analyze

이 폴더는 따릉이 데이터 분석 흐름을 확인하기 위한 탐색용 노트북을 저장한다.

## 파일 설명

- `seoul_bike_eda.ipynb`
  - Spark DataFrame으로 데이터 구조를 확인하고, 월별/시간대별/대여소별 집계 방향을 탐색한 노트북
  - 최종 실행용 코드는 `src/pipeline/spark_analysis.py`에 정리함

## 실행 환경

이 노트북은 Mac 로컬 Python 커널이 아니라, HDP Sandbox의 PySpark 환경에서 실행하는 것을 기준으로 작성하였다.

입력 데이터 경로는 다음 HDFS 경로를 사용한다.

- `hdfs:///user/maria_dev/seoul_bike/processed/seoul_bike_2017_utf8.csv`

따라서 Mac 로컬 Jupyter Notebook에서 바로 실행하면 HDFS 경로를 읽지 못할 수 있다.

## 역할 구분

- `seoul_bike_eda.ipynb`: 분석 과정 확인용
- `src/pipeline/spark_analysis.py`: 최종 재현용 Spark 실행 스크립트

최종 결과 CSV는 `spark_analysis.py`를 `spark-submit`으로 실행하여 생성한다.
