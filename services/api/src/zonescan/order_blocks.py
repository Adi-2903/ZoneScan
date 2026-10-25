from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from hashlib import sha256
from math import isfinite
from zoneinfo import ZoneInfo

from .models import ReplayBar, Swing, Zone


@dataclass(frozen=True, slots=True)
class OrderBlockParameters:
    displacement_atr_multiple: float = 1.5
    minimum_mean_rvol: float = 1.2
    maximum_displacement_bars: int = 3
    maximum_active_per_side: int = 3
    expiry_sessions: int = 5
    algorithm_version: str = "v0.1-ob"
    parameter_version: str = "2026-10-26.2"

    def __post_init__(self) -> None:
        if not isfinite(self.displacement_atr_multiple) or self.displacement_atr_multiple <= 0:
            raise ValueError("displacement_atr_multiple must be positive and finite")
        if not isfinite(self.minimum_mean_rvol) or self.minimum_mean_rvol < 0:
            raise ValueError("minimum_mean_rvol must be nonnegative and finite")
        if not 1 <= self.maximum_displacement_bars <= 3:
            raise ValueError("maximum_displacement_bars must be between 1 and 3")
        if self.maximum_active_per_side < 1 or self.expiry_sessions < 1:
            raise ValueError("active-zone cap and expiry sessions must be positive")
        if not self.algorithm_version or not self.parameter_version:
            raise ValueError("algorithm and parameter versions are required")


def _stable_zone_id(instrument_id: str, side: str, timeframe: str,
                    formed_at: datetime, origin_at: datetime) -> str:
    raw = f"{instrument_id}|{side}|{timeframe}|{formed_at.isoformat()}|{origin_at.isoformat()}"
    return sha256(raw.encode("utf-8")).hexdigest()[:24]


def _has_fvg(run: tuple[ReplayBar, ...], side: str) -> bool:
    # A three-candle FVG is the non-overlap between candle 1 and candle 3.
    for first, _, third in zip(run, run[1:], run[2:]):
        if side == "bullish" and first.candle.high < third.candle.low:
            return True
        if side == "bearish" and first.candle.low > third.candle.high:
            return True
    return False


def detect_order_blocks(history: tuple[ReplayBar, ...],
                        swings: tuple[Swing, ...],
                        current_timestamp: datetime,
                        parameters: OrderBlockParameters = OrderBlockParameters()
                        ) -> tuple[Zone, ...]:
    """Find candidates ending now; all bars and required inputs must be complete."""
    if not history:
        return ()
    end = len(history) - 1
    endpoint = history[end]
    if endpoint.candle.timestamp != current_timestamp or not endpoint.candle.complete:
        return ()
    candidates: list[tuple[int, Zone]] = []
    max_len = min(parameters.maximum_displacement_bars, 3)
    for length in range(1, max_len + 1):
        start = end - length + 1
        origin_index = start - 1
        if origin_index < 0:
            continue
        run = history[start:end + 1]
        origin = history[origin_index]
        if not all(bar.candle.complete for bar in run + (origin,)):
            continue
        if any(bar.candle.instrument_id != endpoint.candle.instrument_id or
               bar.timeframe != endpoint.timeframe for bar in run + (origin,)):
            continue
        if any(bar.atr is None or bar.rvol is None for bar in run):
            continue
        if any(bar.atr <= 0 or bar.rvol < 0 for bar in run):
            continue
        bullish = all(bar.candle.close > bar.candle.open for bar in run)
        bearish = all(bar.candle.close < bar.candle.open for bar in run)
        if not (bullish or bearish):
            continue
        side = "bullish" if bullish else "bearish"
        if (bullish and not origin.candle.close < origin.candle.open) or \
           (bearish and not origin.candle.close > origin.candle.open):
            continue
        width = max(bar.candle.high for bar in run) - min(bar.candle.low for bar in run)
        atr = run[-1].atr
        if width < parameters.displacement_atr_multiple * atr:
            continue
        if sum(bar.rvol for bar in run) / length < parameters.minimum_mean_rvol:
            continue
        eligible = [s for s in swings if s.kind == ("high" if bullish else "low")
                    and s.confirmed_at <= origin.candle.timestamp]
        if not eligible:
            continue
        swing = max(eligible, key=lambda s: s.confirmed_at)
        closes_beyond = (run[-1].candle.close > swing.price if bullish
                         else run[-1].candle.close < swing.price)
        if not closes_beyond:
            continue
        candidates.append((length, Zone(
            zone_id=_stable_zone_id(endpoint.candle.instrument_id, side,
                                    endpoint.timeframe, endpoint.candle.timestamp,
                                    origin.candle.timestamp),
            instrument_id=endpoint.candle.instrument_id,
            side=side,
            low=origin.candle.low,
            high=origin.candle.high,
            timeframe=endpoint.timeframe,
            formed_at=endpoint.candle.timestamp,
            recognized_at=current_timestamp,
            has_fvg=_has_fvg(run, side),
            algorithm_version=parameters.algorithm_version,
            parameter_version=parameters.parameter_version,
        )))
    # The longest qualifying run ending now represents the full displacement.
    if not candidates:
        return ()
    return (max(candidates, key=lambda item: (item[0], item[1].zone_id))[1],)


