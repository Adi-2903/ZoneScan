# 03 — System Architecture

## Architectural style

Start with a **modular monolith plus a dedicated market-scoring worker**, not microservices. The dominant live computation is roughly the same for 200–250 instruments whether there are 10 or 10,000 users. Compute it once, persist a snapshot, cache the latest board, and serve many readers cheaply.

The Financial Intelligence workspaces (Company, Relationship, Supply Chain, News, Research) add a separate **document ingestion pipeline** that runs on a schedule, not in real time. It processes official filings, financial statements, and licensed data into normalized storage. This pipeline is architecturally isolated from the live market-scoring worker.

## Proposed stack

| Layer | Default | Notes |
|---|---|---|
| Web | Next.js App Router, React, TypeScript | SSR for public pages; client components for live terminal interactions |
| Styling | Tailwind CSS with CSS variables | Dark-first, light theme supported |
| Charts | TradingView Lightweight Charts (market); Recharts (fundamentals KPI charts) | Check current version, license and attribution before use; Recharts is a candidate, not yet adopted |
| API | Python 3.12 + FastAPI | REST plus SSE; typed request/response schemas |
| Algorithm | Python, NumPy; pandas where useful | Pure deterministic functions |
| Primary DB | PostgreSQL | Accounts, billing, configuration, journal, content, snapshots metadata, financial data |
| Time-series storage | PostgreSQL; evaluate TimescaleDB only after compatibility/licensing/operations review | Candles and score snapshots |
| Document store | PostgreSQL (JSONB) initially; evaluate a dedicated document DB only when volume justifies it | Financial statement extracts, filing metadata, extracted text |
| Cache/pub-sub | Redis | Current board, status, event publishing, short-lived data cache |
| Jobs | Redis Streams/Celery or equivalent | Notifications, invoices, scheduled ingestion, housekeeping |
| Payments | Razorpay, subject to merchant approval | Webhooks are authoritative; production activation gated |
| CDN/WAF | Cloudflare or equivalent | Static caching, basic edge controls |
| Deploy | Docker; CI via GitHub Actions | Start simply, document rollback and environment separation |

Pin actual dependency versions when scaffolding the repo.

## Logical data flow — Market Intelligence (existing)

```text
Licensed provider / permitted development fixture
                    |
                    v
          Provider adapter layer
                    |
                    v
        Tick normalizer + validator
                    |
                    v
         1-minute candle builder
                    |
                    v
  Indicators + market structure + zones
                    |
                    v
    Scoring / classification / ranking
                    |
          +---------+----------+
          |                    |
          v                    v
   Redis current board    Historical snapshots
          |                    |
          v                    v
    REST API + SSE      PostgreSQL/time-series DB
          |
          v
   Next.js client terminal (Workspace 1)
```

## Logical data flow — Financial Intelligence (planned)

```text
Official & Licensed Sources
  BSE XBRL filings          NSE company master
  BSE/NSE announcements     MCA21 filings
  Licensed financial vendor  Commodity price feed
          |                         |
          v                         v
   Ingestion Scheduler       Provider Adapter Layer
   (cron-based, not live)    (same isolation pattern
          |                   as market data adapter)
          v                         |
  Extraction & Parsing             v
  (XBRL tag parsing,         Normalization & Validation
   PDF structured extract,   (unit, period, currency,
   API response normalization) quality flags)
          |
          v
  Entity Matching & Deduplication
  (ISIN/CIN linking, name disambiguation,
   period alignment across sources)
          |
          v
  Evidence Tagger
  (assign Disclosed/Inferred/Unconfirmed
   status to every stored data point)
          |
          v
  Normalized Document Store (PostgreSQL)
  (companies, financials, relationships,
   filings, segments, commodities, news)
          |
          v
  REST API (/api/v1/companies/..., /api/v1/filings/...)
          |
          v
  Next.js client terminal (Workspaces 2–6)
```

The Financial Intelligence pipeline is **read-heavy and schedule-driven**. It does not need to update within seconds; daily or per-filing ingestion is the target cadence. It must not block or share compute resources with the real-time market scoring worker.

## Recommended code boundaries

The final repository may use a layout like this; refine only after the initial scaffold establishes the concrete package manager/build system.

```text
/
  AGENTS.md
  README.md
  docs/
  apps/
    web/                   # Next.js app (all workspaces)
  services/
    api/                   # FastAPI endpoints, auth/billing, market + company APIs
    market-worker/         # provider adapter, candles, algorithms, board publishing
    ingestion-worker/      # scheduled financial data ingestion pipeline (planned)
  packages/
    contracts/             # shared API schemas/generated types if valuable
  infra/
    docker/                # local/dev containers and deployment templates
  tests/
    fixtures/              # synthetic candles and deterministic market sessions
```

