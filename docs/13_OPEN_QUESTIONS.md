# 13 — Open Questions and Blockers

Do not silently decide the items marked **BLOCKER**. The owner should assign a person and record the resolution here or in a linked ADR.

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
| Q-009 | What is the exact candle-overlap measure for the choppy filter? | “Overlap >70%” needs a reproducible formula. | Algorithm owner: define in code/docs before enabling filter. | Open |
| Q-010 | What is the final score display threshold and neutral-direction policy? | Impacts board membership and user interpretation. | Algorithm owner; start with deterministic fixture tests and compare results. | Open |
| Q-011 | Should there be a free preview, delayed board, monthly plan, annual plan, trial, or paid-only launch? | Affects business model, data licensing and entitlements. | Product owner after data cost is known. | Open |
| Q-012 | What are final prices, taxes, refund/cancellation policy and renewal policy? | Commercial and legal decision; never copy competitor pricing. | Product owner + CA/counsel + payment provider. | Open |
| Q-013 | Which login methods at launch: Google only, or also email/phone OTP? | OTP adds provider cost and abuse controls. | Product owner. Default: Google first. | Open; default documented |
| Q-014 | One or two simultaneous devices per account? | Entitlement/privacy/support trade-off. | Product owner. Default: allow phone + laptop unless abuse evidence says otherwise. | Open; default documented |
| Q-015 | Which alert channels are launched first, and are derived data messages permitted on those channels by the provider contract? | Alert messages can be redistribution of market data. | Product owner + data provider + counsel. | Open |
| Q-016 | What public backtest statistics, if any, may be shown and under what review process? | Methodology and data rights must support them. | Algorithm owner + counsel. | Open |
| Q-017 | Is community needed at all? | Adds moderation, privacy and regulatory risk. | Product owner after closed beta. Default: no in-app community for MVP. | Open; default documented |
| Q-018 | What team capacity, launch window, cloud region and monthly operating budget are available? | Determines deployment and schedule; costs depend strongly on data licensing. | Product owner. | Open |
| Q-019 | Should sector direction classification use traded-value weighting, member-count participation, or both, and what timestamp/coverage makes a sector state available? | The provisional Strength Score specifies a traded-value-weighted aggregate but describes its initial 60% participation threshold by member count; the scoring function currently consumes an upstream categorical state. | Algorithm owner: define and version the sector aggregation before integrating board scoring. | Open |

## Work that can proceed while blockers are open

- Documentation, UI prototype, algorithm fixtures and backtest framework using synthetic or expressly permitted historical fixtures.
- Provider-neutral adapters and mock provider.
- Internal chart rendering and interface accessibility tests.
- Legal/provider interview preparation.

## Work that must not be enabled before blockers resolve

- Public display of real live/derived data without a matching licence.
- Paid commercial launch.
- Public claims about hits, accuracy, profitability or backtested edge without a reviewed methodology and supporting data.
- Personalized calls, trade execution, broker-account integration or other scope expansion.
