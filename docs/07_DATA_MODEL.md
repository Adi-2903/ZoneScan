# 07 — Data Model

This is a starting relational model, not a finalized migration. Normalize names, constraints and indexes during implementation; review all data retention against provider licences and legal requirements before storing market data or financial data.

---

## Part A — Market Intelligence data model (existing)

### Market reference tables

#### `instruments`

Suggested fields: `id`, `symbol`, `display_name`, `exchange`, `segment`, `sector_id`, `lot_size`, `cash_provider_token`, `futures_provider_token`, `active`, `valid_from`, `valid_to`, `updated_at`.

The eligible list must be refreshed from an authorized source. Do not hardcode the F&O universe as a permanent static list.

#### `sectors`

Suggested fields: `id`, `name`, `index_symbol`, `mapping_source`, `updated_at`.

#### `trading_calendar`

Suggested fields: `date`, `is_open`, `open_time`, `close_time`, `session_type`, `source`, `note`.

### Time-series / market tables

#### `candles_1m`

Suggested fields: `instrument_id`, `contract_id` (nullable for cash-equity candles), `ts`, `open`, `high`, `low`, `close`, `volume`, `oi`, `source_timestamp`, `received_at`, `filled_flag`, `quality_flags`, `provider_id`.

Unique key should prevent duplicate candles for the same instrument/contract/timestamp.

#### `daily_candles`

Suggested fields: `instrument_id`, `date`, `open`, `high`, `low`, `close`, `volume`, `oi`, `source`, `reconciled_at`.

#### `indicators`

Suggested fields: `instrument_id`, `ts`, `atr14_5m`, `adx14_5m`, `vwap`, `ema20_5m`, `rvol`, `daily_sigma20`, `oi_change_daily_pct`, `oi_change_30m_pct`, `quality_flags`, `parameter_version`.

#### `zones`

Suggested fields: `id`, `instrument_id`, `side`, `low`, `high`, `timeframe`, `formed_at`, `recognized_at`, `state`, `has_fvg`, `last_touched_at`, `mitigated_at`, `expired_at`, `active`, `algorithm_version`, `parameter_version`. `recognized_at` is when replay/live processing had enough information to emit the zone; it may not precede the displacement close. `active=false` retains history for a zone mitigated, expired, or deactivated by timeframe overlap/active-zone cap. The current in-memory prototype uses a deterministic hash ID and does not persist zones.

#### Replay inputs (in-memory prototype)

Each `ReplayBar` wraps a completed/incomplete `Candle`, optional ATR/RVOL, a `5m`/`15m` timeframe, an optional exchange session date and mapped symbol, and optional point-in-time score inputs (`day_return`, `daily_sigma20`, daily and 30-minute futures OI changes, VWAP/EMA side booleans, and categorical sector direction). Missing values remain `None`; they are not imputed. Replay derives structure only from swings confirmed by that candle's timestamp, derives direction from the documented rule, and uses the candle close as current price. `ReplayScore` retains the shared `ScoreResult`, directional classification, Choppy result, Choppy-filtered score, session-local smoothed score, RVOL, completed-bar traded-value tie-break input, and a separate `EarlyMoveResult`. Early-Move is calculated on 5m records from exact 15m-prior closes and the latest session-anchored 15m volume window; it requires 20 prior session calendars and same-slot 5m volume candles. Incomplete candles have an explicit unavailable result. Replay returns transient `BoardSnapshot` values for completed 5m timestamps; each ranked `BoardRow` retains its full `ReplayScore`. These are in-memory provider-neutral models, not persisted history or a provider-normalized store.

The indicator layer adds `TradingSession` for explicit session bounds, `CandleAggregation` plus `MissingCandleInterval` for completed 5m/15m candles and source gaps, and `FuturesContractMapping` for mapping an underlying to a contract-specific OI series. `IndicatorFrame` contains an optional aggregate candle and typed `IndicatorValue(available, value, reason)` outputs. `to_replay_bars` maps only available values, including 30-minute OI change, to existing replay inputs; cash price candles remain distinct from futures OI observations. These models remain in-memory and provider-neutral.

