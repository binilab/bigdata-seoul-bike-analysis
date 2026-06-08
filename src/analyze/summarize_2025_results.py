# -*- coding: utf-8 -*-

from pathlib import Path
import platform

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter


BASE_DIR = Path(__file__).resolve().parents[2]
CSV_DIR = BASE_DIR / "results" / "csv"
FIGURE_DIR = BASE_DIR / "results" / "figures"
SOURCE_DIR = CSV_DIR / "2025_summary_text"

MONTHS = [f"{month:02d}" for month in range(1, 13)]
EXPECTED_2025_ROWS = 37_372_654
PRIMARY_COLOR = "#168069"
SECONDARY_COLOR = PRIMARY_COLOR
MUTED_COLOR = "#6B7780"
GRID_COLOR = "#E2E8E5"
SEASON_LABELS = {
    1: "winter",
    2: "winter",
    3: "spring",
    4: "spring",
    5: "spring",
    6: "summer",
    7: "summer",
    8: "summer",
    9: "fall",
    10: "fall",
    11: "fall",
    12: "winter",
}


def set_korean_font():
    if platform.system() == "Darwin":
        plt.rcParams["font.family"] = "AppleGothic"

    plt.rcParams["axes.unicode_minus"] = False


def read_monthly_usage():
    frames = []

    for month in MONTHS:
        path = SOURCE_DIR / f"monthly_usage_2025_{month}.csv"
        df = pd.read_csv(path)
        df["month_no"] = int(month)
        frames.append(df)

    monthly = pd.concat(frames, ignore_index=True)
    monthly = monthly[["month_no", "month", "rental_count"]]
    monthly.to_csv(CSV_DIR / "2025_monthly_usage.csv", index=False)
    return monthly


def read_hourly_usage():
    frames = []

    for month in MONTHS:
        path = SOURCE_DIR / f"hourly_usage_2025_{month}.csv"
        df = pd.read_csv(path)
        df["month_no"] = int(month)
        df["month"] = f"2025-{month}"
        frames.append(df)

    hourly_by_month = pd.concat(frames, ignore_index=True)
    hourly_by_month = hourly_by_month[["month_no", "month", "hour", "rental_count"]]
    hourly_by_month.to_csv(CSV_DIR / "2025_hourly_usage_by_month.csv", index=False)

    hourly_total = hourly_by_month.groupby("hour", as_index=False)["rental_count"].sum()
    hourly_total = hourly_total.sort_values("hour")
    hourly_total.to_csv(CSV_DIR / "2025_hourly_usage.csv", index=False)

    hourly_peak_by_month = hourly_by_month.loc[
        hourly_by_month.groupby("month_no")["rental_count"].idxmax()
    ].copy()
    hourly_peak_by_month = hourly_peak_by_month.rename(
        columns={"hour": "peak_hour", "rental_count": "peak_rental_count"}
    )
    hourly_peak_by_month.to_csv(CSV_DIR / "2025_hourly_peak_by_month.csv", index=False)

    return hourly_by_month, hourly_total, hourly_peak_by_month


def read_usage_summary():
    frames = []

    for month in MONTHS:
        path = SOURCE_DIR / f"usage_summary_2025_{month}.csv"
        df = pd.read_csv(path)
        df["month_no"] = int(month)
        df["month"] = f"2025-{month}"
        frames.append(df)

    summary = pd.concat(frames, ignore_index=True)
    summary = summary[
        [
            "month_no",
            "month",
            "row_count",
            "avg_use_min",
            "min_use_min",
            "max_use_min",
            "avg_distance_m",
            "min_distance_m",
            "max_distance_m",
        ]
    ]
    summary.to_csv(CSV_DIR / "2025_usage_summary_by_month.csv", index=False)

    total_rows = summary["row_count"].sum()
    total = pd.DataFrame(
        [
            {
                "row_count": total_rows,
                "avg_use_min": (summary["avg_use_min"] * summary["row_count"]).sum()
                / total_rows,
                "min_use_min": summary["min_use_min"].min(),
                "max_use_min": summary["max_use_min"].max(),
                "avg_distance_m": (
                    summary["avg_distance_m"] * summary["row_count"]
                ).sum()
                / total_rows,
                "min_distance_m": summary["min_distance_m"].min(),
                "max_distance_m": summary["max_distance_m"].max(),
            }
        ]
    )
    total.to_csv(CSV_DIR / "2025_usage_summary_total.csv", index=False)

    return summary, total


