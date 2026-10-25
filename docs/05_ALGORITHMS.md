# 05 — Market Algorithms and Score Definitions

**Status:** Version-0.1 proposal for implementation and testing, not a validated trading strategy. Thresholds are starting values. No performance claim is approved. Every change must be parameter-versioned and evaluated out of sample.

## 1. Terminology

- **Order block (OB):** a rule-defined price zone associated with the last opposing candle before a displacement that breaks confirmed market structure. It is a technical-analysis heuristic, not proof of institutional orders.
- **Liquidity level:** a price reference such as a confirmed swing, equal highs/lows, previous-session extreme, or opening-range extreme. It does not represent a direct feed of resting orders.
- **Strength Score:** score used to rank directional stocks.
- **Early-Move Score:** proposed name for the secondary score that rewards directional OI/momentum/volume acceleration while penalizing a move that has already extended. The original brief called this a “liquidity score”; this documentation separates the concept from chart liquidity levels to avoid ambiguity.
- **BOS:** break of structure, confirmed by a completed candle closing beyond the relevant confirmed swing.
- **ATR:** average true range, here ATR(14) of completed 5-minute candles unless a function states otherwise.
- **RVOL:** relative volume against a time-of-day baseline.

## 2. Inputs, unit conventions and warm-up

For each eligible equity and each completed minute, calculate or update:

- `day_return = (last_price - session_open) / session_open` (fraction, not percentage number).
- `daily_sigma20 = standard deviation of the most recent 20 completed daily returns` (fraction).
- `ATR14_5m` from completed 5-minute candles, in price units.
- `RVOL = volume_so_far_today / average_volume_up_to_same_elapsed_time_over_previous_20_sessions`.
- `OI_change_daily_pct` = percentage change in the chosen futures contract's OI versus the documented prior-session reference.
- `OI_change_30m_pct` = percentage change in the same selected contract's OI over the trailing 30 minutes.
- `VWAP`, `EMA20` on completed 5-minute closes; `ADX14` on completed 5-minute candles.
- `sector_bias` from a weighted aggregate of covered sector members.
- Nearest valid fresh/tested zone and its distance in ATR units.

Use decimal fractions in formulas: 5% is `0.05`, not `5`. OI calculations must retain contract identity so a rollover does not create a false change. Indicators are unavailable until enough history exists; never backfill missing history with future observations.

### Indicator engine conventions (v0.1-indicators)

`zonescan.indicators` consumes normalized `Candle`, `TradingSession`, `OpenInterestObservation`, and `FuturesContractMapping` models. Input minute timestamps denote interval starts; aggregate timestamps denote interval ends. Session windows are `[opens_at, closes_at)`, use Asia/Kolkata session dates, and never cross sessions. A window is emitted only when every 1-minute candle is present and complete; gaps/incomplete source bars are returned as `MissingCandleInterval` records. No missing candle is synthesized.

- ATR(14) is Wilder-smoothed true range on completed aggregate bars, seeded by the arithmetic mean of 14 true ranges. The first true range is high-low. A missing aggregate resets ATR/EMA/ADX warm-up.
- EMA(20) uses completed aggregate closes, alpha `2/(20+1)`, and an SMA of the first 20 consecutive closes as its seed.
- ADX(14) uses Wilder +DM/-DM/TR smoothing, DX, and an arithmetic mean of 14 valid DX values as initial ADX. It is unavailable when directional movement has a zero denominator.
- VWAP uses completed aggregate close times aggregate volume, accumulated from session open. Zero cumulative volume makes VWAP and its price-side flag unavailable.
- Day return uses current completed close against the first completed aggregate candle's open. If that first candle is absent, the day's return remains unavailable.
- Daily sigma uses sample standard deviation (`n-1`) over 20 simple close-to-close returns from 21 completed daily closes strictly before the current session. Supply the prior session calendar as `TradingSession` history; if any of those 21 sessions lacks a completed daily candle, sigma is unavailable rather than bridging the gap.
- RVOL compares cumulative completed aggregate volume through the current elapsed slot with the arithmetic mean of cumulative volume through the same slot over the previous 20 supplied sessions. Any missing baseline slot/current-session interval, fewer than 20 baseline sessions, or zero baseline makes RVOL unavailable.
- OI observations remain keyed by futures contract and timestamp; they are never sourced from the cash-equity candle. At an aggregate close, current OI is the last constituent 1-minute timestamp. The 30-minute reference is the exact observation 30 minutes earlier. Daily comparison uses the previous supplied session's last minute and is unavailable across contract-ID change. Missing timestamp/reference or invalid denominator remains unavailable; values are not carried forward.

