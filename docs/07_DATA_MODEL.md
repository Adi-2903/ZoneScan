# 07 — Data Model

This is a starting relational model, not a finalized migration. Normalize names, constraints and indexes during implementation; review all data retention against provider licences and legal requirements before storing market data.

## Market reference tables

### `instruments`

Suggested fields: `id`, `symbol`, `display_name`, `exchange`, `segment`, `sector_id`, `lot_size`, `cash_provider_token`, `futures_provider_token`, `active`, `valid_from`, `valid_to`, `updated_at`.

The eligible list must be refreshed from an authorized source. Do not hardcode the F&O universe as a permanent static list.

### `sectors`

Suggested fields: `id`, `name`, `index_symbol`, `mapping_source`, `updated_at`.

### `trading_calendar`

Suggested fields: `date`, `is_open`, `open_time`, `close_time`, `session_type`, `source`, `note`.

## Time-series / market tables

### `candles_1m`

Suggested fields: `instrument_id`, `contract_id` (nullable for cash-equity candles), `ts`, `open`, `high`, `low`, `close`, `volume`, `oi`, `source_timestamp`, `received_at`, `filled_flag`, `quality_flags`, `provider_id`.

Unique key should prevent duplicate candles for the same instrument/contract/timestamp. If a time-series extension is chosen, confirm its retention, backup and licensing/operational implications first.

### `daily_candles`

Suggested fields: `instrument_id`, `date`, `open`, `high`, `low`, `close`, `volume`, `oi`, `source`, `reconciled_at`.

### `indicators`

Suggested fields: `instrument_id`, `ts`, `atr14_5m`, `adx14_5m`, `vwap`, `ema20_5m`, `rvol`, `daily_sigma20`, `oi_change_daily_pct`, `oi_change_30m_pct`, `quality_flags`, `parameter_version`.

### `zones`

Suggested fields: `id`, `instrument_id`, `side`, `low`, `high`, `timeframe`, `formed_at`, `recognized_at`, `state`, `has_fvg`, `last_touched_at`, `mitigated_at`, `expired_at`, `active`, `algorithm_version`, `parameter_version`. `recognized_at` is when replay/live processing had enough information to emit the zone; it may not precede the displacement close. `active=false` retains history for a zone mitigated, expired, or deactivated by timeframe overlap/active-zone cap. The current in-memory prototype uses a deterministic hash ID and does not persist zones.

### Replay inputs (in-memory prototype)

Each `ReplayBar` wraps a completed/incomplete `Candle`, optional ATR/RVOL, a `5m`/`15m` timeframe, an optional exchange session date and mapped symbol, and optional point-in-time score inputs (`day_return`, `daily_sigma20`, daily and 30-minute futures OI changes, VWAP/EMA side booleans, and categorical sector direction). Missing values remain `None`; they are not imputed. Replay derives structure only from swings confirmed by that candle's timestamp, derives direction from the documented rule, and uses the candle close as current price. `ReplayScore` retains the shared `ScoreResult`, directional classification, Choppy result, Choppy-filtered score, session-local smoothed score, RVOL, completed-bar traded-value tie-break input, and a separate `EarlyMoveResult`. Early-Move is calculated on 5m records from exact 15m-prior closes and the latest session-anchored 15m volume window; it requires 20 prior session calendars and same-slot 5m volume candles. Incomplete candles have an explicit unavailable result. Replay returns transient `BoardSnapshot` values for completed 5m timestamps; each ranked `BoardRow` retains its full `ReplayScore`. These are in-memory provider-neutral models, not persisted history or a provider-normalized store.

The indicator layer adds `TradingSession` for explicit session bounds, `CandleAggregation` plus `MissingCandleInterval` for completed 5m/15m candles and source gaps, and `FuturesContractMapping` for mapping an underlying to a contract-specific OI series. `IndicatorFrame` contains an optional aggregate candle and typed `IndicatorValue(available, value, reason)` outputs. `to_replay_bars` maps only available values, including 30-minute OI change, to existing replay inputs; cash price candles remain distinct from futures OI observations. These models remain in-memory and provider-neutral.

### Historical evaluation input contract (prototype)

`HistoricalDataset` accepts point-in-time `ReplayBar` records, an explicit `(instrument_id, symbol)` mapping, session bounds and expected instrument IDs per session, a supported 5m/15m interval, and `DatasetProvenance`. Provenance must identify a dataset, source/reference, and written usage permission reference, with an explicit internal-evaluation permission attestation. This attestation is supplied by the data owner; the code cannot verify a contract. Timestamps must carry the India `+05:30` offset and session-aligned close timestamps in `(session open, session close]`. No missing candle, volume, indicator, or OI is imputed. Required volume is carried by `Candle.volume`; OI absence remains a warning and produces the shared score function's unavailable OI component. Incomplete point-in-time universe coverage is reported. Synthetic datasets can exercise replay but all forward-performance outcomes are explicitly unavailable. This is an in-memory evaluation contract, not persistence or provider integration.

### `liquidity_levels`

Suggested fields: `id`, `instrument_id`, `side`, `price`, `kind`, `formed_at`, `confirmed_at`, `swept_at`, `expired_at`, `source_zone_id` (optional), `algorithm_version`.

Kinds include: `swing_high`, `swing_low`, `equal_high`, `equal_low`, `pdh`, `pdl`, `pwh`, `pwl`, `opening_range_high`, `opening_range_low`.

