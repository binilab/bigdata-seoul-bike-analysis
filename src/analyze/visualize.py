# -*- coding: utf-8 -*-

from pathlib import Path
import platform

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_DIR = BASE_DIR / "results" / "csv"
FIGURE_DIR = BASE_DIR / "results" / "figures"


def set_korean_font():
    # Mac에서 한글 대여소명이 깨지지 않도록 설정
    if platform.system() == "Darwin":
        plt.rcParams["font.family"] = "AppleGothic"

    plt.rcParams["axes.unicode_minus"] = False


def save_monthly_usage():
    df = pd.read_csv(CSV_DIR / "monthly_usage.csv")

    plt.figure(figsize=(10, 5))
    plt.plot(df["month"], df["rental_count"], marker="o")
    plt.title("Monthly Seoul Bike Rentals in 2017")
    plt.xlabel("Month")
    plt.ylabel("Rental Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "monthly_usage.png", dpi=150)
    plt.close()


def save_hourly_usage():
    df = pd.read_csv(CSV_DIR / "hourly_usage.csv")

    plt.figure(figsize=(10, 5))
    plt.bar(df["hour"], df["rental_count"])
    plt.title("Hourly Seoul Bike Rentals in 2017")
    plt.xlabel("Hour")
    plt.ylabel("Rental Count")
    plt.xticks(df["hour"])
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "hourly_usage.png", dpi=150)
    plt.close()


def save_station_top10():
    df = pd.read_csv(CSV_DIR / "station_top10.csv")
    df = df.sort_values("rental_count")

    plt.figure(figsize=(12, 7))
    plt.barh(df["rent_station_name"], df["rental_count"])
    plt.title("Top 10 Rental Stations in 2017")
    plt.xlabel("Rental Count")
    plt.ylabel("Station")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "station_top10.png", dpi=150)
    plt.close()


def save_duration_distribution():
    df = pd.read_csv(CSV_DIR / "duration_distribution.csv")

    plt.figure(figsize=(10, 5))
    plt.bar(df["duration_group"], df["rental_count"])
    plt.title("Rental Duration Distribution in 2017")
    plt.xlabel("Duration Group")
    plt.ylabel("Rental Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "duration_distribution.png", dpi=150)
    plt.close()


def save_distance_distribution():
    df = pd.read_csv(CSV_DIR / "distance_distribution.csv")

    plt.figure(figsize=(10, 5))
    plt.bar(df["distance_group"], df["rental_count"])
    plt.title("Rental Distance Distribution in 2017")
    plt.xlabel("Distance Group")
    plt.ylabel("Rental Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "distance_distribution.png", dpi=150)
    plt.close()


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    set_korean_font()

    save_monthly_usage()
    save_hourly_usage()
    save_station_top10()

    # 분포 CSV는 Spark 재실행 후 생성됨
    if (CSV_DIR / "duration_distribution.csv").exists():
        save_duration_distribution()

    if (CSV_DIR / "distance_distribution.csv").exists():
        save_distance_distribution()

    print("saved_figures")
    print(FIGURE_DIR)


if __name__ == "__main__":
    main()
