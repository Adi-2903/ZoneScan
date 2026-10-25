from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .models import ReplayBar, ReplayEvent, ReplayScore, ScoreInputs, ScoreResult, Swing, Zone
from .order_blocks import (OrderBlockParameters, _session_day,
                           detect_order_blocks, resolve_zone_overlap,
                           update_zone_lifecycle)
from .scoring import calculate_strength, classify_direction
from .structure import confirmed_swings, structure_label


@dataclass(frozen=True, slots=True)
class ReplayResult:
    events: tuple[ReplayEvent, ...]
    swings: tuple[Swing, ...]
    zones: tuple[Zone, ...]
    scores: tuple[ReplayScore, ...]


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


def replay(bars: tuple[ReplayBar, ...] | list[ReplayBar],
           parameters: OrderBlockParameters = OrderBlockParameters(),
           swing_left: int = 3, swing_right: int = 3) -> ReplayResult:
    """Replay chronologically with a prefix-only view for every decision."""
    history: dict[tuple[str, str], list[ReplayBar]] = {}
    sessions: dict[tuple[str, str], list[date]] = {}
    zones: list[Zone] = []
    scores: list[ReplayScore] = []
    zone_formation_sessions: dict[str, int] = {}
    events: list[ReplayEvent] = []
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
        candles = tuple(item.candle for item in stream)
        swings = confirmed_swings(candles, swing_left, swing_right,
                                  decision_time=candle.timestamp)
        for swing in swings:
            swing_key = (candle.instrument_id, bar.timeframe, swing.kind, swing.timestamp)
            if swing_key not in all_swings:
                all_swings[swing_key] = swing
                events.append(ReplayEvent(swing.confirmed_at, "swing_confirmed",
                                          detail=f"{swing.kind}:{swing.price}"))

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
            scores.append(ReplayScore(candle.instrument_id, candle.timestamp,
                                      calculate_strength(score_inputs), direction))
        else:
            unavailable = ScoreResult(
                available=False,
                strength=None,
                components={key: None for key in ("M", "V", "O", "T", "S", "Z")},
                reason="incomplete_candle",
                component_reasons={key: "incomplete_candle"
                                  for key in ("M", "V", "O", "T", "S", "Z")},
            )
            scores.append(ReplayScore(candle.instrument_id, candle.timestamp, unavailable))

    return ReplayResult(tuple(events), tuple(all_swings.values()), tuple(zones), tuple(scores))