The result is one `IndicatorFrame` per expected aggregate slot, including explicit gaps. It can map available fields to existing `ReplayBar` values; unavailable values remain `None`. Sector classification stays upstream and Q-019 remains open. Calculations are prefix-causal: future candles, daily closes, or OI observations are not consulted for an earlier frame.

## 3. Confirmed swing points and structure

A swing high is a candle whose high exceeds the highs of the three candles before and the three candles after. A swing low is the mirror. The point becomes confirmed only after the three later candles close. Therefore, the engine may record a swing's original timestamp, but must not use it before confirmation time.

- Bullish BOS: a completed candle closes above the latest confirmed swing high available at that candle's decision time.
- Bearish BOS: a completed candle closes below the latest confirmed swing low available at that decision time.
- Structure label: bullish when the latest two confirmed swing highs and lows are rising; bearish when both are falling; otherwise range/neutral.

Use only information available at the timestamp being processed. This rule is mandatory for live scoring and historical replay.

## 4. Order-block detection

### Bullish candidate

1. Identify a run of 1–3 consecutive up candles in the completed 5-minute series.
2. The combined displacement range must be at least `1.5 × ATR14_5m`.
3. Mean RVOL across the run must be at least `1.2`.
4. The run must close above the most recent confirmed swing high available before the run began (bullish BOS).
5. Select the last down candle immediately before the displacement run.
6. Zone default is that candle's low-to-high range. Support for body-only/open-to-close zone bounds may be added as a versioned configuration later.
7. Mark `has_fvg=true` if a three-candle fair-value gap exists within the displacement under the documented candle definition; this is a confirmation attribute, not an automatic order instruction.

Bearish detection is the exact directional mirror: down displacement, BOS below a confirmed swing low, and the last up candle immediately before the run.

### Zone lifecycle

| State | Deterministic rule | UI |
|---|---|---|
| Fresh | Price has not returned to the zone after formation | Solid translucent rectangle |
| Tested | A later candle's range intersects the zone but closes outside the invalidation side | Lighter rectangle + label |
| Mitigated | A completed candle closes through the far side of the zone | Remove from current shortlist; keep in history |
| Expired | Untouched for five completed trading sessions | Archive/stop showing as active |

Additional rules:

- Detect on completed 5-minute and 15-minute series. If zones overlap under a documented overlap test, prefer the 15-minute zone.
- Keep at most three active zones per side per instrument.
- For the core setup card, select the nearest valid fresh/tested zone on the correct side of price and within 4 ATR.
- A bullish setup's nearest zone is below/containing price; a bearish setup's nearest zone is above/containing price. If no valid zone exists, show “No qualifying zone” and do not invent one.
- Record formation time, timeframe, high/low, state transitions and algorithm version.
- Live/preview updates may update the last price, but an unfinished candle cannot create or confirm a zone.

#### Implemented v0.1 prototype semantics

`services/api/src/zonescan/order_blocks.py` implements the rules above for completed 5m/15m candles. The displacement range is the maximum high minus minimum low across the run; the latest run candle's ATR is used for the `1.5 × ATR` comparison, and mean run RVOL must be at least `1.2`. The final displacement candle must close through the most recent relevant swing that was already confirmed by the timestamp of the immediately preceding opposing candle. A zone uses that opposing candle's full low/high range. Missing ATR or RVOL, nonpositive ATR, an incomplete candle, or missing confirmed structure produces no zone. A three-candle FVG means the first candle's high is below the third candle's low for bullish displacement (mirrored for bearish).

Lifecycle details: only a completed candle strictly after formation can touch a zone. An intersection with the zone changes Fresh to Tested and records `last_touched_at`; a close strictly beyond the far boundary changes either active state to Mitigated, even when a gap leaves the candle's range wholly beyond the zone. Mitigated and Expired zones never reactivate. A zone is Expired only while still Fresh, after five subsequent distinct observed session dates without a touch; dates come from the supplied session calendar date, or the candle timestamp in `Asia/Kolkata` when absent. Calendar dates with no candles do not count as sessions.