def compare_2017_2025(monthly_2025):
    monthly_2017 = pd.read_csv(CSV_DIR / "monthly_usage.csv")
    monthly_2017["month_no"] = pd.to_datetime(monthly_2017["month"]).dt.month
    monthly_2017 = monthly_2017.rename(
        columns={"rental_count": "rental_count_2017"}
    )[["month_no", "rental_count_2017"]]

    comparison = monthly_2025.rename(
        columns={"rental_count": "rental_count_2025"}
    )[["month_no", "month", "rental_count_2025"]]
    comparison = comparison.merge(monthly_2017, on="month_no", how="left")
    comparison["growth_multiple"] = (
        comparison["rental_count_2025"] / comparison["rental_count_2017"]
    )
    comparison = comparison[
        [
            "month_no",
            "month",
            "rental_count_2017",
            "rental_count_2025",
            "growth_multiple",
        ]
    ]
    comparison.to_csv(CSV_DIR / "2017_2025_monthly_comparison.csv", index=False)
    return comparison


def save_interpretation_metrics(monthly_2025, hourly_total, total, comparison):
    hourly_2017 = pd.read_csv(CSV_DIR / "hourly_usage.csv")
    summary_2017 = pd.read_csv(CSV_DIR / "usage_summary.csv").iloc[0]

    monthly = monthly_2025.copy()
    monthly["season"] = monthly["month_no"].map(SEASON_LABELS)
    season_order = ["spring", "summer", "fall", "winter"]

    season_usage = (
        monthly.groupby("season", as_index=False)["rental_count"]
        .sum()
        .assign(
            share_pct=lambda df: df["rental_count"]
            / monthly["rental_count"].sum()
            * 100
        )
    )
    season_usage["season"] = pd.Categorical(
        season_usage["season"], categories=season_order, ordered=True
    )
    season_usage = season_usage.sort_values("season")
    season_usage.to_csv(CSV_DIR / "2025_season_usage.csv", index=False)

    comparison_by_season = comparison.copy()
    comparison_by_season["season"] = comparison_by_season["month_no"].map(
        SEASON_LABELS
    )
    season_growth = (
        comparison_by_season.groupby("season", as_index=False)[
            ["rental_count_2017", "rental_count_2025"]
        ]
        .sum()
        .assign(
            growth_multiple=lambda df: df["rental_count_2025"]
            / df["rental_count_2017"]
        )
    )
    season_growth["season"] = pd.Categorical(
        season_growth["season"], categories=season_order, ordered=True
    )
    season_growth = season_growth.sort_values("season")
    season_growth.to_csv(CSV_DIR / "2017_2025_season_growth.csv", index=False)

    def hour_metrics(hourly):
        total_rentals = int(hourly["rental_count"].sum())
        morning_8 = int(hourly.loc[hourly["hour"] == 8, "rental_count"].sum())
        evening_17_19 = int(
            hourly.loc[hourly["hour"].isin([17, 18, 19]), "rental_count"].sum()
        )
        commute_8_17_19 = int(
            hourly.loc[hourly["hour"].isin([8, 17, 18, 19]), "rental_count"].sum()
        )
        hour_18 = int(hourly.loc[hourly["hour"] == 18, "rental_count"].sum())
        return {
            "total_rentals": total_rentals,
            "morning_8": morning_8,
            "evening_17_19": evening_17_19,
            "commute_8_17_19": commute_8_17_19,
            "hour_18": hour_18,
            "morning_8_share_pct": morning_8 / total_rentals * 100,
            "evening_17_19_share_pct": evening_17_19 / total_rentals * 100,
            "commute_8_17_19_share_pct": commute_8_17_19 / total_rentals * 100,
            "hour_18_share_pct": hour_18 / total_rentals * 100,
        }

    hour_2017 = hour_metrics(hourly_2017)
    hour_2025 = hour_metrics(hourly_total)
    total_rentals = hour_2025["total_rentals"]
    avg_use_2017 = float(summary_2017["avg_use_min"])
    avg_use_2025 = float(total.iloc[0]["avg_use_min"])
    avg_distance_2017 = float(summary_2017["avg_distance_m"]) / 1000
    avg_distance_2025 = float(total.iloc[0]["avg_distance_m"]) / 1000

    metrics = pd.DataFrame(
        [
            ["total_2017_rentals", hour_2017["total_rentals"], "count"],
            ["total_2025_rentals", total_rentals, "count"],
            [
                "total_growth_multiple_2017_to_2025",
                total_rentals / comparison["rental_count_2017"].sum(),
                "multiple",
            ],
            ["avg_use_min_2017", avg_use_2017, "minute"],
            ["avg_use_min_2025", avg_use_2025, "minute"],
            [
                "avg_use_min_change_pct_2017_to_2025",
                (avg_use_2025 / avg_use_2017 - 1) * 100,
                "percent",
            ],
            ["avg_distance_km_2017", avg_distance_2017, "km"],
            [
                "avg_distance_km_2025",
                avg_distance_2025,
                "km",
            ],
            [
                "avg_distance_change_pct_2017_to_2025",
                (avg_distance_2025 / avg_distance_2017 - 1) * 100,
                "percent",
            ],
            [
                "morning_8_share_pct_2017",
                hour_2017["morning_8_share_pct"],
                "percent",
            ],
            ["morning_8_share_pct", hour_2025["morning_8_share_pct"], "percent"],
            [
                "morning_8_share_pp_change_2017_to_2025",
                hour_2025["morning_8_share_pct"] - hour_2017["morning_8_share_pct"],
                "percentage_point",
            ],
            [
                "evening_17_19_share_pct_2017",
                hour_2017["evening_17_19_share_pct"],
                "percent",
            ],
            [
                "evening_17_19_share_pct",
                hour_2025["evening_17_19_share_pct"],
                "percent",
            ],
            [
                "commute_8_17_18_19_share_pct_2017",
                hour_2017["commute_8_17_19_share_pct"],
                "percent",
            ],
            [
                "commute_8_17_18_19_share_pct",
                hour_2025["commute_8_17_19_share_pct"],
                "percent",
            ],
            [
                "commute_share_pp_change_2017_to_2025",
                hour_2025["commute_8_17_19_share_pct"]
                - hour_2017["commute_8_17_19_share_pct"],
                "percentage_point",
            ],
            [
                "hour_18_growth_multiple_2017_to_2025",
                hour_2025["hour_18"] / hour_2017["hour_18"],
                "multiple",
            ],
            [
                "winter_growth_multiple_2017_to_2025",
                float(
                    season_growth.loc[
                        season_growth["season"] == "winter", "growth_multiple"
                    ].iloc[0]
                ),
                "multiple",
            ],
        ],
        columns=["metric", "value", "unit"],
    )
    metrics.to_csv(CSV_DIR / "2025_interpretation_metrics.csv", index=False)

    role_comparison = pd.DataFrame(
        [
            [
                "전체 대여 건수",
                f"{hour_2017['total_rentals']:,}건",
                f"{hour_2025['total_rentals']:,}건",
                f"{hour_2025['total_rentals'] / hour_2017['total_rentals']:.2f}배",
                "전체 이용량은 감소하지 않고 크게 증가",
            ],
            [
                "최고 이용 시간",
                "18시",
                "18시",
                f"18시 대여 {hour_2025['hour_18'] / hour_2017['hour_18']:.2f}배",
                "퇴근 피크 패턴 유지",
            ],
            [
                "8시 이용 비중",
                f"{hour_2017['morning_8_share_pct']:.1f}%",
                f"{hour_2025['morning_8_share_pct']:.1f}%",
                f"+{hour_2025['morning_8_share_pct'] - hour_2017['morning_8_share_pct']:.1f}%p",
                "출근 시간대 비중 확대",
            ],
            [
                "8시·17~19시 이용 비중",
                f"{hour_2017['commute_8_17_19_share_pct']:.1f}%",
                f"{hour_2025['commute_8_17_19_share_pct']:.1f}%",
                f"+{hour_2025['commute_8_17_19_share_pct'] - hour_2017['commute_8_17_19_share_pct']:.1f}%p",
                "생활 이동 성격 유지 및 소폭 강화",
            ],
            [
                "평균 이용시간",
                f"{avg_use_2017:.2f}분",
                f"{avg_use_2025:.2f}분",
                f"{(avg_use_2025 / avg_use_2017 - 1) * 100:.1f}%",
                "더 짧은 시간 단위의 이용",
            ],
            [
                "평균 이동거리",
                f"{avg_distance_2017:.2f}km",
                f"{avg_distance_2025:.2f}km",
                f"{(avg_distance_2025 / avg_distance_2017 - 1) * 100:.1f}%",
                "생활권 단거리 이동 중심성 강화",
            ],
        ],
        columns=["metric", "value_2017", "value_2025", "change", "interpretation"],
    )
    role_comparison.to_csv(CSV_DIR / "2017_2025_role_comparison.csv", index=False)

    hourly_share_comparison = hourly_2017.rename(
        columns={"rental_count": "rental_count_2017"}
    ).merge(
        hourly_total.rename(columns={"rental_count": "rental_count_2025"}),
        on="hour",
        how="inner",
    )
    hourly_share_comparison["share_2017_pct"] = (
        hourly_share_comparison["rental_count_2017"]
        / hourly_share_comparison["rental_count_2017"].sum()
        * 100
    )
    hourly_share_comparison["share_2025_pct"] = (
        hourly_share_comparison["rental_count_2025"]
        / hourly_share_comparison["rental_count_2025"].sum()
        * 100
    )
    hourly_share_comparison["share_change_pp"] = (
        hourly_share_comparison["share_2025_pct"]
        - hourly_share_comparison["share_2017_pct"]
    )
    hourly_share_comparison.to_csv(
        CSV_DIR / "2017_2025_hourly_share_comparison.csv", index=False
    )

    return season_usage, season_growth, metrics


