## 2026-10-30 — Data Foundation Milestone 1: Close Integrity Flags

**Data integrity foundation; persistence schema, boundary validation, entity resolution, and fixture guard implementation; 139 total tests passing across backend and frontend.**

- **Flag 1 (Fixture Realism Drift): CLOSED**
  - Added CI test suites in frontend (`apps/web/src/lib/fixtures/company-intelligence.test.ts`) and backend (`services/api/tests/test_fixtures_synthetic_guard.py`).
  - Enforced that every synthetic company, CIN/ISIN identifier, filing, and evidence citation carries explicit `(Demo)` or `SYN-` markers.
  - Implemented regression drift tests verifying that mutating/stripping `(Demo)` or `SYN-` markers causes immediate test assertion failure.
- **Flag 2 (Fact Provenance): CLOSED**
  - Implemented the actual `financial_facts` relational persistence schema (`services/api/src/zonescan/financial_facts.py`) using Python standard library SQLite with strict database-level constraints.
  - Schema covers 13 mandatory provenance fields: `company_id`, `metric`, `value`, `unit`, `financial_period`, `statement_scope`, `source_document`, `source_url`, `page_note_table_reference`, `document_date`, `retrieval_timestamp`, `extraction_method`, and `evidence_status`.
  - Persisted genuine, individually traceable fact from official permitted source: **Bharat Forge Limited** Audited Consolidated Revenue FY2023-24 (₹15,682.07 Cr, BSE Annual Report FY24 Page 218 Note 23, disclosed, `fact-bf-rev-fy24`).
- **Flag 3 (Ingestion Validation): CLOSED**
  - Added boundary validation function `validate_financial_fact()` and SQLite `CHECK` constraints on table `financial_facts`.
  - Rejects writes missing company identity, metric, unit, financial period, source document, source date, or evidence status.
  - Rejects non-finite values (NaN/Inf), invalid statement scopes, and non-timezone-aware retrieval timestamps.
  - Added test suite (`services/api/tests/test_financial_facts.py`) testing successful persistence and all rejected write failure cases, including direct raw SQL constraint violations.
- **Flag 4 (Entity Resolution - FI-007): CLOSED**
  - Implemented deterministic entity resolution engine (`services/api/src/zonescan/entity_resolution.py`) mapping security identifiers to canonical companies with temporal validity windows `[valid_from, valid_to]`.
  - Added regression test on real, independently verified corporate action: **Tata Steel Limited** (CIN: `L27100MH1907PLC000260`) 10:1 stock split on 2022-07-29 (pre-split `INE081A01012` valid through 2022-07-28; post-split `INE081A01020` valid from 2022-07-29).
  - Enforced strict invariant preventing merging companies with similar names (`Tata Steel Limited` vs `Tata Steel Long Products Limited`; `Bharat Forge Limited` vs `Bharat Electronics Limited`).
- **Documentation & Architecture Decisions**:
  - Updated `docs/07_DATA_MODEL.md` with implemented persistence schemas and validation rules.
  - Added D-028 (financial facts schema), D-029 (deterministic entity resolution), and D-030 (fixture realism drift guard) to `docs/12_DECISIONS.md`.
  - Updated `FI-007` in `docs/13_OPEN_QUESTIONS.md` to `Resolved provisionally; regression-tested`.
  - Documented integrity verification test suites in `docs/09_TESTING_BACKTESTING.md`.

## 2026-10-30 — Company Intelligence Technical Reference & Implementation Guide

**Documentation and code-audit task only; authored comprehensive technical reference for Company Intelligence; zero application code changes.**

