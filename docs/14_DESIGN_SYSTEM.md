# 14 — Design System Baseline

## Visual direction

A quiet, professional market terminal: compact and data-dense without looking cluttered. Dark theme is the default; light theme is supported. Do not imitate the exact visual identity of the reference product.

## Semantic colors

Use CSS variables so themes can change without editing components.

- Bullish: green plus text/icon `Bullish` or up-arrow.
- Bearish: red plus text/icon `Bearish` or down-arrow.
- Choppy/neutral: amber or neutral plus explicit text label.
- Delayed/data warning: amber with clear message and timestamp.
- Error/unavailable: accessible error color plus plain-language text.
- Synthetic data: persistent badge/band, never just a subtle footer.

No direction or status can be conveyed by color alone.

## Typography and numbers

- Use tabular numerals for ranks, prices, percentages and scores.
- Keep symbols, prices and scores visually scannable.
- Use consistent precision per field; avoid showing spurious decimals beyond the data source's precision.
- Label percentages and units clearly.

## Layout

- Design mobile first at 360 CSS px.
- The board row includes rank, symbol, last price, percent change, strength, sector and movement indicator. On narrow screens, move secondary content into a detail view rather than shrinking text to illegibility.
- Provide top-level Bullish/Bearish switching without requiring horizontal scrolling.
- The X-Ray can offer a landscape/desktop visualization, but must have an accessible list/table version.
- Chart layers include toggles where clutter becomes a problem; do not render every historical object by default.

## Interaction and accessibility

- Aim for 4.5:1 contrast for normal text.
- Minimum interactive target: 44×44 CSS px.
- Focus indicators must be visible and keyboard navigation supported.
- Controls need labels; tooltips cannot be the only place important information exists.
- Use motion sparingly; respect reduced-motion preferences.
- Chart zones/lines require readable labels and must avoid overlap.
- Loading, offline, delayed, unavailable and synthetic states must use clear text, not icon-only signs.

## Components to standardize

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

Build only components needed for the phase currently under development.
