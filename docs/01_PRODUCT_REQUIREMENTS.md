# 01 — Product Requirements

**Status:** Baseline specification; acceptance criteria are targets until validated in implementation.
**Priority:** P0 = core MVP; P1 = first expansion; P2 = later; P3 = Financial Intelligence modules.
**Release gates can block any priority.**

---

## P0 — Core MVP (Market Intelligence)

### PR-001: Market status and board

The home/board screen must present the top 20 eligible bullish and top 20 eligible bearish NSE F&O equity stocks, updated once per completed minute during the defined market session.

Each row must include: rank, symbol, last price, percentage change, strength score, score timestamp, sector, and rank/trend movement versus the prior board snapshot. Tap/click opens the stock detail chart. Choppy symbols are excluded from the ranked lists and are visible only in market-wide counts/diagnostics.

**Acceptance:**
- Board data is generated server-side from one authoritative scoring cycle.
- Board response includes `as_of`, market state, settling state, data quality status, and algorithm version.
- Rows are sorted deterministically, with documented tie-breaks.
- No row is rendered as live if its source data is stale or synthetic.
- When market is closed, show the last completed session snapshot with its timestamp and a visible closed banner.

### PR-002: Settling state

The board must show a `settling` status during the opening window because volume, market structure, and OI inputs are not yet mature. The proposed default is from 09:15 through 09:25 IST. This is a configurable rule, not a claim that all markets or all symbols have reliable data by 09:25.

**Acceptance:** During settling, the UI visibly labels the board and never implies that the ranking is final. Transition to normal only when session-time and data-readiness checks both pass.

### PR-003: Stock detail chart and setup card

Show candlesticks with 1m, 5m, 15m, and daily timeframes; 5m is the default. The chart overlays relevant order-block zones, support/resistance, and unswept liquidity levels. A levels strip repeats the numbers and makes them copyable. Display zone state: Fresh, Tested, or Mitigated/History.

**Acceptance:** Each line/zone has a label, a timestamp/formation origin where applicable, and an exact numeric value. If no valid zone exists, display an explicit no-zone state; never fabricate a zone to fill the card. Chart data must correspond to the stated instrument and timeframe.

### PR-004: Rule-based order-block engine

Detect order blocks using the rules in `05_ALGORITHMS.md`. The engine must only use confirmed swings and completed candles. It must track zone lifecycle and preserve historical state for replay.

**Acceptance:** Deterministic fixtures test bullish/bearish BOS, displacement, opposite-candle selection, FVG detection, retest, mitigation, overlap, and expiry. A replay of identical data with the same parameter version produces identical results.

### PR-005: Strength score and early-move score

Display a 0–100 Strength Score for ranking. An additional provisional Early-Move Score may be shown when all input requirements are satisfied. These scores are heuristic and require out-of-sample evaluation; they must not be marketed as accuracy or profit guarantees.

**Acceptance:** Every score is reproducible, has a parameter version, and has a human-readable component breakdown in detail view when available. Missing required inputs result in an explicit unavailable state, not silent imputation.

### PR-006: Basic Market X-Ray

The target product shows covered F&O stocks as a dot map based on percentage move, using direction/status labels in addition to color; it shows bullish, bearish, and choppy counts, leading/lagging sectors, and index context only after documented rules and data coverage are available. The current local prototype is fixture-scoped and must label fixture coverage as partial. Sector aggregation and index bias remain out of scope while the required rules are unresolved.

**Acceptance:** The visualization is keyboard/touch usable or has an accessible table alternative. Synthetic and partial-universe coverage are explicit.

### PR-007: Authentication and entitlements

Support Google sign-in and server-side user sessions. Entitlement layer must support preview, active subscription, expired, and admin states.

**Acceptance:** Unauthorized users cannot obtain paid board rows, zones, or protected endpoints by calling the API directly.

### PR-008: Marketing site and legal placeholders

Provide original landing, how-it-works, pricing, FAQ, about/contact, updates/blog, terms, privacy, refund, disclaimer, and disclosures pages.

**Acceptance:** Marketing claims match verified product behavior. No fake testimonials, unsupported performance claims, or placeholder legal wording published as final.

### PR-009: Data and system status

Distinguish normal, settling, closed/holiday, delayed, missing, synthetic/demo, and offline states.

**Acceptance:** Every market-data display has an `as_of` timestamp or an explicitly documented alternative.

---

## P1 — First expansion (Market Intelligence tools)

- Sector filters, price range, trading-value and volume-spike sorting.
- Sector flow badge for each stock: aligned, neutral, or against.
- Watchlist with live score, zone distance, and per-symbol notification settings.
- Alerts: enters top 20, price enters zone, zone becomes mitigated. Channels: browser push and Telegram first.
- Trading journal: trade form, setup tags, notes, screenshots, board snapshot, reports, CSV export.
- Learning library with short lessons and progress tracking.
- Full sector heatmap and click-through.
- PWA installability and push support after browser/platform requirements are tested.
- Production Razorpay integration with signed webhooks, invoice support, and refund/expiry flows.
- Admin panel for users, subscription state, payments, instruments, data health, content, algorithm parameters, support, and audit logs.

