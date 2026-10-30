# 19 — Financial Intelligence Module Specification

**Status:** Planning/documentation only. No implementation has started.
**Last reviewed:** 2026-10-30
**Depends on:** `00_PROJECT_BRIEF.md`, `03_ARCHITECTURE.md`, `07_DATA_MODEL.md`, `11_ROADMAP.md`

---

## 1. Purpose

This document specifies the five additional workspaces that extend ZoneScan beyond intraday market analytics into full company and relationship intelligence. All five workspaces share the core product principle: **Bloomberg-level information depth, understandable through progressive disclosure.**

The existing Market Intelligence module (Workspace 1) is specified in `01_PRODUCT_REQUIREMENTS.md`, `05_ALGORITHMS.md`, and `06_API_CONTRACTS.md`. This document covers Workspaces 2–6.

---

## 2. Information quality framework

Every piece of information displayed in Workspaces 2–6 must carry an explicit evidence and confidence status:

| Status | Meaning | UI Treatment |
|---|---|---|
| **Disclosed** | Directly stated in a regulatory filing, annual report, or official exchange disclosure | Plain text with source and filing date |
| **Verified** | Disclosed data cross-checked against an independent licensed source | Source label; both references accessible |
| **Inferred** | Derived by documented computation from disclosed data (e.g., gross margin from revenue/cost of sales) | Calculation shown on demand; labelled "Inferred" |
| **Unconfirmed** | Reported in news or analyst estimates; not yet confirmed in a filing | Clear badge: "Unconfirmed — source: [outlet/date]" |
| **Unavailable** | Data not currently available or not yet extracted | Explicit empty state; never substituted with zero or a placeholder |

Never present Inferred or Unconfirmed data as if it were Disclosed. Never invent relationships, financial figures, or supply-chain impacts.

---

## 3. Workspace 2 — Company Intelligence

### 3.1 Purpose

Provide a one-stop company profile that answers: "What does this company do, how profitable is it, how is it valued, and who owns it?"

### 3.2 Core views

#### 3.2.1 Company Overview
- Legal name, BSE/NSE listing codes, CIN/ISIN, registered address, year of incorporation, industry, sector.
- One-line plain-language description of the business and its primary revenue source.
- Source: BSE/NSE company master, MCA21. Data status: Disclosed.

#### 3.2.2 Financial Statements
Display the three core financial statements for the most recent annual period and, where available, quarterly:
- **Income Statement:** Revenue, Cost of Goods Sold, Gross Profit, EBITDA, EBIT, PBT, PAT, EPS (basic/diluted). Each line carries its reporting period and source filing reference.
- **Balance Sheet:** Total Assets, Fixed Assets, Current Assets, Cash, Total Liabilities, Equity, Book Value per Share.
- **Cash Flow Statement:** Operating, Investing, Financing cash flows; Free Cash Flow (inferred).

All values in INR crores (₹ Cr) unless the filing uses a different unit, which must be shown explicitly.

Progressive disclosure: the entry view shows 8–10 headline numbers; the full statement is one tap away.

**Data source options (not yet selected; requires rights verification):**
- BSE XBRL tagged filings (Disclosed, machine-parseable).
- NSE public data.
- Licensed financial data aggregator (e.g., Tijori Finance, Screener.in API, licensed data vendor).

**Release gate:** No financial data may be displayed without confirming the permitted use of the source. BSE XBRL is publicly available but aggregating and re-serving it commercially requires legal review.

#### 3.2.3 Profitability & Margins
Derived (Inferred) metrics with formulas shown on demand:
- Gross Margin, EBITDA Margin, PAT Margin, ROE, ROCE, ROIC, Asset Turnover.
- Three-year trend sparkline. "Margin improved / declined" plain-language summary.

#### 3.2.4 Segment Breakdown
- Revenue and profit by business segment, geography, or product where disclosed.
- Source: segment note in annual report / BSE filing. Status: Disclosed.
- If no segment data is disclosed, show explicit "Segment data not separately disclosed in available filings."

#### 3.2.5 Valuation Multiples
- P/E (trailing and forward estimate if available), P/B, EV/EBITDA, Dividend Yield, Market Cap.
- Forward estimates must be labelled "Analyst consensus estimate — Unconfirmed" with source and date.
- Never present a target price or buy/sell recommendation.

#### 3.2.6 Shareholding Pattern
- Promoter, FII, DII, Retail, Other categorized holdings from the latest BSE/NSE quarterly shareholding disclosure.
- Change quarter-over-quarter with plain-language summary ("Promoter stake increased by 1.2% this quarter").
- Source: BSE shareholding data. Status: Disclosed.

