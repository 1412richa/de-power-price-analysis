"""
Fetch German day-ahead electricity prices from the ENTSO-E Transparency Platform.

Requires a free ENTSO-E API key. Request one via your account settings at:
https://transparency.entsoe.eu/

Setup:
    pip install -r requirements.txt
    export ENTSOE_API_KEY="your_key_here"

Usage:
    python src/fetch_prices.py \
        --start 2022-01-01 --end 2025-01-01 \
        --out data/de_day_ahead_prices_2022_2024.csv

Notes:
    - Germany's ENTSO-E bidding zone is "DE_LU" (Germany-Luxembourg), effective
      since the Oct 2018 bidding zone split. Using the old "DE" code will fail
      for dates after that split.
    - The query is chunked by year because very long date ranges can be slow
      or hit platform-side limits.
"""
import argparse
import os
import sys
from pathlib import Path

import pandas as pd
from entsoe import EntsoePandasClient


def fetch_day_ahead_prices(client: EntsoePandasClient, start: pd.Timestamp,
                            end: pd.Timestamp, country_code: str = "DE_LU") -> pd.Series:
    """Fetch a single contiguous block of day-ahead prices."""
    return client.query_day_ahead_prices(country_code, start=start, end=end)


def main():
    parser = argparse.ArgumentParser(description="Fetch DE day-ahead prices from ENTSO-E")
    parser.add_argument("--start", default="2022-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default="2025-01-01", help="End date, exclusive (YYYY-MM-DD)")
    parser.add_argument("--country", default="DE_LU", help="ENTSO-E bidding zone code")
    parser.add_argument("--out", default="data/de_day_ahead_prices_2022_2024.csv")
    args = parser.parse_args()

    api_key = os.environ.get("ENTSOE_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: ENTSOE_API_KEY environment variable not set.\n"
            "Get a free key at https://transparency.entsoe.eu/ (Account Settings -> "
            "Web Service section) and run:\n"
            "    export ENTSOE_API_KEY='your_key_here'"
        )

    client = EntsoePandasClient(api_key=api_key)

    start = pd.Timestamp(args.start, tz="Europe/Brussels")
    end = pd.Timestamp(args.end, tz="Europe/Brussels")

    print(f"Fetching {args.country} day-ahead prices: {start.date()} -> {end.date()}")

    chunks = []
    current = start
    while current < end:
        chunk_end = min(current + pd.DateOffset(years=1), end)
        print(f"  chunk: {current.date()} -> {chunk_end.date()}")
        try:
            s = fetch_day_ahead_prices(client, current, chunk_end, country_code=args.country)
            chunks.append(s)
        except Exception as exc:
            print(f"  WARNING: chunk failed ({exc}); continuing with next chunk", file=sys.stderr)
        current = chunk_end

    if not chunks:
        sys.exit("No data fetched. Check your API key, date range, and network connection.")

    prices = pd.concat(chunks)
    prices = prices[~prices.index.duplicated(keep="first")].sort_index()

    df = prices.to_frame(name="price_eur_mwh")
    df.index = df.index.tz_convert("UTC")
    df.index.name = "datetime_utc"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path)
    print(f"Saved {len(df)} rows to {out_path}")


if __name__ == "__main__":
    main()