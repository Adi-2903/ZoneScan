# 14 — Design System Baseline

## Visual direction

A quiet, professional market terminal: compact and data-dense without looking cluttered. Dark theme is the default; light theme is supported. Do not imitate the exact visual identity of any reference product.

The expanded product vision — a six-workspace Financial Intelligence Terminal — demands that the design system scale beyond the intraday board to accommodate:
- Dense financial tables with multi-period column groups.
- Evidence status badges (Disclosed, Inferred, Unconfirmed, Unavailable).
- Progressive disclosure panels (summary → detail → source → document).
- Relationship map visualizations.
- Research workspace drag-and-drop canvas.

The core terminal aesthetic (dark, data-dense, professional) applies across all workspaces. Financial data panels are deliberately information-rich; their density is intentional, not a bug.

---

## Semantic colors

Use CSS variables so themes can change without editing components.

**Market Intelligence:**
- Bullish: green plus text/icon `Bullish` or up-arrow.
- Bearish: red plus text/icon `Bearish` or down-arrow.
- Choppy/neutral: amber or neutral plus explicit text label.
- Delayed/data warning: amber with clear message and timestamp.
- Error/unavailable: accessible error color plus plain-language text.
- Synthetic data: persistent badge/band, never just a subtle footer.

**Financial Intelligence (additional):**
- Disclosed: muted green badge — solid data from official filing.
- Inferred: muted blue badge — computed from disclosed data; formula accessible.
- Unconfirmed: amber badge — from news or analyst source; not in a filing.
- Unavailable: neutral/muted badge — data not available; never substituted with zero.
- Data rights gate: a distinct muted surface indicating "Coming soon — pending data licensing."

No direction, status, or evidence class may be conveyed by color alone. Every semantic color has an accompanying text label.

---

## Typography and numbers

- Use tabular numerals for ranks, prices, percentages, scores, and all financial values.
- Keep symbols, prices and scores visually scannable.
- Use consistent precision per field; avoid showing spurious decimals beyond the data source's precision.
- Label percentages and units clearly; financial values show INR ₹ Cr or explicit unit in column headers.
- Financial table cells: right-align numeric values; left-align text identifiers.
- Negative financial values: use parentheses in addition to the negative sign and a distinct text style (not color only).
- Restatement indicator: a superscript `R` or explicit inline label "Restated", not color alone.

---

## Layout

- Design mobile first at 360 CSS px.
- **Market Intelligence board row:** rank, symbol, last price, percent change, strength, sector and movement indicator. On narrow screens, move secondary content into a detail view rather than shrinking text to illegibility.
- **Financial Intelligence entry view:** headline KPIs as a card grid (max 2 columns on mobile, 4 on desktop). Full table is one tap away.
- **Financial table layout:** horizontal scrolling is acceptable for multi-period column groups on mobile. Freeze the row-label column. Provide a summary card view as the default on narrow screens.
- Provide top-level Bullish/Bearish switching and workspace switching without requiring horizontal scrolling of the primary navigation.
- The X-Ray can offer a landscape/desktop visualization, but must have an accessible list/table version.
- Research Workspace: draggable panels collapse to a vertical stack on mobile; drag-to-reorder is the mobile interaction.
- Chart layers include toggles where clutter becomes a problem; do not render every historical object by default.

---

## Progressive disclosure pattern

Applied to all Financial Intelligence screens:

```
Level 1: Entry card (always visible)
  → 4–6 headline values + evidence status badges + plain-language summary
Level 2: Expanded view (one tap/click)
  → Full table or chart with period selector
Level 3: Source panel (on demand)
  → Formula derivation or filing reference with section name and date
Level 4: Original document (linked)
  → Direct link to BSE/NSE filing PDF or official source
```

Implementation rule: the "Source" action must always be reachable within two interactions from any displayed data point. It is not optional.

---

## Interaction and accessibility

- Aim for 4.5:1 contrast for normal text.
- Minimum interactive target: 44×44 CSS px.
- Focus indicators must be visible and keyboard navigation supported.
- Controls need labels; tooltips cannot be the only place important information exists.
- Use motion sparingly; respect reduced-motion preferences.
- Chart zones/lines require readable labels and must avoid overlap.
- Loading, offline, delayed, unavailable and synthetic states must use clear text, not icon-only signs.
- Evidence status badges: must be text-labeled, not color-only. Accessible name must include the evidence class.
- Financial tables: column headers require scope attributes. Numeric cells require accessible names when the column header alone is insufficient.
- Relationship map nodes: every node must be keyboard-focusable with a visible label and accessible name.
- Research Workspace drag handles: must have keyboard-equivalent reorder actions (move up/down panel buttons as fallback).