#### Historical evaluation input contract (prototype)

`HistoricalDataset` accepts point-in-time `ReplayBar` records, an explicit `(instrument_id, symbol)` mapping, session bounds and expected instrument IDs per session, a supported 5m/15m interval, and `DatasetProvenance`. Provenance must identify a dataset, source/reference, and written usage permission reference, with an explicit internal-evaluation permission attestation. This attestation is supplied by the data owner; the code cannot verify a contract. Timestamps must carry the India `+05:30` offset and session-aligned close timestamps in `(session open, session close]`. No missing candle, volume, indicator, or OI is imputed. Required volume is carried by `Candle.volume`; OI absence remains a warning and produces the shared score function's unavailable OI component. Incomplete point-in-time universe coverage is reported. Synthetic datasets can exercise replay but all forward-performance outcomes are explicitly unavailable. This is an in-memory evaluation contract, not persistence or provider integration.

#### `liquidity_levels`

Suggested fields: `id`, `instrument_id`, `side`, `price`, `kind`, `formed_at`, `confirmed_at`, `swept_at`, `expired_at`, `source_zone_id` (optional), `algorithm_version`.

Kinds include: `swing_high`, `swing_low`, `equal_high`, `equal_low`, `pdh`, `pdl`, `pwh`, `pwl`, `opening_range_high`, `opening_range_low`.

The in-memory `LiquidityLevel` adds timeframe, lifecycle state (`unswept`, `swept`, `invalidated`, `expired`, or `unavailable`), pending excursion details, source swing/candle timestamps, and unavailable reason/time. Replay exposes retained levels and `ReplayEvent` records with `liquidity_level_id`; they are separate from score components.

#### `scores`

Suggested fields: `instrument_id`, `ts`, `direction`, `strength_raw`, `strength_smoothed`, `early_move_score`, `component_m`, `component_v`, `component_o`, `component_t`, `component_s`, `component_z`, `choppy_flag`, `classification_reason`, `quality_flags`, `algorithm_version`, `parameter_version`.

#### `board_snapshots`

The in-memory `BoardSnapshot` contains `timestamp`, `session_date`, bullish and bearish row tuples, and algorithm/parameter versions. `BoardRow` contains rank, instrument ID, mapped symbol, side, and the complete `ReplayScore`. Each completed 5m timestamp produces one snapshot; boards contain at most 20 eligible records per side. Persistence and zone/level references in board rows remain unimplemented.

### Identity and business tables

- `users`: `id`, `email`, `name`, `google_subject`, optional `phone`, `status`, `created_at`, `last_login_at`, `deleted_at`.
- `plans`: `id`, `code`, `name`, `price_minor_units`, `currency`, `duration_days`, `active`.
- `subscriptions`: `id`, `user_id`, `plan_id`, `status`, `starts_at`, `ends_at`, `provider_subscription_id`, `auto_renew`, timestamps.
- `payments`: `id`, `user_id`, `subscription_id`, `amount_minor_units`, `tax_minor_units`, `currency`, `provider_payment_id`, `provider_event_id`, `status`, `invoice_number`, `paid_at`.
- `coupons` (optional): `id`, `code`, `discount_type`, `discount_value`, `max_uses`, `valid_until`, `active`.
- `devices`/`sessions`: user ID, server-side session/device identifier hash, last seen, revoked/expired timestamps.
- `watchlist_items`: `user_id`, `instrument_id`, `created_at`.
- `alerts`: `id`, `user_id`, `instrument_id`, `kind`, `params_json`, `channel`, `active`, `last_fired_at`.
- `notification_log`: alert ID, created/sent timestamps, channel, delivery status, provider response ID, safe error code.
- `journal_trades`: `id`, `user_id`, `instrument_id`, `side`, `entry_price`, `stop_price` (user-entered only), `target_price` (user-entered only), `quantity`, `entry_at`, `exit_price`, `exit_at`, `notes`, `tags`, `snapshot_id`, `screenshot_object_key`, created/updated timestamps.
- `lessons`: `id`, `title`, `description`, `video_asset_id`, `sort_order`, `duration_seconds`, `published_at`.
- `lesson_progress`: `user_id`, `lesson_id`, `percent`, `completed_at`, updated timestamp.
- `posts`: blog/update content with `title`, `slug`, `body`, `published_at`, `author_id`, `status`.
- `testimonials`: only real, consented records with provenance and permission fields.
- `support_tickets`: user, subject, status, created/updated timestamps.
- `audit_log`: actor, action, entity, entity ID, timestamp, request ID, metadata with sensitive fields redacted.