def save_figures(monthly_2025, hourly_total, summary, comparison):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    million_formatter = FuncFormatter(lambda value, _: f"{value / 1_000_000:.1f}")

    plt.figure(figsize=(10, 5))
    plt.plot(
        monthly_2025["month"],
        monthly_2025["rental_count"],
        marker="o",
        color=PRIMARY_COLOR,
        linewidth=2.4,
    )
    plt.title("Monthly Seoul Bike Rentals in 2025")
    plt.xlabel("Month")
    plt.ylabel("Rental Count (million)")
    plt.gca().yaxis.set_major_formatter(million_formatter)
    plt.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "2025_monthly_usage.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.bar(hourly_total["hour"], hourly_total["rental_count"], color=SECONDARY_COLOR)
    plt.title("Hourly Seoul Bike Rentals in 2025")
    plt.xlabel("Hour")
    plt.ylabel("Rental Count (million)")
    plt.gca().yaxis.set_major_formatter(million_formatter)
    plt.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    plt.xticks(hourly_total["hour"])
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "2025_hourly_usage.png", dpi=150)
    plt.close()

    plt.figure(figsize=(11, 5))
    plt.plot(
        comparison["month_no"],
        comparison["rental_count_2017"],
        marker="o",
        label="2017",
        color=MUTED_COLOR,
        linewidth=2.0,
    )
    plt.plot(
        comparison["month_no"],
        comparison["rental_count_2025"],
        marker="o",
        label="2025",
        color=PRIMARY_COLOR,
        linewidth=2.4,
    )
    plt.title("Monthly Rental Count Comparison: 2017 vs 2025")
    plt.xlabel("Month")
    plt.ylabel("Rental Count (million)")
    plt.gca().yaxis.set_major_formatter(million_formatter)
    plt.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    plt.xticks(comparison["month_no"])
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "2017_2025_monthly_usage_compare.png", dpi=150)
    plt.close()

    hourly_share_comparison = pd.read_csv(CSV_DIR / "2017_2025_hourly_share_comparison.csv")
    plt.figure(figsize=(10, 5))
    plt.plot(
        hourly_share_comparison["hour"],
        hourly_share_comparison["share_2017_pct"],
        marker="o",
        label="2017",
        color=MUTED_COLOR,
        linewidth=2.0,
    )
    plt.plot(
        hourly_share_comparison["hour"],
        hourly_share_comparison["share_2025_pct"],
        marker="o",
        label="2025",
        color=PRIMARY_COLOR,
        linewidth=2.4,
    )
    plt.title("Hourly Rental Share Comparison: 2017 vs 2025")
    plt.xlabel("Hour")
    plt.ylabel("Share of Daily Rentals (%)")
    plt.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    plt.xticks(hourly_share_comparison["hour"])
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "2017_2025_hourly_share_compare.png", dpi=150)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(
        summary["month"],
        summary["avg_use_min"],
        marker="o",
        color=PRIMARY_COLOR,
        linewidth=2.4,
    )
    plt.title("Average Rental Duration by Month in 2025")
    plt.xlabel("Month")
    plt.ylabel("Average Duration (min)")
    plt.grid(axis="y", color=GRID_COLOR, linewidth=0.8)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIGURE_DIR / "2025_avg_duration_by_month.png", dpi=150)
    plt.close()


