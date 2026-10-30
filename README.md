# ZoneScan — Financial Intelligence Terminal

> **Working codename only.** The final product name, domain, logo, and visual identity are not approved. Run trademark/domain checks before public branding.

## What is this?

ZoneScan is a **Financial Intelligence Terminal** for Indian markets — a mobile-first, browser-based platform combining intraday market analytics with company intelligence, relationship mapping, supply-chain context, and regulatory filing research in one workspace.

**Design principle:** Bloomberg-level information depth, understandable through progressive disclosure.

## Current status

| Component | Status |
|---|---|
| Algorithm prototype | ✅ Implemented — 115 tests passing |
| Synthetic API (FastAPI) | ✅ Running — fixture data only |
| Frontend dashboard | ✅ Running — synthetic data only |
| Live market data | 🔴 **Blocked** — data provider and licence not yet selected (Q-001) |
| Financial Intelligence workspaces | 📋 **Planning** — documented; blocked on data rights (FI-001 to FI-012) |
| Public launch | 🔴 **Blocked** — requires Gate 1 (data), Gate 2 (algorithm), legal review (Q-002) |

**This is a prototype, not a production scanner.** No market feed, credentials, payments, or production infrastructure are configured. All current data is synthetic and explicitly labelled.

## Six workspaces

| # | Workspace | Status |
|---|---|---|
| 1 | **Market Intelligence** — board, scores, zones, X-Ray | Prototype (synthetic) |
| 2 | **Company Intelligence** — financials, valuation, shareholding | Planning only |
| 3 | **Relationship Intelligence** — suppliers, customers, ownership | Planning only |
| 4 | **Supply Chain & Commodities** — raw materials, commodity prices | Planning only |
| 5 | **News & Filings** — announcements, annual reports, filings | Planning only |
| 6 | **Research Workspace** — draggable panels, notes, comparison | Planning only |

## Read in this order

1. [`AGENTS.md`](./AGENTS.md) — mandatory instructions for AI coding agents and contributors.
2. [`docs/00_PROJECT_BRIEF.md`](./docs/00_PROJECT_BRIEF.md) — product and scope overview.
3. [`docs/12_DECISIONS.md`](./docs/12_DECISIONS.md) — accepted product and algorithm decisions.
4. [`docs/13_OPEN_QUESTIONS.md`](./docs/13_OPEN_QUESTIONS.md) — blockers and open items.
5. Task-specific documents from the index below.

## Documentation map

| File | What it governs |
|---|---|
| [`01_PRODUCT_REQUIREMENTS.md`](./docs/01_PRODUCT_REQUIREMENTS.md) | Feature scope (P0–P3), priorities, acceptance criteria |
| [`02_UX_FLOWS.md`](./docs/02_UX_FLOWS.md) | Six workspaces, user journeys, screen inventory, all states |
| [`03_ARCHITECTURE.md`](./docs/03_ARCHITECTURE.md) | Service boundaries, stack, market + FI data flows |
| [`04_MARKET_DATA.md`](./docs/04_MARKET_DATA.md) | Market data requirements, provider evaluation, ingestion |
| [`05_ALGORITHMS.md`](./docs/05_ALGORITHMS.md) | Scoring, order blocks, liquidity levels, choppy filter |
| [`06_API_CONTRACTS.md`](./docs/06_API_CONTRACTS.md) | Versioned API, response shapes, live stream |
| [`07_DATA_MODEL.md`](./docs/07_DATA_MODEL.md) | Market + Financial Intelligence relational schema |
| [`08_SECURITY_PRIVACY_COMPLIANCE.md`](./docs/08_SECURITY_PRIVACY_COMPLIANCE.md) | Security, privacy, data licensing, regulatory review |
| [`09_TESTING_BACKTESTING.md`](./docs/09_TESTING_BACKTESTING.md) | Tests, replay, backtests, evaluation metrics |
| [`10_DEPLOYMENT_OPERATIONS.md`](./docs/10_DEPLOYMENT_OPERATIONS.md) | Market-day operations, monitoring, incident behavior |
| [`11_ROADMAP.md`](./docs/11_ROADMAP.md) | Gates, phases, and release sequencing |
| [`14_DESIGN_SYSTEM.md`](./docs/14_DESIGN_SYSTEM.md) | Interface principles, evidence status, accessibility |
| [`15_GLOSSARY.md`](./docs/15_GLOSSARY.md) | Shared vocabulary |
| [`16_REFERENCES.md`](./docs/16_REFERENCES.md) | Research links and source notes |
| [`17_CHANGELOG.md`](./docs/17_CHANGELOG.md) | Implementation history |
| [`18_DATA_PROVIDER_EVALUATION.md`](./docs/18_DATA_PROVIDER_EVALUATION.md) | Market data provider evaluation matrix |
| [`19_FINANCIAL_INTELLIGENCE.md`](./docs/19_FINANCIAL_INTELLIGENCE.md) | Full Financial Intelligence module specification |

## Non-negotiable launch gates

- **Market-data rights:** No public live-data product until a written agreement expressly allows display, derived analytics, storage, and redistribution.
- **Financial data rights:** No company financials or filing data in a paid product without confirmed licensed source.
- **Regulatory review:** Written advice from qualified Indian securities counsel before any public launch or monetization.
- **Algorithm validation:** No performance claims without a leakage-resistant, out-of-sample backtest.
- **Truthful data status:** Never label synthetic, inferred, delayed, or unconfirmed data as live or verified.

## Local development setup

### Backend (Python 3.12+, from `services/api`)

```powershell
pip install -e ".[api]"
$env:PYTHONPATH = "src"
uvicorn zonescan.app:app --app-dir src --reload
```

### Frontend (Node.js 20.9+, from `apps/web`)

```powershell
Copy-Item .env.example .env.local
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:3000`. The API pre-warms its synthetic replay cache on startup (~75s); all endpoints respond immediately after startup completes.

### Tests (from `services/api`)

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

115 tests, all passing. Runs in ~70s. No credentials or network access required.

All data is synthetic. The dashboard identifies itself as synthetic on every screen.