Overlap means a positive-width intersection (`a.low < b.high` and `b.low < a.high`) for the same instrument and side. An overlapping 15m zone deactivates overlapping 5m zones; an overlapping 5m candidate is suppressed when an active 15m zone exists. Historical zones are retained with `active=false`. If a side exceeds three active zones, the oldest by formation timestamp (then stable zone ID) is deactivated. These tie-breaking rules are deterministic. Session calendars, candle aggregation and exchange holiday validation remain upstream responsibilities.

The replay implementation emits a zone only at the displacement close, after its BOS and required inputs are known. It feeds one chronological candle at a time into the same swing and detection functions used by a live caller. Replay records missing same-session intervals as `data_gap` events and never fabricates replacement candles. Algorithm/parameter versions are stored on each zone. These are implemented prototype semantics, not validated market signals.

#### Sequential Strength Score replay

For each completed replay candle, the engine derives market structure only from swings whose three right-side candles have closed by that candle's timestamp. Direction uses the documented day-return/structure/VWAP classification rule. It calls the same `calculate_strength` implementation as other consumers and attaches a `ReplayScore` with the candle timestamp, `ScoreResult`, six components, unavailable reasons and score versions. Current close supplies the price input; the replay bar supplies time-aligned day return, daily sigma, RVOL, OI change, VWAP/EMA side booleans, ATR and an optional categorical sector direction. The nearest eligible zone is selected from zones active by that timestamp. Incomplete candles receive an explicit unavailable result and are not scored. Missing inputs remain unavailable, except no eligible zone is the documented valid `Z=0`. Sector classification is not aggregated in replay; a missing sector input makes S unavailable, and future sector values are never read for earlier scores. Callers supplying the per-candle fields must ensure each is point-in-time and uses the documented units. This is deterministic fixture replay, not historical performance validation.

## 5. Chart liquidity levels and sweeps

Candidate levels:

- Confirmed swing highs and lows.
- Equal-high/equal-low clusters: confirmed swing points within `0.1 × ATR14_5m`; use the documented extreme/cluster convention consistently.
- Previous day high/low (PDH/PDL).
- Previous week high/low (PWH/PWL), when history is available.
- Opening-range high/low for the first 15 minutes of the session; do not compute the final range before that period has completed.

A sweep candidate occurs when price trades beyond a defined level and then closes back inside within three completed candles. Mark the level `Swept` and remove it from the list of unswept levels. A sweep beside a fresh order block can be recorded as a confluence feature for later validation; it must not be called a guaranteed liquidity trap.

#### Replay conventions (provisional v0.1-liquidity)

Replay emits `LiquidityLevel` records and timestamped liquidity events independently from `ReplayScore`. A swing level becomes available only at its existing confirmed swing's `confirmed_at`. Equal highs/lows are built from same-kind confirmed swing points no farther than `0.1 × current ATR14_5m`; the outer cluster extreme is used as the level price (maximum for highs, minimum for lows). ATR must be positive and available on a 5m replay bar or equal-level formation is reported unavailable; 15m-only replay emits an unavailable diagnostic for equal-level detection because it has no 5m ATR input. Levels above price are high-side references and those below price are low-side references.

Previous-day levels use the immediately preceding supplied `TradingSession`; previous-week levels use all supplied sessions in the preceding ISO calendar week. Every expected candle in those periods must be present and complete. The first-15-minute range is emitted only when every expected 5m candle (three bars) or 15m candle (one bar) through the range close is complete. Missing calendar/history produces a `liquidity_unavailable` event rather than partial extrema. The caller must supply the exchange session calendar; special sessions require their actual bounds.

For a high-side level, an excursion means `high > level`; return inside means `close <= level`. Low-side comparisons mirror this (`low < level`, `close >= level`). The excursion bar counts as candle one: a return in that bar sweeps immediately; otherwise a return by the third completed candle confirms the sweep. If the third completed candle still closes beyond, the level becomes `invalidated`. Day/opening levels expire at the next session and week levels at the next ISO week. A data gap or incomplete candle makes every currently unswept level for that stream `unavailable`, since an unseen high/low may have crossed it; an interrupted pending window is therefore not guessed. Swept, invalidated, expired, and unavailable records remain in replay output for audit and are excluded from unswept levels. These cluster-price, window-count, invalidation, and completeness conventions are provisional pending owner review.

