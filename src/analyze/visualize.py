# -*- coding: utf-8 -*-

from pathlib import Path
import platform

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_DIR = BASE_DIR / "results" / "csv"
FIGURE_DIR = BASE_DIR / "results" / "figures"


def set_korean_font():
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

    plt.figure(figsize=(10, 6))
    plt.barh(df["rent_station_name"], df["rental_count"])
    plt.title("Top 10 Rental Stations in 2017")
    plt.xlabel("Rental Count")
    plt.ylabel("Station")
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "station_top10.png", dpi=150)
    plt.close()


def main():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    set_korean_font()

    save_monthly_usage()
    save_hourly_usage()
    save_station_top10()

    print("saved_figures")
    print(FIGURE_DIR)


if __name__ == "__main__":
    main()
