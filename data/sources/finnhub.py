"""Finnhub adapter planning.

Data types to fetch:
- Equity/FX/crypto quote snapshots.
- Company profile and symbol metadata.
- Market-moving news and event calendar endpoints.
"""

DATA_TYPES = (
    "multi_asset_quote_snapshot",
    "company_profile_and_symbol_metadata",
    "market_moving_news_and_events",
)

TODO_ITEMS = (
    "Read Finnhub API token from env/config with startup validation.",
    "Implement quote endpoint client with symbol and asset-type abstraction.",
    "Implement company-profile endpoint client and metadata normalization.",
    "Implement news endpoint client with category/date filtering.",
    "Add request budget control to respect free-tier rate limits.",
    "Normalize all timestamps to UTC and enforce consistent numeric types.",
    "Add tests for auth errors, quota errors, and malformed payloads.",
)
