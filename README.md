# German Power Price Analysis

Aim: This project conducts time series analysis of the hourly German day-ahead electricity prices from ENTSO-E, with a focus on seasonality, spikes and negative price trends.

Motivation: Investigate the occurrences of negative prices and explain in terms of the merit order model.

## Setup
### Setting up a Python project in VS Code
Setting the project structure as below:

```
de-power-price-analysis/
├── src/
│   ├── fetch_prices.py        # pulls real data from ENTSO-E (needs your API key)
├── data/                       # CSVs
├── plots/                      
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── .github
├── LICENSE (MIT)
└── README.md
```

Set up env to store the secrets, i.e. the API key obtained from ENTSO-E website.
Include entsoe-py in the requirements to access the day-ahead prices through an API pipeline.
requirements-dev is included too.
env is included in gitignore to protect secrets.

### Functions
1. fetch_prices: a function used to call price data in a given time period and country
2. clean_data: cleaning and exploratory analysis of the day-ahead prices
3. visualize: time series visualizations of the day-ahead prices
4. generate_demo_data: stimulate data so the repo runs without a key

## Usage
Run fetch_prices to retrieve data for the desired timeframe and bidding region. For example, in Python, it will look like:
```
python src/fetch_prices.py --start 2022-01-01 --end 2025-01-01 --out data/de_day_ahead_prices_2022_2024.csv
```
Next, call the clean_data function to run housekeeping and have a first look at the trends.

Then, run visualize to plot time series trends decomposed into trend, seasonality and cyclic variations.

## Project Structure
Below is the planned project structure

```
de-power-price-analysis/
├── src/
│   ├── fetch_prices.py        # pulls real data from ENTSO-E (needs your API key)
│   ├── clean_data.py          # continuous hourly grid, gap-filling, negative/spike flags
│   ├── visualize.py           # 4 plots + summary stats
│   └── generate_demo_data.py  # synthetic data so the repo runs without a key
├── data/                      # CSVs
├── plots/                      
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── LICENSE (MIT)
└── README.md
```

## Data Notes
Germany's ENTSO-E bidding zone is "DE_LU" (Germany-Luxembourg), effective since the Oct 2018 bidding zone split. Using the old "DE" code will fail for dates after that split.

The query is chunked by year because very long date ranges can be slow or hit platform-side limits.

## Status
Waiting for the API key access.

Received the API key from ENTSO-E. Pulled the hourly data between 2022 and 2025. There were three entries with a two-hour difference due to DST changes; however, the time continuity is intact. Drastic rare occurance of negative price in mid 2023 with the price reaching -500 eur/mwh, apart from this occurance the negative prices are strongly skewed towards right, meaning they are mostly close to zero. The mean of the negative prices was -11.2 eur/mwh and the median was -1.6 eur/mwh.
