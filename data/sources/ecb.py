"""ECB SDMX adapter planning.

Data types to fetch:
- ECB SDMX macro/market series (rates, inflation proxies, FX via EXR).
- Dataset + dimension metadata for key construction.
- Observation timestamps and values with frequency tags.
"""

DATA_TYPES = (
    "sdmx_macro_and_fx_series",
    "sdmx_dataset_dimension_metadata",
    "timestamped_observations_with_frequency",
)

TODO_ITEMS = (
    "Implement SDMX key builder helpers (dataset, dimensions, filters).",
    "Implement ECB data endpoint client with robust timeout and headers.",
    "Parse SDMX-JSON structure into flat tabular rows.",
    "Normalize periodicity fields (D/W/M/Q) into canonical date conventions.",
    "Implement symbol mapping for common dashboard aliases (EURUSD, DE10Y, etc.).",
    "Add retry/backoff and handling for empty/partial SDMX responses.",
    "Add tests using recorded SDMX fixtures for parser stability.",
)
