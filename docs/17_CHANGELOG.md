# Documentation Changelog

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
