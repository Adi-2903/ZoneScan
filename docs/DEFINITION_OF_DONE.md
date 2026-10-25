# Definition of Done

A feature or task is not done merely because the happy path renders.

## Product and implementation

- [ ] Scope matches `AGENTS.md`, `01_PRODUCT_REQUIREMENTS.md` and the current roadmap phase.
- [ ] Relevant decision/open-question items were checked; any new assumption is recorded.
- [ ] UI clearly distinguishes live, delayed, closed, unavailable, offline and synthetic states where applicable.
- [ ] Backend authorization is enforced for protected data and actions.
- [ ] No unsupported trading, legal, data-source or performance claim was added.

## Correctness

- [ ] Inputs and edge cases are validated.
- [ ] Missing/stale data is represented explicitly rather than silently replaced.
- [ ] Timezone/session behavior is tested for relevant cases.
- [ ] Algorithm changes use versioned parameters and do not introduce look-ahead/repainting.
- [ ] Payment changes are idempotent, webhook-verified and tested in provider test mode.

## Quality

- [ ] Unit/integration/E2E tests appropriate to the change were added or updated.
- [ ] Tests, lint, type checking and build were run; any skipped check is disclosed.
- [ ] Accessibility and responsive behavior were reviewed for UI changes.
- [ ] Security/privacy implications were reviewed for auth, payments, storage, logging or external integrations.

## Documentation and delivery

- [ ] API/schema/algorithm/product/ops docs were updated if behavior changed.
- [ ] No secrets, real user data or prohibited market data are committed.
- [ ] The final summary names files changed, tests run, known gaps and release gates.
- [ ] Claims of `implemented` or `verified` are supported by execution/test evidence.
