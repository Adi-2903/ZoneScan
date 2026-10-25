from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from statistics import fmean
from zoneinfo import ZoneInfo

from .boards import build_board_snapshots, smooth_score
from .choppy import (candle_overlap_ratio, classify_choppy,
                     unavailable_choppy)
from .early_move import (EarlyMoveInputs, calculate_early_move,
                         unavailable_early_move)
from .liquidity import (equal_level_for_swing, expected_candle_timestamps,
                        invalidate_levels_for_gap, level_from_extreme,
                        level_from_swing, session_complete, update_sweep)
from .models import (BoardSnapshot, ChoppyResult, EarlyMoveResult, LiquidityLevel,
                     ReplayBar, ReplayEvent, ReplayScore,
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
    boards: tuple[BoardSnapshot, ...] = ()


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
                    bos_today: bool,
                    trading_sessions: tuple[TradingSession, ...] | list[TradingSession]
                    ) -> ChoppyResult:
    if not bar.candle.complete:
        return unavailable_choppy("incomplete_candle")
    if bar.timeframe != "5m":
        return unavailable_choppy("choppy_filter_requires_5m_replay")

    day = _session_day(bar)
    session_records = [item for item in stream if _session_day(item) == day]
    if len(session_records) < 12:
        overlap, overlap_reason = None, "insufficient_12_completed_5m_candles"
    else:
        overlap, overlap_reason = candle_overlap_ratio(
            tuple(item.candle for item in session_records[-12:]))

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


