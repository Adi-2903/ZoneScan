# 11 — Roadmap and Release Gates

The roadmap is ordered by risk reduction, not by which feature is most visually attractive. Dates are intentionally omitted until the data provider, team capacity and legal review are known.

---

## Phase 0 — Documentation and decision baseline ✓ (in progress)

Deliverables:
- Product brief, feature priorities, architecture, algorithm proposal, API/data model, compliance checklist and agent instructions committed.
- Expanded product vision: six-workspace Financial Intelligence Terminal documented.
- Owner assigned for provider selection, algorithm, frontend/backend, legal review and launch approval.

Exit when: high-risk questions are assigned and the team agrees on the prototype scope.

**Status:** Gate 0 is in progress. Market Intelligence documentation and algorithm prototype are substantially complete. Financial Intelligence documentation is newly added (2026-10-30); legal and data gates remain open.

---

## Gate 1 — Feasibility: market data and legal (Market Intelligence)

Tasks:
- Obtain written quotes and terms from at least 2–3 credible market data provider options.
- Confirm fields: live/history OHLCV, futures OI, instruments, indices, sectors and permitted storage.
- Confirm whether commercial display of live and derived data is allowed, with fees and user limits.
- Ask qualified Indian securities counsel for written review of product classification and proposed features.
- Check current privacy/consumer/tax/payment obligations before finalizing billing.

Exit criteria:
- Written data path and estimated operating cost approved.
- No blocking contract restriction left unresolved.
- Regulatory review has a documented plan and required changes are known.

**No public live-data release or paid marketing before this gate passes.**

---

## Gate 2 — Algorithm proof (Market Intelligence)

Tasks:
- Implement swing/BOS/order-block and score functions using deterministic fixtures. ✓ (complete)
- Build the replay loop and run historical evaluation using permitted data.
- Check look-ahead bias, survivorship bias, contract rollovers, missing data and sensitivity to parameters.
- Compare against simple baselines; publish internally the full result, positive or negative.

Exit criteria:
- Core rules are deterministic and covered by tests. ✓ (115/115 passing)
- Backtest methodology is reviewed; tuning and final test periods are separated.
- No unsupported claim of performance is required for product positioning.

---

## Gate 3 — Feasibility: financial intelligence data and legal (new)

This gate must pass before any Financial Intelligence workspace moves past documentation and planning.

Tasks:
- Confirm the licensing status and commercial re-serving rights for BSE XBRL filings and NSE announcements.
- Evaluate licensed financial data aggregators (e.g., Tijori Finance, licensed BSE/NSE data vendor); obtain written terms.
- Confirm commodity price data rights (MCX/NCDEX or licensed vendor) for commercial display.
- Confirm whether PDF text extraction and verbatim quote display from annual reports is permitted.
- Obtain written advice on whether Financial Intelligence content changes the regulatory classification of the product.
- Map required API infrastructure: BSE announcements API, financial data provider API, commodity feed.

Exit criteria:
- At least one financial data source confirmed in writing with commercial display and redistribution rights.
- Commodity data source confirmed for commercial display.
- Legal review of Financial Intelligence scope completed; no blocking classification change.

**No Financial Intelligence data displayed to paying users before this gate passes.**

---

## Phase 1 — Core internal MVP (Market Intelligence)

Scope:
- Provider-neutral adapter and fixture provider.
- Candle builder and quality flags.
- Bullish/bearish board, status chip, settling/delayed states.
- Strength score, zone detection and stock chart.
- Basic Market X-Ray, sector context and board snapshots.
- Google sign-in and server-side entitlements.
- Internal admin/diagnostic view sufficient for development.

Exit criteria:
- Acceptance criteria from `01_PRODUCT_REQUIREMENTS.md` (PR-001 through PR-009) pass.
- Synthetic mode is always clearly labelled.
- Replay and live path use same algorithm functions.
- Feed failures cannot display as live data.

**Dependencies:** Gate 1 for live data; Gate 2 for any public algorithm quality claims.

---

## Phase 2 — Closed beta / launch readiness (Market Intelligence)

Scope:
- Approved licensed provider connector.
- Production hardening, error monitoring, backup/restore and status page.
- Legal-approved terms/disclosures/privacy/refund materials.
- Payment integration tested; production billing remains feature-gated until every release gate passes.
- Security, load, access-control and paper-observation tests.
- User onboarding and support process.

Exit criteria:
- Gate 1 and Gate 2 signed off.
- Legal sign-off implemented.
- Approved commercial data rights cover all displayed and derived outputs.
- At least four weeks of proposed paper-observation completed or a documented alternative.
- Incident/rollback owner available for market hours.

---

## Phase 3 — P1 member tools (Market Intelligence)

Add watchlist, alerts, journal, learning library, full sector flow, filters, PWA and admin content/billing features. Prioritize using closed-beta feedback. Re-check legal/data terms if new delivery channels expose derived or live market information.

---

## Phase 4 — Financial Intelligence alpha (new; planning only)

**Pre-condition:** Gate 3 must pass before this phase begins. Do not create production ingestion infrastructure before data rights are confirmed.

Scope (one workspace at a time):
- Ingestion pipeline skeleton with provider-neutral adapter pattern (mirroring market data approach).
- Company Intelligence workspace: financial statements from one confirmed licensed source; evidence status system; company profile API.
- News & Filings workspace: BSE/NSE announcement feed if rights confirmed; filing metadata display; original document links.

Exit criteria:
- All displayed financial data traces to a confirmed licensed source.
- Evidence status shown on every data point.
- Progressive disclosure pattern implemented and tested.
- No financial data is invented or inferred without the formula shown.

---

## Phase 5 — Financial Intelligence expansion (new; planning only)

Scope:
- Relationship Intelligence workspace: corporate ownership, subsidiary map, disclosed customer/supplier relationships.
- Supply Chain & Commodities workspace: raw material exposure from filings, commodity price feed, impact scenarios.
- Research Workspace: draggable panels, saved layouts, company comparison, notes.
- Full company search and cross-workspace navigation.

Exit criteria:
- All relationship and exposure data traces to disclosed filings with source reference.
- Commodity price source confirmed and licensed.
- Impact scenarios clearly labelled as illustrative; formula always shown.

---

## Phase 6 — P2 trust, retention, and expansion

Consider historical replay, public backtest page, community, extra languages and additional markets only after evidence that the core terminal is useful, licensed and reliable.

Consider AI-assisted research (e.g., filing summarization) only after: rights to process filing text are confirmed, the summarization pipeline is explainable and auditable, summaries are clearly labelled AI-generated, and the legal classification impact is reviewed.

---

## First 10 working sessions (Market Intelligence — suggested, not a schedule commitment)

1. Confirm project owner, name-as-codename and unresolved decisions.
2. Draft provider questionnaire and request quotes.
3. Request legal scoping call and share the actual user flows/screens/score concept.
4. Create 20-symbol synthetic instrument fixture and deterministic candle fixtures. ✓
5. Implement confirmed swing points and BOS tests. ✓
6. Implement order-block detection and zone-state tests. ✓
7. Implement score normalization and boundary tests. ✓
8. Build a plain stock detail chart using fixture data. ✓
9. Build board UI with explicit synthetic-data banner and market states. ✓
10. Wire replay tests and compare outputs; decide whether to proceed. ✓

Market Intelligence prototype phase complete. Gates 1 and 2 remain open.