The word “liquidity” in the UI must refer to these price levels, not to an assertion that the application can see the exchange order book or all resting stops.

## 6. Strength Score (0–100)

Each component is in `[0, 1]`. Inputs use decimal fractions for returns and OI changes (`0.025` means 2.5%), ratios for RVOL, price units for price/ATR, and explicit direction labels. Component functions validate inputs and preserve raw component precision; display/serialization layers may round separately.

### Components

**M — Move strength (weight 0.25)**

`M = min(abs(day_return) / (1.5 × daily_sigma20), 1)`

`daily_sigma20` must be finite and positive. Missing, non-finite, zero, or negative sigma makes M unavailable; a genuine zero return with valid sigma produces `M=0`.

**V — Relative volume (weight 0.15)**

`V = clip((RVOL - 1) / 2, 0, 1)`

RVOL must be finite and nonnegative. Missing or invalid RVOL makes V unavailable. Thus normal volume or lower contributes zero; 3× baseline or more reaches one.

**O — Open-interest participation (weight 0.20)**

`OI_magnitude = min(abs(OI_change_daily_pct) / 0.05, 1)`

Use price direction and OI direction to classify the context:

| Price direction | OI change | Interpretation for same-side score | Factor |
|---|---|---|---:|
| Up | Up | Long buildup | 1.0 |
| Up | Down | Short covering | 0.5 |
| Down | Up | Short buildup | 1.0 |
| Down | Down | Long unwinding | 0.5 |

O = OI_magnitude * factor only when price direction agrees with the scored direction. Rising OI uses factor 1.0 (long buildup when price rises; short buildup when price falls); falling OI uses factor 0.5 (short covering when price rises; long unwinding when price falls). A flat OI change is valid zero. Nonzero OI change with zero price return, or a scored direction that conflicts with price-return sign, makes O unavailable. OI changes are decimal fractions: 0.025 is 2.5%. Deriving OI percent change requires finite OI values and a strictly positive reference OI; otherwise it is unavailable.

**T — Trend alignment (weight 0.20)**

Use three direction-alignment checks: price is on the correct side of VWAP; price is on the correct side of EMA20; market-structure label agrees with direction. For structure, assign 1 when structure matches, 0.5 for range, and 0 when it opposes. `T = (VWAP_check + EMA_check + structure_value) / 3`. Direction must be `bullish` or `bearish`, indicators must be actual booleans, and structure must be `bullish`, `bearish`, or `range`; missing or invalid values make T unavailable.

**S — Sector participation (weight 0.10)**

`S = 1` if sector direction aligns, `0.5` if neutral/mixed, and `0` if it opposes. Input classification must be `bullish`, `bearish`, `neutral`, or `mixed`; missing/unknown classification makes S unavailable. Proposed sector direction uses a traded-value-weighted aggregate and a configurable participation threshold. Initial default: call sector aligned only when at least 60% of covered sector members (by count) share the direction; otherwise neutral unless the opposite direction itself reaches the threshold. The 60% rule is provisional and must be tested.

**Z — Zone proximity (weight 0.10)**

Let `d` be the distance to the nearest eligible fresh/tested order block in the scored direction divided by ATR. If no qualifying zone exists, `Z=0` and the UI explicitly says no zone is present. Otherwise:

- `Z=1` when `d <= 1`.
- `Z=(4-d)/3` when `1 < d < 4`.
- `Z=0` when `d >= 4`.

The scorer receives current price, ATR, and a candidate zone. No zone, inactive/mitigated/expired zone, or wrong-direction zone contributes valid `Z=0`. A valid fresh/tested supporting zone requires finite positive current price and ATR, valid bounds, and correct side relative to price; missing or nonpositive ATR for such a zone makes Z unavailable. For bullish direction, an eligible zone is below or contains current price; bearish is mirrored. Distance is to the nearest zone edge (zero while price is inside). The linear interpolation above is the existing v0.1 formula.