- **Created Technical Reference (`docs/20_COMPANY_INTELLIGENCE_IMPLEMENTATION.md`)**:
  - Authored super-detailed, 12-section technical reference document covering the actual Company Intelligence frontend implementation.
  - Documented complete architecture, Next.js 16/React 19 component tree, workspace navigation flows, and 3-level progressive disclosure pattern.
  - Documented company fixtures (`apps/web/src/lib/fixtures/company-intelligence.ts`), covering `ZENITHFAB` and `APEXALLOY`, reporting periods (FY23–FY25, Q1/Q2 FY26), business segments (Ind AS 108), shareholding distributions (SEBI Reg 31), and 13 mapped ecosystem entities.
  - Formatted all core TypeScript interfaces, enums (`EvidenceStatus`, `RecordOrigin`), and data models.
  - Documented exact mathematical formulas, units, and worked numerical calculations for Gross Margin, EBITDA Margin, PAT Margin, ROCE, Debt/Equity, and the commodity sensitivity calculator (`apps/web/src/lib/calculations/supply-chain-impact.ts`), validating the period and denominator invariant identity.
  - Detailed Cytoscape.js concentric visualizer implementation (`apps/web/src/components/company/RelationshipMap.tsx`), node/edge styling, directed arrow semantics, and accessible HTML adjacency table fallback.
  - Documented regulatory filings feed (`apps/web/src/components/company/FilingList.tsx`), Level 3 progressive disclosure drawer (`SourcePanel.tsx`), and synthetic notice restrictions.
  - Catalogued complete 11-component inventory with file paths, responsibilities, props, and progressive disclosure levels.
  - Documented installed dependencies (`cytoscape`, `@types/cytoscape`), automated test suite (`node --test`), build verification results, and canvas inspection boundaries.
  - Summarized integrity audit findings, resolved label issues, and remaining implementation gaps.
  - Detailed the real-data readiness transition path to replace demo fixtures with source-backed Indian company data post-Gate 3.
  - Provided feature status matrix and a prioritized list of the next five development tasks.

## 2026-10-30 — Company Intelligence Integrity Audit & Pilot Provenance Specification

**Frontend integrity refactor; synthetic demo classification separation; mathematical simulator audit; zero backend/database changes.**

- **Separated Synthetic Demo Presentation from Statutory Records**:
  - Refactored `EvidenceBadge` to support explicit demo classifications (`Demo Disclosed`, `Demo Verified`, `Demo Inferred`, `Demo Unconfirmed`, `Unavailable`) with dashed border styling and explicit `aria-label` tags, preventing any confusion with genuine statutory records.
  - Kept production-grade evidence classification types (`disclosed`, `verified`, `inferred`, `unconfirmed`, `unavailable`) ready for future live data feeds.
  - Replaced misleading labels (`Audited`, `Verified Statutory Record`, `Exchange Submission`) in `FinancialTable`, `FilingList`, `RelationshipMap`, and `SourcePanel` with explicit synthetic demo identifiers (`Demo Model`, `Synthetic Demo Model · Fictional Disclosure`, `Modelled Citation Reference`).
  - Added fictional identification to corporate identity badges (`SYN-L28910MH2012PLC987654 (Demo)`, `SYN-INE999X01099 (Demo)`, `SYNTHETIC DEMO ENTITY`).
- **Mathematical Sensitivity Simulator Audit**:
  - Created pure mathematical utility `apps/web/src/lib/calculations/supply-chain-impact.ts` computing raw material cost deltas, modelled COGS, and gross margin compression basis points with identical annual revenue and COGS periods and denominators.
  - Created automated test suite `apps/web/src/lib/calculations/supply-chain-impact.test.ts` running via `node --test` (5 passing tests). Added `npm test` script to `package.json`.
  - Replaced hardcoded Zenith numbers in `SupplyChainSimulator.tsx` with dynamic company baseline figures (`baselineRevenue`, `baselineCOGS`, dynamic `${company.legalName}`, dynamic formula display).
- **Fixture Reconciliation & Dynamic Profiling**:
  - Reconciled Apex Ferrous (`APEXALLOY`) valuation metrics: Market Cap ₹2,178.00 Cr, PE 16.50, Total Equity ₹575.00 Cr, Enterprise Value ₹2,383.00 Cr, Debt/Equity 0.43×.
  - Expanded Apex financial statements to include complete 5-period Income Statement, Balance Sheet Highlights, and margin ratios matching Zenith's schema.
  - Made margin sparklines in `CompanyIntelligence.tsx` dynamic, pulling real statement rows instead of static constants.
- **Real-Data Readiness Pilot Documentation**:
  - Authored `docs/20_REAL_DATA_PILOT_SPEC.md` documenting an end-to-end provenance contract for **Bharat Forge Limited** (NSE: `BHARATFORG` / BSE: `500493`), mapping official source URLs, document dates, reporting periods, metrics, units, extraction locations, retrieval dates, and evidence classifications across Master Data, P&L, Segments, Shareholding, and Raw Material Notes without scraping or downloading external data (Gate 3 compliant).
- Verified `npm test` (5/5 passed), `npm run typecheck` (`tsc --noEmit`), `npm run lint` (`eslint .`), `npm run build` (`next build`), and `git diff --check`.

## 2026-10-30 — Company Intelligence UI Prototype

**Frontend-only prototype; synthetic demo fixtures only; no production database or backend changes.**