---

## Part B — Financial Intelligence data model

Production broad scraping and bulk ingestion remain gated on Gate 3. In Milestone 1, the core **persistence foundation** (`financial_facts`, `companies`, and `company_identifiers`) is implemented with strict boundary validation and deterministic temporal mapping.

### Implemented persistence schemas (Milestone 1)

Implemented in `services/api/src/zonescan/financial_facts.py` and `services/api/src/zonescan/entity_resolution.py`.

#### `financial_facts`

Stores individual, fully traceable financial statement items and metrics with complete provenance metadata:

| Column | Type | Constraints | Description |
|---|---|---|---|
| `fact_id` | TEXT | PRIMARY KEY | Unique fact identifier (e.g. `fact-bf-rev-fy24`) |
| `company_id` | TEXT | NOT NULL, non-empty | Canonical company identifier / CIN |
| `metric` | TEXT | NOT NULL, non-empty | Standard metric name (e.g. `revenue_from_operations`) |
| `value` | REAL | NOT NULL, finite | Numerical value (e.g. `15682.07`) |
| `unit` | TEXT | NOT NULL, non-empty | Unit denomination (e.g. `INR_CRORES`, `₹ Cr`) |
| `financial_period` | TEXT | NOT NULL, non-empty | Reporting period (e.g. `FY2023-24`) |
| `statement_scope` | TEXT | NOT NULL, CHECK IN (`consolidated`, `standalone`) | Consolidation boundary |
| `source_document` | TEXT | NOT NULL, non-empty | Official document name (e.g. `Annual Report FY 2023-24`) |
| `source_url` | TEXT | Nullable | Direct URL to public filing PDF/portal |
| `page_note_table_reference`| TEXT | Nullable | Exact reference (e.g. `Consolidated P&L, Page 218, Note 23`) |
| `document_date` | TEXT | NOT NULL (ISO date `YYYY-MM-DD`) | Date of source document / filing approval |
| `retrieval_timestamp` | TEXT | NOT NULL (ISO 8601 with tz) | Exact timestamp when fact was ingested/extracted |
| `extraction_method` | TEXT | NOT NULL | Extraction technique (`manual_audited_filing_extract`, `xbrl`) |
| `evidence_status` | TEXT | NOT NULL, CHECK IN (`disclosed`, `verified`, `inferred`, `unconfirmed`, `unavailable`) | Fact provenance status |
| `is_synthetic` | INTEGER | NOT NULL DEFAULT 0, CHECK IN (0, 1) | Strict flag isolating demo prototypes from real disclosures |
| `verification_notes` | TEXT | Nullable | Audit details or calculation formula rationale |
| `created_at` | TEXT | NOT NULL | Record creation timestamp |

**Boundary Validation Rules:**
- Ingestion boundary rejects writes missing `company_id`, `metric`, `unit`, `financial_period`, `source_document`, `document_date`, or `evidence_status`.
- Both Python domain validator (`FactValidationError`) and SQLite table-level `CHECK` constraints enforce integrity.

#### `companies`

Canonical company master record:

| Column | Type | Constraints | Description |
|---|---|---|---|
| `company_id` | TEXT | PRIMARY KEY | Canonical company ID (e.g. `comp-bharat-forge`) |
| `canonical_name` | TEXT | NOT NULL, non-empty | Primary display name |
| `legal_name` | TEXT | NOT NULL, non-empty | Statutory registered name |
| `cin` | TEXT | NOT NULL, UNIQUE, non-empty | 21-character MCA Corporate Identification Number |
| `is_synthetic` | INTEGER | NOT NULL DEFAULT 0, CHECK IN (0, 1) | Flag separating demo companies from real entities |
| `created_at` | TEXT | NOT NULL | Creation timestamp |

