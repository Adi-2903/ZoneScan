# 02 — UX Flows and Screen Inventory

## Primary navigation

ZoneScan uses a six-workspace navigation model. The first workspace (Market Intelligence) is the default landing screen after authentication.

**Workspaces:**
1. Market Intelligence (existing)
2. Company Intelligence (P3 — planning)
3. Relationship Intelligence (P3 — planning)
4. Supply Chain & Commodities (P3 — planning)
5. News & Filings (P3 — planning)
6. Research Workspace (P3 — planning)

**Within Market Intelligence:**
- Board (default)
- Stock Detail
- Market X-Ray
- Watchlist (P1)
- Alerts (P1)
- Journal (P1)
- Learn (P1)
- Account / Plan
- Marketing and legal pages

Keep the primary board reachable in one tap from every Market Intelligence screen on mobile. The workspace switcher must not interfere with board-level navigation on narrow screens.

Navigation pattern:
- Mobile: bottom navigation bar with workspace icons (≤5 primary), with a "more" sheet for additional workspaces.
- Tablet/Desktop: left sidebar with workspace icons and labels, collapsible.
- Every workspace tab must be keyboard-focusable with a visible focus indicator.

Do not add a complicated navigation system before real user testing. The Financial Intelligence workspaces share the header navigation but are behind their own feature and access gate.

---

## Key user flows

### Visitor → signed-in user

1. Visitor lands on the marketing page and views an honest product demo.
2. Visitor reads what the scores do and do not mean, pricing if enabled, and relevant risk/data disclosures.
3. Visitor signs in with Google.
4. User sees a preview or the permitted board according to backend entitlements.
5. If checkout is enabled, user selects a plan and completes payment through the approved payment provider.
6. The server verifies the payment webhook and updates subscription state; browser callback alone never grants access.
7. User sees a short onboarding walkthrough: board → stock chart → score/zone interpretation → (optionally) company profile overview.

### Daily trader workflow (Market Intelligence)

1. Before open, show previous session's board and clearly label the snapshot as historical.
2. From 09:15 until the configured settling period ends, show a settling indicator and explain what data is still stabilizing.
3. Review Bullish and Bearish boards and the market/sector context.
4. Open a stock detail chart and inspect the zone, its state, support/resistance, liquidity and score breakdown.
5. Optionally navigate to Company Intelligence for fundamentals context on the selected stock.
6. Optionally review relevant filings or news in the News & Filings workspace.
7. Optionally add to the watchlist or set a permitted alert.
8. User makes any trading decision independently in a separate broker application; ZoneScan has no order-placement flow.
9. Optionally log a trade manually in the journal.

### Company research workflow (Financial Intelligence — planned)

1. User searches for a company or navigates from a stock in the board.
2. Company Overview loads with headline financials and source badges.
3. User reads the plain-language business description and key metrics.
4. User drills into the financial statements; progressive disclosure reveals full income statement.
5. User navigates to Relationship Intelligence to view suppliers and customers.
6. User checks commodity exposure in the Supply Chain workspace.
7. User opens the latest filing in News & Filings for management commentary.
8. User saves relevant panels to the Research Workspace for ongoing monitoring.

### Feed interruption (Market Intelligence)

1. The backend detects delayed or missing feed data.
2. Board response carries a degraded data state and source timestamp.
3. UI displays a clear warning and stops presenting old data as current.
4. Ingestion attempts reconnection and historical gap backfill.
5. Once data completeness checks pass, the backend publishes a fresh board and the UI removes the warning.
6. Operational events are logged for incident review.

---

## Screen inventory

### Market Intelligence screens (existing)

| Screen | Required content | Key actions |
|---|---|---|
| Landing | Original value proposition, demo, core features, methodology, pricing if approved, FAQ, disclosures | Sign in, learn how it works |
| Login | Google sign-in, terms/privacy links, error state | Authenticate |
| Board | Market status, timestamp, delay/settling banner, Bullish/Bearish tabs, ranked rows, top setup preview | Search, change side, open stock |
| Stock Detail | Candlestick chart, timeframe switch, zone overlays, levels strip, score breakdown, sector context, data timestamp | Change timeframe/layers, copy level, add watchlist, navigate to Company Profile |
| Market X-Ray | Dot map, bullish/bearish/choppy counts, sector leaders/laggards, index context | Select sector or stock (full click-through P1) |
| Watchlist (P1) | Saved instruments, latest score, zone distance, alert state | Add/remove stock, configure alert |
| Alerts (P1) | Alert rules, channels, quiet hours, recent delivery status | Create/pause/delete rule |
| Journal (P1) | Trade form, user trade history, snapshots, analytics, export | Add/edit/delete own trade, export CSV |
| Learn (P1) | Categorized short lessons and progress | Watch, resume, mark complete |
| Account | User profile, entitlement/plan, renewal date, invoices, devices/sessions, theme, logout | Manage account, sign out, request deletion |
| Admin | Feed health, instruments, users, entitlements, payments, alerts, parameters, content, audit | Role-protected operational actions |

### Financial Intelligence screens (Prototype implemented for Company Intelligence; production data/backend P3 pending Gate 3)