- Built complete Company Intelligence experience adhering to the `ui-ux-pro-max` skill and the ZoneScan terminal design system (`design-system/zonescan/MASTER.md`).
- Added typed synthetic fixtures (`apps/web/src/lib/fixtures/company-intelligence.ts`) with two detailed fictional Indian manufacturing companies (`ZENITHFAB` and `APEXALLOY`), complete 3-year audited and quarterly financial statements, segment breakdowns, shareholding profiles, 13 mapped relationships with evidence statuses, raw material cost structures, and statutory filings.
- Created reusable Financial Intelligence components:
  - `EvidenceBadge`: accessible color, text, and glyph tags for Disclosed, Verified, Inferred, Unconfirmed, and Unavailable data with source inspection triggers.
  - `SourcePanel`: accessible slide-out drawer providing Level 3 progressive disclosure of exact calculation formulas (e.g. Gross Margin, EBITDA) and statutory filing excerpts on demand.
  - `FinancialTable`: multi-period statement table featuring frozen sticky row headers, Consolidated/Standalone and Annual/Quarterly toggle modes, accounting parentheses for negative values, and line-item source inspection.
  - `KPICard`: high-density terminal cards with tabular numerals, units (₹ Cr, %, ×), YoY delta arrows, and evidence badges.
  - `MetricSparkline`: bespoke pure-SVG trend visualizer with gradient area fills, hoverable tooltip pills, and accessible data table summaries.
  - `ShareholdingBar`: segmented promoter/DII/FII/retail distribution bar with QoQ change badges and promoter pledge tracking.
  - `SegmentChart`: division revenue/profit share visualizer with spotlight cards and accessible table alternative.
  - `RelationshipMap`: interactive Cytoscape.js network graph featuring concentric layout, typed node and edge styling, pan/zoom/reset controls, interactive node inspector drawer, category filters, and accessible adjacency table alternative.
  - `SupplyChainSimulator`: raw material dependency cards, interactive commodity price shock slider (-20% to +30%), real-time gross margin compression and EBITDA impact calculator with transparent mathematical formulas and synthetic disclaimers.
  - `FilingList`: reverse-chronological statutory filing feed with category badges (Quarterly Results, Material Contract, Shareholding, Expansion) and excerpt inspection.
  - `CompanyIntelligence`: master workspace orchestrator with company selector dropdown and seamless cross-tab navigation.
- Integrated Company Intelligence into main application (`apps/web/src/app/page.tsx`), adding primary navigation, breadcrumbs, back-to-board links, and quick jump buttons from Market Board and X-Ray.
- Installed `cytoscape` and `@types/cytoscape`.
- Updated `docs/02_UX_FLOWS.md` and `docs/14_DESIGN_SYSTEM.md`.
- Verified type safety (`tsc --noEmit`), linting (`eslint .`), production build (`next build`), formatting (`git diff --check`), and visual appearance across desktop, mobile, dark, and light themes.

## 2026-10-30 — Product vision expansion: Financial Intelligence Terminal

**Documentation and planning only; no application code changed.**

- Evolved product positioning from Indian stock scanner to Bloomberg-inspired **Financial Intelligence Terminal** with six connected workspaces: Market Intelligence (existing), Company Intelligence, Relationship Intelligence, Supply Chain & Commodities, News & Filings, and Research Workspace.
- Added guiding design principle: "Bloomberg-level information depth, understandable through progressive disclosure."
- Defined four-level evidence quality framework: Disclosed / Inferred / Unconfirmed / Unavailable.
- Updated `docs/00_PROJECT_BRIEF.md`: six-workspace product summary, principles, out-of-scope, and gate list.
- Created `docs/19_FINANCIAL_INTELLIGENCE.md`: full specification for Workspaces 2–6, data pipeline architecture, evidence framework, GitHub component evaluation table, and 12 open questions.
- Updated `docs/01_PRODUCT_REQUIREMENTS.md`: added P3 requirements (PR-FI-001 through PR-FI-005) for each Financial Intelligence workspace; preserved all existing P0–P2 requirements.
- Updated `docs/02_UX_FLOWS.md`: six-workspace navigation, company research user flow, Financial Intelligence screen inventory, data rights gate state, and progressive disclosure pattern.
- Updated `docs/03_ARCHITECTURE.md`: Financial Intelligence ingestion pipeline (scheduled, not real-time), planned `ingestion-worker` service boundary, and per-workspace API grouping.
- Updated `docs/07_DATA_MODEL.md`: Part B with Financial Intelligence schema (companies, financials, shareholding, relationships, filings, commodities, research workspace tables); Part A market model preserved unchanged.
- Updated `docs/11_ROADMAP.md`: added Gate 3 (Financial Intelligence data/legal feasibility), Phases 4–5 (Financial Intelligence alpha and expansion), Phase 6 (P2 and AI-assisted research); marked Market Intelligence prototype milestones as complete.
- Updated `docs/13_OPEN_QUESTIONS.md`: added 12 FI-series blockers (FI-001 through FI-012); all 21 existing market intelligence questions preserved.
- Updated `docs/14_DESIGN_SYSTEM.md`: evidence status color semantics, progressive disclosure pattern, financial table guidelines, new accessibility requirements, planned FI component inventory, candidate third-party component evaluation.
- Updated `README.md`: six-workspace framing, current status table per module, simplified docs map.
- Updated `AGENTS.md`: document-lookup table for selective context loading, P3 priority definition, Financial Intelligence guardrails, evidence status rule, Gate 3 implementation guard.
- `git diff --check` passed (exit 0). No application code modified.