#### `company_identifiers`

Point-in-time security identifier mapping enforcing temporal validity intervals and source citations (FI-007):

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal record ID |
| `company_id` | TEXT | NOT NULL, FOREIGN KEY -> `companies(company_id)` | Linked canonical company |
| `identifier_type` | TEXT | NOT NULL, CHECK IN (`isin`, `cin`, `nse_symbol`, `bse_code`) | Identifier kind |
| `identifier_value` | TEXT | NOT NULL, non-empty | Identifier string (e.g. `INE081A01020`) |
| `valid_from` | TEXT | Nullable (ISO date) | Effective start date (inclusive) |
| `valid_to` | TEXT | Nullable (ISO date), CHECK (`valid_to >= valid_from`) | Expiration date (inclusive); NULL if currently active |
| `source` | TEXT | NOT NULL, non-empty | Evidence citation (e.g. BSE/NSE corporate action circular) |
| `evidence_status` | TEXT | NOT NULL, CHECK IN (`disclosed`, `verified`, `inferred`, `unconfirmed`, `unavailable`) | Provenance classification |
| `created_at` | TEXT | NOT NULL | Mapping timestamp |

### Future planned tables (Gate 3+)

### Financial statement tables

All financial values stored in **INR paise** (integer minor units) to avoid floating-point issues with amounts. Display layer converts to crores/lakhs with appropriate precision.

#### `financial_periods`

Suggested fields: `id`, `company_id`, `period_type` (annual/quarterly/half-year), `period_start`, `period_end`, `fiscal_year`, `quarter` (nullable), `basis` (consolidated/standalone), `currency`, `unit_multiplier` (e.g., 100000 for lakhs), `filing_id` (reference to source filing).

#### `income_statement_line_items`

Suggested fields: `id`, `period_id`, `line_code` (revenue/cogs/gross_profit/ebitda/ebit/pbt/pat/eps_basic/eps_diluted), `value_paise` (nullable), `evidence_status` (disclosed/inferred/unavailable), `computation_formula` (nullable, for inferred values), `source_xbrl_tag` (nullable), `extraction_method` (xbrl/structured_pdf/manual), `extracted_at`.

#### `balance_sheet_line_items`

Same structure as income statement. Line codes: total_assets/fixed_assets/current_assets/cash/total_liabilities/equity/book_value_per_share.

#### `cash_flow_line_items`

Same structure. Line codes: operating_cfo/investing_cfi/financing_cff/free_cash_flow (inferred).

#### `computed_ratios`

Pre-computed derived ratios to avoid recomputing on every request.

Suggested fields: `id`, `period_id`, `ratio_code` (gross_margin/ebitda_margin/pat_margin/roe/roce/roic/pe/pb/ev_ebitda), `value` (decimal), `evidence_status` (inferred for ratios, unconfirmed for analyst estimates), `computed_at`, `formula_version`.

### Shareholding tables

#### `shareholding_snapshots`

Suggested fields: `id`, `company_id`, `period_end_date`, `source` (bse_shareholding/nse_shareholding), `filing_id`.

#### `shareholding_categories`

Suggested fields: `id`, `snapshot_id`, `category` (promoter/fii/dii/retail/other), `holding_pct` (decimal, 4 places), `shares_held`, `evidence_status`.

### Segment tables

#### `segment_disclosures`

Suggested fields: `id`, `company_id`, `period_id`, `segment_type` (business/geography/product), `segment_name`, `revenue_paise`, `profit_paise`, `assets_paise` (nullable), `revenue_pct` (inferred), `evidence_status`, `source_filing_id`.

### Relationship tables

#### `corporate_relationships`

Suggested fields: `id`, `parent_company_id`, `child_company_id`, `relationship_type` (subsidiary/associate/joint_venture/holding_company/promoter_entity), `holding_pct` (nullable), `evidence_status`, `source_filing_id`, `valid_from`, `valid_to`.

#### `business_relationships`

Supplier/customer/competitor relationships.

