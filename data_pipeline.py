"""
East Africa Economic Lens — Data Pipeline
Fetches World Bank WDI indicators for EAC-5 countries (2000–2024)
using the standard World Bank REST API v2 (wbgapi's internal source-2 endpoint
is broken; we use the well-supported /country/indicator endpoint directly).
Saves merged parquet to data/processed/eac_economy.parquet.
"""

import os
import time
import requests
import pandas as pd
from itertools import product

COUNTRIES = ['KE', 'UG', 'TZ', 'ET', 'RW']
COUNTRY_NAMES = {
    'KE': 'Kenya',
    'UG': 'Uganda',
    'TZ': 'Tanzania',
    'ET': 'Ethiopia',
    'RW': 'Rwanda',
}

INDICATORS = {
    'NY.GDP.MKTP.KD.ZG':   'GDP Growth (%)',
    'NY.GDP.PCAP.KD':      'GDP per Capita (2015 USD)',
    'NY.GDP.PCAP.PP.KD':   'GDP per Capita PPP',
    'NY.GDP.MKTP.CD':      'GDP (current USD)',
    'FP.CPI.TOTL.ZG':      'Inflation (%)',
    'BX.KLT.DINV.CD.WD':   'FDI Inflows (USD)',
    'BX.KLT.DINV.WD.GD.ZS': 'FDI % GDP',
    'NE.TRD.GNFS.ZS':      'Trade % GDP',
    'NE.EXP.GNFS.ZS':      'Exports % GDP',
    'NE.IMP.GNFS.ZS':      'Imports % GDP',
    'SL.UEM.TOTL.ZS':      'Unemployment Rate (%)',
    'SI.POV.DDAY':          'Poverty Rate ($2.15/day)',
    'SI.POV.GINI':          'Gini Index',
    'BX.TRF.PWKR.DT.GD.ZS': 'Remittances % GDP',
    'GC.TAX.TOTL.GD.ZS':   'Tax Revenue % GDP',
}

WB_BASE = 'https://api.worldbank.org/v2'
COUNTRY_STR = ';'.join(COUNTRIES)


def fetch_indicator(code: str, label: str) -> pd.DataFrame | None:
    """Fetch one indicator for all 5 countries, 2000-2024. Retries once on timeout."""
    url = (
        f"{WB_BASE}/country/{COUNTRY_STR}/indicator/{code}"
        f"?format=json&per_page=2000&date=2000:2024"
    )
    for attempt in range(2):
      try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        break
      except requests.exceptions.Timeout:
        if attempt == 0:
            print(f"  RETRY {label} (timeout)...")
            time.sleep(5)
            continue
        else:
            print(f"  SKIP {label}: timeout after retry")
            return None
      except Exception as exc:
        print(f"  SKIP {label}: {exc}")
        return None
    try:
        payload = resp.json()
        meta, records = payload[0], payload[1]

        if not records:
            print(f"  EMPTY  {label}")
            return None

        # Handle pagination (shouldn't need it for 5 countries x 25 years = 125 rows)
        all_records = list(records)
        pages = meta.get('pages', 1)
        for page in range(2, pages + 1):
            r2 = requests.get(url + f"&page={page}", timeout=30)
            r2.raise_for_status()
            all_records.extend(r2.json()[1] or [])

        rows = []
        for rec in all_records:
            iso2 = rec['country']['id']
            if iso2 not in COUNTRIES:
                continue
            rows.append({
                'economy': iso2,
                'year': int(rec['date']),
                label: rec['value'],
            })

        df = pd.DataFrame(rows)
        non_null = df[label].notna().sum()
        print(f"  OK   {label:38s}  non-null: {non_null}/{len(df)}")
        return df

    except Exception as exc:
        print(f"  SKIP {label}: {exc}")
        return None


def fetch_all():
    os.makedirs('data/processed', exist_ok=True)
    frames = []

    for code, label in INDICATORS.items():
        df = fetch_indicator(code, label)
        if df is not None and not df.empty:
            frames.append(df)
        time.sleep(0.3)   # be polite to the API

    if not frames:
        raise RuntimeError("No indicators fetched — check internet connection.")

    # Build skeleton: all country × year combos
    skeleton = pd.DataFrame(
        list(product(COUNTRIES, range(2000, 2025))),
        columns=['economy', 'year']
    )

    result = skeleton.copy()
    for f in frames:
        result = result.merge(f, on=['economy', 'year'], how='left')

    result['country'] = result['economy'].map(COUNTRY_NAMES)
    result = result.sort_values(['economy', 'year']).reset_index(drop=True)

    out_path = 'data/processed/eac_economy.parquet'
    result.to_parquet(out_path, index=False)

    total_rows = len(result)
    yr_min = result['year'].min()
    yr_max = result['year'].max()
    print(f"\nSaved {total_rows} rows  |  years {yr_min}-{yr_max}  ->  {out_path}")

    # Sparsity report
    print("\n--- Indicator sparsity (% missing) ---")
    for label in INDICATORS.values():
        if label in result.columns:
            pct_missing = result[label].isna().mean() * 100
            flag = " *** sparse" if pct_missing > 50 else ""
            print(f"  {label:38s}  {pct_missing:5.1f}% missing{flag}")

    return result


if __name__ == '__main__':
    fetch_all()
