# 10 — Deployment and Market-Day Operations

## Environments and secrets

- Local development uses synthetic fixtures by default.
- Development and staging must not be publicly marketed as live if data rights do not allow it.
- Keep production secrets in a managed secret store or platform secret manager. `.env` files with real secrets must never be committed.
- Keep payment test and production keys separate.
- Production deploys require migrations, tests, rollback notes and an operational owner.

## Market-day checklist (initial runbook)

### Before session

- 08:30 IST: universe refresh completed; expected instrument count and changes reviewed.
- 09:00 IST: provider authenticated; first ticks arriving; clock/timezone verified; source timestamps look sane.
- Check current-session calendar; special sessions and shortened sessions override normal defaults.
- Verify last historical candle, OI contract mapping and data readiness.

### At open / settling

- From 09:15 IST: board state changes to open/settling according to calendar.
- Keep the settling badge visible until both the configured opening window ends and data checks pass.
- Confirm finalized-minute cycle, scoring duration and board timestamp are within target.

### During session

Monitor:

- Feed lag and last source timestamp.
- Tick/candle counts per symbol and missing-minute ratio.
- Number of eligible, ranked and excluded instruments, plus reason counts.
- Duration of candle build, indicator/structure computation, scoring, ranking, persistence and SSE publish.
- Worker health, standby status, Redis availability/hit rate, API error rate/latency and SSE connection count.
- Payment/auth errors separately from market-data issues.

If market data is delayed, show an amber data-quality status, stop claiming the board is live and suppress features dependent on unavailable inputs. If scoring output is inconsistent, freeze the last verified snapshot only with a visible stale/frozen status; never silently serve it as current.

### After close

- Close/stop subscriptions according to provider/session requirements.
- Reconcile provisional daily candles with authorized final data.
- Store final board snapshot and data-quality report.
- Review feed errors, excluded symbols, worker incidents and support messages.
- Avoid routine deployment during market hours; schedule release windows after market close.

## Reliability targets (provisional)

| Measure | Target |
|---|---|
| Board publish after finalized minute | p95 under 5 seconds |
| Feed reconnect after temporary drop | under 10 seconds where provider permits, followed by gap backfill |
| Recovery after worker failure | under 2 minutes with standby/fail-safe behavior |
| Board availability during defined session | 99.9% target; measure over a defined reporting window before publishing any claim |

These are engineering goals, not proven service-level commitments. Do not publish an SLA until operations can measure and support it.

## Incident priorities

- **P0:** feed data wrong/stale but shown as live; corrupted scores; unauthorized data exposure; payment entitlement error; leaked credential.
- **P1:** broad API outage; board does not update; missing symbols/sector data; SSE recovery failure.
- **P2:** isolated chart overlay issue; content/lesson problem; non-critical admin inconvenience.

For a P0 market-data incident: stop new board publication if correctness is uncertain, mark status unavailable/delayed, preserve diagnostics, notify the on-call owner, and do not backfill a misleading board until data and calculations pass validation.

## Monitoring and alerts

Required metrics:

- Feed connected state, lag, ticks/sec, missing minutes per symbol.
- Candle/algorithm cycle duration by stage.
- Number of symbols blocked by quality gates.
- API latency/error rate, SSE sessions and disconnects.
- Redis errors/hit rate, database latency/connections.
- Payment webhook failure/reconciliation mismatch.
- Notification delivery failure.
- CPU/memory/disk, backups, uptime and certificate expiry.

A tool such as Sentry for errors and Prometheus/Grafana or a managed equivalent for metrics may be selected during implementation. Do not add monitoring vendors until data retention, access and costs are reviewed.

## Release and rollback

- Never deploy routine changes during supported market hours.
- Algorithm threshold changes require a new parameter version, replay comparison and written rationale.
- Use staged rollout or a canary where practical.
- Keep prior working build/config available for rollback.
- If rollback restores older algorithm code, preserve the parameter and algorithm versions of historic snapshots.
