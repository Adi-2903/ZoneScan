# 04 — Market Data and Provider Requirements

**Criticality: P0 / release blocker.** Provider selection decides cost, permitted usage, fields available, historical backtest feasibility, and whether a commercial product is possible.

## Required data

| Data | Purpose | Preferred granularity |
|---|---|---|
| NSE cash-equity OHLCV for eligible F&O stocks | Chart candles, swing structure, order blocks, VWAP and price movement | Tick or reliable 1-minute data |
| Near-month/current relevant stock futures price, volume and OI | OI interpretation and futures confirmation | Tick or 1-minute values; contract ID must be stored |
| Nifty 50, Bank Nifty, relevant sector indices | Market and sector context | 1-minute or better |
| Historical candles and daily OHLC | ATR/sigma baselines, zones, backtests | At least 12 months target for initial evaluation; more if available and licensed |
| Historical time-of-day volume baseline | RVOL and volume burst | At least 20 completed sessions for the initial formulas |
| F&O instrument list and lot sizes | Dynamic universe, valid symbols, futures contracts | Updated daily before session |
| Sector mapping | Sector strength | Maintained reference data with source and update timestamp |
| Exchange holiday/special-session calendar | Session handling | Official calendar, updated when announced |

Use the **cash equity series** for stock chart zones by default; use the relevant futures series for OI and futures confirmation. This prevents contract-roll or futures-basis effects from silently changing the chart-zone definition. Document that distinction in the product help.

## Data-provider options

### Broker API

Useful for local prototyping only when the current terms permit the specific use. Do not assume that one retail API subscription permits redistributing live market data or derived outputs to public users. Kite Connect's published terms specifically state that its live market data cannot be displayed to the public at large and restrict redistribution. Other providers have their own current terms; verify each separately.

### Licensed data vendor

Preferred route for a commercial service if the contract expressly covers the data fields, users, geography, live/delayed display, historical storage, derived analytics and any redistribution needed by the product. Get written answers, not a verbal estimate.

### Direct exchange data

Evaluate official exchange/data products if feasible. Confirm format, fees, usage permissions, contractual approvals, and operational requirements in writing.

**Decision rule:** No provider is approved until there is a written record of fields, latency, historical access, commercial display/derived-output rights, redistribution terms, retention restrictions, fees, support and rate limits.

## Provider evaluation checklist

Ask each candidate:

1. Do you cover every current NSE F&O equity symbol and the relevant futures contracts?
2. Is OI available at the granularity required for the formula? Are historical OI snapshots available?
3. Are live ticks, 1-minute candles and 12+ months of historical candles available?
4. Are indices and sector indices included?
5. Can the data be shown in a paid browser application to multiple end users?
6. Can we store the feed, historical candles, derived scores, screenshots and board snapshots? For how long?
7. Are derived indicators/scores allowed? Are any output/display/user-count restrictions applicable?
8. Are user-facing display fees, per-seat fees, exchange approvals or reporting duties applicable?
9. What are rate limits, concurrent stream limits, reconnect behavior, maintenance windows and SLA/support commitments?
10. What are pricing, taxes, setup fees, minimum contract term and termination/transition terms?
11. Can the provider supply written permission for the specific product architecture and launch plan?

## Ingestion pipeline

1. **08:30 IST — universe refresh:** retrieve the permitted current F&O list and lot sizes; refresh symbol-to-provider-token mappings, sector mapping, and current futures contracts.
2. **09:00 IST — connect:** establish provider connection, authenticate, subscribe to instruments and validate first ticks. Record provider and source timestamps.
3. **Normalize:** convert provider payloads to internal `Tick`/`Quote` models, normalize units and timestamps, validate instrument ID, and preserve source identifiers.
4. **Build 1-minute candles:** aggregate tick data. Higher timeframes (5m/15m) derive from normalized 1m candles so that calculations agree. Do not mix session boundaries.
5. **Handle gaps:** on reconnect, request missing intervals from the historical endpoint if allowed. Mark candles filled from last close with zero volume; never pass them off as observed trades.
6. **Contract rollover:** use an explicit futures-contract selection policy. Store the instrument/contract ID alongside every OI point. Never splice two contracts without a documented continuity rule.
7. **Quality gate:** reject clearly corrupt ticks by configurable validation; compare cash/futures relationships only as a diagnostic, not as a reason to arbitrarily rewrite values. Flag affected symbols if critical inputs fail.
8. **15:35 IST — close feed:** finish session processing when provider/session state confirms closure.
9. **15:45 IST — end-of-day reconciliation:** replace provisional daily aggregates with official/authorized final data where allowed; create closing board snapshot and record any corrections.

All times are operational defaults for NSE regular sessions and must follow official special-session schedules rather than a fixed clock when the exchange announces an exception.

## Data quality rules

- Every quote/candle carries source timestamp, received timestamp, provider ID and quality flags.
- A stale-data threshold is configurable and visible. The initial target is to warn if the data path is older than 5 seconds where the provider supplies timestamps that support this measurement.
- Do not rank a symbol until the minimum warm-up and required-input checks pass; the initial proposal is at least 10 minutes of usable candles, with normal ranked output withheld during settling.
- A missing required input makes that score unavailable or the symbol ineligible, according to an explicit rule. It is not silently replaced by zero.
- Keep raw licensed data only as permitted by the provider agreement.
- Keep a daily count of symbols expected, received, eligible, excluded and the reason for exclusion.
- Preserve corporate-action adjustments and instrument changes in historical backtests.

## Provisional data assumptions requiring owner approval

- Relative-volume baseline: same elapsed market time over the preceding 20 completed sessions.
- Historical baseline for daily sigma: 20 completed daily returns.
- OI source: appropriate current/near-month futures contract, with stored contract identity and an explicit rollover policy.
- Chart price series: cash equity; futures data is a confirmation input.

These choices are algorithm parameters, not facts guaranteed by any provider. Confirm the data fields and license before implementing a production connector.
