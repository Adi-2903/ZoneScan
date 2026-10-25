from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .choppy import (candle_overlap_ratio, classify_choppy,
                     unavailable_choppy)
from .liquidity import (equal_level_for_swing, expected_candle_timestamps,
                        invalidate_levels_for_gap, level_from_extreme,
                        level_from_swing, session_complete, update_sweep)
from .models import (ChoppyResult, LiquidityLevel, ReplayBar, ReplayEvent, ReplayScore,
                     ScoreInputs, ScoreResult, Swing, TradingSession, Zone)
from .order_blocks import (OrderBlockParameters, _session_day,
                           detect_order_blocks, resolve_zone_overlap,
                           update_zone_lifecycle)
from .scoring import calculate_strength, classify_direction
from .structure import break_of_structure, confirmed_swings, structure_label

_IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True, slots=True)
class ReplayResult:
    events: tuple[ReplayEvent, ...]
    swings: tuple[Swing, ...]
    zones: tuple[Zone, ...]
    scores: tuple[ReplayScore, ...]
    liquidity_levels: tuple[LiquidityLevel, ...] = ()


def _structure_if_warm(swings: tuple[Swing, ...]) -> str | None:
    if sum(s.kind == "high" for s in swings) < 2 or sum(s.kind == "low" for s in swings) < 2:
        return None
    return structure_label(swings)


def _nearest_supporting_zone(zones: list[Zone], direction: str | None,
                             current_price: float) -> Zone | None:
    if direction not in ("bullish", "bearish"):
        return None
    candidates: list[tuple[float, float, str, Zone]] = []
    for zone in zones:
        if not zone.active or zone.state not in ("fresh", "tested") or zone.side != direction:
            continue
        if direction == "bullish":
            if zone.low > current_price:
                continue
            distance = max(0.0, current_price - zone.high)
        else:
            if zone.high < current_price:
                continue
            distance = max(0.0, zone.low - current_price)
        candidates.append((distance, -zone.formed_at.timestamp(), zone.zone_id, zone))
    return min(candidates, default=(0.0, 0.0, "", None), key=lambda row: row[:3])[3]


def _choppy_for_bar(bar: ReplayBar, stream: list[ReplayBar],
                    swings: tuple[Swing, ...],
                    trading_sessions: tuple[TradingSession, ...] | list[TradingSession]
                    ) -> ChoppyResult:
    if not bar.candle.complete:
        return unavailable_choppy("incomplete_candle")
    if bar.timeframe != "5m":
        return unavailable_choppy("choppy_filter_requires_5m_replay")

    day = _session_day(bar)
    current_records = [(index, item) for index, item in enumerate(stream)
                       if _session_day(item) == day]
    session_records = [item for _, item in current_records]
    if len(session_records) < 12:
        overlap, overlap_reason = None, "insufficient_12_completed_5m_candles"
    else:
        overlap, overlap_reason = candle_overlap_ratio(
            tuple(item.candle for item in session_records[-12:]))

    session_start_index = current_records[0][0] if current_records else len(stream)
    bos_events = break_of_structure(tuple(item.candle for item in stream), swings)
    bos_today = any(index >= session_start_index for index, _ in bos_events)
    session = next((item for item in trading_sessions
                    if item.instrument_id == bar.candle.instrument_id
                    and item.session_date == day), None)
    no_bos: bool | None
    bos_reason: str | None = None
    if bos_today:
        no_bos = False
    elif session is None:
        no_bos = None
        bos_reason = "missing_session_calendar_for_bos"
    else:
        expected = tuple(timestamp for timestamp in expected_candle_timestamps(session, "5m")
                         if timestamp <= bar.candle.timestamp)
        by_time = {item.candle.timestamp: item.candle for item in session_records}
        covered = (bool(expected) and expected[-1] == bar.candle.timestamp
                   and all(timestamp in by_time and by_time[timestamp].complete
                           for timestamp in expected))
        if covered:
            no_bos = True
        else:
            no_bos = None
            bos_reason = "incomplete_session_history_for_bos"

    reasons = dict(bar.indicator_unavailable_reasons)
    return classify_choppy(bar.adx14, bar.day_return, bar.daily_sigma20, bar.rvol,
                           overlap, no_bos, reasons, overlap_reason, bos_reason)


