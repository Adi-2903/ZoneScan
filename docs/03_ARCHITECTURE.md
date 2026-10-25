# 03 — System Architecture

## Architectural style

Start with a **modular monolith plus a dedicated market-scoring worker**, not microservices. The dominant live computation is roughly the same for 200–250 instruments whether there are 10 or 10,000 users. Compute it once, persist a snapshot, cache the latest board, and serve many readers cheaply.

## Proposed stack

| Layer | Default | Notes |
|---|---|---|
| Web | Next.js App Router, React, TypeScript | SSR for public pages; client components for live terminal interactions |
| Styling | Tailwind CSS with CSS variables | Dark-first, light theme supported |
| Charts | TradingView Lightweight Charts or equivalent | Check current version, license and attribution before use |
| API | Python 3.12 + FastAPI | REST plus SSE; typed request/response schemas |
| Algorithm | Python, NumPy; pandas where useful | Pure deterministic functions; avoid unnecessary dataframe work in each hot-path step |
| Primary DB | PostgreSQL | Accounts, billing, configuration, journal, content, snapshots metadata |
| Time-series storage | PostgreSQL; evaluate TimescaleDB only after compatibility/licensing/operations review | Candles and snapshots; no hard dependency until load/retention tests justify it |
| Cache/pub-sub | Redis | Current board, status, event publishing, short-lived data cache |
| Jobs | Redis Streams/Celery or equivalent | Notifications, invoices, housekeeping; choose one when implementation starts |
| Payments | Razorpay, subject to merchant approval | Webhooks are authoritative; production activation gated |
| CDN/WAF | Cloudflare or equivalent | Static caching, basic edge controls |
| Deploy | Docker; CI via GitHub Actions | Start simply, document rollback and environment separation |

Pin actual dependency versions when scaffolding the repo. Do not assume that a package's latest version is compatible with every plugin; validate the chosen versions in CI.

## Logical data flow

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
   Next.js client terminal
```

The provider adapter isolates vendor-specific authentication, symbol IDs, field names, rate limits, reconnects, and licensing assumptions. The algorithm must depend on normalized internal models, not provider-specific payloads.

## Recommended code boundaries

The final repository may use a layout like this; refine only after the initial scaffold establishes the concrete package manager/build system.

```text
/
  AGENTS.md
  README.md
  docs/
  apps/
    web/                 # Next.js app
  services/
    api/                 # FastAPI endpoints and auth/billing integration
    market-worker/       # provider adapter, candles, algorithms, board publishing
  packages/
    contracts/           # shared API schemas/generated types if valuable
  infra/
    docker/              # local/dev containers and deployment templates
  tests/
    fixtures/            # synthetic candles and deterministic market sessions
```

Do not create this entire structure just to store docs. Create code directories only when implementation begins.

## Core services/modules

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

## Single-writer and determinism invariants

- A single logical worker owns board publication. A standby can take over but must not publish competing board states.
- The worker retains rolling state in memory for hot-path calculation; persistent storage is the source for replay/backfill and recovery.
- Reprocessing the same complete input candles with the same parameter version must produce the same output.
- Each board snapshot records `as_of`, `data_as_of`, session date, source status, algorithm version and parameter version.
- Replay/backtest invokes the same algorithm package used by live scoring.
- A feed gap must not be disguised by filling data without a `filled_flag` and quality rules.

## API transport

Use REST for snapshots and changes initiated by a user. Use Server-Sent Events for one-way board/status updates. SSE should send event IDs and support reconnect with `Last-Event-ID`; when the client has missed too much history, tell it to reload a full snapshot.

WebSockets are not needed for the first version unless a measured requirement justifies bi-directional, high-frequency interaction.

### Local fixture API prototype

The optional FastAPI boundary exposes read-only status, board, and stock-detail routes over `AnalyticsService`. The service aggregates fixed synthetic 1-minute fixture candles, calculates point-in-time indicators, then invokes the shared chronological replay and board implementation once per process. Requests read its cached immutable snapshot instead of replaying the data again. The legacy health and development-snapshot routes remain available. This is local prototype behavior only: it has no live provider, persistence, authentication, entitlement enforcement, or production worker and must label all fixture output synthetic. The optional Upstox historical sample remains a separate command/workflow.

## Environments

- `local`: synthetic fixtures only by default; no production credentials.
- `development`: non-public; use data sources only under their permitted terms.
- `staging`: payment test mode and synthetic/specially licensed test data.
- `production`: approved licensed market data, reviewed legal/compliance state, production secrets, monitoring, backups and a rollback plan.

## Performance target

Target the minute processing cycle to publish within 5 seconds of the minute close at p95 during the supported market session. Instrument each stage (ingestion, candle finalization, indicators, zone detection, scoring, persistence, push). If a stage exceeds budget, diagnose using metrics rather than prematurely adding distributed architecture.
