# 02 — UX Flows and Screen Inventory

## Primary navigation

1. Home / Board
2. Stock Detail
3. Market X-Ray
4. Watchlist (P1)
5. Alerts (P1)
6. Journal (P1)
7. Learn (P1)
8. Account / Plan
9. Marketing and legal pages

Keep the primary board reachable in one tap from every app screen on mobile. Do not add a complicated navigation system before real user testing.

## Key user flows

### Visitor → signed-in user

1. Visitor lands on the marketing page and views an honest product demo.
2. Visitor reads what the scores do and do not mean, pricing if enabled, and relevant risk/data disclosures.
3. Visitor signs in with Google.
4. User sees a preview or the permitted board according to backend entitlements.
5. If checkout is enabled, user selects a plan and completes payment through the approved payment provider.
6. The server verifies the payment webhook and updates subscription state; browser callback alone never grants access.
7. User sees a short onboarding walkthrough: board → stock chart → score/zone interpretation.

### Daily trader workflow

1. Before open, show previous session's board and clearly label the snapshot as historical.
2. From 09:15 until the configured settling period ends, show a settling indicator and explain what data is still stabilizing.
3. Review Bullish and Bearish boards and the market/sector context.
4. Open a stock detail chart and inspect the zone, its state, support/resistance, liquidity and score breakdown.
5. Optionally add to the watchlist or set a permitted alert.
6. User makes any trading decision independently in a separate broker application; ZoneScan has no order-placement flow.
7. Optionally log a trade manually in the journal.
8. Review personal statistics after the session.

### Feed interruption

1. The backend detects delayed or missing feed data.
2. Board response carries a degraded data state and source timestamp.
3. UI displays a clear warning and stops presenting old data as current.
4. Ingestion attempts reconnection and historical gap backfill.
5. Once data completeness checks pass, the backend publishes a fresh board and the UI removes the warning.
6. Operational events are logged for incident review.

## Screen specifications

| Screen | Required content | Key actions |
|---|---|---|
| Landing | Original value proposition, demo, core features, methodology, pricing if approved, FAQ, disclosures | Sign in, learn how it works |
| Login | Google sign-in, terms/privacy links, error state | Authenticate |
| Board | Market status, timestamp, delay/settling banner, Bullish/Bearish tabs, ranked rows, top setup preview | Search, change side, open stock |
| Stock Detail | Candlestick chart, timeframe switch, zone overlays, levels strip, score breakdown, sector context, data timestamp | Change timeframe/layers, copy level, add watchlist |
| Market X-Ray | Dot map, bullish/bearish/choppy counts, sector leaders/laggards, index context | Select sector or stock (full click-through P1) |
| Watchlist (P1) | Saved instruments, latest score, zone distance, alert state | Add/remove stock, configure alert |
| Alerts (P1) | Alert rules, channels, quiet hours, recent delivery status | Create/pause/delete rule |
| Journal (P1) | Trade form, user trade history, snapshots, analytics, export | Add/edit/delete own trade, export CSV |
| Learn (P1) | Categorized short lessons and progress | Watch, resume, mark complete |
| Account | User profile, entitlement/plan, renewal date, invoices, devices/sessions, theme, logout | Manage account, sign out, request deletion |
| Admin | Feed health, instruments, users, entitlements, payments, alerts, parameters, content, audit | Role-protected operational actions |

## Required screen states

Every screen must account for relevant states from this list:

- Loading: skeletons or progress; never an unexplained blank surface.
- Empty: explain why there is no data and how to proceed.
- Error: clear message, retry only when safe, and request/correlation ID where appropriate.
- Market closed / holiday: show last session's timestamp and closed state.
- Settling: label the board until the opening window and data-readiness gates pass.
- Delayed: show age/delay, not a live indicator.
- Missing/invalid data: disclose the affected symbol/metric; exclude it when required inputs are missing.
- Synthetic demo: persistent label on every screen using mock data.
- Offline: retain last view only with a visible offline label and timestamp.
- Expired entitlement: show permitted preview and a path to renew; protect server endpoints.
- Payment pending/failed: do not unlock paid features until verified confirmation.

## Interaction guidelines

- Board rows should be dense but readable. Align numbers with tabular numerals.
- Use arrows and text labels along with red/green/amber colors; never communicate direction by color alone.
- Chart zone/level labels must not collide. On narrow screens, prefer a compact levels strip and expandable details.
- Provide an accessible table alternative to the X-Ray dot map.
- Do not animate every row on each one-minute update. Use brief, restrained indication of what changed.
- Avoid dark patterns: no fake countdown timers, fake crossed-out prices, obstructive cancellation, or preselected paid add-ons.
