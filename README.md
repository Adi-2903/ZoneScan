# ZoneScan — Project Documentation

> **Working codename only.** The final product name, domain, logo, and visual identity are not approved. Run trademark/domain checks before public branding.

## Current status

This repository contains the ZoneScan documentation baseline and an initial, fixture-backed Python analytical foundation. No market feed, credentials, payments, or production infrastructure are configured. The current code is a prototype, not a production scanner.

ZoneScan is an original product concept informed by public research into the order-block/liquidity scanner category. It must not copy another product's branding, text, code, testimonials, proprietary formula, or visual assets.

## Read in this order

1. [`AGENTS.md`](./AGENTS.md) — mandatory instructions for AI coding agents and contributors.
2. [`docs/00_PROJECT_BRIEF.md`](./docs/00_PROJECT_BRIEF.md) — one-page product and scope overview.
3. [`docs/12_DECISIONS.md`](./docs/12_DECISIONS.md) — decisions agents should not reopen casually.
4. [`docs/13_OPEN_QUESTIONS.md`](./docs/13_OPEN_QUESTIONS.md) — unknowns, blockers, and items requiring an owner.
5. Read the task-specific docs from the index below before implementing a feature.

## Documentation map

| File | What it governs |
|---|---|
| [`01_PRODUCT_REQUIREMENTS.md`](./docs/01_PRODUCT_REQUIREMENTS.md) | Feature scope, priorities, acceptance criteria |
| [`02_UX_FLOWS.md`](./docs/02_UX_FLOWS.md) | Screens, user journeys, loading/error/market states |
| [`03_ARCHITECTURE.md`](./docs/03_ARCHITECTURE.md) | Service boundaries, stack, data flow, architectural rules |
| [`04_MARKET_DATA.md`](./docs/04_MARKET_DATA.md) | Data requirements, provider/licensing gate, ingestion |
| [`05_ALGORITHMS.md`](./docs/05_ALGORITHMS.md) | Scoring, order blocks, liquidity levels, choppy filter |
| [`06_API_CONTRACTS.md`](./docs/06_API_CONTRACTS.md) | Versioned API, response shapes, live stream |
| [`07_DATA_MODEL.md`](./docs/07_DATA_MODEL.md) | Suggested relational and time-series schema |
| [`08_SECURITY_PRIVACY_COMPLIANCE.md`](./docs/08_SECURITY_PRIVACY_COMPLIANCE.md) | Security, privacy, data licensing, regulatory review |
| [`09_TESTING_BACKTESTING.md`](./docs/09_TESTING_BACKTESTING.md) | Tests, replay, backtests, evaluation metrics |
| [`10_DEPLOYMENT_OPERATIONS.md`](./docs/10_DEPLOYMENT_OPERATIONS.md) | Market-day operations, monitoring, incident behavior |
| [`11_ROADMAP.md`](./docs/11_ROADMAP.md) | Sequencing and release gates |
| [`14_DESIGN_SYSTEM.md`](./docs/14_DESIGN_SYSTEM.md) | Interface principles, states, accessibility |
| [`15_GLOSSARY.md`](./docs/15_GLOSSARY.md) | Shared vocabulary |
| [`16_REFERENCES.md`](./docs/16_REFERENCES.md) | Research links and source notes |
| [`DEFINITION_OF_DONE.md`](./docs/DEFINITION_OF_DONE.md) | Definition of done for every implementation task |

## Product in one sentence

A mobile-first browser-based analytics terminal that ranks NSE F&O equity stocks by transparent, rule-based intraday strength and displays potential price zones and market context; it does **not** place orders or tell users what to buy or sell.

## Non-negotiable launch gates

- **Market-data rights:** No public or paid live-data product until the selected provider/exchange agreement expressly allows the required display, derived analytics, storage, and redistribution.
- **Regulatory review:** Obtain written advice from qualified Indian securities counsel on the classification of the product and its ranked market outputs before public launch or monetization.
- **Algorithm validation:** Do not publish hit rates, accuracy claims, or performance claims until a leakage-resistant, out-of-sample backtest supports them.
- **Truthful data status:** Never label delayed, missing, synthetic, or stale data as live.

See [`docs/08_SECURITY_PRIVACY_COMPLIANCE.md`](./docs/08_SECURITY_PRIVACY_COMPLIANCE.md) and [`docs/11_ROADMAP.md`](./docs/11_ROADMAP.md).

## Development foundation

Python 3.12 or newer is required. From `services/api`, run the standard-library test suite with `python -m unittest discover -s tests` (set `PYTHONPATH=src` in environments that do not install the package). To run the optional HTTP boundary, install `pip install -e ".[api]"`, then run `uvicorn zonescan.app:app --app-dir src --reload`. The app exposes `/health`, `/api/v1/market/status`, `/api/v1/dev/market`, `/api/v1/board?side=bull`, `/api/v1/board?side=bear`, and `/api/v1/stocks/SYNBULL` or `/api/v1/stocks/SYNBEAR`. The analytical endpoints build one fixed synthetic replay per process; the first analytical request takes several seconds. Every response labels the data synthetic; these are not live prices or historical performance evidence. No credentials or network access are needed. The optional Upstox historical sample remains separate and does not change API mode.

The current foundation includes candle validation, a provider protocol, deterministic synthetic fixture data, confirmed swing detection, Strength Score calculation, order-block detection/lifecycle, chronological replay, indicators, liquidity levels, choppy filtering, Early-Move Score, and timestamped boards. Run tests from `services/api` with `$env:PYTHONPATH='src'; python -m unittest discover -s tests -v` in PowerShell. To see a synthetic score breakdown, run `$env:PYTHONPATH='src'; python examples/score_synthetic.py`. To see replay zone creation, test, and mitigation, run `$env:PYTHONPATH='src'; python examples/replay_synthetic.py`. The local API is fixture-backed only; licensed data ingestion, persistence, authentication, and public service remain unimplemented.