### Final score

`Strength = 100 × (0.25M + 0.15V + 0.20O + 0.20T + 0.10S + 0.10Z)`

All six component weights sum to 1. If a required component is unavailable, do not silently renormalize the remaining weights; mark the score unavailable and exclude the symbol until the policy is explicitly changed and versioned. `ScoreResult.components` preserves computed values and stores `null` for unavailable components; `component_reasons` identifies each unavailable component. A genuine zero remains numeric zero. Component values are not rounded before weighting; the final score is clamped only for floating-point boundary noise and carries algorithm/parameter versions. The current implementation reports `v0.1-score` and `2026-10-26.3`.

## 7. Early-Move Score (provisional name)

This is a separate heuristic intended to reward early directional acceleration and penalize a move that has already run. It is **not** a chart-liquidity measurement.

`EarlyMove = 100 × (0.40 × OI30 + 0.35 × Mom15 + 0.25 × Burst15) × (1 - RunPenalty)`

Proposed deterministic component definitions:

- `OI30`: `min(abs(OI_change_30m_pct)/0.05, 1) × same-side OI factor`, using the table above.
- `Mom15`: `clip(abs(price_now - price_15m_ago) / ATR14_5m, 0, 1)`, provided the movement aligns with the scored direction; otherwise 0.
- `Burst15`: compare the last completed 15-minute volume with the average 15-minute volume for the same elapsed time over the previous 20 sessions; `clip((ratio - 1)/1, 0, 1)`. This maps normal baseline volume to 0 and 2× baseline or higher to 1.
- `RunPenalty`: let `x = abs(day_return)/daily_sigma20`. `RunPenalty=0` for `x <= 1.5`; increase linearly from 0 to 0.6 for `1.5 < x < 3`; cap at `0.6` for `x >= 3`.

These component normalizations are proposed defaults where the original brief was not dimensionally or operationally precise. They must be validated against historical data and kept versioned. If required OI or baseline volume is unavailable, the score is unavailable.

## 8. Choppy filter

A stock is `Choppy` when **at least two** of these conditions hold:

1. ADX(14) on 5-minute candles is below 18.
2. `abs(day_return) < 0.5 × daily_sigma20`.
3. RVOL is below 1.0.
4. The last 12 completed 5-minute candles overlap more than 70% by the agreed overlap metric and no BOS has occurred in the current session.

For Q-009, overlap is calculated across the 11 adjacent pairs in those 12 candles. For each pair, compute `max(0, min(high_a, high_b) - max(low_a, low_b)) / min(high_a - low_a, high_b - low_b)`, then take the arithmetic mean. A pair with either candle range equal to zero contributes `0`. The 12 candles must be complete, consecutive 5-minute candles from the same Asia/Kolkata session; a gap, incomplete candle, or insufficient history makes the overlap condition unavailable. The test is strict: the mean must be `> 0.70`.

The no-BOS part of condition 4 is false once a confirmed BOS is observed in the current session. To establish that no BOS occurred, replay requires the supplied session calendar and complete candles from session open through the current timestamp; otherwise that subcondition is unavailable. Conditions use three-valued results (`true`, `false`, unavailable) and carry per-condition reasons. Classification is Choppy if at least two conditions are true; it is valid non-Choppy if true conditions plus unavailable conditions cannot reach two; otherwise the classification is unavailable. Missing conditions never count as true or false.

Replay attaches `ChoppyResult` and `filtered_strength` to each `ReplayScore`. When Choppy, `filtered_strength` is zero, while the original `ScoreResult` and its component breakdown are retained. A valid non-Choppy classification passes through the available raw Strength Score; an unavailable classification leaves `filtered_strength` unavailable. Early-Move Score is not implemented and is not changed by this milestone. Ranking and board omission remain downstream work.

## 9. Direction, smoothing and ranking

### Direction classification

- Bullish requires a positive day return and either bullish structure or range structure with price above VWAP.
- Bearish requires a negative day return and either bearish structure or range structure with price below VWAP.
- A valid signed return/structure combination that satisfies neither direction is `neutral`. Missing day return or structure is unavailable; range structure also requires a known VWAP side. Zero day return is neutral.
- The Choppy filter remains a separate classification. A Choppy result excludes the row from either directional board; it does not rewrite the directional label or raw score.

