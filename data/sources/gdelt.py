"""GDELT adapter planning.

Data types to fetch:
- Global news headlines with publication timestamp and source.
- Query-level relevance metadata for market filters.
- Optional event/enriched fields (theme, tone, location).
"""

DATA_TYPES = (
    "global_news_headlines",
    "relevance_metadata_for_market_filters",
    "optional_event_theme_tone_location",
)

TODO_ITEMS = (
    "Implement query builder for keyword/language/country/source filters.",
    "Implement GDELT DOC API client with pagination controls.",
    "Normalize result schema (published_at, source, title, url, tone, theme).",
    "Implement duplicate suppression by canonical URL + published timestamp.",
    "Add post-fetch relevance scoring flag for market-moving headlines.",
    "Add retry/backoff and handling for throttling/empty result windows.",
    "Add tests for query encoding and deduplication logic.",
)
