"""Stooq adapter planning.

Data types to fetch:
- End-of-day OHLCV for equities, ETFs, indices.
- Basic instrument identifiers from symbol universe mapping.
- Optional split/adjustment hints when available.
"""

DATA_TYPES = (
    "ohlcv_eod_prices",
    "instrument_identifier_mapping",
    "optional_corporate_action_hints",
)

TODO_ITEMS = (
    "Implement HTTP client with base URL and strict timeout defaults.",
    "Build query helpers for symbol + date range extraction.",
    "Parse CSV payloads and coerce numeric fields safely.",
    "Normalize to canonical price schema (ticker, ts, open, high, low, close, volume, source).",
    "Add incremental ingestion logic with last successful date checkpoint.",
    "Add retry/backoff and explicit handling for 4xx/5xx and empty payloads.",
    "Add fixture-based tests for parser edge cases (missing columns, invalid rows).",
)
