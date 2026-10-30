# 06 — API Contracts

**Base path:** `/api/v1`  
**Transport:** HTTPS JSON for REST; SSE for one-way live updates.  
**Time:** ISO 8601 with explicit `+05:30` offset for all market timestamps.

This document describes the proposed product contract. The local API prototype implements read-only synthetic status, board, stock detail, candles, and a fixture-scoped Market X-Ray; it does not implement authentication, subscriber access, or public/live service.

## Endpoint inventory

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/api/v1/market/status` | Public | Session state, last source timestamp, settling/delay status |
| GET | `/api/v1/board?side=bull` | Preview/subscriber | Current bullish rows |
| GET | `/api/v1/board?side=bear` | Preview/subscriber | Current bearish rows |
| GET | `/api/v1/stocks/{symbol}` | Subscriber | Score, breakdown, active zone, levels, sector context |
| GET | `/api/v1/stocks/{symbol}/candles?tf=5m&from=&to=` | Subscriber | Chart candle series |
| GET | `/api/v1/stocks/{symbol}/zones` | Subscriber | Current/history zones and liquidity levels |
| GET | `/api/v1/xray` | Subscriber/allowed preview | Covered-instrument dot map, classifications, counts, and fixture coverage |
| GET | `/api/v1/sectors` | Subscriber | Sector strength/context |
| GET/POST | `/api/v1/watchlist` | Subscriber (P1) | List/add watchlist items |
| DELETE | `/api/v1/watchlist/{symbol}` | Subscriber (P1) | Remove item |
| GET/POST/PATCH/DELETE | `/api/v1/alerts` | Subscriber (P1) | Manage alert rules |
| GET/POST/PATCH/DELETE | `/api/v1/journal/trades` | Subscriber (P1) | Manage a user's own trades |
| GET | `/api/v1/journal/report?from=&to=` | Subscriber (P1) | Aggregated personal stats |
| GET | `/api/v1/lessons` | Subscriber (P1) | Learning library |
| POST | `/api/v1/lessons/{id}/progress` | Subscriber (P1) | Save lesson progress |
| GET | `/api/v1/me` | Logged in | User, plan, expiry, devices |
| POST | `/api/v1/auth/google` | Public | Verify Google identity token server-side and establish session |
| POST | `/api/v1/billing/checkout` | Logged in | Create a payment-provider order |
| POST | `/api/v1/billing/webhook` | Provider callback | Verify signature and update entitlement idempotently |
| GET | `/api/v1/stream` | Subscriber | SSE stream for board/status changes |

An endpoint not implemented in the current phase should be omitted or return a documented not-available response. Do not expose dummy endpoints that pretend to work.

### Local analytical prototype

`GET /api/v1/market/status`, `GET /api/v1/board?side=bull|bear`, `GET /api/v1/stocks/{symbol}`, and `GET /api/v1/xray` are implemented for local development. They use a process-cached, fixed synthetic dataset, a chronological indicator/replay pass, and the production scoring and board functions. Every response reports `data_mode: synthetic`, `data_status: synthetic`, and `data_source: deterministic_synthetic_fixture`; `market_state` is `unknown`. The fixture's fixed `as_of` time is not a current market timestamp. Sector labels are explicit fixture inputs, not sector aggregation.

The X-Ray response reuses each instrument's replay direction, Choppy result, and day return at the fixed snapshot. `instruments` carries symbol/id, underlying direction, percentage change, one of `bullish`, `bearish`, `choppy`, `neutral`, or `unavailable`, availability reason, and timestamp. If either direction or Choppy classification is unavailable, the display classification is unavailable. `counts` covers all five states; `leaders` and `laggards` sort covered instruments with an available change. `coverage.universe_complete` is always `false` for this fixture and the label explicitly calls the instruments synthetic examples. The fixture currently includes five examples, including an intentionally missing latest candle to exercise unavailable values. This endpoint does not calculate sectors or index context; Q-019 remains open, and no market-wide completeness is implied.

`GET /api/v1/stocks/{symbol}/candles?tf=5m` serves the corresponding cash-equity synthetic fixture candles for `1m`, `5m`, `15m`, or `1d`. Intraday requests return the fixed fixture's final session; daily requests return supplied fixture history. 5m and 15m candles use the shared session-bounded aggregation function. The endpoint returns source/quality metadata and does not synthesize missing candles.

Board rows include raw/component Strength Score output, filtered and smoothed values, Early-Move availability/breakdown, current synthetic close, active-zone state, liquidity levels, direction, and quality flags. Stock detail includes the same timestamp/source/version metadata, indicator availability/value/reason fields, score details, zones, and levels. Missing analytics remain `null` with explicit availability/reason metadata. Board side must be `bull` or `bear` (400 otherwise); unknown stock symbols return 404. Invalid requests use `{ "error": { "code", "message", "request_id" } }`.

This local fixture API does not enable Upstox as an API source. The optional Upstox workflow remains a separately invoked historical sample; it is not a live feed. The local endpoints do not imply data rights, Gate approval, or performance validation.

## Common board response shape

```json
{
  "as_of": "2026-10-26T10:14:00+05:30",
  "data_as_of": "2026-10-26T10:14:00+05:30",
  "market_state": "open",
  "settling": false,
  "data_status": "live",
  "data_mode": "licensed_feed",
  "side": "bull",
  "algorithm_version": "v0.1",
  "parameter_version": "2026-10-26.1",
  "rows": [
    {
      "rank": 1,
      "symbol": "DEMO1",
      "price": 123.45,
      "change_pct": 1.2,
      "strength": 71.0,
      "early_move": 62.0,
      "sector": "Example Sector",
      "sector_badge": "aligned",
      "zone": {"state": "fresh", "low": 121.0, "high": 122.0},
      "levels": {"resistance": 125.0, "support": 119.0, "liquidity": 118.5},
      "trend": "up",
      "quality_flags": []
    }
  ]
}
```

**Example values above are synthetic documentation fixtures, not live prices or actual signals.** Tests should mark these fixtures as synthetic and the UI must show a demo badge if used interactively.

## Market status shape

Must include:

- `market_state`: `pre_open | open | closed | holiday | special_session | unknown`.
- `session_open_at`, `session_close_at` when known.
- `settling` boolean and reason.
- `data_status`: `live | delayed | stale | unavailable | synthetic`.
- `data_as_of`, `received_at`, `delay_seconds` where available.
- `universe_expected`, `universe_eligible`, `symbols_excluded` and exclusion summary for operations/admin.

## Error format

Use one standard error structure:

```json
{
  "error": {
    "code": "DATA_DELAYED",
    "message": "Market data is delayed. The displayed board is not current.",
    "request_id": "req_example_123"
  }
}
```

Do not return stack traces, secrets, database details, or provider tokens to a client.

## Access control and rate limits

- Authentication is enforced server-side for private endpoints.
- Entitlements are checked on every protected request; UI blur/lock alone is not security.
- A free/expired user may receive only explicitly permitted preview rows. Strip private zones/score details from the response itself where required.
- Initial default rate limit: 60 REST requests per minute per user, configurable after observing expected chart polling and browser behavior.
- One SSE stream per active device/tab policy should be enforced in a way that does not unexpectedly break a legitimate user opening a phone and a laptop; final device policy is an open decision.
- Cache the public/current board briefly (initial target 5 seconds). Do not cache private account data across users.

## SSE contract

- One SSE connection per active app tab/device, subject to entitlement/device policy.
- Send event IDs and support reconnect using `Last-Event-ID`.
- Events: `board_delta`, `market_status`, `data_quality`, and optionally a throttled `price_tick` for visible rows.
- Default board delta frequency: once per finalized minute. Optional price-tick events may be throttled to at most once every two seconds and must not imply a new finalized ranking.
- If event history has a gap larger than the retained replay window (initial proposal: two minutes), tell the client to fetch a full board snapshot.
- Close streams when authorization expires or the user revokes the relevant session; return a useful client-visible reason when possible.

## Payment webhook requirements

- Verify the provider signature against the raw request body using server-held secret material.
- Treat the provider webhook as authoritative, not the frontend success callback.
- Make every payment event idempotent using provider event/payment IDs.
- Persist event receipt and outcome for troubleshooting; handle duplicate and out-of-order events.
- Keep production webhook endpoints disabled until the compliance gate passes.
