"""Chart liquidity references and chronological sweep lifecycle helpers."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from hashlib import sha256

from .models import Candle, LiquidityLevel, ReplayBar, Swing, TradingSession


def _id(instrument_id: str, timeframe: str, kind: str,
        source_timestamps: tuple[datetime, ...], price: float) -> str:
    raw = "|".join((instrument_id, timeframe, kind,
                    *(stamp.isoformat() for stamp in source_timestamps), repr(price)))
    return sha256(raw.encode("utf-8")).hexdigest()[:24]


def level_from_swing(instrument_id: str, timeframe: str, swing: Swing) -> LiquidityLevel:
    kind = "swing_high" if swing.kind == "high" else "swing_low"
    side = "above" if swing.kind == "high" else "below"
    sources = (swing.timestamp,)
    return LiquidityLevel(_id(instrument_id, timeframe, kind, sources, swing.price),
                          instrument_id, timeframe, side, swing.price, kind,
                          swing.timestamp, swing.confirmed_at,
                          source_timestamps=sources)


def equal_level_for_swing(instrument_id: str, timeframe: str, swing: Swing,
                          confirmed: tuple[Swing, ...], atr: float | None
                          ) -> tuple[LiquidityLevel | None, str | None]:
    """Make one level from same-kind confirmed points within 0.1 current ATR."""
    if atr is None or atr <= 0:
        return None, "equal_levels_require_positive_atr14_5m"
    same_kind = [item for item in confirmed if item.kind == swing.kind
                 and item.confirmed_at <= swing.confirmed_at]
    members = [item for item in same_kind if abs(item.price - swing.price) <= .1 * atr]
    if len(members) < 2:
        return None, None
    # High pools use their outer high; low pools use their outer low.
    price = max(item.price for item in members) if swing.kind == "high" else min(item.price for item in members)
    sources = tuple(sorted((item.timestamp for item in members)))
    kind = "equal_high" if swing.kind == "high" else "equal_low"
    side = "above" if swing.kind == "high" else "below"
    return (LiquidityLevel(_id(instrument_id, timeframe, kind, sources, price),
                           instrument_id, timeframe, side, price, kind,
                           swing.timestamp, swing.confirmed_at,
                           source_timestamps=sources), None)


def level_from_extreme(instrument_id: str, timeframe: str, kind: str,
                       price: float, formed_at: datetime,
                       sources: tuple[datetime, ...],
                       confirmed_at: datetime | None = None) -> LiquidityLevel:
    side = "above" if kind.endswith(("high", "dh", "wh")) or kind in ("pdh", "pwh", "opening_range_high") else "below"
    return LiquidityLevel(_id(instrument_id, timeframe, kind, sources, price),
                          instrument_id, timeframe, side, price, kind,
                          formed_at, confirmed_at or formed_at, source_timestamps=sources)


def expected_candle_timestamps(session: TradingSession, timeframe: str) -> tuple[datetime, ...]:
    width = int(timeframe[:-1])
    total_minutes = int((session.closes_at - session.opens_at).total_seconds() // 60)
    if total_minutes <= 0 or total_minutes % width:
        return ()
    return tuple(session.opens_at + timedelta(minutes=width * i)
                 for i in range(1, total_minutes // width + 1))


def update_sweep(level: LiquidityLevel, bar: ReplayBar) -> tuple[LiquidityLevel, str | None]:
    """Update one already-known level using only this completed bar."""
    candle = bar.candle
    if (not candle.complete or level.state != "unswept" or
            level.instrument_id != candle.instrument_id or level.timeframe != bar.timeframe or
            candle.timestamp <= level.confirmed_at):
        return level, None
    if level.side == "above":
        excursion = candle.high > level.price
        returned = candle.close <= level.price
    else:
        excursion = candle.low < level.price
        returned = candle.close >= level.price

    if level.pending_candles:
        count = level.pending_candles + 1
        if returned:
            return replace(level, state="swept", swept_at=candle.timestamp,
                           pending_since=None, pending_candles=0), "liquidity_swept"
        if count >= 3:
            return replace(level, state="invalidated", invalidated_at=candle.timestamp,
                           pending_candles=count), "liquidity_invalidated"
        return replace(level, pending_candles=count), None
    if not excursion:
        return level, None
    if returned:
        return replace(level, state="swept", swept_at=candle.timestamp), "liquidity_swept"
    return replace(level, pending_since=candle.timestamp, pending_candles=1), None


def invalidate_levels_for_gap(level: LiquidityLevel, timestamp: datetime,
                              reason: str = "missing_candle_during_sweep_window") -> tuple[LiquidityLevel, str | None]:
    # A missing bar could have swept any still-active level, whether or not an
    # earlier visible candle had already started an excursion.
    if level.state != "unswept":
        return level, None
    return replace(level, state="unavailable", unavailable_at=timestamp,
                   unavailable_reason=reason), "liquidity_unavailable"


def session_complete(session: TradingSession, timeframe: str,
                     candles: dict[datetime, Candle]) -> bool:
    expected = expected_candle_timestamps(session, timeframe)
    return bool(expected) and all(stamp in candles and candles[stamp].complete for stamp in expected)
