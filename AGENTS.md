# Agent Instructions — ZoneScan

These instructions apply to every coding agent and contributor. Follow them before changing code or documentation.

## 1. Mandatory context load

At the start of a task, read:

1. `README.md`
2. `docs/00_PROJECT_BRIEF.md`
3. `docs/12_DECISIONS.md`
4. `docs/13_OPEN_QUESTIONS.md`
5. The specific documents relevant to the assigned task

Do not dump every document into context for a small task. Use this index to load only the relevant detail. If instructions conflict, `AGENTS.md` controls execution policy; `12_DECISIONS.md` controls accepted product decisions; feature-specific docs control their feature details. Flag a real conflict rather than silently choosing whichever is convenient.

## 2. Product guardrails

- Build **ZoneScan**, an original analytics product. The name is a working codename, not a cleared trademark or approved public brand.
- Do not copy OrderBlock's brand, logos, copy, screenshots, testimonials, proprietary implementation, or claim of performance. It is a category/reference source only.
- The product is analytics-only. Do not add order placement, automated execution, broker-account trading access, personalized recommendations, buy/sell calls, targets, or stop-loss instructions unless the owner explicitly changes scope after legal review.
- A score or zone is a heuristic derived from market data; it is not proof of institutional orders, certainty, or a profitable trade.
- Never invent market data, backtest outcomes, testimonials, licenses, regulatory approvals, pricing, or provider capabilities.
- Sample/demo data must be clearly identified in the UI and API as synthetic. Never make sample values look like real-time market data.
- Use `Asia/Kolkata` for exchange-session logic and ISO 8601 timestamps with `+05:30` in API examples.

## 3. Data licensing and legal release gates

- Treat live market-data licensing and Indian securities-law classification as **release blockers**, not TODOs to bypass.
- A retail broker API may be used only for a purpose expressly permitted by its current contract. Do not use it to power a public product or redistribute live/derived data unless written terms expressly allow that use.
- Use a `MarketDataProvider` interface and deterministic fixtures until the correct provider/licence has been approved.
- Never put provider API keys, OAuth secrets, webhook secrets, OTP credentials, or private user data in source control or browser code.
- Do not enable production billing or invite paying users before the gates in `docs/11_ROADMAP.md` have passed.

## 4. Architecture invariants

- The backend is the source of truth for scores, classifications, zones, membership entitlements, and market status.
- One logical scoring worker publishes a single authoritative board per minute. The browser must not independently recalculate ranked scores.
- Cache the current board; push board changes through Server-Sent Events (SSE) unless a documented decision changes this.
- Live scoring and historical replay/backtesting must call the **same algorithm implementation**.
- All algorithm parameters must be versioned. Store the version with board snapshots.
- Never use an unfinished candle to confirm a swing, break of structure, or order block. Confirm swings only after all required right-side candles close; prevent look-ahead and repainting.
- Missing required inputs must be surfaced as missing/insufficient data. Do not silently replace them with zero or an invented value.
- API routes are versioned under `/api/v1` from the start.
- The server enforces subscription access. Hiding data only in the frontend is not authorization.

## 5. Scope discipline

- Implement only the assigned task and features marked in-scope in `docs/01_PRODUCT_REQUIREMENTS.md` and `docs/11_ROADMAP.md`.
- Priority definitions: **P0** = core proof/MVP; **P1** = first expansion; **P2** = later. A priority does not override a legal/data gate.
- Prefer a modular monolith and small, testable modules over premature microservices.
- Do not introduce new infrastructure, services, state libraries, or dependencies without a clear need and a short explanation in the PR/task summary.
- Do not add AI/ML merely to make the product sound advanced. The first engine is deterministic and explainable.

## 6. Required workflow for every task

1. Identify the relevant requirement and acceptance criteria.
2. Check the relevant decision and open-question records.
3. State assumptions briefly if the task depends on an unresolved point; follow a documented default where one exists.
4. Implement the smallest coherent change.
5. Add or update tests, including failure/empty/stale states where applicable.
6. Run the available tests, lint, type checks, and build. Report anything not run and why.
7. Update the relevant docs whenever behavior, endpoint shape, data schema, threshold, release status, or decision changes.
8. Do not claim that a feature works unless verified. Label work as `planned`, `prototype`, `implemented`, or `verified` in task summaries when useful.

## 7. Quality and safety standards

- Favor explicit types, small pure algorithm functions, stable identifiers, parameterized database operations, and idempotent background jobs.
- Keep money values in integer minor units or a documented decimal type; never use binary floating point for payment amounts.
- Verify payment-provider webhook signatures on the server and make webhook processing idempotent.
- Use secure, HTTP-only cookies for web sessions; apply CSRF protection to state-changing cookie-authenticated endpoints.
- Use accessible labels and icons as well as color. Bullish/bearish/choppy states must remain understandable without color perception.
- Handle loading, market closed, settling, delayed feed, unavailable data, subscription expiry, offline, and API error states.
- Never deploy during NSE market hours except for a documented emergency procedure.

## 8. When a spec is incomplete

Do not invent a proprietary formula or provider contract. Prefer one of these actions:

- Use a clearly documented provisional default from the relevant spec and version it.
- Build a provider-neutral interface or a fixture-driven prototype.
- Add a concrete item to `docs/13_OPEN_QUESTIONS.md` with its impact and required owner.
- Ask the project owner only when progress would otherwise create irreversible or high-risk behavior.

## 9. Final response for an implementation task

Report: what changed, relevant files, tests run and results, known gaps, and any release gates still open. Do not report a green build unless the build was actually run and passed.
