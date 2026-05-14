# 서울시 공공자전거 따릉이 이용 패턴 빅데이터 분석

## 1. 문제 정의

서울시 공공자전거 따릉이는 출퇴근, 등하교, 단거리 이동 등 일상적인 이동 수단으로 많이 사용된다.  
하지만 특정 시간대나 특정 대여소에서는 자전거가 부족하거나, 반대로 자전거가 몰리는 현상이 발생할 수 있다.

본 프로젝트에서는 서울시 공공자전거 따릉이 대여이력 데이터를 활용하여 따릉이 이용 패턴을 분석하고자 한다.  
특히 월별 이용량, 시간대별 대여량, 대여소별 이용량, 이용 시간과 이동 거리 분포를 확인하여 따릉이가 언제, 어디서, 어떤 방식으로 많이 사용되는지 파악하는 것이 목표이다.

사용할 데이터는 서울 열린데이터광장에서 제공하는 따릉이 대여이력 데이터이다.  
프로젝트 요구사항에 맞추어 누적 100MB 이상의 공개 데이터를 수집할 예정이며, 대용량 원본 데이터는 GitHub에 업로드하지 않고 샘플 데이터만 업로드할 계획이다.

주요 분석 질문은 다음과 같다.

1. 월별 따릉이 이용량은 어떻게 변화하는가?
2. 시간대별 따릉이 대여량은 언제 가장 많은가?
3. 대여소별 이용량 Top 10은 어디인가?
4. 이용 시간과 이동 거리는 어떤 분포를 보이는가?

---

## 2. 기술 스택

본 프로젝트는 강의 실습 환경인 HDP Sandbox에서 실행 가능한 Hadoop 기반 기술 스택을 사용한다.

| 구분 | 기술 | 사용 목적 |
|---|---|---|
| 데이터 수집 | Python 또는 Bash | 서울 열린데이터광장 데이터를 재실행 가능한 방식으로 수집 |
| 데이터 저장 | HDFS | 수집한 대용량 따릉이 원본 데이터를 저장 |
| 데이터 관리 | Hive | HDFS에 저장된 CSV 데이터에 테이블 구조를 부여하고 SQL 방식으로 확인 |
| 핵심 분석 | Spark / Spark SQL | 월별, 시간대별, 대여소별 이용량 및 이용 시간·거리 분석 |
| 보조 처리 | Pig | 일부 전처리 또는 집계 결과 검증 |
| 시각화 | Matplotlib 또는 Plotly | 분석 결과를 그래프로 표현 |
| 버전 관리 | Git / GitHub | 코드, README, 샘플 데이터, 결과물 관리 |

Spark와 Hive를 중심으로 배치 분석 파이프라인을 구성하고, Pig는 강의에서 배운 데이터 처리 흐름을 실제 데이터에 적용하는 보조 도구로 사용할 예정이다.

실시간 데이터 처리가 핵심인 주제는 아니므로 Kafka나 Flink보다는, 월별·시간대별 누적 데이터를 안정적으로 처리할 수 있는 배치 분석 구조가 더 적합하다고 판단했다.

---

## 3. 구현 계획

전체 파이프라인은 다음과 같이 구성할 계획이다.

서울 열린데이터광장  
→ Python 또는 Bash 수집 스크립트  
→ Local raw CSV 저장  
→ HDFS 적재  
→ Hive 테이블 생성 및 데이터 구조 확인  
→ Spark / Spark SQL 기반 핵심 분석  
→ Pig를 활용한 보조 집계 또는 검증  
→ 분석 결과 CSV 저장  
→ Matplotlib 또는 Plotly 시각화  
→ README 및 최종 보고서 정리

세부 구현 계획은 다음과 같다.

1. 서울 열린데이터광장에서 따릉이 대여이력 데이터를 수집한다.
2. 수집 과정을 Python 또는 Bash 스크립트로 작성하여 재실행 가능하게 만든다.
3. 수집한 CSV 데이터를 HDP Sandbox 환경의 HDFS에 저장한다.
4. Hive에서 따릉이 데이터 테이블을 생성하고 데이터 구조를 확인한다.
5. Spark 또는 Spark SQL을 사용하여 월별, 시간대별, 대여소별 이용량을 분석한다.
6. 이용 시간과 이동 거리의 평균 및 분포를 분석한다.
7. Pig를 사용하여 일부 집계 결과를 보조적으로 생성하거나 검증한다.
8. 분석 결과를 CSV와 그래프로 저장하고, 최종 보고서에 정리한다.

---

## 4. 데이터 관리 계획

대용량 원본 데이터는 GitHub에 업로드하지 않는다.  
GitHub에는 프로젝트 코드, README, 샘플 데이터만 업로드한다.

예상 데이터 관리 방식은 다음과 같다.

- data/
  - README.md
  - sample/
    - seoul_bike_sample.csv

전체 원본 데이터는 로컬 환경 또는 HDP Sandbox 내부에 저장하고, 실제 분석에는 HDFS 경로를 사용한다.

예상 HDFS 경로는 다음과 같다.

- /user/maria_dev/seoul_bike/raw/

---

## 5. 실행 환경

본 프로젝트는 강의 실습 환경인 HDP Sandbox에서 실행할 예정이다.

- Local machine: MacBook
- Editor: VS Code
- Big Data environment: HDP Sandbox
- Hadoop user: maria_dev
- HDFS raw data path: /user/maria_dev/seoul_bike/raw/
- Main tools: HDFS, Hive, Spark, Pig

---

## 6. 예상 Repository 구조

- README.md
- data/
  - README.md
  - sample/
    - seoul_bike_sample.csv
- src/
  - ingest/
    - download_data.py
  - pipeline/
    - create_hive_table.sql
    - spark_analysis.py
    - bike_summary.pig
  - analyze/
    - visualize.py
- results/
  - csv/
  - figures/
- infra/
- .gitignore

현재 1단계 제출에서는 README.md를 중심으로 작성하고, 이후 데이터 수집 및 분석 코드가 구현되면 위 구조에 맞게 파일을 추가할 예정이다.

---

## 7. 현재 단계

현재 단계는 프로젝트 수행을 위한 GitHub repository 생성 및 README.md 작성 단계이다.

아직 실제 데이터 수집, HDFS 적재, Hive 테이블 생성, Spark 분석, Pig 분석은 수행하지 않았다.  
이번 README에서는 앞으로 어떤 문제를 풀고, 어떤 데이터를 사용하며, 어떤 기술 스택과 파이프라인으로 구현할 것인지 정리한다.

---

## 8. AI Tool Usage

- ChatGPT 활용 범위: 본 프로젝트의 기획, README 구조 개선 및 문구 교정 과정에서 ChatGPT를 활용하였습니다.