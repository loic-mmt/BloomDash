# BloomDash — Bloomberg-like Amateur Terminal (Dash)

BloomDash est un terminal “Bloomberg-like” **amateur** construit en **Python + Dash + C++**.  
Objectif : fournir une interface type terminal pour **explorer des instruments**, visualiser des **marchés multi-actifs**, faire du **screening**, des **stats de risque**, et (optionnellement) du **backtesting** — avec une architecture propre (data layer + cache + DB).

> ⚠️ Projet éducatif : pas de garantie de qualité des données, pas de conseil en investissement.

---

## Fonctionnalités

### Core (MVP)
- **Instrument Page** : OHLCV, rendements, volatilité, drawdowns, stats rapides
- **Markets** : snapshot multi-asset (Equities / Rates / FX / Crypto)
- **Watchlists** : listes personnalisées + perf (1D/1W)
- **Screener** : filtres basés sur market data (perf, vol, trend/mean reversion scores)
- **Admin / Data Status** : état ingestion, erreurs, couverture, refresh manuel

### Optionnel (phase 2)
- **Factor Lab** : scores (momentum, low vol…), déciles, corrélations
- **Backtester** : stratégies simples (mean reversion / trend), equity curve, métriques
- **Portfolio & Risk** : positions CSV, allocation, VaR, corr matrix, stress tests
- **Macro** : séries FRED/BCE, chart multi-séries
- **News** : headlines filtrables (GDELT)

---

## Sources de données (free tier / publiques)

- **Prix historiques** : Stooq (download)  / YahooFinance
- **Macro US** : FRED API (clé)  
- **Macro/FX EUR** : BCE SDMX API  
- **Crypto** : CoinGecko / Binance (market data)  
- **News** : GDELT  
- **(Optionnel) Quotes actions** : Finnhub (free tier, limité)

---

## Stack technique

- **UI** : Dash, Plotly, dash-bootstrap-components
- **Data** : pandas, numpy, requests/httpx
- **DB** : PostgreSQL (SQLAlchemy + psycopg2)
- **Cache** : Redis
- **Scheduling** : APScheduler (ou cron)
- **Tests** : pytest
- **Optionnel** : scraping (BeautifulSoup + lxml / Playwright), validation (pydantic), retry (tenacity)

---

## Pré-requis
- **Python 3.13 recommandé** (évite des incompatibilités avec certaines libs scientifiques)

---

## Installation

### 1) Cloner le repo
```bash
git clone <REPO_URL>
cd bloomdash