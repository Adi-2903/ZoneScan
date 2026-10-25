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
- Strength Score boundaries: zero/half-sigma/1.5-sigma moves; RVOL 0/1/1.5/2/3+; OI zero/2.5%/5%/above-5% and all four price/OI contexts; trend/sector classifications; zone interpolation, wrong-side/inactive zones, invalid denominators, non-finite inputs, fixed weights, exact extrema and repeated calculations.
- Early-Move Score normalization, run penalty boundaries and OI interpretation.
- Choppy classification when 0, 1, 2, 3 or 4 conditions hold.
- Smoothing, top-20 sorting, tie-breaks, hysteresis, removals and data-invalid exclusions.

Use golden fixtures: fixed input session → expected outputs with versioned expected values. When a rule changes, update fixture outputs only with an explanation and parameter/algorithm version change.

`services/api/tests/test_scoring.py` uses independently calculated expected values rather than values copied from the scorer. It tests each component, unavailable reasons, no early rounding, fixed-weight contribution, exact zero/100 results, and repeatability. Passing these tests does not validate provider data quality or out-of-sample value.

`services/api/tests/test_replay_scoring.py` verifies that completed replay bars receive scores at their own timestamps; confirmed structure is unavailable before its right-side bars close; future bars and future sector classifications do not change earlier score outputs; missing required fields propagate component reasons; repeated replay is identical; and scoring records coexist with order-block lifecycle events. Inputs are hand-built synthetic observations, not historical market results.

### Historical evaluation prototype

The in-memory `zonescan.evaluation` module validates provenance/permission attestations, instrument mapping, `+05:30` timestamps, session bounds, chronological uniqueness, OHLC/volume validity, expected candle intervals, OI availability, and point-in-time expected-universe coverage before invoking the same chronological production replay. It reports per-score forward close returns only for exact 30m/60m/session-close candles and directional MFE/MAE over subsequent candles in ATR units. Missing candles, ATR, direction, OI, sector classification, or session completion remain explicit unavailable states; values are never filled. An order-block touch label requires a zone emitted at the score timestamp and later lifecycle events establishing a touch; bounce outcome is unsupported. Permission references are owner-supplied metadata, not legal verification. Synthetic fixtures suppress performance outcome metrics and cannot support a Gate 2 or edge claim. Without a historically accurate point-in-time universe, survivorship bias remains unresolved. Fixture tests validate mechanics only, not historical performance.

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

The implemented Python prototype in `services/api/src/zonescan/replay.py` accepts chronological `ReplayBar` records and returns timestamped swing/zone/lifecycle/data-gap events plus retained zones. It uses the same `confirmed_swings`, order-block detector, overlap resolver and lifecycle updater as other callers. It does not aggregate raw ticks into candles or calculate ATR/RVOL; callers must provide those values or leave them unavailable. Missing same-session candle intervals are reported, not filled. Unit coverage includes both directions, required-input and threshold failures, prior-opposing-candle selection, non-repainting recognition timing, lifecycle transitions, session-based expiry, overlap/cap rules, input ordering, and identical reruns. This fixture coverage does not validate signal performance or a live feed.

`services/api/src/zonescan/indicators.py` provides deterministic one-minute to 5m/15m aggregation and point-in-time indicator frames. `tests/test_indicators.py` covers aggregate OHLCV and close timestamps, session isolation, missing/incomplete intervals, warm-up and known-value checks, daily sigma/RVOL history, separate contract OI and rollover availability, explicit zero-volume/missing-OI states, and invariance of earlier outputs when future candles change. These are mechanics tests on fixed fixtures, not historical performance validation.

`services/api/src/zonescan/choppy.py` defines the Q-009 overlap calculation and tri-state four-condition classification. `tests/test_choppy.py` covers each strict condition boundary, exactly-two classification, missing/incomplete inputs, zero-range candles, BOS behavior, raw-score preservation with zero filtered strength, replay determinism, and future-bar isolation. These fixture tests validate mechanics only.

The replay liquidity prototype uses existing confirmed swings and an explicit session calendar for period/opening levels. `tests/test_liquidity.py` checks high/low and equal-level formation, ATR tolerance and outer-price convention, sweep timing within three completed candles, timeout invalidation, missing-history/gap availability, opening-range boundaries, deterministic replay, and confirmation-time causality. These tests establish implementation behavior only; they are not historical performance validation.

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
