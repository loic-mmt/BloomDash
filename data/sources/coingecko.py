"""CoinGecko adapter planning.

Data types to fetch:
- Crypto market snapshot (price, market cap, volume, rank).
- Historical market chart points (price, cap, volume).
- Coin metadata (id, symbol, name) for symbol<->id mapping.
"""

DATA_TYPES = (
    "crypto_market_snapshot",
    "crypto_historical_market_chart",
    "coin_metadata_mapping",
)

TODO_ITEMS = (
    "Implement coin list bootstrap and cache symbol-to-coin-id mapping.",
    "Implement snapshot endpoint client (/coins/markets) for watchlists.",
    "Implement history endpoint client (/coins/{id}/market_chart).",
    "Normalize quote currency handling (usd/eur) and numeric coercion.",
    "Add rate-limit guardrails and adaptive sleep for free-tier limits.",
    "Implement deduplication by (coin_id, ts) before persistence.",
    "Add tests for mapping collisions and missing-market-data cases.",
)
