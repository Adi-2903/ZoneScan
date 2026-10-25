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

Suggested fields: `id`, `instrument_id`, `side`, `low`, `high`, `timeframe`, `formed_at`, `confirmed_at`, `state`, `has_fvg`, `last_touched_at`, `mitigated_at`, `expired_at`, `algorithm_version`, `parameter_version`.

### `liquidity_levels`

Suggested fields: `id`, `instrument_id`, `side`, `price`, `kind`, `formed_at`, `confirmed_at`, `swept_at`, `expired_at`, `source_zone_id` (optional), `algorithm_version`.

Kinds include: `swing_high`, `swing_low`, `equal_high`, `equal_low`, `pdh`, `pdl`, `pwh`, `pwl`, `opening_range_high`, `opening_range_low`.

### `scores`

Suggested fields: `instrument_id`, `ts`, `direction`, `strength_raw`, `strength_smoothed`, `early_move_score`, `component_m`, `component_v`, `component_o`, `component_t`, `component_s`, `component_z`, `choppy_flag`, `classification_reason`, `quality_flags`, `algorithm_version`, `parameter_version`.

### `board_snapshots`

Suggested fields: `id`, `session_date`, `ts`, `side`, `rank`, `instrument_id`, `strength`, `early_move_score`, `zone_id`, `levels_json`, `data_status`, `algorithm_version`, `parameter_version`.

Unique key should prevent two authoritative entries for the same session timestamp, side and instrument/rank combination according to the chosen snapshot design.

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
