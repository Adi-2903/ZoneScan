# 01 — Product Requirements

**Status:** Baseline specification; acceptance criteria are targets until validated in implementation.  
**Priority:** P0 = core MVP; P1 = first expansion; P2 = later.  
**Release gates can block any priority.**

## P0 — Core MVP

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

Show all covered F&O stocks as a dot map based on percentage move, using direction/status labels in addition to color; show bullish, bearish, and choppy counts; display leading/lagging sectors; and display an index-context/bias indicator derived from documented rules.

**Acceptance:** The visualization is keyboard/touch usable or has an accessible table alternative. The definition and timestamp of each count are available to the user.

### PR-007: Authentication and entitlements

Support Google sign-in and server-side user sessions. A user's access rights are determined by the backend. An entitlement layer must support preview, active subscription, expired, and admin states, even while payments are in test mode.

**Acceptance:** Unauthorized users cannot obtain paid board rows, zones, or protected endpoints by calling the API directly. Session cookies are secure, HTTP-only, and appropriately scoped. Account recovery and deletion are documented before public launch.

### PR-008: Marketing site and legal placeholders

Provide original landing, how-it-works, pricing, FAQ, about/contact, updates/blog, terms, privacy, refund, disclaimer, and disclosures pages. Legal text is not to be generated as a substitute for counsel review; use a clearly marked unpublished placeholder until approved.

**Acceptance:** Marketing claims match verified product behavior. No fake testimonial, unsupported performance claim, copied competitor text, or placeholder legal wording is published as final.

### PR-009: Data and system status

The product must distinguish normal, settling, closed/holiday, delayed, missing, synthetic/demo, and offline states.

**Acceptance:** Every market-data display has an `as_of` timestamp or an explicitly documented alternative. If the feed is stale, the UI warns the user and suppresses misleading real-time styling.

## P1 — First expansion

- Sector filters, price range, trading-value and volume-spike sorting.
- Sector flow badge for each stock: aligned, neutral, or against.
- Watchlist with live score, zone distance, and per-symbol notification settings.
- Alerts: enters top 20, price enters zone, zone becomes mitigated. Channels: browser push and Telegram first; email optional. WhatsApp deferred due provider/template/cost complexity.
- Trading journal: trade form, setup tags, notes, screenshots, board snapshot, reports, CSV export.
- Learning library with short lessons and progress tracking.
- Full sector heatmap and click-through.
- PWA installability and push support after browser/platform requirements are tested.
- Production Razorpay integration with signed webhooks, invoice support, and refund/expiry flows. Test-mode integration can be prototyped earlier; production activation remains gated.
- Admin panel for users, subscription state, payments, instruments, data health, content, algorithm parameters, support, and audit logs.

## P2 — Later

- Minute-by-minute replay of historical sessions and a public methodology/backtest page.
- Moderated in-app discussion threads. Initial community, if any, should use a third-party private group only after legal review and written moderation policy.
- More languages, additional market segments, richer history, and further integrations only after user validation.

## Explicit non-functional requirements

- Board should become interactive in under 2 seconds on a mid-range Android phone using a realistic 4G test profile; measure this, do not assume it.
- Landing page target: first contentful paint under 1.5 seconds on a defined 4G test profile.
- Board update target: publish within 5 seconds of a minute close at p95 during the supported session.
- Feed recovery target: reconnect within 10 seconds, then backfill gaps; if not recovered, surface delay.
- One scoring cycle must be safe to rerun idempotently.
- Contrast target of at least 4.5:1 for normal text and tap targets of at least 44×44 CSS px.
- Use a content security policy and standard web security protections before public release.

## Product copy constraints

Allowed direction: “Ranks stocks using transparent, rule-based intraday measurements.”  
Avoid: “sure-shot”, “guaranteed”, “institutional orders detected”, “accurate calls”, profit promises, cherry-picked winning screenshots, or language that implies an output is a personalized recommendation.

Legal classification must be determined by counsel from the complete product and marketing, not by this copy rule alone.
