# 09 — Testing and Backtesting Strategy

## Testing principles

- Market algorithms are deterministic functions with fixtures; avoid tests that depend on live market conditions.
- Live scoring and replay must call the same code paths.
- Tests must make look-ahead bias, repainting, missing data and contract rollover visible.
- A passing unit test proves implementation behavior, not predictive value.

## 1. Algorithm unit tests

Create hand-built OHLCV/OI sequences for:

- Swing highs/lows and confirmation only after three right-side candles close.
- Bullish and bearish BOS.
- Displacement size and RVOL threshold boundaries.
- Last opposing candle selection.
- FVG condition.
- Fresh → Tested → Mitigated and expiry after five completed sessions.
- Overlapping 5m/15m zones, max active zones and nearest-zone selection.
- Equal-high/equal-low cluster tolerance and sweep definition.
- All Strength Score components at lower/upper boundaries and missing-input behavior.
- Early-Move Score normalization, run penalty boundaries and OI interpretation.
- Choppy classification when 0, 1, 2, 3 or 4 conditions hold.
- Smoothing, top-20 sorting, tie-breaks, hysteresis, removals and data-invalid exclusions.

Use golden fixtures: fixed input session → expected outputs with versioned expected values. When a rule changes, update fixture outputs only with an explanation and parameter/algorithm version change.

## 2. Ingestion and provider tests

- Provider connection and authentication failure.
- Duplicate, out-of-order, corrupt and stale ticks.
- Missing minute, filled candle flag and historical gap backfill.
- Cash/futures contract mapping and expiry-week rollover.
- Session open/close, holidays and special sessions.
- End-of-day reconciliation/correction.
- Missing OI, zero volume, invalid timestamp, halted symbol and new/removed F&O symbol.
- Reconnection after feed drop; ensure no duplicate or missed board snapshots.

Use provider sandbox/replay data where allowed; use synthetic fixtures otherwise. Do not make tests hit a real provider on every CI run.

## 3. API, entitlement and payment tests

- Every endpoint's schema and standard error response.
- Entitlement matrix: logged out, preview/free, active, expired, admin.
- Confirm hidden fields are absent from protected responses, not merely hidden in the UI.
- Cross-user isolation for watchlist, journal, screenshots and lesson progress.
- Rate limit and SSE reconnect/Last-Event-ID handling.
- Payment success, failure, pending, duplicate webhook, invalid signature, out-of-order events, refund and expiry.
- Browser callback without verified webhook must not activate an entitlement.

## 4. Frontend and accessibility tests

- Main flows from sign-in to board and stock details on 360px, tablet and desktop widths.
- Loading/empty/closed/settling/delayed/synthetic/offline/expired/error states.
- Chart layer labels, zone overlays, timeframe changes and mobile landscape.
- Keyboard navigation, screen-reader labels, contrast, touch target sizes and accessible table alternative for X-Ray.
- Avoid screenshot test flakiness caused by live timestamps or network data; inject deterministic fixtures.

## 5. Replay/backtest design

### Dataset

- Aim for at least 12 months of licensed 1-minute OHLCV and suitable historical OI for the initial evaluation.
- Use the eligible universe as it existed on each historical date, including subsequently removed symbols when the licensed history allows it, to reduce survivorship bias.
- Record missing data and exclusions; do not silently drop difficult sessions.

### Replay

- Replay candles chronologically, one decision point at a time, through the exact production scoring functions.
- At every point, provide only data available by that timestamp.
- Do not confirm a swing until its right-side candles have actually closed.
- Capture board snapshots at predeclared times (initial proposal: 09:30, 10:30, 11:30 and 13:30 IST) and evaluate forward windows of 30 minutes, 60 minutes and session close.
- Record maximum favorable/adverse excursion in ATR units, zone touch/bounce state, rank stability and symbol exclusions.
- Keep parameter tuning on an early period, validation on the next period and a final untouched test period. A suggested first split is 6 months / 3 months / 3 months; adjust for data availability before running, then freeze the dates.

### Metrics

- Hit rate by score band, with precise outcome definition and denominators.
- Average forward move versus a fair baseline/universe comparison.
- Zone-touch and bounce frequency using unambiguous zone/timeout definitions.
- Choppy-filter comparison between filtered and unfiltered stocks.
- Rank change per minute and shortlist turnover.
- Performance by market regime, sector, time of day, data-quality state and instrument liquidity.
- Sensitivity to thresholds and transaction costs where simulated trade outcomes are reported.

Do not call a zone “accurate” based only on visually compelling examples. Report confidence intervals/sample sizes where appropriate and show negative results. If the score does not add robust information beyond a simple baseline, revise the product positioning instead of overstating the result.

## 6. Paper-trading validation

Before public launch, run a minimum proposed four-week market-day paper-observation period. Compare randomly selected board timestamps against manual review; log disagreements, feed gaps and incorrect zone lifecycle transitions. No live orders are placed by the application.

## 7. Reliability/load tests

- Target 5,000 simulated SSE clients for a full test session before claiming that scale has been tested.
- Measure p50/p95/p99 board and API latency, CPU/memory, Redis hit rate, event loop pressure and DB utilization.
- Kill/restart the scoring worker during a simulated session; confirm standby/fail-safe behavior and visible stale-data banner.
- Restore database and configuration from backups in a scheduled test.

Never claim that a load target has been met until test results, date, environment and scenario are recorded.