def _early_move_for_score(
        score: ReplayScore,
        bars_by_key: dict[tuple[str, str, datetime], ReplayBar],
        sessions_by_key: dict[tuple[str, date], TradingSession],
        prior_sessions_by_key: dict[tuple[str, date], tuple[TradingSession, ...]],
        ) -> EarlyMoveResult:
    if score.result.reason == "incomplete_candle":
        return unavailable_early_move("incomplete_candle")
    if score.timeframe != "5m":
        return unavailable_early_move("early_move_requires_5m_replay")
    current = bars_by_key.get((score.instrument_id, "5m", score.timestamp))
    if current is None or not current.candle.complete:
        return unavailable_early_move("incomplete_or_missing_5m_candle")
    at = score.timestamp
    current_day = _session_day(current)
    current_session = sessions_by_key.get((score.instrument_id, current_day))
    reasons: dict[str, str] = {}
    current_volume: float | None = None
    slot = 0

    previous = bars_by_key.get((score.instrument_id, "5m",
                                at - timedelta(minutes=15)))
    if previous is not None and _session_day(previous) != current_day:
        previous = None
    previous_price = previous.candle.close if previous and previous.candle.complete else None
    if previous_price is None:
        reasons["missing_price_15m_ago"] = "missing_or_incomplete_previous_15m_candle"

    atr = current.atr if current.candle.complete else None
    if atr is None:
        reasons["missing_atr14_5m"] = "missing_or_incomplete_aligned_5m_atr"

    baseline: float | None = None
    if current_session is None:
        reasons["missing_baseline_volume_15m"] = "missing_current_session_calendar"
        reasons["missing_current_volume_15m"] = "missing_current_session_calendar"
    else:
        elapsed = at - current_session.opens_at
        slot = int(elapsed.total_seconds() // timedelta(minutes=15).total_seconds())
        if at <= current_session.opens_at or at > current_session.closes_at:
            reasons["missing_baseline_volume_15m"] = "timestamp_outside_current_session"
            reasons["missing_current_volume_15m"] = "timestamp_outside_current_session"
        elif elapsed.total_seconds() % 300:
            reasons["missing_baseline_volume_15m"] = "timestamp_not_aligned_to_5m_session_slot"
            reasons["missing_current_volume_15m"] = "timestamp_not_aligned_to_5m_session_slot"
        elif slot < 1:
            reasons["missing_baseline_volume_15m"] = "no_completed_15m_volume_slot"
            reasons["missing_current_volume_15m"] = "no_completed_15m_volume_slot"
        else:
            period_end = current_session.opens_at + timedelta(minutes=15 * slot)

            def period_volume(session: TradingSession, end: datetime) -> float | None:
                start = end - timedelta(minutes=10)
                period_bars = [bars_by_key.get((score.instrument_id, "5m", stamp))
                               for stamp in (start, start + timedelta(minutes=5), end)]
                if any(bar is None or not bar.candle.complete
                       or _session_day(bar) != session.session_date
                       for bar in period_bars):
                    return None
                return sum(bar.candle.volume for bar in period_bars if bar is not None)

            current_volume = period_volume(current_session, period_end)
            if current_volume is None:
                reasons["missing_baseline_volume_15m"] = "missing_or_incomplete_current_15m_window"
                reasons["missing_current_volume_15m"] = "missing_or_incomplete_current_15m_window"
            prior_sessions = prior_sessions_by_key.get(
                (score.instrument_id, current_session.session_date), ())[-20:]
            if len(prior_sessions) < 20:
                reasons["missing_baseline_volume_15m"] = "insufficient_20_prior_sessions"
            elif current_volume is not None:
                reference_volumes: list[float] = []
                for session in prior_sessions:
                    reference_end = session.opens_at + timedelta(minutes=15 * slot)
                    if reference_end > session.closes_at:
                        reference_volumes = []
                        reasons["missing_baseline_volume_15m"] = "prior_session_slot_outside_session"
                        break
                    volume = period_volume(session, reference_end)
                    if volume is None:
                        reference_volumes = []
                        reasons["missing_baseline_volume_15m"] = "missing_prior_session_15m_volume"
                        break
                    reference_volumes.append(volume)
                if len(reference_volumes) == 20:
                    baseline = fmean(reference_volumes)
                    if baseline <= 0:
                        reasons["missing_baseline_volume_15m"] = "zero_prior_session_volume_baseline"
                        baseline = None

    unavailable = dict(current.indicator_unavailable_reasons)
    if current.oi_change_30m_pct is None:
        reasons["missing_oi_change_30m_pct"] = unavailable.get(
            "oi_change_30m_pct", "missing_oi_change_30m_pct")
    if current.day_return is None:
        reasons["missing_day_return"] = unavailable.get("day_return", "missing_day_return")
    if current.daily_sigma20 is None:
        reasons["missing_daily_sigma20"] = unavailable.get(
            "daily_sigma20", "missing_daily_sigma20")

    return calculate_early_move(EarlyMoveInputs(
        direction=score.direction,
        day_return=current.day_return,
        daily_sigma20=current.daily_sigma20,
        oi_change_30m_pct=current.oi_change_30m_pct,
        current_price=current.candle.close,
        price_15m_ago=previous_price,
        atr14_5m=atr,
        current_volume_15m=current_volume if current_session and slot >= 1 else None,
        baseline_volume_15m=baseline,
        unavailable_reasons=tuple(reasons.items())))


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
    previous_smoothed: dict[tuple[str, str, date], float] = {}
    session_bos_seen: set[tuple[str, str, date]] = set()
    symbols: dict[str, str] = {}
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
        if bar.symbol is not None:
            previous_symbol = symbols.setdefault(candle.instrument_id, bar.symbol)
            if previous_symbol != bar.symbol:
                raise ValueError("symbol mapping changed within replay")
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
        bos_key = (candle.instrument_id, bar.timeframe, day)
        if (candle.complete and bar.timeframe == "5m"
                and break_of_structure((candle,), swings)):
            session_bos_seen.add(bos_key)
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
            choppy = _choppy_for_bar(bar, stream, swings,
                                     bos_key in session_bos_seen, trading_sessions)
            filtered_strength = None
            if choppy.available:
                filtered_strength = (0.0 if choppy.is_choppy else score.strength)
            smoothing_key = (candle.instrument_id, bar.timeframe, day)
            prior = previous_smoothed.get(smoothing_key)
            smoothed = smooth_score(filtered_strength, prior)
            if smoothed is None:
                previous_smoothed.pop(smoothing_key, None)
            else:
                previous_smoothed[smoothing_key] = smoothed
            scores.append(ReplayScore(
                candle.instrument_id, candle.timestamp, score, direction,
                choppy, filtered_strength, smoothed, bar.rvol,
                candle.close * candle.volume if candle.complete else None,
                day, bar.timeframe))
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
                                      choppy=unavailable_choppy("incomplete_candle"),
                                      session_date=day, timeframe=bar.timeframe))

    bars_by_key = {(bar.candle.instrument_id, bar.timeframe, bar.candle.timestamp): bar
                   for bar in bars}
    sessions_by_key = {(session.instrument_id, session.session_date): session
                       for session in trading_sessions}
    sessions_by_instrument: dict[str, list[TradingSession]] = {}
    for session in trading_sessions:
        sessions_by_instrument.setdefault(session.instrument_id, []).append(session)
    prior_sessions_by_key = {
        key: tuple(sorted((session for session in values
                           if session.session_date < key[1]),
                          key=lambda session: session.session_date))
        for instrument_id, values in sessions_by_instrument.items()
        for key in ((instrument_id, session.session_date) for session in values)
    }
    scored = [replace(score, early_move=_early_move_for_score(
        score, bars_by_key, sessions_by_key, prior_sessions_by_key))
              for score in scores]
    boards = build_board_snapshots(scored, symbols)
    return ReplayResult(tuple(events), tuple(all_swings.values()), tuple(zones), tuple(scored),
                        tuple(liquidity_levels), boards)
