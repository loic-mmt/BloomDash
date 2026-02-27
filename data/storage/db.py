from __future__ import annotations

import sqlite3

import numpy as np
import pandas as pd


def init_prices_last_dates_db(conn: sqlite3.Connection) -> None:
    """Create SQLite objects used to track latest ingested prices.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection to the metadata database.

    Returns
    -------
    None
        The function creates table/indexes in-place and commits the transaction.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS last_dates (
          ticker     TEXT NOT NULL,
          date       TEXT NOT NULL,  -- YYYY-MM-DD
          open       REAL,
          high       REAL,
          low        REAL,
          close      REAL,
          adj_close  REAL,
          volume     INTEGER,
          PRIMARY KEY (ticker, date)
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_last_dates_ticker ON last_dates(ticker);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_last_dates_date ON last_dates(date);")
    conn.commit()


def get_last_price_date(conn: sqlite3.Connection, ticker: str) -> str | None:
    """Fetch the last ingested price date for one ticker.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    ticker : str
        Ticker symbol.

    Returns
    -------
    str | None
        Latest date in ``YYYY-MM-DD`` format, or ``None`` if no record exists.
    """
    row = conn.execute(
        "SELECT MAX(date) FROM last_dates WHERE ticker = ?",
        (ticker,),
    ).fetchone()
    return row[0]


def upsert_price_last_dates(conn: sqlite3.Connection, df: pd.DataFrame) -> str | None:
    """Upsert the most recent OHLCV row for a ticker.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    df : pd.DataFrame
        Price rows for a single ticker with columns matching ``last_dates``
        (ticker, date, open, high, low, close, adj_close, volume).

    Returns
    -------
    str | None
        Upserted latest date in ``YYYY-MM-DD`` format, or ``None`` if input is empty.
    """
    if df is None or df.empty:
        return None

    df_last = df.sort_values("date").tail(1)
    last_date = df_last.iloc[0]["date"]

    sql = """
    INSERT INTO last_dates (ticker, date, open, high, low, close, adj_close, volume)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(ticker, date) DO UPDATE SET
      open      = excluded.open,
      high      = excluded.high,
      low       = excluded.low,
      close     = excluded.close,
      adj_close = excluded.adj_close,
      volume    = excluded.volume;
    """

    row = (
        df_last.iloc[0]["ticker"],
        df_last.iloc[0]["date"],
        float(df_last.iloc[0]["open"]) if pd.notna(df_last.iloc[0]["open"]) else None,
        float(df_last.iloc[0]["high"]) if pd.notna(df_last.iloc[0]["high"]) else None,
        float(df_last.iloc[0]["low"]) if pd.notna(df_last.iloc[0]["low"]) else None,
        float(df_last.iloc[0]["close"]) if pd.notna(df_last.iloc[0]["close"]) else None,
        float(df_last.iloc[0]["adj_close"]) if pd.notna(df_last.iloc[0]["adj_close"]) else None,
        int(df_last.iloc[0]["volume"]) if pd.notna(df_last.iloc[0]["volume"]) else None,
    )

    conn.execute(sql, row)
    conn.commit()
    return last_date


def init_feature_last_dates_db(conn: sqlite3.Connection) -> None:
    """Create SQLite objects used to track latest feature dates.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection to the metadata database.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS feature_last_dates (
          feature   TEXT NOT NULL,
          ticker    TEXT NOT NULL,
          date      TEXT NOT NULL,  -- YYYY-MM-DD
          PRIMARY KEY (feature, ticker)
        );
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_feature_last_dates_feature ON feature_last_dates(feature);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_feature_last_dates_ticker ON feature_last_dates(ticker);"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_feature_last_dates_date ON feature_last_dates(date);"
    )
    conn.commit()


def get_last_feature_date(conn: sqlite3.Connection, feature: str, ticker: str) -> str | None:
    """Fetch the latest computed date for one feature/ticker pair.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    feature : str
        Feature family name (for example ``"regime"`` or ``"assets"``).
    ticker : str
        Ticker identifier.

    Returns
    -------
    str | None
        Latest date in ``YYYY-MM-DD`` format, or ``None`` when absent.
    """
    row = conn.execute(
        "SELECT date FROM feature_last_dates WHERE feature = ? AND ticker = ?",
        (feature, ticker),
    ).fetchone()
    return row[0] if row else None