def _session_day(bar: ReplayBar) -> date:
    return bar.session_date or bar.candle.timestamp.astimezone(ZoneInfo("Asia/Kolkata")).date()


def update_zone_lifecycle(zone: Zone, bar: ReplayBar, formed_session_index: int,
                          current_session_index: int,
                          parameters: OrderBlockParameters = OrderBlockParameters()
                          ) -> Zone:
    """Apply one later completed candle. Missing time is never filled synthetically."""
    candle = bar.candle
    if not candle.complete or candle.instrument_id != zone.instrument_id:
        return zone
    if candle.timestamp <= zone.formed_at or zone.state in ("mitigated", "expired"):
        return zone
    if zone.side == "bullish" and candle.close < zone.low:
        return replace(zone, state="mitigated", last_touched_at=candle.timestamp, active=False)
    if zone.side == "bearish" and candle.close > zone.high:
        return replace(zone, state="mitigated", last_touched_at=candle.timestamp, active=False)
    intersects = candle.low <= zone.high and candle.high >= zone.low
    if intersects and zone.state == "fresh":
        return replace(zone, state="tested", last_touched_at=candle.timestamp)
    if zone.state == "fresh" and current_session_index - formed_session_index >= parameters.expiry_sessions:
        return replace(zone, state="expired", expired_at=candle.timestamp, active=False)
    return zone


def resolve_zone_overlap(zones: tuple[Zone, ...], candidate: Zone,
                         parameters: OrderBlockParameters = OrderBlockParameters()
                         ) -> tuple[tuple[Zone, ...], Zone | None]:
    """Positive-width overlap; 15m wins, otherwise preserve older active zones up to cap."""
    active = list(zones)
    overlaps = [z for z in active if z.active and z.instrument_id == candidate.instrument_id
                and z.side == candidate.side and z.low < candidate.high and candidate.low < z.high]
    if candidate.timeframe == "5m" and any(z.timeframe == "15m" for z in overlaps):
        return zones, None
    if candidate.timeframe == "15m":
        active = [replace(z, active=False) if z in overlaps and z.timeframe == "5m" else z
                  for z in active]
    active.append(candidate)
    siblings = [z for z in active if z.active and z.instrument_id == candidate.instrument_id
                and z.side == candidate.side]
    while len(siblings) > parameters.maximum_active_per_side:
        oldest = min(siblings, key=lambda z: (z.formed_at, z.zone_id))
        active = [replace(z, active=False) if z.zone_id == oldest.zone_id else z for z in active]
        siblings.remove(oldest)
    return tuple(active), candidate