The in-memory `LiquidityLevel` adds timeframe, lifecycle state (`unswept`, `swept`, `invalidated`, `expired`, or `unavailable`), pending excursion details, source swing/candle timestamps, and unavailable reason/time. Replay exposes retained levels and `ReplayEvent` records with `liquidity_level_id`; they are separate from score components. Prior-day/week and opening-range levels require explicit `TradingSession` calendar entries and complete expected bars. Day/opening levels expire at the next session; week levels expire at the next ISO week.

### `scores`

Suggested fields: `instrument_id`, `ts`, `direction`, `strength_raw`, `strength_smoothed`, `early_move_score`, `component_m`, `component_v`, `component_o`, `component_t`, `component_s`, `component_z`, `choppy_flag`, `classification_reason`, `quality_flags`, `algorithm_version`, `parameter_version`.

The in-memory `ScoreInputs` contract takes fractional `day_return`, `daily_sigma20`, `rvol`, fractional `oi_change_daily_pct`, explicit direction/VWAP/EMA/structure/sector classifications, and current price/ATR/nearest `Zone` for proximity. `EarlyMoveResult` carries an independent total score, OI30/Mom15/Burst15/RunPenalty component values, unavailable reasons, and algorithm/parameter versions. Missing inputs remain `None`. `ComponentResult` distinguishes unavailable values (`value=None` plus reason) from valid zero. `ScoreResult` carries computed components, unavailable-component reasons, OI context labels, and algorithm/parameter versions. Sequential replay attaches `ScoreResult` to timestamped `ReplayScore` records; persistent score storage is not implemented.

### `board_snapshots`

The in-memory `BoardSnapshot` contains `timestamp`, `session_date`, bullish and bearish row tuples, and algorithm/parameter versions. `BoardRow` contains rank, instrument ID, mapped symbol, side, and the complete `ReplayScore` (raw components and availability reasons, filtered score, smoothed score, Choppy state, and versions). Each completed 5m timestamp produces one snapshot; boards contain at most 20 eligible records per side. Hysteresis membership is per side and session. Persistence, zone/level references in board rows, and storage under provider licensing constraints remain unimplemented.

## Identity and business tables

- `users`: `id`, `email`, `name`, `google_subject`, optional `phone`, `status`, `created_at`, `last_login_at`, `deleted_at`.
- `plans`: `id`, `code`, `name`, `price_minor_units`, `currency`, `duration_days`, `active`.
- `subscriptions`: `id`, `user_id`, `plan_id`, `status`, `starts_at`, `ends_at`, `provider_subscription_id`, `auto_renew`, timestamps.
- `payments`: `id`, `user_id`, `subscription_id`, `amount_minor_units`, `tax_minor_units`, `currency`, `provider_payment_id`, `provider_event_id`, `status`, `invoice_number`, `paid_at`.
- `coupons` (optional): `id`, `code`, `discount_type`, `discount_value`, `max_uses`, `valid_until`, `active`.
- `devices`/`sessions`: user ID, server-side session/device identifier hash, last seen, revoked/expired timestamps. Avoid invasive fingerprinting; finalize device policy with privacy review.
- `watchlist_items`: `user_id`, `instrument_id`, `created_at`.
- `alerts`: `id`, `user_id`, `instrument_id`, `kind`, `params_json`, `channel`, `active`, `last_fired_at`.
- `notification_log`: alert ID, created/sent timestamps, channel, delivery status, provider response ID, safe error code.
- `journal_trades`: `id`, `user_id`, `instrument_id`, `side`, `entry_price`, `stop_price` (user-entered only), `target_price` (user-entered only), `quantity`, `entry_at`, `exit_price`, `exit_at`, `notes`, `tags`, `snapshot_id`, `screenshot_object_key`, created/updated timestamps. These are user records, not application recommendations.
- `lessons`: `id`, `title`, `description`, `video_asset_id`, `sort_order`, `duration_seconds`, `published_at`.
- `lesson_progress`: `user_id`, `lesson_id`, `percent`, `completed_at`, updated timestamp.
- `posts`: blog/update content with `title`, `slug`, `body`, `published_at`, `author_id`, `status`.
- `testimonials`: only real, consented records with provenance and permission fields.
- `support_tickets`: user, subject, status, created/updated timestamps; may be delegated to a helpdesk.
- `audit_log`: actor, action, entity, entity ID, timestamp, request ID, metadata with sensitive fields redacted.

## Relationships and integrity

- A board snapshot references the exact instrument and, when applicable, the zone that was active at snapshot time. Store the relevant numeric levels in the snapshot too; do not depend on mutable zone state to reconstruct past boards.
- Journal snapshots attach to a specific board snapshot. Users must not see another user's journal records.
- Payment records and subscriptions use provider IDs with idempotency constraints.
- Historical market records include provider source and timestamps. Delete/retain them only within the applicable data licence.
- Every change to algorithm parameters and instrument mappings is versioned/audited.

## Retention starting points (must be reviewed)

- One-minute candles and computed indicators: proposed two-year working retention, compress/archive older data only if allowed by provider agreement and needed for backtests.
- Board snapshots: retain as long as licence, privacy and product commitments permit; they support reproducibility but may contain derived data controlled by the provider contract.
- Notification delivery logs: proposed 90 days.
- Admin audit logs: proposed three years, subject to legal/security policy.
- Journal data belongs to the user; support export and deletion requests. Explain any legal retention exception before launch.

Do not implement a retention duration as a hard fact until the provider agreement and privacy review are complete.
