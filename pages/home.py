"""BloomDash Home page (wireframe + temporary mock data)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
from typing import Any

import dash
from dash import Input, Output, State, callback, dash_table, dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

dash.register_page(__name__, path="/home", name="Home")

TIMEFRAME_POINTS = {
    "1D": 24,
    "5D": 48,
    "1M": 96,
    "6M": 160,
    "1Y": 220,
}

PANEL_STYLE = {
    "backgroundColor": "#111923",
    "border": "1px solid #223247",
    "borderRadius": "10px",
    "padding": "12px",
}

BUTTON_STYLE = {
    "backgroundColor": "#15263B",
    "color": "#CFE3FF",
    "border": "1px solid #2A4463",
    "borderRadius": "7px",
    "padding": "8px 12px",
    "cursor": "pointer",
}


def _format_price(value: float, currency: str) -> str:
    symbol = "$" if currency == "USD" else "EUR "
    return f"{symbol}{value:,.2f}"


def _format_delta(delta: float, pct_delta: float, currency: str) -> str:
    symbol = "$" if currency == "USD" else "EUR "
    sign = "+" if delta >= 0 else "-"
    return f"{sign}{symbol}{abs(delta):,.2f} ({pct_delta:+.2f}%)"


# ============================================================
# MOCK DATA (TEMPORARY) - KEEP ALL FAKE DATA LOGIC HERE
# Replace this whole block once real data/source layers are ready.
# ============================================================
def _random_walk(
    seed: int,
    points: int,
    start: float,
    drift_pct: float,
    vol_pct: float,
) -> list[float]:
    rng = random.Random(seed)
    values = [start]
    for _ in range(points - 1):
        step = 1.0 + drift_pct + rng.gauss(0.0, vol_pct)
        values.append(max(0.01, values[-1] * step))
    return values


def _build_mock_payload(seed_offset: int = 0) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    base_seed = int(now.timestamp() // 60) + seed_offset
    total_points = TIMEFRAME_POINTS["1Y"]

    snapshot_bases = {
        "SPX": 5300.0,
        "NDX": 18600.0,
        "DAX": 17800.0,
        "CAC": 7950.0,
        "VIX": 15.2,
        "US10Y": 4.22,
        "EURUSD": 1.08,
        "BTC": 61200.0,
    }

    snapshot: list[dict[str, Any]] = []
    regime: dict[str, dict[str, float]] = {}

    for idx, (symbol, start) in enumerate(snapshot_bases.items()):
        rng = random.Random(base_seed + idx * 101)
        series = _random_walk(
            seed=base_seed + idx * 37,
            points=total_points,
            start=start,
            drift_pct=rng.uniform(-0.00035, 0.00085),
            vol_pct=rng.uniform(0.0012, 0.0150),
        )
        volume = [max(500, int(rng.gauss(2_000_000, 450_000))) for _ in range(total_points)]

        last = series[-1]
        prev = series[-2]
        delta = last - prev
        pct_delta = (delta / prev * 100.0) if prev else 0.0

        snapshot.append(
            {
                "symbol": symbol,
                "last": round(last, 6),
                "delta": round(delta, 6),
                "pct_delta": round(pct_delta, 3),
                "series": [round(point, 6) for point in series],
                "volume": volume,
            }
        )

        regime[symbol] = {
            "vol_20d": round(abs(rng.gauss(18.5, 5.0)), 2),
            "trend_score": round(max(-1.0, min(1.0, rng.gauss(0.2, 0.4))), 2),
            "drawdown_ytd": round(-abs(rng.gauss(5.3, 3.1)), 2),
        }

    movers_rng = random.Random(base_seed * 17)
    mover_symbols = [
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA",
        "AMZN",
        "META",
        "ASML",
        "ORCL",
        "NFLX",
        "INTC",
    ]

    movers_all = []
    for symbol in mover_symbols:
        last = movers_rng.uniform(20.0, 1100.0)
        pct = movers_rng.uniform(-8.0, 8.0)
        movers_all.append(
            {
                "symbol": symbol,
                "last": round(last, 2),
                "pct_delta": round(pct, 2),
            }
        )

    gainers = sorted(movers_all, key=lambda row: row["pct_delta"], reverse=True)[:5]
    losers = sorted(movers_all, key=lambda row: row["pct_delta"])[:5]

    news = [
        {
            "time": (now - timedelta(minutes=12)).strftime("%H:%M"),
            "source": "Reuters",
            "headline": "US yields edge higher as traders reprice rate-cut path.",
        },
        {
            "time": (now - timedelta(minutes=25)).strftime("%H:%M"),
            "source": "Bloomberg",
            "headline": "Mega-cap tech lifts Nasdaq futures ahead of opening bell.",
        },
        {
            "time": (now - timedelta(minutes=39)).strftime("%H:%M"),
            "source": "WSJ",
            "headline": "Energy shares rise after renewed crude supply concerns.",
        },
        {
            "time": (now - timedelta(minutes=54)).strftime("%H:%M"),
            "source": "FT",
            "headline": "European equities mixed while PMIs signal uneven demand.",
        },
        {
            "time": (now - timedelta(minutes=75)).strftime("%H:%M"),
            "source": "CNBC",
            "headline": "Dollar holds gains as investors await inflation print.",
        },
        {
            "time": (now - timedelta(minutes=95)).strftime("%H:%M"),
            "source": "MarketWatch",
            "headline": "Gold pauses after strong week despite softer real yields.",
        },
        {
            "time": (now - timedelta(minutes=108)).strftime("%H:%M"),
            "source": "Reuters",
            "headline": "Chip-equipment makers extend rally on robust AI pipeline.",
        },
        {
            "time": (now - timedelta(minutes=131)).strftime("%H:%M"),
            "source": "Bloomberg",
            "headline": "FX desks flag elevated implied vols into payrolls release.",
        },
        {
            "time": (now - timedelta(minutes=149)).strftime("%H:%M"),
            "source": "FT",
            "headline": "Banks outperform in Europe as term premium steepens.",
        },
        {
            "time": (now - timedelta(minutes=166)).strftime("%H:%M"),
            "source": "WSJ",
            "headline": "Crypto steadies after sharp intraday swings in BTC.",
        },
    ]

    calendar = [
        {"day": "Today", "time": "08:30", "event": "US Initial Jobless Claims", "impact": "High"},
        {"day": "Today", "time": "10:00", "event": "US Existing Home Sales", "impact": "Medium"},
        {"day": "Today", "time": "14:00", "event": "FOMC Minutes Speech", "impact": "High"},
        {"day": "Tomorrow", "time": "08:30", "event": "US PCE Price Index", "impact": "High"},
        {"day": "Tomorrow", "time": "09:45", "event": "US PMI Composite", "impact": "Medium"},
        {"day": "Tomorrow", "time": "11:00", "event": "ECB President Remarks", "impact": "Medium"},
    ]

    status_rng = random.Random(base_seed * 29)
    data_status = [
        {
            "source": "Stooq",
            "last_refresh": (now - timedelta(minutes=status_rng.randint(1, 9))).strftime("%H:%M:%S"),
            "errors": status_rng.randint(0, 1),
            "avg_latency_ms": round(status_rng.uniform(120, 430), 1),
        },
        {
            "source": "YahooFinance",
            "last_refresh": (now - timedelta(minutes=status_rng.randint(1, 10))).strftime("%H:%M:%S"),
            "errors": status_rng.randint(0, 2),
            "avg_latency_ms": round(status_rng.uniform(140, 510), 1),
        },
        {
            "source": "FRED",
            "last_refresh": (now - timedelta(minutes=status_rng.randint(4, 18))).strftime("%H:%M:%S"),
            "errors": status_rng.randint(0, 1),
            "avg_latency_ms": round(status_rng.uniform(80, 280), 1),
        },
        {
            "source": "CoinGecko",
            "last_refresh": (now - timedelta(minutes=status_rng.randint(1, 7))).strftime("%H:%M:%S"),
            "errors": status_rng.randint(0, 1),
            "avg_latency_ms": round(status_rng.uniform(90, 320), 1),
        },
        {
            "source": "GDELT",
            "last_refresh": (now - timedelta(minutes=status_rng.randint(2, 12))).strftime("%H:%M:%S"),
            "errors": status_rng.randint(0, 2),
            "avg_latency_ms": round(status_rng.uniform(180, 620), 1),
        },
    ]

    return {
        "generated_at": now.isoformat(),
        "fx": {"USD": 1.0, "EUR": 0.93},
        "snapshot": snapshot,
        "movers": {"gainers": gainers, "losers": losers},
        "regime": regime,
        "news": news,
        "calendar": calendar,
        "data_status": data_status,
    }


MOCK_DATA = _build_mock_payload()
# ============================================================
# END MOCK DATA BLOCK
# ============================================================


def _sparkline_figure(series: list[float], positive: bool) -> go.Figure:
    color = "#49D17D" if positive else "#E2616B"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=series,
            mode="lines",
            line={"width": 1.8, "color": color},
            hoverinfo="skip",
            fill="tozeroy",
            fillcolor="rgba(73, 209, 125, 0.08)" if positive else "rgba(226, 97, 107, 0.08)",
        )
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="#111923",
        plot_bgcolor="#111923",
        xaxis={"visible": False},
        yaxis={"visible": False},
        height=58,
    )
    return fig


def _focus_figure(symbol: str, series: list[float], volume: list[int], currency: str) -> go.Figure:
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.72, 0.28],
    )

    fig.add_trace(
        go.Scatter(
            x=list(range(len(series))),
            y=series,
            mode="lines",
            line={"color": "#79B8FF", "width": 2.2},
            name=f"{symbol} Price",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=list(range(len(volume))),
            y=volume,
            marker={"color": "#3E5F8A"},
            name="Volume",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        margin={"l": 40, "r": 20, "t": 20, "b": 30},
        paper_bgcolor="#111923",
        plot_bgcolor="#111923",
        font={"color": "#DFE9F8"},
        showlegend=False,
        height=420,
        yaxis_title="Price",
        yaxis2_title="Volume",
    )
    fig.update_xaxes(showgrid=False, color="#91A4BD")
    fig.update_yaxes(showgrid=True, gridcolor="#1C2A3C", color="#91A4BD")
    fig.update_annotations(font={"color": "#DFE9F8"})
    fig.update_layout(
        title={
            "text": f"{symbol} ({currency})",
            "x": 0.01,
            "xanchor": "left",
            "font": {"size": 15},
        }
    )
    return fig


def _regime_stats_children(regime: dict[str, float]) -> list[html.Div]:
    items = [
        ("Vol 20D", f"{regime.get('vol_20d', 0.0):.2f}%"),
        ("Trend Score", f"{regime.get('trend_score', 0.0):+.2f}"),
        ("Drawdown YTD", f"{regime.get('drawdown_ytd', 0.0):.2f}%"),
    ]
    blocks = []
    for label, value in items:
        blocks.append(
            html.Div(
                [html.Div(label, style={"fontSize": "12px", "color": "#9CB2CE"}), html.Div(value, style={"fontSize": "18px", "fontWeight": "700"})],
                style={
                    "backgroundColor": "#0F1620",
                    "border": "1px solid #223247",
                    "borderRadius": "8px",
                    "padding": "10px",
                },
            )
        )
    return blocks


layout = html.Div(
    [
        dcc.Store(id="home-mock-store", data=MOCK_DATA),
        html.Div(
            [
                html.Div("BloomDash Home", style={"fontSize": "18px", "fontWeight": "700", "color": "#E8EEF7"}),
                html.Div(
                    [
                        dcc.Input(
                            id="home-search-input",
                            value="SPX",
                            debounce=True,
                            placeholder="Search ticker",
                            style={
                                "width": "160px",
                                "height": "34px",
                                "borderRadius": "7px",
                                "border": "1px solid #324C6D",
                                "padding": "0 10px",
                                "backgroundColor": "#0D1520",
                                "color": "#E4F1FF",
                            },
                        ),
                        dcc.RadioItems(
                            id="home-timeframe",
                            options=[{"label": label, "value": label} for label in ["1D", "5D", "1M", "6M", "1Y"]],
                            value="1M",
                            inline=True,
                            labelStyle={"marginRight": "10px"},
                            style={"color": "#D6E4F7", "fontSize": "13px"},
                        ),
                        dcc.RadioItems(
                            id="home-currency",
                            options=[{"label": label, "value": label} for label in ["EUR", "USD"]],
                            value="USD",
                            inline=True,
                            labelStyle={"marginRight": "10px"},
                            style={"color": "#D6E4F7", "fontSize": "13px"},
                        ),
                        html.Button("Watchlist", id="home-watchlist-btn", n_clicks=0, style=BUTTON_STYLE),
                        html.Button("Refresh", id="home-refresh-btn", n_clicks=0, style=BUTTON_STYLE),
                        html.Button("Settings", id="home-settings-btn", n_clicks=0, style=BUTTON_STYLE),
                    ],
                    style={"display": "flex", "gap": "10px", "alignItems": "center", "flexWrap": "wrap"},
                ),
            ],
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "zIndex": "1000",
                "backgroundColor": "#0A111A",
                "borderBottom": "1px solid #25384F",
                "padding": "10px 14px",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "gap": "12px",
                "flexWrap": "wrap",
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div("Market Snapshot", style={"fontSize": "16px", "fontWeight": "700", "marginBottom": "10px"}),
                        html.Div(
                            id="home-snapshot-cards",
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(170px, 1fr))",
                                "gap": "10px",
                            },
                        ),
                    ],
                    style=PANEL_STYLE,
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4("Movers", style={"marginTop": 0, "marginBottom": "8px"}),
                                html.Div("Top Gainers", style={"fontWeight": "600", "marginBottom": "6px"}),
                                dash_table.DataTable(
                                    id="home-gainers-table",
                                    columns=[
                                        {"name": "Ticker", "id": "symbol"},
                                        {"name": "Last", "id": "last"},
                                        {"name": "%Delta", "id": "pct_delta"},
                                    ],
                                    data=[],
                                    page_action="none",
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "padding": "8px",
                                        "backgroundColor": "#0F1620",
                                        "color": "#D9E6F6",
                                        "border": "1px solid #203046",
                                        "fontSize": "12px",
                                    },
                                    style_header={"backgroundColor": "#15263B", "fontWeight": "700", "border": "1px solid #2E4564"},
                                ),
                                html.Div("Top Losers", style={"fontWeight": "600", "margin": "12px 0 6px 0"}),
                                dash_table.DataTable(
                                    id="home-losers-table",
                                    columns=[
                                        {"name": "Ticker", "id": "symbol"},
                                        {"name": "Last", "id": "last"},
                                        {"name": "%Delta", "id": "pct_delta"},
                                    ],
                                    data=[],
                                    page_action="none",
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "padding": "8px",
                                        "backgroundColor": "#0F1620",
                                        "color": "#D9E6F6",
                                        "border": "1px solid #203046",
                                        "fontSize": "12px",
                                    },
                                    style_header={"backgroundColor": "#15263B", "fontWeight": "700", "border": "1px solid #2E4564"},
                                ),
                            ],
                            style=PANEL_STYLE,
                        ),
                        html.Div(
                            [
                                html.H4("Focus", id="home-focus-title", style={"marginTop": 0, "marginBottom": "8px"}),
                                dcc.Graph(id="home-focus-chart", config={"displayModeBar": False}),
                                html.Div(
                                    "Regime stats",
                                    style={"fontWeight": "600", "fontSize": "14px", "margin": "8px 0 6px 0"},
                                ),
                                html.Div(
                                    id="home-regime-stats",
                                    style={"display": "grid", "gridTemplateColumns": "repeat(3, minmax(90px, 1fr))", "gap": "8px"},
                                ),
                            ],
                            style=PANEL_STYLE,
                        ),
                        html.Div(
                            [
                                html.H4("News + Calendar", style={"marginTop": 0, "marginBottom": "8px"}),
                                html.Div(
                                    "News feed (market moving)",
                                    style={"fontWeight": "600", "marginBottom": "6px"},
                                ),
                                html.Div(
                                    id="home-news-feed",
                                    style={
                                        "maxHeight": "320px",
                                        "overflowY": "auto",
                                        "border": "1px solid #203046",
                                        "borderRadius": "8px",
                                        "padding": "8px",
                                        "backgroundColor": "#0F1620",
                                        "fontSize": "13px",
                                    },
                                ),
                                html.Div("Mini Macro Calendar", style={"fontWeight": "600", "margin": "12px 0 6px 0"}),
                                dash_table.DataTable(
                                    id="home-calendar-table",
                                    columns=[
                                        {"name": "Day", "id": "day"},
                                        {"name": "Time", "id": "time"},
                                        {"name": "Event", "id": "event"},
                                        {"name": "Impact", "id": "impact"},
                                    ],
                                    data=[],
                                    page_action="none",
                                    style_table={"overflowX": "auto"},
                                    style_cell={
                                        "padding": "8px",
                                        "backgroundColor": "#0F1620",
                                        "color": "#D9E6F6",
                                        "border": "1px solid #203046",
                                        "fontSize": "12px",
                                        "textAlign": "left",
                                    },
                                    style_header={"backgroundColor": "#15263B", "fontWeight": "700", "border": "1px solid #2E4564"},
                                ),
                            ],
                            style=PANEL_STYLE,
                        ),
                    ],
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                        "gap": "10px",
                    },
                ),
                html.Div(
                    [
                        html.Div("Data status", style={"fontWeight": "700", "fontSize": "15px", "marginBottom": "8px"}),
                        dash_table.DataTable(
                            id="home-data-status-table",
                            columns=[
                                {"name": "Source", "id": "source"},
                                {"name": "Last refresh", "id": "last_refresh"},
                                {"name": "Errors", "id": "errors"},
                                {"name": "Avg API latency (ms)", "id": "avg_latency_ms"},
                            ],
                            data=[],
                            page_action="none",
                            style_table={"overflowX": "auto"},
                            style_cell={
                                "padding": "8px",
                                "backgroundColor": "#0F1620",
                                "color": "#D9E6F6",
                                "border": "1px solid #203046",
                                "fontSize": "12px",
                            },
                            style_header={"backgroundColor": "#15263B", "fontWeight": "700", "border": "1px solid #2E4564"},
                        ),
                        html.Div(id="home-generated-at", style={"marginTop": "8px", "fontSize": "12px", "color": "#9CB2CE"}),
                    ],
                    style=PANEL_STYLE,
                ),
            ],
            style={
                "marginTop": "88px",
                "padding": "14px",
                "display": "grid",
                "gap": "10px",
                "backgroundColor": "#0B111A",
                "minHeight": "100vh",
                "color": "#E6F0FF",
            },
        ),
    ],
)


@callback(
    Output("home-mock-store", "data"),
    Input("home-refresh-btn", "n_clicks"),
    State("home-mock-store", "data"),
    prevent_initial_call=True,
)
def _refresh_mock_data(n_clicks: int, current_data: dict[str, Any] | None) -> dict[str, Any]:
    if not n_clicks:
        return current_data or MOCK_DATA
    return _build_mock_payload(seed_offset=n_clicks)


@callback(
    Output("home-snapshot-cards", "children"),
    Output("home-gainers-table", "data"),
    Output("home-losers-table", "data"),
    Output("home-focus-chart", "figure"),
    Output("home-focus-title", "children"),
    Output("home-regime-stats", "children"),
    Output("home-news-feed", "children"),
    Output("home-calendar-table", "data"),
    Output("home-data-status-table", "data"),
    Output("home-generated-at", "children"),
    Input("home-mock-store", "data"),
    Input("home-search-input", "value"),
    Input("home-timeframe", "value"),
    Input("home-currency", "value"),
)
def _render_home_view(
    payload: dict[str, Any] | None,
    ticker_query: str | None,
    timeframe: str,
    currency: str,
) -> tuple[list[html.Div], list[dict[str, str]], list[dict[str, str]], go.Figure, str, list[html.Div], list[html.Div], list[dict[str, str]], list[dict[str, Any]], str]:
    payload = payload or MOCK_DATA
    snapshot = payload["snapshot"]
    by_symbol = {item["symbol"]: item for item in snapshot}

    focus_symbol = (ticker_query or "").strip().upper()
    if focus_symbol not in by_symbol:
        focus_symbol = "SPX" if "SPX" in by_symbol else snapshot[0]["symbol"]

    points = TIMEFRAME_POINTS.get(timeframe, TIMEFRAME_POINTS["1M"])
    currency_factor = payload["fx"]["EUR"] if currency == "EUR" else payload["fx"]["USD"]

    snapshot_cards: list[html.Div] = []
    for item in snapshot:
        price_series = [point * currency_factor for point in item["series"][-points:]]
        delta = item["delta"] * currency_factor
        positive = item["pct_delta"] >= 0
        snapshot_cards.append(
            html.Div(
                [
                    html.Div(item["symbol"], style={"fontWeight": "700", "fontSize": "13px", "marginBottom": "2px"}),
                    html.Div(_format_price(item["last"] * currency_factor, currency), style={"fontSize": "18px", "fontWeight": "700"}),
                    html.Div(
                        _format_delta(delta, item["pct_delta"], currency),
                        style={"fontSize": "12px", "fontWeight": "600", "color": "#49D17D" if positive else "#E2616B"},
                    ),
                    dcc.Graph(
                        figure=_sparkline_figure(price_series, positive),
                        config={"displayModeBar": False},
                        style={"height": "58px"},
                    ),
                ],
                style={
                    "backgroundColor": "#111923",
                    "border": "1px solid #223247",
                    "borderRadius": "8px",
                    "padding": "8px",
                },
            )
        )

    def _mover_row(item: dict[str, Any]) -> dict[str, str]:
        return {
            "symbol": item["symbol"],
            "last": _format_price(item["last"] * currency_factor, currency),
            "pct_delta": f"{item['pct_delta']:+.2f}%",
        }

    gainers_table = [_mover_row(row) for row in payload["movers"]["gainers"]]
    losers_table = [_mover_row(row) for row in payload["movers"]["losers"]]

    focus_item = by_symbol[focus_symbol]
    focus_series = [point * currency_factor for point in focus_item["series"][-points:]]
    focus_volume = focus_item["volume"][-points:]
    focus_chart = _focus_figure(focus_symbol, focus_series, focus_volume, currency)
    regime_children = _regime_stats_children(payload["regime"].get(focus_symbol, {}))

    news_children = [
        html.Div(
            [
                html.Span(f"{news['time']} ", style={"color": "#8FA4C0", "fontWeight": "600"}),
                html.Span(f"[{news['source']}] ", style={"color": "#79B8FF"}),
                html.Span(news["headline"]),
            ],
            style={"padding": "6px 4px", "borderBottom": "1px solid #1E2C40"},
        )
        for news in payload["news"][:10]
    ]

    data_status = [
        {
            "source": row["source"],
            "last_refresh": row["last_refresh"],
            "errors": row["errors"],
            "avg_latency_ms": row["avg_latency_ms"],
        }
        for row in payload["data_status"]
    ]

    generated_at = datetime.fromisoformat(payload["generated_at"]).astimezone(timezone.utc)
    generated_txt = f"Mock payload generated at {generated_at.strftime('%Y-%m-%d %H:%M UTC')}."

    return (
        snapshot_cards,
        gainers_table,
        losers_table,
        focus_chart,
        f"Focus: {focus_symbol}",
        regime_children,
        news_children,
        payload["calendar"],
        data_status,
        generated_txt,
    )