### 3.3 Required screen states
All states from `02_UX_FLOWS.md` apply plus:
- **Filing lag:** when the most recent period is older than one quarter, show explicit "Most recent available filing: [period]".
- **Restatement:** if data was restated, mark the affected period with a restatement indicator and note.

---

## 4. Workspace 3 — Relationship Intelligence

### 4.1 Purpose

Map who this company buys from, sells to, competes with, and who controls or owns it. Every displayed relationship must trace back to an evidence source.

### 4.2 Core views

#### 4.2.1 Suppliers & Customers
- List of disclosed major customers and suppliers (top 10% concentration customers, major raw-material suppliers).
- Source: Risk factors, related-party disclosures, MDA in annual reports/filings. Status: Disclosed.
- Relationship strength: revenue/spend concentration percentage where disclosed; otherwise Unconfirmed.
- "Why does this matter?" tooltip: plain-language explanation of the customer/supplier dependency.

**Important:** Do not infer supplier relationships from commodity prices or industry averages without an explicit filing reference. Label any industry-standard inference as Inferred with the derivation rule shown.

#### 4.2.2 Competitors
- Peer group: companies in the same sub-industry with comparative key metrics (Revenue, EBITDA Margin, P/E, ROCE).
- Source: company-defined peer comparison in annual report where disclosed, or BSE industry classification. Status: Disclosed or Inferred depending on method.
- "How to compare" tooltip: explain what each ratio measures and why peers are useful context.

#### 4.2.3 Corporate Ownership
- Promoter group entities, holding companies, subsidiaries, and associates as disclosed in filings.
- Beneficial ownership per the latest shareholder list where available.
- Source: MCA21, annual report subsidiary list, BSE disclosures. Status: Disclosed.
- Ownership chain visualization: tree or simple indented list. Depth limited to three levels; deeper chains linked to the source filing.

#### 4.2.4 Subsidiary Map
- Consolidated subsidiary list from annual report: name, jurisdiction, holding percentage, activity.
- Plain-language note: "This subsidiary contributed X% of revenue in FY[year]" where disclosed.

### 4.3 Evidence transparency requirements
Every relationship node must display:
- Evidence status badge (Disclosed / Inferred / Unconfirmed).
- Source document name, section, and date.
- A "Question this?" or "View source" link where the underlying document is publicly accessible.

---

## 5. Workspace 4 — Supply Chain & Commodities

### 5.1 Purpose

Help users understand whether a company's cost base or margins are exposed to commodity price movements, and what the evidence says about the magnitude of that exposure.

### 5.2 Core views

#### 5.2.1 Raw Material Profile
- Key raw materials identified in cost-of-production notes, management commentary, or risk factors.
- Approximate share of COGS/revenue where disclosed.
- Source: annual report, BSE filing. Status: Disclosed.
- If not explicitly disclosed, show "Raw material breakdown not separately disclosed in available filings."

#### 5.2.2 Commodity Price Feed
- Current and 30-day trailing price for relevant commodities (e.g., steel, aluminium, crude oil, cotton, specialty chemicals).
- Source: official commodity exchanges (MCX, NCDEX) or licensed price data provider. Data must never be invented or scraped without authorization.
- Plain-language context: "Steel HRC is ₹52,000/tonne, up 8% this month. This company purchases ~40% of its raw materials from steel, per its FY25 annual report."

**Release gate:** Commodity price display requires a licensed or officially permitted data source. MCX/NCDEX publicly available end-of-day data may be usable but requires legal confirmation for commercial re-serving.

#### 5.2.3 Impact Scenarios (Evidence-Based)
Deterministic scenario modelling — not AI forecasting:
- User selects a commodity price change (e.g., "Steel +10%").
- System applies the disclosed exposure percentage to compute a gross-margin impact estimate.
- Formula is shown: `Impact = Revenue × Raw-material share × Price change %`.
- Output is labelled "Illustrative scenario based on disclosed exposure; assumes no hedging, pricing power, or other offsetting factors. Not a forecast."

Rules:
- Only run scenarios where a numeric exposure percentage is disclosed or clearly calculable from filings.
- Never present a scenario output as a forecast, target, or recommendation.
- Sensitivity bounds must acknowledge the assumptions.