Do not create this entire structure just to store docs. Create code directories only when implementation begins. The `ingestion-worker` does not yet exist and must not be scaffolded until Financial Intelligence data rights are confirmed.

## Core services/modules

**Market Intelligence (existing/in progress):**
- **Instrument universe:** daily eligible symbols, exchange IDs/tokens, sector mapping, futures contract mapping and active status.
- **Provider adapter:** abstracts live and historical data access, contract constraints and feed health.
- **Candle builder:** produces deterministic OHLCV/OI aggregates and flags filled/gap candles.
- **Indicator/structure engine:** ATR, daily sigma, RVOL, VWAP, EMA, ADX, swings, BOS, zones and liquidity levels.
- **Scoring engine:** score components, choppy gate, directional class, smoothing and ranking hysteresis.
- **Board publisher:** writes a single board snapshot per minute, with timestamps and parameter version.
- **API:** authenticated REST access, entitlement enforcement, market status, board reads and SSE.
- **Membership:** authentication, plans, entitlements, payments and invoices.
- **Member tools:** watchlist, alerts, journal, learning.
- **Admin/operations:** provider health, parameter versioning, user/billing support, content and audit logs.

**Financial Intelligence (planned — do not implement before data rights gates pass):**
- **Ingestion scheduler:** triggers per-source ingestion jobs on a defined schedule (BSE announcements: near-real-time if API permitted; financial statements: daily/quarterly).
- **Filing parser:** extracts structured data from XBRL or PDF sources; records extraction method and confidence.
- **Entity resolver:** links company identifiers (ISIN, CIN, BSE code, NSE symbol) into a canonical company record.
- **Evidence tagger:** assigns Disclosed/Inferred/Unconfirmed status and source provenance to every stored field.
- **Financial normalizer:** aligns periods, currencies, and units across sources; flags restatements.
- **Company API:** read-only endpoints for company profile, financial statements, relationships, segments.
- **Filing API:** filing feed, annual report metadata, commodity prices, news items.
- **Research persistence:** user-owned layouts, notes, comparison configurations.

## Single-writer and determinism invariants

- A single logical worker owns board publication. A standby can take over but must not publish competing board states.
- The worker retains rolling state in memory for hot-path calculation; persistent storage is the source for replay/backfill and recovery.
- Reprocessing the same complete input candles with the same parameter version must produce the same output.
- Each board snapshot records `as_of`, `data_as_of`, session date, source status, algorithm version and parameter version.
- Replay/backtest invokes the same algorithm package used by live scoring.
- A feed gap must not be disguised by filling data without a `filled_flag` and quality rules.
- Financial Intelligence data is immutable per extraction event; updates create new versioned records, not silent overwrites.

## API transport

Use REST for snapshots and changes initiated by a user. Use Server-Sent Events for one-way board/status updates. SSE should send event IDs and support reconnect with `Last-Event-ID`.

Financial Intelligence endpoints are REST only (no live stream needed). Response times may be higher than market endpoints due to data volume; use pagination, field selection, and explicit caching headers.

WebSockets are not needed for the first version unless a measured requirement justifies bi-directional, high-frequency interaction.

API routes are versioned under `/api/v1` for all workspaces.

### Local fixture API prototype

The optional FastAPI boundary exposes read-only status, board, and stock-detail routes over `AnalyticsService`. The service aggregates fixed synthetic 1-minute fixture candles, calculates point-in-time indicators, then invokes the shared chronological replay and board implementation once per process. Requests read its cached immutable snapshot. All fixture output is labelled synthetic. No live provider, persistence, authentication, entitlement enforcement, or production worker is implemented in the prototype.

The optional Upstox historical sample remains a separate command/workflow and a provisional local development adapter only. See `docs/04_MARKET_DATA.md`.

## Environments

- `local`: synthetic fixtures only by default; no production credentials.
- `development`: non-public; use data sources only under their permitted terms.
- `staging`: payment test mode and synthetic/specially licensed test data.
- `production`: approved licensed market data, reviewed legal/compliance state, production secrets, monitoring, backups and a rollback plan.

Financial Intelligence pipeline environments follow the same separation. A production ingestion worker must not be connected to a development database.

## Performance targets

- Market scoring cycle: publish within 5 seconds of the minute close at p95 during the supported market session.
- Financial Intelligence page load: initial company profile within 2 seconds for a cached response; first-load ingestion completion is asynchronous and must not block the UI.
- API response time for financial data endpoints: p95 under 500ms for cached results; complex queries may be pre-computed and stored.
