## 2026-10-26 ? Early-Move Score replay prototype

- Added an independent Early-Move score with OI30, 15m momentum, 15m volume burst, run-penalty breakdown, and explicit unavailable reasons.
- Wired 5m replay to the shared OI interpretation, exact prior 15m close, aligned ATR14_5m, and same-slot completed 15m volume from 20 prior supplied sessions.
- Kept Strength, board ranking, and chart liquidity outputs separate. Deterministic fixture tests only; no historical performance claim.

## 2026-10-26 ? Direction classification and deterministic boards

- Tightened directional classification to require signed day return with matching structure/VWAP context, distinguishing neutral from unavailable inputs.
- Added per-instrument/session score smoothing, timestamp-local bullish/bearish 5m snapshots, deterministic sorting, top-20 caps, and explicit hysteresis.
- Added model and replay coverage while retaining raw Strength components. Bar turnover/cutoff conventions are provisional; synthetic fixtures only, with no historical performance claim.

# Documentation Changelog

## 2026-10-26 — Q-009 resolution and Choppy filter

- Defined 12-candle overlap as the mean normalized range intersection across 11 adjacent pairs; zero-range pairs contribute zero, and missing/nonconsecutive bars are unavailable.
- Added point-in-time tri-state evaluation of the four documented Choppy conditions, using confirmed same-session BOS and session-calendar coverage to establish BOS absence.
- Added a filtered Strength value of zero for Choppy while retaining the raw `ScoreResult` and components. Early-Move Score and ranking remain unimplemented; fixture tests make no performance claim.

## 2026-10-26 — Chart liquidity levels and sweeps

- Added retained swing, equal-high/low, prior-day/week, and first-15-minute levels to chronological replay, with session-calendar/history requirements and explicit unavailable diagnostics.
- Added high/low sweep confirmation within three completed candles, timeout invalidation, next-session/next-week expiry for period levels, and unavailable lifecycle state when candles are missing.
- Kept chart liquidity records separate from scoring; documented provisional implementation conventions in D-024. Deterministic fixtures only; no historical performance claim.

## 2026-10-26 — Deterministic indicator engine

- Added provider-independent completed 5m/15m aggregation from normalized 1m candles with explicit missing/incomplete intervals and session boundaries.
- Added point-in-time ATR(14), sample daily sigma(20), day return, elapsed-time RVOL, contract-specific OI changes, close-based VWAP, EMA(20), and ADX(14) with typed availability reasons.
- Documented provisional smoothing, seeding, timestamp, volume, and OI alignment conventions in D-023; these fixture tests establish mechanics only and do not validate historical performance.

## 2026-10-26 — Optional Upstox historical candles

- Added a read-only Upstox Historical Candle V3 adapter for explicitly configured one-minute instrument/date requests, with month-window chunking, validated parsing, chronological merge, duplicate handling, and separate optional futures OI observations.
- Kept `DATA_PROVIDER=synthetic` as the default and added an opt-in small-sample script using `UPSTOX_ACCESS_TOKEN`; mocked tests do not call the provider.
- Documented the API timestamp-format inconsistency and kept Upstox provisional for local development only; no redistribution permission or Gate 2 approval is implied.

## 2026-10-26 — Historical evaluation pipeline prototype

- Added authorized-dataset metadata and validation for instrument mapping, timezone/session timestamps, ordering/duplicates, OHLCV, missing intervals, OI, and point-in-time universe coverage.
- Added deterministic evaluation over production chronological replay with explicit forward-return/ATR/touch availability states; synthetic fixtures suppress performance outcomes.
- Added focused tests for malformed data, missing data, repeatability, and future-input isolation. Fixture mechanics only; Gate 2 is not passed.

## 2026-10-26 — Strength Score in sequential replay

- Added timestamped replay score records using the shared Strength Score implementation.
- Added point-in-time replay fields for score inputs, derived structure only from confirmed swings, and selected the nearest active supporting zone available at each replay timestamp.
- Added explicit unavailable results for incomplete candles and missing required inputs; kept sector aggregation unresolved and covered future-data isolation with synthetic tests.

## 2026-10-26 — Strength Score boundary and validation pass

- Split M/V/O/T/S/Z into pure component functions and added an OI percent-change helper with reference-denominator validation.
- Corrected OI participation so falling-price/rising-OI is short buildup (factor 1.0); falling OI receives factor 0.5. Unclassifiable context is explicitly unavailable.
- Changed zone scoring to validate active state, direction, price placement, ATR, and bounds; inactive or wrong-side zones contribute the documented no-zone zero.
- Preserved unrounded components, added partial component/reason/context output and score versions, and added deterministic boundary tests and documentation.

## 2026-10-26 — Initial analytical foundation prototype

- Added a Python package with validated candle/instrument/snapshot models and a provider-neutral market-data protocol.
- Added deterministic synthetic fixture data, with synthetic status and quality flags.
- Implemented confirmed swing detection that gates availability on the closing time of the right-side candles, and v0.1 Strength Score calculation with explicit unavailable states.
- Added an optional FastAPI development boundary for health, market status, and synthetic fixture inspection.
- Added standard-library tests and documented setup. Order blocks, full replay, ranking, and other score/filter functions remain unimplemented.

## 2026-10-26 — Order-block replay prototype

- Implemented mirrored bullish/bearish order-block detection using confirmed swings, completed candles, explicit ATR/RVOL inputs, and deterministic zone IDs.
- Added Fresh/Tested/Mitigated/Expired lifecycle handling, five observed-session expiry, 15m overlap precedence, and a three-active-zone cap while retaining inactive history.
- Added chronological replay with confirmation-time swing events, zone recognition timestamps, explicit data-gap diagnostics, and no candle backfilling.
- Added tests for directional setups, thresholds/missing data, lifecycle, expiry, overlap/cap, replay determinism, and look-ahead prevention; documented prototype limitations.

## 2026-10-26 — Initial repo-ready documentation baseline

- Converted the initial product specification into focused, cross-linked Markdown files.
- Added root agent instructions and a lightweight GitHub Copilot instruction pointer.
- Clarified data-quality, market-data licensing, regulatory review and production-payment release gates.
- Distinguished chart liquidity levels from the provisional Early-Move Score.
- Defined provisional score normalizations and flagged them for out-of-sample validation.
- Added API/data model proposals, operating states, testing/backtesting expectations, open questions and a definition of done.
