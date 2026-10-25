# Documentation Changelog

## 2026-10-26 — Initial analytical foundation prototype

- Added a Python package with validated candle/instrument/snapshot models and a provider-neutral market-data protocol.
- Added deterministic synthetic fixture data, with synthetic status and quality flags.
- Implemented confirmed swing detection that gates availability on the closing time of the right-side candles, and v0.1 Strength Score calculation with explicit unavailable states.
- Added an optional FastAPI development boundary for health, market status, and synthetic fixture inspection.
- Added standard-library tests and documented setup. Order blocks, full replay, ranking, and other score/filter functions remain unimplemented.

## 2026-10-26 — Initial repo-ready documentation baseline

- Converted the initial product specification into focused, cross-linked Markdown files.
- Added root agent instructions and a lightweight GitHub Copilot instruction pointer.
- Clarified data-quality, market-data licensing, regulatory review and production-payment release gates.
- Distinguished chart liquidity levels from the provisional Early-Move Score.
- Defined provisional score normalizations and flagged them for out-of-sample validation.
- Added API/data model proposals, operating states, testing/backtesting expectations, open questions and a definition of done.
