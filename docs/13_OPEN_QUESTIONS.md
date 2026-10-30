# 13 — Open Questions and Blockers

Do not silently decide the items marked **BLOCKER**. The owner should assign a person and record the resolution here or in a linked ADR.

---

## Market Intelligence open questions (existing)

| ID | Question | Why it matters | Required owner / next action | Status |
|---|---|---|---|---|
| Q-001 — BLOCKER | Which market-data provider and licence will cover historical replay, live display, storage, OI, indices and derived scores for end users? | Determines whether Gate 2 can use historical data and whether the product can legally operate; API access alone does not grant commercial display or derived-output rights. Upstox is only a provisional local-development adapter, not an approved data licence. | Product owner + counsel: request separate internal-research and paid multi-user product terms and quotes from NSE Data & Analytics, TrueData, Global Datafeeds and Upstox; compare as specified in `18_DATA_PROVIDER_EVALUATION.md`. | Open |
| Q-002 — BLOCKER | What is the written Indian securities-law classification of a paid ranked scanner with zone overlays and alerts? | Disclaimer text does not settle classification; features/marketing may affect obligations. | Product owner + qualified securities counsel. | Open |
| Q-003 — BLOCKER | Which privacy, consumer, tax/invoice, payment and retention obligations apply at launch under current rules? | Avoid incorrect legal assumptions or payment setup. | Counsel + CA + payment provider. | Open |
| Q-004 | Is the public name really ZoneScan, or is this only a temporary codename? | Trademark/domain and branding decision. | Owner: approve name after checks. | Open |
| Q-005 | Is the launch universe NSE F&O equities only, with indices in context, or do indices also need ranked boards? | Changes ranking and chart model. | Product owner. Default: equities only. | Open; default documented |
| Q-006 | Can a licensed source provide at least 12 months of aligned cash OHLCV and same-window stock-futures OI, 20 prior sessions for time-of-day volume, and point-in-time F&O membership/mappings including removed or delisted instruments? | Required for the initial historical evaluation, indicator warm-up, OI context and survivorship-aware universe. Upstox V3 documents minute history from January 2022, but endpoint documentation does not establish OI completeness, historical instrument coverage, dataset rights, or universe membership. | Data owner: verify provider coverage, permission, and manifest against `18_DATA_PROVIDER_EVALUATION.md`. | Open |
| Q-007 | How exactly should the futures contract rollover be selected and historical OI continuity handled? | OI changes can be distorted by contract changes. | Algorithm owner + data provider. | Open; provider-dependent |
| Q-008 | Are the provisional Strength/Early-Move formulas and normalizations useful out of sample? | Thresholds may not carry predictive information. | Algorithm owner; evaluate as specified in `09_TESTING_BACKTESTING.md`. | Open |
| Q-009 | What is the exact candle-overlap measure for the choppy filter? | "Overlap >70%" needs a reproducible formula. | Resolved by provisional D-025: mean adjacent-pair range-intersection ratio over 12 complete consecutive same-session 5m candles; owner may revise only with a versioned decision and tests. | Resolved provisionally; fixture-tested |
| Q-010 | What final Strength Score display threshold, if any, should govern board eligibility? | Impacts board membership and user interpretation. Directional neutral/unavailable handling is now provisionally specified by D-026. | Algorithm owner; evaluate with permitted historical data before setting a display threshold. | Open |
| Q-011 | Should there be a free preview, delayed board, monthly plan, annual plan, trial, or paid-only launch? | Affects business model, data licensing and entitlements. | Product owner after data cost is known. | Open |
| Q-012 | What are final prices, taxes, refund/cancellation policy and renewal policy? | Commercial and legal decision; never copy competitor pricing. | Product owner + CA/counsel + payment provider. | Open |
| Q-013 | Which login methods at launch: Google only, or also email/phone OTP? | OTP adds provider cost and abuse controls. | Product owner. Default: Google first. | Open; default documented |
| Q-014 | One or two simultaneous devices per account? | Entitlement/privacy/support trade-off. | Product owner. Default: allow phone + laptop unless abuse evidence says otherwise. | Open; default documented |
| Q-015 | Which alert channels are launched first, and are derived data messages permitted on those channels by the provider contract? | Alert messages can be redistribution of market data. | Product owner + data provider + counsel. | Open |
| Q-016 | What public backtest statistics, if any, may be shown and under what review process? | Methodology and data rights must support them. | Algorithm owner + counsel. | Open |
| Q-017 | Is community needed at all? | Adds moderation, privacy and regulatory risk. | Product owner after closed beta. Default: no in-app community for MVP. | Open; default documented |
| Q-018 | What team capacity, launch window, cloud region and monthly operating budget are available? | Determines deployment and schedule; costs depend strongly on data licensing. | Product owner. | Open |
| Q-019 | Should sector direction classification use traded-value weighting, member-count participation, or both, and what timestamp/coverage makes a sector state available? | The provisional Strength Score specifies a traded-value-weighted aggregate but describes its initial 60% participation threshold by member count; the scoring function currently consumes an upstream categorical state. | Algorithm owner: define and version the sector aggregation before integrating board scoring. | Open |
| Q-020 | Should board tie-break traded value use completed-bar close * volume or cumulative session turnover, and should hysteresis use the prior snapshot 20th score as its cutoff? | The replay model has per-candle volume but no cumulative turnover; the current deterministic choices affect rank membership and persistence. | Algorithm owner: review D-026 and revise only with parameter versioning and tests. | Open; provisional implementation |
| Q-021 | Should Early-Move be emitted on each completed 5m replay candle, use the same-timestamp replay classification as its side, and use daily return sign for OI context? | These provisional conventions determine score cadence and how directional OI/momentum are treated. | Algorithm owner: review D-027 before historical evaluation; version any changes. | Open; provisional implementation |