#### 5.2.4 Supply Chain Disruption Context
- Unconfirmed: news items mentioning supply disruption for this company's key inputs, tagged with source and date.
- Label clearly: "Reported but unconfirmed. Source: [outlet], [date]."

---

## 6. Workspace 5 — News & Filings

### 6.1 Purpose

Surface relevant regulatory filings, investor presentations, management commentary, and news in context — with source links, plain-language explanations, and clear evidence status.

### 6.2 Core views

#### 6.2.1 Regulatory Filings Feed
- BSE/NSE announcements for this company in reverse chronological order.
- Filing type labels: Board Meeting Outcome, Shareholding, Earnings Result, AGM Notice, Insider Trading, DRHP, DRHP Amendment, Investor Presentation, etc.
- Plain-language summary per filing type: "Board approved interim dividend of ₹5/share (yield ~1.2% at current price)."
- Source: BSE/NSE public disclosure portal. Status: Disclosed.
- Link to original filing PDF — never substitute a rewritten version for the original document.

**Release gate:** BSE/NSE provide a public API for company announcements. Terms must be confirmed for commercial aggregation and display.

#### 6.2.2 Annual Reports
- Link to the most recent 3 annual reports (PDF) from BSE/NSE public disclosure.
- Highlighted sections: MD&A, Key Financial Highlights, Auditor's Report, Related-Party Disclosures, Segment Notes.
- Extracted quotes from management commentary shown verbatim with paragraph reference. Label: "From [Company] Annual Report FY[year], p.[page]."

#### 6.2.3 Earnings Call Context
- If transcripts are publicly available (from BSE filing or licensed provider): show verbatim excerpts for key topics (guidance, margin comments, capex plans).
- No paraphrasing that could alter the meaning; show exact quotes only.
- Status: Disclosed where transcript is from official filing; Unconfirmed if from third-party aggregator.

#### 6.2.4 News Feed
- News items from licensed news sources or official exchange feeds, tagged by relevance to this company.
- Status: Unconfirmed unless the item references an official filing.
- Never present news speculation as confirmed fact.

---

## 7. Workspace 6 — Research Workspace

### 7.1 Purpose

A customizable canvas where a user can compose their own research view from any combination of data panels, save it, and revisit it.

### 7.2 Core capabilities

#### 7.2.1 Draggable Panel System
- Users can add, remove, resize, and reposition data panels.
- Panel types: Chart, Score Breakdown, Financial Summary, Shareholding, Relationship Map, Commodity Exposure, Filing Feed, Notes.
- Layouts saved per user, per company or as a named template.
- On narrow screens (mobile), panels collapse to a vertical stack in the user's preferred order.

#### 7.2.2 Company Comparison
- Side-by-side display of up to four companies across any financial metric available in the system.
- Column headers show each company's symbol, name, and reporting period. Cells show values with availability status.

#### 7.2.3 Saved Notes
- User-owned plain text notes attached to a company or a specific filing/announcement.
- Notes are private to the user; never shared without explicit user action.
- Exported in the journal CSV export.

#### 7.2.4 Research Graph
- Simple node-edge visualization of a company's mapped relationships (from Workspace 3) overlaid with any user-pinned data points (e.g., competitor margin, shared supplier).
- Not a recommendation; it is a user-composable context map.

---

## 8. Data pipeline architecture

The following pipeline applies to Workspaces 2–5. It supplements the existing Market Intelligence pipeline in `03_ARCHITECTURE.md`.

```
Official Sources
  BSE XBRL filings          NSE company master
  MCA21 filings             Commodity exchange APIs
  BSE/NSE announcements     Licensed financial data vendor
        |                         |
        v                         v
   Ingestion Worker         Provider Adapter Layer
   (scheduled, not live)    (same pattern as market data)
        |                         |
        v                         v
  Extraction & Parsing      Normalization & Validation
  (XBRL tags, PDF text      (unit normalization, period
   extraction — planned)     alignment, quality flags)
        |
        v
  Entity Matching & Deduplication
  (ISIN/CIN linking, name disambiguation)
        |
        v
  Evidence Tagger
  (assign Disclosed/Inferred/Unconfirmed to each field)
        |
        v
  Normalized Document Store
  (PostgreSQL: companies, financials, relationships,
   filings, commodities, news)
        |
        v
  API Layer (/api/v1/companies/..., /api/v1/filings/...)
        |
        v
  Next.js Frontend (Workspaces 2–6)
```

### Key pipeline rules