Suggested fields: `id`, `company_id`, `related_company_id` (nullable; null if named party is not a listed company), `related_party_name`, `relationship_type` (customer/supplier/competitor/peer), `concentration_pct` (nullable; from filing disclosure), `evidence_status`, `source_filing_id`, `valid_from`, `valid_to`.

### Filing and document tables

#### `filings`

Suggested fields: `id`, `company_id`, `exchange` (bse/nse), `filing_type` (board_meeting_outcome/shareholding/result/agm_notice/insider_trading/investor_presentation/annual_report/drhp/other), `filing_date`, `period_covered` (nullable), `title`, `document_url`, `local_storage_key` (nullable), `ingested_at`, `evidence_status` (disclosed).

Store only the metadata and a link to the original document; do not store full PDF text unless rights are confirmed.

#### `filing_extracts`

Verbatim text extracts from filings, with source reference.

Suggested fields: `id`, `filing_id`, `section_name`, `extract_text`, `page_reference` (nullable), `extraction_method`, `extracted_at`. The `extract_text` must be verbatim; no paraphrase or AI-generated rewrite.

#### `company_news`

Suggested fields: `id`, `company_id`, `headline`, `source_outlet`, `article_url`, `published_at`, `ingested_at`, `evidence_status` (unconfirmed by default for news).

### Commodity tables

#### `commodity_definitions`

Suggested fields: `id`, `commodity_code`, `display_name`, `exchange` (mcx/ncdex/other), `unit`, `currency`, `data_source`.

#### `commodity_prices`

Suggested fields: `id`, `commodity_id`, `date`, `open`, `high`, `low`, `close` (all in integer minor units of the commodity currency), `source_timestamp`, `received_at`.

#### `company_commodity_exposures`

Maps company to commodity based on disclosed filing references.

Suggested fields: `id`, `company_id`, `commodity_id`, `exposure_pct_of_cogs` (nullable), `description`, `evidence_status`, `source_filing_id`, `valid_from`, `valid_to`.

### Research workspace tables

#### `user_research_layouts`

Suggested fields: `id`, `user_id`, `layout_name`, `panel_config_json`, `created_at`, `updated_at`.

The `panel_config_json` stores panel types, sizes, positions, and data references. It must not store raw financial data; it references data by company ID and panel type.

#### `user_notes`

Suggested fields: `id`, `user_id`, `company_id` (nullable), `filing_id` (nullable), `note_text`, `created_at`, `updated_at`.

Notes are private to the user; never readable by other users without explicit sharing functionality.

---

## Relationships and integrity

- A board snapshot references the exact instrument and, when applicable, the zone that was active at snapshot time. Store the relevant numeric levels in the snapshot too; do not depend on mutable zone state to reconstruct past boards.
- Journal snapshots attach to a specific board snapshot. Users must not see another user's journal records.
- Payment records and subscriptions use provider IDs with idempotency constraints.
- Historical market records include provider source and timestamps. Delete/retain them only within the applicable data licence.
- Every change to algorithm parameters and instrument mappings is versioned/audited.
- Financial Intelligence records: every row must carry `evidence_status` and `source_filing_id` or `source` reference. Rows without a source reference must be rejected at the ingestion boundary.
- A `company_id` in the Financial Intelligence tables must correspond to a verified entity in `companies`; no orphan financial records.

---

## Retention starting points (must be reviewed)

- One-minute candles and computed indicators: proposed two-year working retention, compress/archive older data only if allowed by provider agreement.
- Board snapshots: retain as long as licence, privacy and product commitments permit.
- Notification delivery logs: proposed 90 days.
- Admin audit logs: proposed three years, subject to legal/security policy.
- Journal data: user-owned; support export and deletion requests. Explain any legal retention exception before launch.
- Financial statement data: retain subject to data provider licence; each filing extract must record the source licence reference.
- Filing PDFs: store locally only if rights are confirmed; otherwise link to exchange/official source.
- News items: proposed 90-day retention for recent context; longer retention requires licence confirmation.

Do not implement a retention duration as a hard fact until the provider agreement and privacy review are complete.