### Local dashboard polish defaults

- Keep the mobile Board and X-Ray destinations visible as a two-action navigation row; the stock-detail back action returns to the section that opened it.
- Use at least 44 CSS px for primary mobile navigation, board-side tabs, theme control and timeframe controls. Every interactive map point remains a native keyboard-focusable button with a symbol, move, classification and timestamp/unavailable reason available in its accessible name or tooltip.
- Keep the X-Ray's five states labeled in text and provide a collapsible table view for instrument values. Dot position is a layout only; dot size represents the absolute displayed move. Do not imply sector clustering or market-wide coverage.
- Label the fixed fixture snapshot as synthetic on every screen. A fixture market state of `unknown` must render as "Market status unknown"; never infer open/closed from the timestamp.
- Keep neutral score values visually neutral. Apply direction colors only to labeled directional states, and maintain contrast for muted metadata in both themes.
- At 360 px, prefer stacked cards, wrapping legends and horizontally scrollable dense data over shrinking controls or numeric text. Keep tablet navigation and desktop sidebar layouts within the same spacing and panel system.

---

## Components to standardize

### Market Intelligence (existing)

- `MarketStatusChip`
- `DataFreshnessBanner`
- `BoardTabs`
- `BoardRow`
- `ScoreBadge` / `ScoreBreakdown`
- `SectorAlignmentBadge`
- `ZoneChart`
- `LevelsStrip`
- `ZoneStateLabel`
- `EmptyState`, `ErrorState`, `LoadingSkeleton`
- `PaywallGate`
- `AccessibleXRayTable`

### Financial Intelligence Components

#### Implemented in Prototype (Synthetic Fixtures)

- `EvidenceBadge` — renders Disclosed / Verified / Inferred / Unconfirmed / Unavailable label with accessible styling, glyphs, and source inspection triggers
- `SourcePanel` — accessible slide-out drawer disclosing mathematical formulas, statutory excerpt citations, and synthetic disclaimer on demand
- `FinancialTable` — multi-period financial statement table with frozen sticky row headers, consolidated/standalone and annual/quarterly toggles, accounting parentheses for negatives, and line-item source inspection
- `KPICard` — headline metric card with value, unit, reporting period, evidence badge, YoY delta arrow, and source inspection trigger
- `MetricSparkline` — pure SVG multi-period sparkline with hoverable tooltip pill, gradient area fill, and accessible table summary
- `ShareholdingBar` — segmented horizontal bar showing promoter/FII/DII/retail breakdown with QoQ change badges and pledge indicator
- `SegmentChart` — interactive business segment proportion bar with division spotlight cards and accessible table alternative
- `RelationshipMap` — interactive Cytoscape.js network graph with concentric layout, typed node styles, edge evidence indicators, pan/zoom/reset controls, node inspector panel, and accessible adjacency table alternative
- `SupplyChainSimulator` — raw material profiles, interactive commodity shock slider (-20% to +30%), real-time gross margin impact and bps compression calculator, transparent formula, and disruption signal alerts
- `FilingList` — reverse-chronological statutory filing feed with category pills (Quarterly Results, Material Contract, Shareholding, Expansion) and excerpt inspection

#### Planned (Future Phases)

- `ResearchPanelContainer` — drag-and-drop panel wrapper with keyboard reorder fallback (Workspace 6)
- `CompanyComparisonTable` — side-by-side metric table for up to 4 companies with availability status per cell (Workspace 2 expansion)
- `DataRightsGate` — screen/section placeholder shown when a workspace is not yet enabled due to unresolved data licensing (Production Gate 3)

### Third-party components and evaluation

- **Cytoscape.js** (`cytoscape`, `@types/cytoscape`): **Adopted for Prototype**. Used for interactive Company Intelligence relationship network graphs with concentric layout, typed styling, and accessible fallback.
- `shadcn/ui`: accessible Radix-based dialog, sheet, tabs, select, data table — candidate for Workspaces 2–6 modals and forms.
- `@tanstack/react-table`: headless table for `FinancialTable` implementation — candidate.
- `dnd-kit`: accessible drag-and-drop for Research Workspace panels — candidate.
- `Recharts`: candidate for advanced financial time-series charts; prototype uses lightweight bespoke SVG sparklines.

Build only components needed for the phase currently under development. Evaluate candidates at the start of each phase, not preemptively.
