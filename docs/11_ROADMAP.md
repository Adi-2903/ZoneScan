# 11 — Roadmap and Release Gates

The roadmap is ordered by risk reduction, not by which feature is most visually attractive. Dates are intentionally omitted until the data provider, team capacity and legal review are known.

## Gate 0 — Documentation and decision baseline

Deliverables:
- Product brief, feature priorities, architecture, algorithm proposal, API/data model, compliance checklist and agent instructions committed.
- Owner assigned for provider selection, algorithm, frontend/backend, legal review and launch approval.

Exit when: high-risk questions are assigned and the team agrees on the prototype scope.

## Gate 1 — Feasibility: data and legal

Tasks:
- Obtain written quotes and terms from at least 2–3 credible provider options.
- Confirm fields: live/history OHLCV, futures OI, instruments, indices, sectors and permitted storage.
- Confirm whether commercial display of live and derived data is allowed, with fees and user limits.
- Ask qualified Indian securities counsel for written review of product classification and proposed features.
- Check current privacy/consumer/tax/payment obligations before finalizing billing.

Exit criteria:
- Written data path and estimated operating cost approved.
- No blocking contract restriction left unresolved.
- Regulatory review has a documented plan and required changes are known.

**No public live-data release or paid marketing before this gate passes.** A synthetic-data prototype can continue in parallel.

## Gate 2 — Algorithm proof

Tasks:
- Implement swing/BOS/order-block and score functions using deterministic fixtures.
- Build the replay loop and run historical evaluation using permitted data.
- Check look-ahead bias, survivorship bias, contract rollovers, missing data and sensitivity to parameters.
- Compare against simple baselines; publish internally the full result, positive or negative.

Exit criteria:
- Core rules are deterministic and covered by tests.
- Backtest methodology is reviewed; tuning and final test periods are separated.
- No unsupported claim of performance is required for product positioning. If scores do not add useful information, revise the product rather than hide the result.

## Phase 1 — Core internal MVP

Scope:
- Provider-neutral adapter and fixture provider.
- Candle builder and quality flags.
- Bullish/bearish board, status chip, settling/delayed states.
- Strength score, zone detection and stock chart.
- Basic Market X-Ray, sector context and board snapshots.
- Google sign-in and server-side entitlements.
- Internal admin/diagnostic view sufficient for development.

Exit criteria:
- Acceptance criteria from `01_PRODUCT_REQUIREMENTS.md` pass.
- Synthetic mode is always clearly labelled.
- Replay and live path use same algorithm functions.
- Feed failures cannot display as live data.

## Phase 2 — Closed beta / launch readiness

Scope:
- Approved licensed provider connector.
- Production hardening, error monitoring, backup/restore and status page.
- Legal-approved terms/disclosures/privacy/refund materials.
- Payment integration tested; production billing remains feature-gated until every release gate passes.
- Security, load, access-control and paper-observation tests.
- User onboarding and support process.

Exit criteria:
- Gate 1 and Gate 2 signed off.
- Legal sign-off implemented, not just received.
- Approved commercial data rights cover all displayed and derived outputs.
- At least four weeks of proposed paper-observation completed or a documented, counsel/owner-approved alternative.
- Incident/rollback owner is available for market hours.

## Phase 3 — P1 member tools

Add watchlist, alerts, journal, learning library, full sector flow, filters, PWA and admin content/billing features. Prioritize using closed-beta feedback and operational evidence. Re-check legal/data terms if new delivery channels (e.g., Telegram/WhatsApp/email) expose derived or live market information.

## Phase 4 — P2 trust and retention

Consider historical replay, public backtest page, community, extra languages and additional markets only after evidence that the core terminal is useful, licensed and reliable. Community introduces moderation and regulatory risk; it is not required for the first release.

## First 10 working sessions (suggested, not a schedule commitment)

1. Confirm project owner, name-as-codename and unresolved decisions.
2. Draft provider questionnaire and request quotes.
3. Request legal scoping call and share the actual user flows/screens/score concept.
4. Create 20-symbol synthetic instrument fixture and deterministic candle fixtures.
5. Implement confirmed swing points and BOS tests.
6. Implement order-block detection and zone-state tests.
7. Implement score normalization and boundary tests.
8. Build a plain stock detail chart using fixture data.
9. Build board UI with explicit synthetic-data banner and market states.
10. Wire replay tests and compare outputs; decide whether to proceed based on data/legal feasibility and initial algorithm quality.
