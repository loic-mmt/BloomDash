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
