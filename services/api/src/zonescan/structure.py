from __future__ import annotations

from collections import defaultdict

from .models import Candle, Swing


def confirmed_swings(candles: list[Candle] | tuple[Candle, ...], left: int = 3,
                     right: int = 3, decision_time=None) -> tuple[Swing, ...]:
    """Return only complete swings whose right-side confirmation is available."""
    if left < 1 or right < 1:
        raise ValueError("left and right must be positive")
    ordered = sorted(candles, key=lambda c: c.timestamp)
    if len({c.timestamp for c in ordered}) != len(ordered):
        raise ValueError("duplicate candle timestamps")
    result: list[Swing] = []
    for i in range(left, len(ordered) - right):
        window = ordered[i-left:i+right+1]
        center = ordered[i]
        if not all(c.complete for c in window):
            continue
        confirmed_at = ordered[i + right].timestamp
        if decision_time is not None and confirmed_at > decision_time:
            continue
        before, after = window[:left], window[left+1:]
        if all(center.high > c.high for c in before + after):
            result.append(Swing(i, center.timestamp, center.high, "high", confirmed_at))
        if all(center.low < c.low for c in before + after):
            result.append(Swing(i, center.timestamp, center.low, "low", confirmed_at))
    return tuple(result)


def structure_label(swings: tuple[Swing, ...]) -> str:
    highs = [s.price for s in swings if s.kind == "high"][-2:]
    lows = [s.price for s in swings if s.kind == "low"][-2:]
    if len(highs) < 2 or len(lows) < 2:
        return "range"
    if highs[1] > highs[0] and lows[1] > lows[0]:
        return "bullish"
    if highs[1] < highs[0] and lows[1] < lows[0]:
        return "bearish"
    return "range"


def break_of_structure(candles: tuple[Candle, ...], swings: tuple[Swing, ...]) -> tuple[tuple[int, str], ...]:
    """Completed closes crossing the latest confirmed swing available at that close."""
    results: list[tuple[int, str]] = []
    for i, candle in enumerate(candles):
        if not candle.complete:
            continue
        available = [s for s in swings if s.confirmed_at <= candle.timestamp]
        highs = [s for s in available if s.kind == "high"]
        lows = [s for s in available if s.kind == "low"]
        if highs and candle.close > highs[-1].price:
            results.append((i, "bullish"))
        elif lows and candle.close < lows[-1].price:
            results.append((i, "bearish"))
    return tuple(results)