1. **Never invent data.** If extraction fails, the field is Unavailable.
2. **Source provenance is mandatory.** Every stored value carries: source system, document reference, extraction timestamp, and extraction method (machine-parsed vs. manual).
3. **Period alignment.** Financial statements from different periods must not be silently combined. Each row carries its exact reporting period (e.g., "FY2025" or "Q2 FY2026").
4. **No re-serving without rights.** Displaying aggregated filing data commercially requires legal confirmation; keep extraction behind an internal-use gate until rights are confirmed.
5. **Evidence tagging is not optional.** The evidence status field is required on every displayed value, not a nice-to-have.
6. **Real-data pilot contract.** See `docs/20_REAL_DATA_PILOT_SPEC.md` for the exact fact provenance, source URLs, extraction notes, and evidence classifications prepared for the Bharat Forge Limited pilot ahead of Gate 3 clearance.

---

## 9. GitHub component evaluation (selective)

The following components were evaluated for potential reuse. **None are installed or cloned.** This is an adoption decision record only.

| Component / Library | License | Evaluation | Decision | Notes |
|---|---|---|---|---|
| **TradingView Lightweight Charts** | Apache 2.0 | Used in Market Intelligence charts; actively maintained | **Adopt (continue)** | Already referenced in `03_ARCHITECTURE.md`; verify attribution requirement |
| **Recharts** (React charting) | MIT | Solid accessible charts; simpler than full TradingView for financial KPI sparklines | **Study** | Evaluate for Company Intelligence bar/line charts where TradingView is heavyweight |
| **React Flow** | MIT | Node/edge graph for relationship maps | **Study** | Candidate for Workspace 3 ownership map and Workspace 6 research graph; check accessibility support |
| **shadcn/ui** | MIT | Accessible, composable Radix-based components; Tailwind integrated | **Adopt (candidate)** | Aligns with existing Tailwind setup; evaluate for modal, sheet, tabs, and data-table components in Workspaces 2–6 |
| **@tanstack/react-table** | MIT | Headless, accessible data tables | **Adopt (candidate)** | Suitable for financial statement tables with sorting and column visibility |
| **react-beautiful-dnd / dnd-kit** | MIT / MIT | Drag-and-drop primitives | **Study** | For Research Workspace panel system; dnd-kit is newer and more accessible |
| **Mermaid** (diagram rendering) | MIT | Good for static relationship diagrams in docs; not suitable for interactive runtime maps | **Reject for runtime** | Continue using in documentation; do not use in the production UI |
| **Zod** | MIT | Schema validation; TypeScript-first | **Adopt (candidate)** | Consistent validation of API response shapes, especially for variable financial data structures |
| **date-fns** | MIT | Lightweight date utilities | **Adopt (candidate)** | Needed for period alignment and filing date display |

**Installation rule:** No component is installed without a confirmed need in an active implementation phase, a reviewed version pinned, and CI validation. Do not install all candidates preemptively.

---

## 10. Limitations and open questions

These open questions must be resolved before implementation begins on any Workspace 2–6 feature:

| ID | Question | Impact | Owner |
|---|---|---|---|
| FI-001 | Which financial data provider/source is licensed for commercial display of Indian company financials? | Blocks all of Workspace 2 | Product owner + counsel |
| FI-002 | Is BSE XBRL data legally re-servable in a paid product? Under what terms? | Blocks Workspace 2 filing display | Legal review |
| FI-003 | Which commodity price feed is licensed for commercial display? | Blocks Workspace 4 commodity prices | Product owner |
| FI-004 | Are BSE/NSE announcement feeds available via a licensed API for commercial aggregation? | Blocks Workspace 5 filing feed | Product owner |
| FI-005 | Is extraction of verbatim quotes from annual report PDFs permitted when re-served in the product? | Blocks annual report quote display | Legal review |
| FI-006 | What is the data architecture for PDF text extraction? (OCR, tagged XBRL, licensed text?) | Implementation decision for Workspaces 2–5 | Engineering |
| FI-007 | How does the entity matching pipeline disambiguate companies with similar names or ISIN changes? | Data quality risk across all workspaces | Engineering + data owner |
| FI-008 | What is the retention policy for financial statements and filing extracts under the chosen data licence? | Compliance | Counsel + engineering |
| FI-009 | Are earnings call transcripts available through a licensed provider? | Blocks Workspace 5 earnings commentary | Product owner |
| FI-010 | How does the Research Workspace store user layouts? (Server-side per user, or client-side?) | Architecture decision | Engineering |

These items must be added to `docs/13_OPEN_QUESTIONS.md` with their owners.