### Smoothing

`smoothed_score = 0.6 * new_score + 0.4 * previous_smoothed_score`

Replay smooths `filtered_strength` (the Choppy-adjusted score), independently per instrument and timeframe. The first available filtered score in a session is used unchanged. A missing filtered score clears the chain; the next available score starts again from its current filtered value. A new session always resets the chain. Choppy's valid zero is a score observation, although that row is excluded from the board. Incomplete candles are unavailable observations.

### Sorting and stability

At each completed 5m timestamp, build both boards only from scores emitted at that timestamp. A candidate must have an available raw score, directional classification for that side, an available non-Choppy classification, filtered and smoothed scores, and valid RVOL/traded value. Missing or invalid values are excluded and hysteresis never retains them. The replay tie-break value `traded_value` is the current completed candle's close multiplied by its volume; cumulative session turnover is not available in `ReplayBar` and this choice is provisional. Sort by smoothed Strength Score descending, then RVOL descending, then this traded value descending, then symbol ascending. If a symbol mapping is absent in a fixture, instrument ID is used as the stable final key; production inputs should supply the mapped symbol.

Hysteresis is evaluated independently per side and resets each session. The cutoff is the prior snapshot's 20th row score, measured using its smoothed Strength Score. A previously listed, still-eligible member is retained when its current smoothed score is at least `cutoff - 3`; a new entrant is admitted only at or above `cutoff + 2`. Eligible retained members and qualifying entrants are sorted by the normal keys and truncated to 20. An incomplete prior board has open slots and is filled by normal rank order without entry margin. A side change makes an instrument a new entrant on the other side. A cutoff is not carried when the prior board had fewer than 20 rows.

Replay returns immutable timestamped `BoardSnapshot` values, with up to 20 rows per side and each row retaining its full `ReplayScore` (raw components, filtered/smoothed values, Choppy result, and versions). These are in-memory deterministic fixtures, not persisted board history. Snapshot production does not use later timestamp scores.

## 10. One-zone setup card

For a bullish stock (mirror for bearish):

- **Order Block:** nearest valid fresh/tested zone on the appropriate side, within 4 ATR.
- **Support:** nearest eligible confirmed swing/reference low just below the chosen zone, if available.
- **Resistance:** nearest eligible confirmed swing/reference high above current price, if available.
- **Liquidity:** nearest unswept relevant level in the documented direction, if available.
- **Zone distance:** signed/absolute convention must be consistent. UI proposal: show absolute percent distance from current price to the nearest zone edge and separately indicate whether price is above, below or inside the zone.

If a level is unavailable, show `—`/`Not available`; never derive a made-up value from an unrelated level.

## 11. Parameter management

All of the following are initial parameters, not validated truths:

| Parameter | Initial default | Validation method |
|---|---:|---|
| Swing left/right bars | 3 / 3 | Historical replay + visual fixtures |
| Displacement size | 1.5 ATR | Out-of-sample backtest |
| Displacement RVOL | 1.2 | Out-of-sample backtest |
| Equal-level tolerance | 0.1 ATR | Visual review + sensitivity analysis |
| ADX choppy threshold | 18 | Out-of-sample backtest |
| Zone expiry | 5 sessions | Sensitivity analysis |
| Score weights | As specified above | Train/validation/test split; no test-set tuning |
| Smoothing | 0.6 new / 0.4 previous | Rank stability and lag analysis |
| Sector directional participation | 60% | Sensitivity analysis |

Each version must have an ID, effective date, author, rationale and associated evaluation report. A parameter update must not rewrite historical output without recording the recalculation.

## 12. Mandatory algorithm safeguards

- Confirmed swings only; no future data at decision time.
- Closed candles only for zone formation and mitigation.
- Same implementation for production and replay/backtesting.
- Include stocks removed from the universe in the corresponding historical universe where data rights permit, to reduce survivorship bias.
- Separate tuning, validation and untouched test periods.
- Include spreads, fees and slippage if making any simulated net-performance claim.
- Report results by market regime and score band; show failures as well as successes.
- Do not claim that a zone or score predicts a guaranteed reaction.
