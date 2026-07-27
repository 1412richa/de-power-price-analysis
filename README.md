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

## Analysis

### Leading questions
- How often do negative prices occur, and how extreme are they?
- When negative prices occur, does the market revert quickly (a brief shock) or does the effect persist?
- Is negative-price behavior driven by isolated hourly events, or by longer weather-driven regimes (e.g., a windy/sunny multi-day stretch)?

### What was done
1. **Data validation** — checked hourly continuity across ~26,300 rows (2022–2025). Found three 2-hour gaps, one per year, matching Germany's spring DST transition — expected, not a data quality issue.
2. **Negative price distribution** — 826 negative-price hours found. Strongly right-skewed: mean -11.2 €/MWh, median -1.6 €/MWh, with a rare extreme of -500 €/MWh. Most negative hours are mild (close to zero); deep drops are rare.
3. **Autocorrelation (ACF)** on the raw price series showed slow decay (still ~0.75 correlation at 48 hours) with peaks roughly every 12 hours — consistent with the daily double-cycle of demand/solar (morning and evening peaks, midday and overnight troughs), rather than a specific reversion signal.
4. **Event study** — for each negative-price hour, tracked the price 1/3/6/12/24 hours later, both in absolute terms and relative to the typical price for that hour of day (to separate genuine reversion from the ordinary diurnal cycle).

### Conclusion
Negative-price shocks show **partial reversion within the same day** (deviation from the hour's typical price shrinks from roughly -130 €/MWh at +1h to -74 €/MWh at +12h), but **do not fully revert even after 24 hours** (deviation widens again to roughly -85 to -98 €/MWh at +24h, nearly as depressed as the +6h mark). This pattern is inconsistent with a single isolated hourly shock, and instead suggests negative-price events cluster over **multi-day periods** — plausibly driven by sustained weather regimes (extended high wind/solar output coinciding with low demand) rather than one-off imbalances.

## Status

Exploratory analysis phase complete for now — see Analysis above.

Fetched hourly DE_LU day-ahead prices for 2022–2025 (~26,300 rows). Verified time continuity: three 2-hour gaps corresponding to spring DST transitions (one per year, 2022–2024) — expected, not missing data.

Found 826 negative-price hours. Distribution is strongly right-skewed: mean -11.2 €/MWh, median -1.6 €/MWh, with a rare extreme drop to -500 €/MWh, and clustering visible in Q2/Q3 of both 2023 and 2024 — consistent with seasonal solar oversupply.
