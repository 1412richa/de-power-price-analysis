# German Power Price Analysis

**Aim:** This project conducts time series analysis of hourly German day-ahead electricity prices from ENTSO-E, focusing on seasonality, spikes, and negative price trends.

**Motivation:** Investigate the occurrence of negative prices and explain them in terms of the merit order model.

## Setup

1. Create and activate a virtual environment (`.venv`).
2. Install dependencies:
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```
3. Get a free API key from the [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) (Account Settings → Web Service).
4. Copy `.env.example` to `.env` and add your key:
```
ENTSOE_API_KEY=your_key_here
```
`.env` is gitignored and never committed — `.env.example` documents the required variable without exposing a real secret.

## Usage

Fetch day-ahead prices for a date range and bidding zone:
```
python src/fetch_prices.py --start 2022-01-01 --end 2025-01-01 --out data/de_day_ahead_prices_2022_2024.csv
```
The script chunks requests by year to stay within platform limits, and stores timestamps in UTC.

Then open `notebooks/explore_prices.ipynb` to load the CSV and explore the data — it reads the static output file rather than calling the API directly, so analysis stays reproducible and doesn't re-hit ENTSO-E on every run.

## Data Notes

- Germany's ENTSO-E bidding zone is `DE_LU` (Germany-Luxembourg), effective since the Oct 2018 bidding zone split. The old `DE` code fails for dates after that split.
- Timestamps are stored in UTC. The underlying market data is published in local time (`Europe/Berlin`), so spring DST transitions ("clocks forward") appear as a missing hour in the raw feed — this is expected, not a data quality issue.
- Negative prices are a real, economically meaningful phenomenon (oversupply from renewables/must-run generation exceeding demand), not an error condition.

## Project Structure
```
de-power-price-analysis/
├── src/
│   ├── fetch_prices.py        # pulls day-ahead prices from ENTSO-E (needs API key)
│   └── generate_demo_data.py  # (planned) synthetic data so the repo runs without a key — not yet built
├── notebooks/
│   ├── explore_prices.ipynb   # exploratory analysis of fetched price data
│   └── ops_exploration.ipynb  # time series analysis of Open Power System data
├── data/                      # fetched CSVs (gitignored)
├── plots/                     # saved figures
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── .github
├── LICENSE (MIT)
└── README.md
```

## Status

Fetched hourly DE_LU day-ahead prices for 2022–2025 (~26,300 rows). Verified time continuity: three 2-hour gaps corresponding to spring DST transitions (one per year, 2022–2024) — expected, not missing data.

Found 826 negative-price hours. Distribution is strongly right-skewed: mean -11.2 €/MWh, median -1.6 €/MWh, with a rare extreme drop to -500 €/MWh, and clustering visible in Q2/Q3 of both 2023 and 2024 — consistent with seasonal solar oversupply.

**Next:** test whether negative-price shocks are mean-reverting (autocorrelation / event-study of price in the hours following a spike).

