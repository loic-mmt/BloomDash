"""Source adapters inventory.

This package centralizes external market/macro/news adapters.
Each module must expose:
- the data scope (what we fetch),
- a precise implementation TODO list.
"""

AVAILABLE_SOURCE_MODULES = (
    "stooq",
    "yfinance",
    "fred",
    "ecb",
    "coingecko",
    "finnhub",
    "gdelt",
)

DATA_TYPES = (
    "source_registry_metadata",
    "shared_adapter_contract_definitions",
)

TODO_ITEMS = (
    "Define a common SourceAdapter protocol (fetch_snapshot, fetch_history, healthcheck).",
    "Standardize normalized schemas by domain (prices, macro, news).",
    "Implement shared retry/backoff + timeout policy.",
    "Implement shared request logging + latency metrics.",
    "Add integration tests for each source behind feature flags.",
)