## 2026-10-26 ? Early-Move Score replay prototype

- Added an independent Early-Move score with OI30, 15m momentum, 15m volume burst, run-penalty breakdown, and explicit unavailable reasons.
- Wired 5m replay to the shared OI interpretation, exact prior 15m close, aligned ATR14_5m, and same-slot completed 15m volume from 20 prior supplied sessions.
- Kept Strength, board ranking, and chart liquidity outputs separate. Deterministic fixture tests only; no historical performance claim.

## 2026-10-26 ? Direction classification and deterministic boards

- Tightened directional classification to require signed day return with matching structure/VWAP context, distinguishing neutral from unavailable inputs.
- Added per-instrument/session score smoothing, timestamp-local bullish/bearish 5m snapshots, deterministic sorting, top-20 caps, and explicit hysteresis.
- Added model and replay coverage while retaining raw Strength components. Bar turnover/cutoff conventions are provisional; synthetic fixtures only, with no historical performance claim.

# Documentation Changelog

## 2026-10-27 — Frontend Polish V1

- Added persistent mobile Board/X-Ray navigation and return-to-origin behavior from stock details; made the unknown market state explicit in the header.
- Improved terminal spacing/contrast tokens, minimum touch targets, keyboard focus and active states; kept score values neutral unless a direction is explicitly labeled.
- Added an accessible table alternative and data tooltip to the synthetic X-Ray map; refined its 360px and tablet layouts without changing the API contract.

## 2026-10-26 — Synthetic Market X-Ray MVP

- Added `GET /api/v1/xray`, deriving five-state counts and leading/lagging covered stocks from the cached point-in-time replay, with deterministic metadata and explicit partial-fixture coverage.
- Extended the deterministic fixture with bullish, bearish, Choppy, neutral, and unavailable examples; the unavailable example has no final completed candle, and values remain `null`.
- Added a responsive dashboard dot map with state glyphs/labels, counts, leading/lagging examples, stock-detail navigation, loading/error/empty states, and persistent synthetic/coverage limits. Sector aggregation and index bias remain omitted; market status stays unknown.
- Added offline response determinism/shape/coverage tests. Fixture behavior only; no market-wide or performance claim.

## 2026-10-26 — Responsive synthetic dashboard prototype

- Added a mobile-first Next.js/TypeScript/Tailwind dashboard for cached synthetic market status, bullish/bearish boards, and stock analytics, with theme extension, loading/error/empty states, accessible text direction labels, and responsive layout.
- Added fixture-backed 1m/5m/15m/daily candles to the API for an interactive candlestick chart with togglable active-zone and unswept-liquidity overlays; 5m/15m use production aggregation.
- Documented local backend/frontend setup. The UI remains a synthetic local prototype and does not enable live data, auth, or trading actions.

## 2026-10-26 — Analytical engine API prototype

- Added a cached synthetic analytics service that aggregates the fixed fixture, calculates indicators, and calls chronological production replay/board functions once per process.
- Exposed read-only market status, bullish/bearish board, and stock-detail endpoints with explicit synthetic metadata, score/component availability, indicator reasons, zones, and liquidity levels; retained health and development snapshot routes.
- Added offline API tests for direction, timestamps/source, validation, unknown symbols, unavailable inputs, and deterministic responses. This remains a local prototype; no live source or performance validation is implied.

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
