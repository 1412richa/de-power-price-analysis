"""Make the figures in plots/ that show derived or aggregated values only.

The raw price, load and generation series are not redistributed (see README,
"Data and licences"), so no figure plots them directly:
- STL decomposition: trend and seasonal components only. The residual panel is
  left out because trend + seasonal + residual add back up to the raw series.
- Residual load vs price: mean price per 5 GW residual-load band, one line per year,
  instead of a scatter of every hour.

Usage (from the repository root, after the data files exist in data/):
    python src/make_plots.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

ROOT = Path(__file__).resolve().parents[1]
DATA, PLOTS = ROOT / "data", ROOT / "plots"
PLOTS.mkdir(exist_ok=True)


def stl_figure():
    df = pd.read_csv(DATA / "de_day_ahead_prices_2022_2024.csv",
                     index_col="datetime_utc", parse_dates=True)
    result = STL(df["price_eur_mwh"], period=24, robust=True).fit()

    fig, (ax_trend, ax_season) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    result.trend.plot(ax=ax_trend, linewidth=0.8)
    ax_trend.set_ylabel("Trend (EUR/MWh)")
    result.seasonal.plot(ax=ax_season, linewidth=0.3)
    ax_season.set_ylabel("Daily seasonal (EUR/MWh)")
    ax_trend.set_title("STL decomposition of DE-LU day-ahead prices, 2022-2024 (period = 24 h)")
    fig.tight_layout()
    fig.savefig(PLOTS / "seasonal_trend_decomposition.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def residual_load_figure():
    cols = ["DE_load_actual_entsoe_transparency", "DE_solar_generation_actual",
            "DE_wind_onshore_generation_actual", "DE_wind_offshore_generation_actual",
            "DE_LU_price_day_ahead"]
    de = pd.read_csv(DATA / "time_series_60min_singleindex.csv", index_col=0,
                     parse_dates=True, usecols=["utc_timestamp"] + cols)
    de["residual_load_gw"] = (de["DE_load_actual_entsoe_transparency"]
                              - de["DE_solar_generation_actual"]
                              - de["DE_wind_onshore_generation_actual"]
                              - de["DE_wind_offshore_generation_actual"].fillna(0)) / 1000
    de = de.dropna(subset=["residual_load_gw", "DE_LU_price_day_ahead"])

    bands = np.arange(np.floor(de["residual_load_gw"].min() / 5) * 5,
                      de["residual_load_gw"].max() + 5, 5)
    de["band_mid"] = pd.cut(de["residual_load_gw"], bands).apply(lambda b: b.mid).astype(float)
    grouped = de.groupby([de.index.year, "band_mid"])["DE_LU_price_day_ahead"].agg(["mean", "size"])
    grouped = grouped[grouped["size"] >= 20]          # leave out thinly populated bands

    fig, ax = plt.subplots(figsize=(9, 5))
    for year, g in grouped.groupby(level=0):
        g = g.droplevel(0)
        ax.plot(g.index, g["mean"], marker="o", label=str(year))
    ax.set_xlabel("Residual load, 5 GW bands (GW)")
    ax.set_ylabel("Mean day-ahead price (EUR/MWh)")
    ax.set_title("Mean price by residual load band (bands with at least 20 hours)")
    ax.legend(title="Year")
    fig.savefig(PLOTS / "residual_load_vs_price_binned.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    stl_figure()
    residual_load_figure()
    print("Saved:", sorted(p.name for p in PLOTS.glob("*.png")))
