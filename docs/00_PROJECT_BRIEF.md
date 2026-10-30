# 00 — Project Brief

**Project:** ZoneScan (working codename)
**Document status:** Revised; expanded scope approved for documentation and planning. Implementation has not started on new modules.
**Last reviewed:** 2026-10-30
**Market:** India; NSE F&O equity stocks, listed companies, sectors, and commodities.

## Product summary

ZoneScan is a **Financial Intelligence Terminal** — a mobile-first, browser-based platform that combines intraday market analytics with company intelligence, relationship mapping, supply-chain context, and news/filing research in a single coherent workspace.

The **Market Intelligence** module (existing) scans NSE F&O equities during the trading session, presenting ranked bullish and bearish stock lists, rule-based order-block zones, price and liquidity levels, and market context. The additional modules bring company fundamentals, ownership and supply-chain intelligence, and a customizable research workspace to the same terminal.

The guiding design principle is:

> **Bloomberg-level information depth, understandable through progressive disclosure.**

Every important metric, relationship, or score must expose:
- A plain-language explanation of what the number means and why it matters.
- Units, reporting period, and data source with as-of date.
- Evidence and confidence status (disclosed, verified, inferred, unconfirmed) where relevant.
- A path to underlying detail without overwhelming the entry view.

The app is a **scanner, analytics, and research aid** — not a broker, exchange, investment adviser, research analyst, or automated trading system. That product description is not a legal classification; a qualified securities lawyer must review the actual features, outputs, and marketing before any public launch.

## User problem

Traders and analysts currently split their research across multiple disconnected tools: a charting app for intraday structure, a financial database for fundamentals, broker research for supply-chain context, and news aggregators for filings. ZoneScan consolidates these into one workspace so that a user can move from "which stocks have strong intraday momentum?" to "what is this company's key raw-material exposure?" to "what did they say in the last investor presentation?" without switching applications.

## Primary users

- Intraday traders examining NSE F&O equity stocks (existing primary use case).
- Fundamental analysts doing pre-earnings research on Indian listed companies.
- Portfolio managers checking sector concentration, ownership, and supplier risk.
- Part-time traders and learners who want explainable, well-sourced context.

These are target personas, not validated customer research. Validate with user interviews before locking positioning or pricing.

## Six connected workspaces

| # | Workspace | Core value |
|---|---|---|
| 1 | **Market Intelligence** | Intraday scanner, scores, zones, X-Ray (existing) |
| 2 | **Company Intelligence** | Financial statements, profitability, segments, valuation, shareholding |
| 3 | **Relationship Intelligence** | Suppliers, customers, competitors, ownership, subsidiaries |
| 4 | **Supply Chain & Commodities** | Raw-material dependencies, commodity prices, evidence-based impact scenarios |
| 5 | **News & Filings** | Regulatory filings, investor presentations, earnings calls, source-linked explanations |
| 6 | **Research Workspace** | Customizable draggable panels, saved layouts, notes, company comparison graphs |

## Core product loop

1. Open the board before or after market opens.
2. Review ranked bullish and bearish stocks with score, zone, and sector context.
3. Open a stock chart to inspect the intraday setup.
4. Navigate to Company Intelligence to check fundamentals and valuation context.
5. Check Relationship Intelligence for supply-chain or ownership risk that may affect the trade thesis.
6. Review recent filings or news that could move the stock.
7. Compile research in the workspace. The user independently decides what action to take in their broker app; ZoneScan does not place orders.

## Product principles

1. **Explain, do not command.** Show calculations and chart levels without buy/sell calls or guaranteed outcomes.
2. **Depth with progressive disclosure.** The summary view serves a fast decision; drill into full detail on demand.
3. **Truthful about everything.** Show source, timestamps, and data status. Distinguish disclosed, verified, inferred, and unconfirmed information for every relationship and claim.
4. **No repainting.** Confirm analysis only from closed candles and confirmed swings.
5. **Measure before marketing.** Backtest transparently; never invent hit rates, accuracy, or profit claims.
6. **Mobile first.** Core board works from 360 px width; research workspace can use desktop layout.
7. **Legal access comes before monetization.** Market-data rights and regulatory review are launch gates and apply to all six workspaces.

## Scope assumptions

- Primary intraday universe: current NSE F&O equity-stock list, refreshed from a permitted source.
- Company intelligence covers Indian-listed companies accessible through official public sources (BSE/NSE filings, MCA, SEBI disclosures) and licensed financial data providers.
- Supply-chain and commodity data derives from disclosed company filings, official commodity exchanges, and licensed secondary sources — never invented or scraped without authorization.
- English UI for the first release.
- INR pricing if monetized; no price is approved in this baseline.

## Out of scope for the first release

- Broker order placement or account-level trading permissions.
- Automated or algorithmic execution.
- Personalized recommendations, explicit trade calls, price targets, or suggested stop-losses.
- A public social feed that lets staff or users post calls or targets.
- International markets beyond NSE.
- AI-generated financial forecasts presented as predictions.

## Non-negotiable launch gates

- **Market-data rights:** No public or paid live-data product until the selected provider/exchange agreement expressly allows the required display, derived analytics, storage, and redistribution.
- **Company/fundamental data rights:** No display of financial statements or filing extracts without confirming permitted use of the source (BSE XBRL, licensed aggregator, MCA portal, etc.).
- **Regulatory review:** Obtain written advice from qualified Indian securities counsel before public launch or monetization.
- **Algorithm validation:** Do not publish hit rates, accuracy claims, or performance claims without a leakage-resistant, out-of-sample backtest.
- **Truthful data status:** Never label delayed, missing, synthetic, inferred, or stale data as live or verified.

See `docs/08_SECURITY_PRIVACY_COMPLIANCE.md` and `docs/11_ROADMAP.md`.
