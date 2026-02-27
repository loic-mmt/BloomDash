"""FRED adapter planning.

Data types to fetch:
- Macro time series observations (rates, inflation, labor, growth).
- Series metadata (title, frequency, units, seasonal adjustment).
- Release timestamps and revision-aware observation dates when available.
"""

DATA_TYPES = (
    "macro_series_observations",
    "macro_series_metadata",
    "release_timestamps_and_revisions",
)

TODO_ITEMS = (
    "Read FRED API key from env/config and fail fast when missing.",
    "Implement observations endpoint client with date/frequency/units params.",
    "Implement series metadata endpoint client and metadata cache.",
    "Normalize values (including missing '.') to typed schema.",
    "Support incremental backfill by keeping last fetched observation date.",
    "Add retry/backoff for transient HTTP errors and server throttling.",
    "Add tests for frequency conversion and missing-value handling.",
)

import pandas_datareader as pdr
from datetime import datetime
from math import tanh
import numpy as np
import pandas as pd
import sqlite3
from pathlib import Path
import sys

PYTHON_ROOT = Path(__file__).resolve().parents[1]
if str(PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(PYTHON_ROOT))

from data.storage.db import (
    get_last_fred_date,
    init_fred_last_dates_db,
    upsert_fred_last_dates,
)
from data.storage.parquet import append_fred_dataset

SERIES = {
    "US": {
        "cpi": "CPIAUCNS",
        "gdp": "GDP",
        "policy": "FEDFUNDS",
        "unemp": "UNRATE",
    },
    "EU": {
        "cpi": "CP0000EZ19M086NEST",
        "gdp": "CLVMNACSCAB1GQEA19",
        "policy": "ECBMRRFR",
        "unemp": "LRHUTTTTEZM156S",
    },
    "FR": {
        "cpi": "FRACPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQFR",
        "policy": "ECBMRRFR",          # taux BCE – même pour la France
        "unemp": "LRHUTTTTFRM156S",
    },
    "DE": {   # Germany
        "cpi": "DEUCPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQDE",
        "policy": "ECBMRRFR",          # ECB main refi rate applies
        "unemp": "LRHUTTTTDEM156S",
    },
    "IT": {   # Italy
        "cpi": "ITACPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQIT",
        "policy": "ECBMRRFR",
        "unemp": "LRHUTTTTITM156S",
    },
    "GR": {   # Greece
        "cpi": "GRCPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQGR",
        "policy": "ECBMRRFR",
        "unemp": "LRHUTTTTGRM156S",
    },
    "CH": {   # Switzerland
        "cpi": "CHECPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQCH",
        "policy": "IR3TIB01CHM156N",    # 3‑month Swiss interbank rate
        "unemp": "LRHUTTTTCHM156S",
    },
    "JP": {   # Japan
        "cpi": "JPNCPIALLMINMEI",
        "gdp": "CLVMNACSCAB1GQJP",
        "policy": "IR3TIB01JPM156N",    # 3‑month Tokyo interbank rate
        "unemp": "LRHUTTTTJPM156S",
    },
}


def get_macro_data(region="FR", start= str | None, end: str | None = None):
    codes = SERIES[region]

    cpi  = pdr.get_data_fred(codes["cpi"],  start, end)
    if cpi.empty:
        raise ValueError(f"Data retrieval failed for CPI in {region}. Please check the data source or the date range.")
    gdp  = pdr.get_data_fred(codes["gdp"],  start, end)
    if gdp.empty:
        raise ValueError(f"Data retrieval failed for GDP in {region}. Please check the data source or the date range.")
    pol  = pdr.get_data_fred(codes["policy"], start, end)
    if pol.empty:
        raise ValueError(f"Data retrieval failed for Policy Rate in {region}. Please check the data source or the date range.")
    unrt = pdr.get_data_fred(codes["unemp"], start, end)
    if unrt.empty:
        raise ValueError(f"Data retrieval failed for Unemployment Rate in {region}. Please check the data source or the date range.")

    return cpi, gdp, pol, unrt


def data_optimization(cpi, gdp, pol, unrt):
    latest_inflation = ((cpi.iloc[-1].item() / cpi.iloc[-13].item()) - 1) * 100
    latest_gdp = ((gdp.iloc[-1].item() / gdp.iloc[-5].item()) - 1) * 100
    pol_mean = pol.rolling(3).mean()
    unrt_mean = unrt.rolling(3).mean()

    z_unrate = (unrt_mean.iloc[-1] - unrt_mean.mean()) / unrt_mean.std()
    z_fed = (pol_mean.iloc[-1] - pol_mean.mean()) / pol_mean.std()

    inflation_pressure = z_fed
    growth_pressure = -z_unrate

    inflation_adj = np.tanh(inflation_pressure)
    growth_adj = np.tanh(growth_pressure)

    return latest_inflation, latest_gdp, pol_mean, unrt_mean, z_unrate, z_fed, inflation_adj, growth_adj

def main()-> None:
    """Run the ingestion pipeline for the zone."""
    conn = sqlite3.connect(DB_PATH)
    init_prices_last_dates_db(conn)
    cpi, gdp, pol, unrt = get_macro_data("FR", datetime(2023, 10, 1))
    latest_inflation, latest_gdp, pol_mean, unrt_mean, z_unrate, z_fed, inflation_adj, growth_adj = data_optimization(cpi, gdp, pol, unrt)