| Screen | Required content | Key actions | Prototype Status |
|---|---|---|---|
| Company Overview | Company name, identifiers, one-line description, headline financial KPIs, source badges, evidence status | Navigate to sub-views, navigate to filing | Implemented (Synthetic) |
| Financial Statements | Income statement, balance sheet, cash flow; period selector; toggle consolidated/standalone | Expand row, view filing source, switch period | Implemented (Synthetic) |
| Profitability & Margins | Margin trends (3-year), ROE, ROCE, ROIC sparklines with plain-language summary | Hover for formula, compare to sector peers | Implemented (Synthetic) |
| Segment Breakdown | Revenue/profit by segment/geography; source reference | View underlying filing section | Implemented (Synthetic) |
| Valuation | P/E, P/B, EV/EBITDA, Market Cap, Dividend Yield; analyst estimate disclaimer | Switch TTM/forward, compare peer | Implemented (Synthetic) |
| Shareholding | Promoter/FII/DII/Retail breakdown; QoQ change; source | View historical pattern | Implemented (Synthetic) |
| Suppliers & Customers | Disclosed relationships with concentration %; evidence status per row | View source document, filter by type | Implemented (Cytoscape.js) |
| Competitors | Peer table with comparative metrics; source of peer definition | Sort column, navigate to competitor profile | Implemented (Cytoscape.js) |
| Corporate Ownership | Ownership tree: holding companies, subsidiaries; depth limit with source link | Expand node, view MCA filing | Planned (Phase 4) |
| Subsidiary Map | Subsidiary list with jurisdiction, holding%, activity; source reference | Link to annual report subsidiary note | Planned (Phase 4) |
| Raw Material Profile | Key raw materials, share of COGS, source filing | View annual report section | Implemented (Synthetic) |
| Commodity Prices | Current and 30-day chart for relevant commodities; source and data status | Run impact scenario | Implemented (Synthetic) |
| Impact Scenario | Commodity price change slider, computed margin impact, formula and assumptions | Change assumption, save to workspace | Implemented (Interactive Heuristic) |
| Regulatory Filings | Reverse-chronological BSE/NSE announcements with type labels and plain-language summary | Open original PDF, filter by type | Implemented (Synthetic) |
| Annual Reports | Filing list; PDF link; extracted highlights with verbatim quotes and references | Open PDF section, navigate to excerpt | Planned (Phase 4) |
| Earnings Commentary | Verbatim transcript excerpts (if available); source and date | Navigate to full transcript | Planned (Phase 4) |
| News Feed | News items with source/date/unconfirmed badge | Open original article | Implemented (Disruption Signals) |
| Research Workspace | Draggable panels, saved layout list, company comparison table, notes editor | Add/remove panel, save layout, export notes | Planned (Phase 5) |

---

## Required screen states

Every screen must account for relevant states from this list:

- **Loading:** skeletons or progress; never an unexplained blank surface.
- **Empty:** explain why there is no data and how to proceed.
- **Error:** clear message, retry only when safe, and request/correlation ID where appropriate.
- **Market closed / holiday:** show last session's timestamp and closed state.
- **Settling:** label the board until the opening window and data-readiness gates pass.
- **Delayed:** show age/delay, not a live indicator.
- **Missing/invalid data:** disclose the affected symbol/metric; exclude it when required inputs are missing.
- **Synthetic demo:** persistent label on every screen using mock data.
- **Offline:** retain last view only with a visible offline label and timestamp.
- **Expired entitlement:** show permitted preview and a path to renew; protect server endpoints.
- **Payment pending/failed:** do not unlock paid features until verified confirmation.
- **Data rights gate (Financial Intelligence):** if a Financial Intelligence workspace is not yet enabled due to an unresolved data licence, show an explicit "Coming soon — pending data licensing" state, not a broken/empty screen.
- **Evidence unavailable:** if a specific data point cannot be sourced, show "Data not available" explicitly; never substitute zero or an estimated value without labelling it Inferred.

---

## Progressive disclosure pattern

Financial Intelligence screens must follow this pattern:
1. **Entry view** (always visible): 4–6 headline metrics with source badge and evidence status. Plain-language summary sentence.
2. **Expanded view** (one tap/click): full data table or chart with period selector.
3. **Source view** (on demand): exact source document reference, filing link, or formula derivation.
4. **Original document** (linked): BSE/NSE filing PDF or official source link.

Do not flatten all four levels onto the entry view. Do not hide the source — it must always be reachable within two interactions.

---

## Interaction guidelines

- Board rows should be dense but readable. Align numbers with tabular numerals.
- Use arrows and text labels along with red/green/amber colors; never communicate direction by color alone.
- Chart zone/level labels must not collide. On narrow screens, prefer a compact levels strip and expandable details.
- Provide an accessible table alternative to the X-Ray dot map.
- Do not animate every row on each one-minute update. Use brief, restrained indication of what changed.
- Avoid dark patterns: no fake countdown timers, fake crossed-out prices, obstructive cancellation, or preselected paid add-ons.
- Evidence status badges must be visually distinct and accessible (not color-only). Use text labels: "Disclosed", "Inferred", "Unconfirmed", "Unavailable".
- Financial table numbers: right-align, tabular numerals, consistent decimal precision per column, explicit unit in header.