def main():
    set_korean_font()

    monthly_2025 = read_monthly_usage()
    _, hourly_total, hourly_peak_by_month = read_hourly_usage()
    summary, total = read_usage_summary()
    comparison = compare_2017_2025(monthly_2025)
    season_usage, season_growth, interpretation_metrics = save_interpretation_metrics(
        monthly_2025, hourly_total, total, comparison
    )
    save_figures(monthly_2025, hourly_total, summary, comparison)

    total_rows = int(monthly_2025["rental_count"].sum())
    if total_rows != EXPECTED_2025_ROWS:
        raise ValueError(
            f"unexpected 2025 row count: expected={EXPECTED_2025_ROWS}, actual={total_rows}"
        )

    print("saved_2025_summary")
    print(CSV_DIR)
    print("total_2025_rows")
    print(total_rows)
    print("peak_month")
    print(monthly_2025.loc[monthly_2025["rental_count"].idxmax()].to_dict())
    print("peak_hour_total")
    print(hourly_total.loc[hourly_total["rental_count"].idxmax()].to_dict())
    print("peak_hour_by_month")
    print(hourly_peak_by_month[["month", "peak_hour", "peak_rental_count"]])
    print("usage_summary_total")
    print(total)
    print("season_usage")
    print(season_usage)
    print("season_growth")
    print(season_growth)
    print("interpretation_metrics")
    print(interpretation_metrics)


if __name__ == "__main__":
    main()