def replay(bars: tuple[ReplayBar, ...] | list[ReplayBar],
           parameters: OrderBlockParameters = OrderBlockParameters(),
           swing_left: int = 3, swing_right: int = 3,
           trading_sessions: tuple[TradingSession, ...] | list[TradingSession] = ()) -> ReplayResult:
    """Replay chronologically with a prefix-only view for every decision."""
    calendar_keys = [(item.instrument_id, item.session_date) for item in trading_sessions]
    if len(calendar_keys) != len(set(calendar_keys)):
        raise ValueError("duplicate trading session in replay calendar")
    history: dict[tuple[str, str], list[ReplayBar]] = {}
    sessions: dict[tuple[str, str], list[date]] = {}
    zones: list[Zone] = []
    scores: list[ReplayScore] = []
    zone_formation_sessions: dict[str, int] = {}
    events: list[ReplayEvent] = []
    liquidity_levels: list[LiquidityLevel] = []
    liquidity_ids: set[str] = set()
    liquidity_notice_keys: set[tuple[str, str, date, str]] = set()
    processed_opening_ranges: set[tuple[str, str, date]] = set()
    all_swings: dict[tuple[str, str, str, datetime], Swing] = {}
    last_timestamp: datetime | None = None
    seen_keys: set[tuple[str, str, datetime]] = set()

    for bar in bars:
        candle = bar.candle
        if last_timestamp is not None and candle.timestamp < last_timestamp:
            raise ValueError("replay bars must be ordered by timestamp")
        last_timestamp = candle.timestamp
        key = (candle.instrument_id, bar.timeframe)
        identity = (candle.instrument_id, bar.timeframe, candle.timestamp)
        if identity in seen_keys:
            raise ValueError("duplicate candle for instrument and timeframe")
        seen_keys.add(identity)
        stream = history.setdefault(key, [])
        day = _session_day(bar)
        session_days = sessions.setdefault(key, [])
        if not session_days or session_days[-1] != day:
            if session_days and day < session_days[-1]:
                raise ValueError("session dates must be nondecreasing within a replay stream")
            session_days.append(day)
        current_session_index = len(session_days) - 1
        stream.append(bar)
        if len(stream) > 1:
            previous = stream[-2].candle
            same_session = _session_day(stream[-2]) == day
            interval_minutes = int(bar.timeframe[:-1])
            elapsed_seconds = (candle.timestamp - previous.timestamp).total_seconds()
            if same_session and elapsed_seconds > interval_minutes * 60:
                events.append(ReplayEvent(candle.timestamp, "data_gap",
                                          detail=f"missing interval before {candle.timestamp.isoformat()}"))
                for index, level in enumerate(tuple(liquidity_levels)):
                    if level.instrument_id != candle.instrument_id or level.timeframe != bar.timeframe:
                        continue
                    updated, kind = invalidate_levels_for_gap(level, candle.timestamp)
                    if kind:
                        liquidity_levels[index] = updated
                        events.append(ReplayEvent(candle.timestamp, kind,
                                                  detail=updated.unavailable_reason,
                                                  liquidity_level_id=level.level_id))
        if not candle.complete:
            for index, level in enumerate(tuple(liquidity_levels)):
                if level.instrument_id != candle.instrument_id or level.timeframe != bar.timeframe:
                    continue
                updated, kind = invalidate_levels_for_gap(
                    level, candle.timestamp, "incomplete_candle_during_sweep_window")
                if kind:
                    liquidity_levels[index] = updated
                    events.append(ReplayEvent(candle.timestamp, kind,
                                              detail=updated.unavailable_reason,
                                              liquidity_level_id=level.level_id))

        # Previous-period extrema become known at the current session open. They require
        # an explicit calendar so replay can distinguish complete history from a partial file.
        current_session = next((s for s in trading_sessions
                                if s.instrument_id == candle.instrument_id and s.session_date == day), None)
        new_session = len(stream) == 1 or _session_day(stream[-2]) != day
        if new_session:
            previous_sessions = sorted((s for s in trading_sessions
                                        if s.instrument_id == candle.instrument_id
                                        and s.session_date < day), key=lambda s: s.session_date)
            bars_by_time = {item.candle.timestamp: item.candle for item in stream
                            if _session_day(item) < day}
            if previous_sessions and not session_complete(previous_sessions[-1], bar.timeframe,
                                                          bars_by_time):
                for index, level in enumerate(tuple(liquidity_levels)):
                    if level.instrument_id != candle.instrument_id or level.timeframe != bar.timeframe:
                        continue
                    updated, kind = invalidate_levels_for_gap(
                        level, candle.timestamp, "prior_session_history_incomplete")
                    if kind:
                        liquidity_levels[index] = updated
                        events.append(ReplayEvent(candle.timestamp, kind,
                                                  detail=updated.unavailable_reason,
                                                  liquidity_level_id=level.level_id))
            elif not previous_sessions:
                for index, level in enumerate(tuple(liquidity_levels)):
                    if level.instrument_id != candle.instrument_id or level.timeframe != bar.timeframe:
                        continue
                    updated, kind = invalidate_levels_for_gap(
                        level, candle.timestamp, "session_calendar_missing")
                    if kind:
                        liquidity_levels[index] = updated
                        events.append(ReplayEvent(candle.timestamp, kind,
                                                  detail=updated.unavailable_reason,
                                                  liquidity_level_id=level.level_id))
            if current_session and previous_sessions and session_complete(
                    previous_sessions[-1], bar.timeframe, bars_by_time):
                expiry_time = current_session.opens_at
                current_week = day.isocalendar()[:2]
                for index, level in enumerate(tuple(liquidity_levels)):
                    if level.state != "unswept" or level.instrument_id != candle.instrument_id \
                            or level.timeframe != bar.timeframe:
                        continue
                    confirmed_day = level.confirmed_at.astimezone(_IST).date()
                    expires_daily = level.kind in ("pdh", "pdl", "opening_range_high", "opening_range_low") \
                        and confirmed_day < day
                    expires_weekly = level.kind in ("pwh", "pwl") \
                        and confirmed_day.isocalendar()[:2] != current_week
                    if expires_daily or expires_weekly:
                        liquidity_levels[index] = replace(level, state="expired", expired_at=expiry_time)
                        events.append(ReplayEvent(candle.timestamp, "liquidity_expired",
                                                  detail=level.kind, liquidity_level_id=level.level_id))
            if previous_sessions:
                prior = previous_sessions[-1]
                if current_session is not None and session_complete(prior, bar.timeframe, bars_by_time):
                    prior_bars = [bars_by_time[t] for t in expected_candle_timestamps(prior, bar.timeframe)]
                    for kind, price in (("pdh", max(c.high for c in prior_bars)),
                                        ("pdl", min(c.low for c in prior_bars))):
                        level = level_from_extreme(candle.instrument_id, bar.timeframe, kind,
                                                   price, prior.closes_at,
                                                   tuple(c.timestamp for c in prior_bars),
                                                   current_session.opens_at if current_session else candle.timestamp)
                        if level.level_id not in liquidity_ids:
                            liquidity_ids.add(level.level_id); liquidity_levels.append(level)
                            events.append(ReplayEvent(candle.timestamp, "liquidity_level_created",
                                                      detail=kind, liquidity_level_id=level.level_id))
                else:
                    key_notice = (candle.instrument_id, bar.timeframe, day, "previous_day_history_incomplete")
                    if key_notice not in liquidity_notice_keys:
                        liquidity_notice_keys.add(key_notice)
                        events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                                  detail="previous_day_history_incomplete"))
            else:
                key_notice = (candle.instrument_id, bar.timeframe, day, "previous_day_history_unavailable")
                if key_notice not in liquidity_notice_keys:
                    liquidity_notice_keys.add(key_notice)
                    events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                              detail="previous_day_history_unavailable"))

            if previous_sessions:
                current_week_start = day - timedelta(days=day.weekday())
                last_week = (current_week_start - timedelta(days=1)).isocalendar()[:2]
                week_sessions = [s for s in previous_sessions
                                 if s.session_date.isocalendar()[:2] == last_week]
                week_candles = [c for s in week_sessions
                                for t in expected_candle_timestamps(s, bar.timeframe)
                                if (c := bars_by_time.get(t)) is not None]
                complete_week = bool(week_sessions) and all(
                    session_complete(s, bar.timeframe, bars_by_time) for s in week_sessions)
                if current_session is not None and complete_week and week_candles:
                    for kind, price in (("pwh", max(c.high for c in week_candles)),
                                        ("pwl", min(c.low for c in week_candles))):
                        level = level_from_extreme(candle.instrument_id, bar.timeframe, kind,
                                                   price, week_sessions[-1].closes_at,
                                                   tuple(c.timestamp for c in week_candles),
                                                   current_session.opens_at if current_session else candle.timestamp)
                        if level.level_id not in liquidity_ids:
                            liquidity_ids.add(level.level_id); liquidity_levels.append(level)
                            events.append(ReplayEvent(candle.timestamp, "liquidity_level_created",
                                                      detail=kind, liquidity_level_id=level.level_id))
                else:
                    key_notice = (candle.instrument_id, bar.timeframe, day, "previous_week_history_incomplete")
                    if key_notice not in liquidity_notice_keys:
                        liquidity_notice_keys.add(key_notice)
                        events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                                  detail="previous_week_history_incomplete"))
            else:
                key_notice = (candle.instrument_id, bar.timeframe, day, "previous_week_history_unavailable")
                if key_notice not in liquidity_notice_keys:
                    liquidity_notice_keys.add(key_notice)
                    events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                              detail="previous_week_history_unavailable"))

        # Previously recognized levels see this completed candle; new swing/range levels
        # below cannot be swept by the bar that first made them knowable.
        for index, level in enumerate(tuple(liquidity_levels)):
            updated, kind = update_sweep(level, bar)
            if kind:
                liquidity_levels[index] = updated
                events.append(ReplayEvent(candle.timestamp, kind, detail=updated.state,
                                          liquidity_level_id=level.level_id))
            elif updated != level:
                liquidity_levels[index] = updated

        candles = tuple(item.candle for item in stream)
        swings = confirmed_swings(candles, swing_left, swing_right,
                                  decision_time=candle.timestamp)
        for swing in swings:
            swing_key = (candle.instrument_id, bar.timeframe, swing.kind, swing.timestamp)
            if swing_key not in all_swings:
                all_swings[swing_key] = swing
                events.append(ReplayEvent(swing.confirmed_at, "swing_confirmed",
                                          detail=f"{swing.kind}:{swing.price}"))
                level = level_from_swing(candle.instrument_id, bar.timeframe, swing)
                if level.level_id not in liquidity_ids:
                    liquidity_ids.add(level.level_id); liquidity_levels.append(level)
                if bar.timeframe == "5m":
                    equal, reason = equal_level_for_swing(candle.instrument_id, bar.timeframe,
                                                          swing, swings, bar.atr)
                    if equal is not None and equal.level_id not in liquidity_ids:
                        liquidity_ids.add(equal.level_id); liquidity_levels.append(equal)
                        events.append(ReplayEvent(candle.timestamp, "liquidity_level_created",
                                                  detail=equal.kind, liquidity_level_id=equal.level_id))
                    elif reason and any(old.kind == swing.kind and old.timestamp != swing.timestamp
                                        for old in swings):
                        key_notice = (candle.instrument_id, bar.timeframe, day, reason)
                        if key_notice not in liquidity_notice_keys:
                            liquidity_notice_keys.add(key_notice)
                            events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                                      detail=reason))
                elif any(old.kind == swing.kind and old.timestamp != swing.timestamp
                         for old in swings):
                    reason = "equal_levels_require_5m_bars_and_atr14_5m"
                    key_notice = (candle.instrument_id, bar.timeframe, day, reason)
                    if key_notice not in liquidity_notice_keys:
                        liquidity_notice_keys.add(key_notice)
                        events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                                  detail=reason))
                events.append(ReplayEvent(candle.timestamp, "liquidity_level_created",
                                          detail=level.kind, liquidity_level_id=level.level_id))

        # First-15-minute range is emitted only once its complete range has closed.
        opening_key = (candle.instrument_id, bar.timeframe, day)
        if current_session and opening_key not in processed_opening_ranges:
            opening_end = current_session.opens_at + timedelta(minutes=15)
            if candle.timestamp >= opening_end:
                expected = tuple(t for t in expected_candle_timestamps(current_session, bar.timeframe)
                                 if t <= opening_end)
                by_time = {item.candle.timestamp: item.candle for item in stream
                           if _session_day(item) == day}
                opening_bars = [by_time.get(t) for t in expected]
                expected_count = 15 // int(bar.timeframe[:-1])
                opening_fits_session = opening_end <= current_session.closes_at
                if (opening_fits_session and len(expected) == expected_count
                        and all(c is not None and c.complete for c in opening_bars)):
                    valid_opening = [c for c in opening_bars if c is not None]
                    for kind, price in (("opening_range_high", max(c.high for c in valid_opening)),
                                        ("opening_range_low", min(c.low for c in valid_opening))):
                        level = level_from_extreme(candle.instrument_id, bar.timeframe, kind,
                                                   price, current_session.opens_at,
                                                   tuple(c.timestamp for c in valid_opening), opening_end)
                        if level.level_id not in liquidity_ids:
                            liquidity_ids.add(level.level_id); liquidity_levels.append(level)
                            events.append(ReplayEvent(candle.timestamp, "liquidity_level_created",
                                                      detail=kind, liquidity_level_id=level.level_id))
                else:
                    events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                              detail="opening_range_history_incomplete"))
                processed_opening_ranges.add(opening_key)
        elif current_session is None and opening_key not in processed_opening_ranges:
            key_notice = (candle.instrument_id, bar.timeframe, day, "trading_session_calendar_missing")
            if key_notice not in liquidity_notice_keys:
                liquidity_notice_keys.add(key_notice)
                events.append(ReplayEvent(candle.timestamp, "liquidity_unavailable",
                                          detail="trading_session_calendar_missing"))

        # Existing zones see only later completed candles from their own timeframe.
        for index, zone in enumerate(tuple(zones)):
            if zone.instrument_id != candle.instrument_id or zone.timeframe != bar.timeframe:
                continue
            formed_index = zone_formation_sessions.get(zone.zone_id, current_session_index)
            updated = update_zone_lifecycle(zone, bar, formed_index,
                                            current_session_index, parameters)
            if updated != zone:
                zones[index] = updated
                if updated.state != zone.state:
                    events.append(ReplayEvent(candle.timestamp, "zone_state_changed",
                                              zone.zone_id, updated.state))
                elif updated.last_touched_at != zone.last_touched_at:
                    events.append(ReplayEvent(candle.timestamp, "zone_touched",
                                              zone.zone_id, updated.state))

        if candle.complete:
            candidates = detect_order_blocks(tuple(stream), swings, candle.timestamp, parameters)
            for candidate in candidates:
                if any(zone.zone_id == candidate.zone_id for zone in zones):
                    continue
                zones_after_resolution, accepted = resolve_zone_overlap(tuple(zones), candidate, parameters)
                zones = list(zones_after_resolution)
                if accepted is not None:
                    zone_formation_sessions[accepted.zone_id] = current_session_index
                    events.append(ReplayEvent(candle.timestamp, "zone_created",
                                              accepted.zone_id, accepted.state))
                else:
                    events.append(ReplayEvent(candle.timestamp, "zone_suppressed",
                                              candidate.zone_id, detail="overlap_precedence"))
            structure = _structure_if_warm(swings)
            direction = classify_direction(bar.day_return, structure,
                                           bar.price_above_vwap)
            nearest_zone = _nearest_supporting_zone(zones, direction, candle.close)
            score_inputs = ScoreInputs(
                day_return=bar.day_return,
                daily_sigma20=bar.daily_sigma20,
                rvol=bar.rvol,
                oi_change_daily_pct=bar.oi_change_daily_pct,
                direction=direction,
                price_above_vwap=bar.price_above_vwap,
                price_above_ema20=bar.price_above_ema20,
                structure=structure,
                sector=bar.sector_direction,
                current_price=candle.close,
                atr=bar.atr,
                nearest_zone=nearest_zone,
            )
            score = calculate_strength(score_inputs)
            choppy = _choppy_for_bar(bar, stream, swings, trading_sessions)
            filtered_strength = None
            if choppy.available:
                filtered_strength = (0.0 if choppy.is_choppy else score.strength)
            scores.append(ReplayScore(candle.instrument_id, candle.timestamp, score, direction,
                                      choppy, filtered_strength))
        else:
            unavailable = ScoreResult(
                available=False,
                strength=None,
                components={key: None for key in ("M", "V", "O", "T", "S", "Z")},
                reason="incomplete_candle",
                component_reasons={key: "incomplete_candle"
                                  for key in ("M", "V", "O", "T", "S", "Z")},
            )
            scores.append(ReplayScore(candle.instrument_id, candle.timestamp, unavailable,
                                      choppy=unavailable_choppy("incomplete_candle")))

    return ReplayResult(tuple(events), tuple(all_swings.values()), tuple(zones), tuple(scores),
                        tuple(liquidity_levels))
