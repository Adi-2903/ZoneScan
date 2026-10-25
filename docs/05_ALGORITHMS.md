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

## 5. Chart liquidity levels and sweeps

Candidate levels:

- Confirmed swing highs and lows.
- Equal-high/equal-low clusters: confirmed swing points within `0.1 × ATR14_5m`; use the documented extreme/cluster convention consistently.
- Previous day high/low (PDH/PDL).
- Previous week high/low (PWH/PWL), when history is available.
- Opening-range high/low for the first 15 minutes of the session; do not compute the final range before that period has completed.

A sweep candidate occurs when price trades beyond a defined level and then closes back inside within three completed candles. Mark the level `Swept` and remove it from the list of unswept levels. A sweep beside a fresh order block can be recorded as a confluence feature for later validation; it must not be called a guaranteed liquidity trap.

The word “liquidity” in the UI must refer to these price levels, not to an assertion that the application can see the exchange order book or all resting stops.

## 6. Strength Score (0–100)

Each component is intended to be in `[0, 1]`. Clip all inputs to the stated range and record component values for explainability.

### Components

**M — Move strength (weight 0.25)**

`M = min(abs(day_return) / (1.5 × daily_sigma20), 1)`

If `daily_sigma20` is zero or unavailable, M is unavailable and the symbol cannot receive a complete score.

**V — Relative volume (weight 0.15)**

`V = clip((RVOL - 1) / 2, 0, 1)`

Thus normal volume or lower contributes zero; 3× baseline or more reaches one.

**O — Open-interest participation (weight 0.20)**

`OI_magnitude = min(abs(OI_change_daily_pct) / 0.05, 1)`

Use price direction and OI direction to classify the context:

| Price direction | OI change | Interpretation for same-side score | Factor |
|---|---|---|---:|
| Up | Up | Long buildup | 1.0 |
| Up | Down | Short covering | 0.5 |
| Down | Up | Short buildup | 1.0 |
| Down | Down | Long unwinding | 0.5 |

`O = OI_magnitude × factor` only if the OI/price context can be classified for the scored direction. Otherwise O is unavailable or zero according to a versioned rule; do not hide poor data quality.

**T — Trend alignment (weight 0.20)**

Use three direction-alignment checks: price is on the correct side of VWAP; price is on the correct side of EMA20; market-structure label agrees with direction. For structure, assign 1 when structure matches, 0.5 for range, and 0 when it opposes. `T = (VWAP_check + EMA_check + structure_value) / 3`.

**S — Sector participation (weight 0.10)**

`S = 1` if sector direction aligns, `0.5` if neutral/mixed, and `0` if it opposes. Proposed sector direction uses a traded-value-weighted aggregate and a configurable participation threshold. Initial default: call sector aligned only when at least 60% of covered sector members (by count) share the direction; otherwise neutral unless the opposite direction itself reaches the threshold. The 60% rule is provisional and must be tested.

**Z — Zone proximity (weight 0.10)**

Let `d` be the distance to the nearest eligible fresh/tested order block in the scored direction divided by ATR. If no qualifying zone exists, `Z=0` and the UI explicitly says no zone is present. Otherwise:

- `Z=1` when `d <= 1`.
- `Z=(4-d)/3` when `1 < d < 4`.
- `Z=0` when `d >= 4`.

### Final score

`Strength = 100 × (0.25M + 0.15V + 0.20O + 0.20T + 0.10S + 0.10Z)`

All six component weights sum to 1. If a required component is unavailable, do not silently renormalize the remaining weights; mark the score unavailable and exclude the symbol until the policy is explicitly changed and versioned.

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

When Choppy, both scores are set to zero for ranking purposes and the stock is omitted from bullish/bearish boards. Keep a separate reason code for diagnostics. The exact candle-overlap metric must be unit-tested and documented in code before production.

## 9. Direction, smoothing and ranking

### Direction classification

- Bullish if day return is positive and structure is bullish, or structure is range with price above VWAP.
- Bearish is the mirror.
- Otherwise Choppy/Neutral.
- Apply the choppy filter before the final ranking.

### Smoothing

`smoothed_score = 0.6 × new_score + 0.4 × previous_smoothed_score`

Reset the previous-score dependency for a new session according to a written rule. On first eligible score of a session, use the raw score; do not carry stale prior-session smoothing without an explicit rule.

### Sorting and stability

Sort by smoothed Strength Score descending, then RVOL descending, then traded value descending, then symbol ascending for deterministic tie-breaks.

Use hysteresis to limit flicker: a new entrant must beat the current 20th score by at least 2 points; a current member may remain until it falls 3 points below the relevant cutoff. Implement the cutoff/side transition logic explicitly and test ties, removals, choppy status and missing data. Hysteresis must never retain an ineligible or data-invalid symbol.

Persist top-20 rows by side as a timestamped snapshot with raw components, smoothed score, zone/level references and the parameter version.

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