def get_all_last_feature_dates(conn: sqlite3.Connection, feature: str) -> dict[str, str]:
    """Fetch latest feature dates for all tickers in one feature family.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    feature : str
        Feature family name.

    Returns
    -------
    dict[str, str]
        Mapping ``ticker -> latest_date``.
    """
    rows = conn.execute(
        "SELECT ticker, date FROM feature_last_dates WHERE feature = ?",
        (feature,),
    ).fetchall()
    return {ticker: date for ticker, date in rows}


def upsert_feature_last_dates(
    conn: sqlite3.Connection,
    feature: str,
    df: pd.DataFrame,
    ticker_col: str = "ticker",
    date_col: str = "date",
) -> None:
    """Upsert latest feature date per ticker for one feature family.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    feature : str
        Feature family name.
    df : pd.DataFrame
        Data containing ticker/date observations.
    ticker_col : str, default "ticker"
        Name of the ticker column in ``df``.
    date_col : str, default "date"
        Name of the date column in ``df``.

    Raises
    ------
    KeyError
        If required columns are missing.
    """
    if df is None or df.empty:
        return
    if ticker_col not in df.columns or date_col not in df.columns:
        missing = ", ".join(sorted({ticker_col, date_col} - set(df.columns)))
        raise KeyError(f"Missing columns: {missing}")

    dt = pd.to_datetime(df[date_col], errors="coerce")
    ok = dt.notna()
    df = df.loc[ok].copy()
    df[date_col] = dt.loc[ok].dt.strftime("%Y-%m-%d")

    last_by_ticker = df.groupby(ticker_col)[date_col].max()
    sql = """
    INSERT INTO feature_last_dates (feature, ticker, date)
    VALUES (?, ?, ?)
    ON CONFLICT(feature, ticker) DO UPDATE SET
      date = excluded.date;
    """
    for ticker, last_date in last_by_ticker.items():
        conn.execute(sql, (feature, str(ticker), str(last_date)))
    conn.commit()



def init_fred_last_dates_db(conn: sqlite3.Connection) -> None:
    """Create SQLite objects used to track latest ingested macro-data.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection to the metadata database.

    Returns
    -------
    None
        The function creates table/indexes in-place and commits the transaction.
    """
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS last_dates_fred (
          zone       TEXT NOT NULL,
          date       TEXT NOT NULL,  -- YYYY-MM-DD
          cpi        REAL,
          gdp        REAL,
          policy     REAL,
          unemp      REAL,
          PRIMARY KEY (zone, date)
        );
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_last_dates_zone ON last_dates(zone);")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_last_dates_date ON last_dates(date);")
    conn.commit()


def get_last_fred_date(conn: sqlite3.Connection, zone: str) -> str | None:
    """Fetch the last ingested price date for one zone.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    zone : str
        Zone symbol.

    Returns
    -------
    str | None
        Latest date in ``YYYY-MM-DD`` format, or ``None`` if no record exists.
    """
    row = conn.execute(
        "SELECT MAX(date) FROM last_dates_fred WHERE zone = ?",
        (zone,),
    ).fetchone()
    return row[0]


def upsert_fred_last_dates(conn: sqlite3.Connection, df: pd.DataFrame) -> str | None:
    """Upsert the most recent data row for a zone.

    Parameters
    ----------
    conn : sqlite3.Connection
        Open SQLite connection.
    df : pd.DataFrame
        Data rows for a single zone with columns matching ``last_dates_fred``
        (zone, date, cpi, gdp, policy, unemp).

    Returns
    -------
    str | None
        Upserted latest date in ``YYYY-MM-DD`` format, or ``None`` if input is empty.
    """
    if df is None or df.empty:
        return None

    df_last = df.sort_values("date").tail(1)
    last_date = df_last.iloc[0]["date"]

    sql = """
    INSERT INTO last_dates_fred (zone, date, cpi, gdp, policy, unemp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(zone, date) DO UPDATE SET
      cpi      = excluded.cpi,
      gdp      = excluded.gdp,
      policy   = excluded.policy,
      unemp    = excluded.unemp;
    """

    row = (
        df_last.iloc[0]["zone"],
        df_last.iloc[0]["date"],
        float(df_last.iloc[0]["cpi"]) if pd.notna(df_last.iloc[0]["cpi"]) else None,
        float(df_last.iloc[0]["gdp"]) if pd.notna(df_last.iloc[0]["gdp"]) else None,
        float(df_last.iloc[0]["policy"]) if pd.notna(df_last.iloc[0]["policy"]) else None,
        float(df_last.iloc[0]["unemp"]) if pd.notna(df_last.iloc[0]["unemp"]) else None,
    )

    conn.execute(sql, row)
    conn.commit()
    return last_date