---

## P2 — Later (Market Intelligence)

- Minute-by-minute replay of historical sessions and a public methodology/backtest page.
- Moderated in-app discussion threads. Initial community, if any, uses a third-party private group only after legal review and written moderation policy.
- More languages, additional market segments, richer history.

---

## P3 — Financial Intelligence modules (planning phase; no implementation started)

These requirements are specified in detail in `docs/19_FINANCIAL_INTELLIGENCE.md`. Each is blocked until the corresponding data licensing and legal gates pass. Do not implement or display any data from these modules without confirming permitted use.

### PR-FI-001: Company Intelligence workspace

A company profile screen providing financial statements, profitability metrics, segment breakdown, valuation multiples, and shareholding pattern for NSE/BSE-listed companies.

**Acceptance:**
- Every data point carries source, as-of date, reporting period, and evidence status (Disclosed / Inferred / Unconfirmed / Unavailable).
- Financial statements use INR crores and show the exact reporting period.
- No financial data is displayed without confirming the licensed or publicly permitted data source.
- If a metric is not available, an explicit unavailable state is shown; zero is never substituted for missing data.
- Forward estimates are labelled "Analyst consensus — Unconfirmed" with source and date.
- Progressive disclosure: summary view → full statement on demand.

**Release gate:** FI-001 and FI-002 (data rights) must be resolved.

### PR-FI-002: Relationship Intelligence workspace

Supplier, customer, competitor, ownership, and subsidiary mapping derived exclusively from official filings and disclosures.

**Acceptance:**
- Every displayed relationship traces to a named source document (filing, annual report section, regulatory disclosure) with date.
- Evidence status is mandatory on every relationship node.
- Inferred relationships (not explicitly stated in a filing) show the derivation rule.
- No relationship is invented or assumed from industry convention without a filing reference.

**Release gate:** FI-001 (data rights), FI-002 (filing display rights).

### PR-FI-003: Supply Chain & Commodities workspace

Raw-material exposure profile derived from disclosed filings, with commodity price feed and evidence-based impact scenarios.

**Acceptance:**
- Commodity prices sourced from licensed or officially permitted data; never invented.
- Impact scenarios are deterministic calculations using disclosed exposure percentages; formula shown on demand.
- Scenario output labelled "Illustrative — not a forecast" with all assumptions explicit.
- No scenario is shown if the exposure percentage is not disclosed or clearly calculable from filings.

**Release gate:** FI-003 (commodity data rights), FI-001 (filing data rights).

### PR-FI-004: News & Filings workspace

Regulatory filings feed, annual report viewer, earnings call excerpts, and a relevant news feed.

**Acceptance:**
- Filing feed sourced from BSE/NSE announcements API under confirmed permitted use.
- Annual report quotes shown verbatim with document reference (filing, page, section).
- News items labelled Unconfirmed with source and date.
- Original filing PDFs linked; summarized text is supplementary, not a substitute.

**Release gate:** FI-004 (announcement API rights), FI-005 (PDF quote rights), FI-009 (earnings transcript rights).

### PR-FI-005: Research Workspace

Customizable draggable panel canvas with saved layouts, company comparison, notes, and relationship graph.

**Acceptance:**
- User layouts saved server-side per user account; inaccessible to other users.
- Panels can display any data already available in the system; no new data sources required for this workspace.
- Company comparison shows availability status per metric and per company; never shows unavailable data as zero.
- Notes are user-owned and exportable.

**Release gate:** Core authentication (PR-007) and at least one of Workspaces 2–5 implemented and verified.

---

## Explicit non-functional requirements

- Board should become interactive in under 2 seconds on a mid-range Android phone using a realistic 4G test profile.
- Landing page target: first contentful paint under 1.5 seconds on a defined 4G test profile.
- Board update target: publish within 5 seconds of a minute close at p95 during the supported session.
- Feed recovery target: reconnect within 10 seconds, then backfill gaps; if not recovered, surface delay.
- One scoring cycle must be safe to rerun idempotently.
- Contrast target of at least 4.5:1 for normal text and tap targets of at least 44×44 CSS px.
- Use a content security policy and standard web security protections before public release.
- Financial data tables: accessible with keyboard navigation, screen reader labels on numeric cells, and sortable columns.

## Product copy constraints

Allowed direction: "Ranks stocks using transparent, rule-based intraday measurements."
For Financial Intelligence: "Shows company information sourced from regulatory filings and licensed data providers."
Avoid: "sure-shot", "guaranteed", "institutional orders detected", "accurate calls", profit promises, cherry-picked winning screenshots, or language that implies an output is a personalized recommendation.

Legal classification must be determined by counsel from the complete product and marketing, not by this copy rule alone.