---

## Financial Intelligence open questions (new — added 2026-10-30)

These questions block the Financial Intelligence workspaces (Workspaces 2–6). All are blockers for Gate 3 in `docs/11_ROADMAP.md`.

| ID | Question | Why it matters | Required owner / next action | Status |
|---|---|---|---|---|
| FI-001 — BLOCKER | Which financial data provider/source is licensed for commercial display and redistribution of Indian company financial statements (income statement, balance sheet, cash flow)? | Blocks all of Workspace 2; BSE XBRL is public but re-serving aggregated data commercially requires explicit rights confirmation. | Product owner + counsel: evaluate Tijori Finance, licensed BSE/NSE data vendors, and direct exchange data terms. | Open |
| FI-002 — BLOCKER | Is BSE XBRL data legally re-servable in a paid commercial product, and if so under what terms and restrictions? | BSE publishes XBRL data under its own terms; re-serving it in a paid product may require a separate data licence or exchange approval. | Legal review + product owner: obtain written clarification from BSE or qualified counsel. | Open |
| FI-003 — BLOCKER | Which commodity price feed (MCX, NCDEX, or licensed vendor) is licensed for commercial display in the product? | Blocks Workspace 4 commodity prices. MCX/NCDEX EOD data is publicly available but commercial re-serving may require licensing. | Product owner + counsel: verify MCX/NCDEX terms; evaluate licensed alternatives. | Open |
| FI-004 — BLOCKER | Is BSE/NSE announcements API data available under terms that permit commercial aggregation and display? | Blocks Workspace 5 filing feed. Exchange APIs may have commercial use restrictions. | Product owner: request written API terms from BSE/NSE or evaluate licensed announcement aggregators. | Open |
| FI-005 | Is extraction and verbatim display of quotes from annual report PDFs (with source attribution) permitted when served through the product? | Annual reports are publicly filed but the right to extract, aggregate, and commercially re-serve verbatim text may require confirmation. | Legal review + product owner. Default: link to original PDF; do not serve extracted text until rights are confirmed. | Open |
| FI-006 | What is the technical architecture for PDF text extraction? (BSE XBRL machine-readable tags vs. PDF OCR/text extraction vs. licensed text provider?) | Implementation decision with major cost/quality implications. XBRL is structured but not all disclosures are tagged. PDF extraction is error-prone and legally sensitive. | Engineering + data owner: evaluate XBRL coverage, licensed text providers, and extraction quality before building the pipeline. | Open |
| FI-007 | How does the entity matching pipeline handle companies with similar names, ISIN changes from splits/mergers, or delisted instruments? | Poor entity matching corrupts financial data across workspaces and creates compliance risk. | Resolved provisionally by D-029: implemented deterministic point-in-time mapping with validity dates `[valid_from, valid_to]` and similar-name merge prevention; verified via regression tests on real Tata Steel 10:1 split ISIN change and peer distinction. | Resolved provisionally; regression-tested |
| FI-008 | What is the retention policy for financial statements, filing extracts, and company data under the chosen data licence? | Provider licence may restrict long-term storage of extracted financial data. | Counsel + engineering: define retention rules per source before storing any financial data. | Open |
| FI-009 | Are earnings call transcripts available through a licensed provider (e.g., licensed aggregator), or only through publicly filed BSE/NSE documents? | Blocks verbatim earnings commentary display in Workspace 5. Unofficial transcript sources may have licensing and accuracy issues. | Product owner: evaluate licensed transcript providers; check which companies file transcripts with exchanges. | Open |
| FI-010 | Should the Research Workspace store user panel layouts server-side (per user account) or client-side (localStorage/IndexedDB)? | Server-side requires user auth; client-side limits cross-device sync. Architecture and privacy implications differ. | Engineering + product owner: decide before implementing Workspace 6. Default: server-side per user account; requires authenticated session. | Open; default documented |
| FI-011 | Does adding financial intelligence content change the Indian securities-law classification of the product? | Company research and fundamental data display may trigger different regulatory obligations than intraday scanning alone. | Product owner + qualified securities counsel: include Financial Intelligence features in the regulatory scoping letter (Q-002). | Open |
| FI-012 | Which primary financial data vendor provides the best coverage, data quality, and commercial terms for Indian listed companies? | Determines feasibility and cost of Workspace 2–4. | Product owner: evaluate and compare Tijori Finance, licensed aggregators, and direct BSE/NSE data as specified in `18_DATA_PROVIDER_EVALUATION.md`. | Open |

---

## Work that can proceed while blockers are open

**Market Intelligence:**
- Documentation, UI prototype, algorithm fixtures and backtest framework using synthetic or expressly permitted historical fixtures.
- Provider-neutral adapters and mock provider.
- Internal chart rendering and interface accessibility tests.
- Legal/provider interview preparation.

**Financial Intelligence:**
- Documentation and planning (completed 2026-10-30).
- UI mockups and component designs for Workspaces 2–6 using synthetic placeholder data.
- Provider-neutral ingestion adapter interface design.
- Entity resolution design and test fixtures.
- Progressive disclosure UI pattern prototyping with static data.

---

## Work that must not be enabled before blockers resolve

- Public display of real live/derived market data without a matching licence.
- Public display of financial statements, filing extracts, or company data without confirmed data rights.
- Commodity price display without a licensed or officially permitted source.
- Paid commercial launch.
- Public claims about hits, accuracy, profitability or backtested edge without reviewed methodology.
- Personalized calls, trade execution, broker-account integration or other scope expansion.
- Production ingestion pipeline for Financial Intelligence data before Gate 3 passes.
