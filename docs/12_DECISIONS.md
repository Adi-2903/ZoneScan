# 12 — Decision Log

This file captures the defaults agents should follow until the owner records a change. “Accepted” here means accepted as the current product baseline, not legally approved or experimentally validated.

| ID | Decision | Rationale / consequence | State |
|---|---|---|---|
| D-001 | Use **ZoneScan** as an internal working codename only. | Avoid blocking documentation; final name, domain and trademark must be checked before public use. | Accepted provisionally |
| D-002 | Build an original product inspired by the category, not a clone of OrderBlock. | No copied logo, layout asset, text, testimonials, proprietary formulas or unverified claims. | Accepted |
| D-003 | Initial market is NSE F&O equity stocks; Nifty/Bank Nifty and sector indices provide context. | Dynamic universe from an authorized source; not a hardcoded fixed list. | Accepted provisionally |
| D-004 | Analytics-only; no broker order placement or account-level trading access. | Reduces scope and security surface; regulatory classification still requires counsel. | Accepted |
| D-005 | Backend is authoritative for market scores, zones, entitlements and board snapshots. | Prevent different users/browsers from calculating different results. | Accepted |
| D-006 | One logical scoring worker publishes the board; cache reads and use SSE for updates. | Simple and deterministic at an initial universe of a few hundred instruments. | Accepted |
| D-007 | Use the same algorithm package for live and historical replay. | Prevent backtest/live behavior divergence. | Accepted |
| D-008 | Cash-equity candles define chart zones; futures data supplies OI/futures confirmation. | Avoid confusion caused by futures basis and contract rollover. | Accepted provisionally; validate provider and research need |
| D-009 | Core zones form only from completed 5m/15m candles; swings require three confirmed right-side candles. | Prevent repainting and look-ahead. | Accepted as baseline |
| D-010 | Rename the secondary OI/momentum/volume score to **Early-Move Score** in product code/docs. | “Liquidity” is reserved for chart levels; reduces conceptual confusion. Rename can be revisited before launch. | Accepted provisionally |
| D-011 | Dark-first responsive UI, with light theme support. | Suits terminal use; must be tested for contrast and readability. | Accepted |
| D-012 | P0 = board, core scoring/zones, basic X-Ray, status states, auth/entitlements and original marketing shell. | Deliver the core product before adding retention modules. | Accepted |
| D-013 | Watchlist, alerts, journal, lessons, full sector analysis and PWA are P1; community/replay are P2. | Keep MVP focused and reduce early maintenance/legal overhead. | Accepted |
| D-014 | Production data and production billing stay disabled until release gates pass. | Technical ability does not grant market-data rights or settle regulatory treatment. | Mandatory |
| D-015 | Any missing required input produces an explicit unavailable/ineligible state; do not renormalize missing score components. | Prevent misleading comparisons and silent changes in methodology. | Accepted |
| D-016 | Algorithm thresholds start as v0.1 hypotheses and must be backtested. | Avoid treating heuristic values as proven. | Accepted |
| D-017 | Prefer a modular monolith plus a worker over initial microservices. | Lower operational overhead while product requirements are still being validated. | Accepted |
| D-018 | API prefix is `/api/v1`; timestamps use ISO 8601 with `+05:30`. | Stable API and explicit India market timezone. | Accepted |
| D-019 | For the v0.1 zone prototype, overlap is positive-width intersection; 15m deactivates intersecting 5m zones, and cap overflow deactivates oldest active zones. Only untouched Fresh zones expire after five subsequent observed trading sessions. | Makes overlap, retention, expiry, and replay behavior deterministic while preserving history; must be reviewed against licensed session-calendar and candle data. | Accepted provisionally |
| D-020 | Strength inputs use decimal fractions; rising OI contributes factor 1.0 and falling OI 0.5 when price direction matches the scored side. Nonzero OI change with flat price, or a mismatch between price-return direction and scored direction, leaves O unavailable; zero OI change is valid zero. Zone proximity uses an active Fresh/Tested supporting zone, current price, and positive ATR; no eligible zone contributes zero. | Implements the existing interpretation table and zone rules without imputing missing context. Preserve component precision and unavailable reasons. | Accepted provisionally; provider reference-OI conventions remain open |
| D-021 | Sequential replay emits a score for each completed candle using only time-aligned inputs and structure derived from swings confirmed by that candle's close. Sector is a supplied categorical input; replay does not calculate sector aggregation. | Shares the production score function and prevents later candles or sector observations from influencing earlier output. | Accepted provisionally; Q-019 remains open |
| D-022 | Historical evaluation accepts datasets with explicit source and internal-use permission metadata, validates timestamps/mapping/order/OHLC/session coverage, and labels exact forward close returns at 30m/60m/session close plus directional ATR excursions. Synthetic fixtures never expose performance outcomes. | Establishes a reproducible evaluation contract without treating permission metadata as legal verification or fixture tests as evidence of edge. | Accepted provisionally; Gate 2 remains open |

## How to change a decision

Add a new decision row or create an ADR for a change with broad consequences. State the old decision, proposed change, reason, impact on docs/data/API, tests/backfill required, and whether owner/legal/provider approval is needed. Do not simply overwrite historical algorithm parameters or board snapshots.
