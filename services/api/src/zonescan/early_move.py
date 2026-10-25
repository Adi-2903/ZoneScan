from __future__ import annotations

from dataclasses import dataclass
from math import fsum, isfinite

from .models import ComponentResult, EarlyMoveResult
from .scoring import calculate_oi_component


WEIGHTS = {"OI_30m": 0.40, "Mom_15m": 0.35, "Burst_15m": 0.25}


@dataclass(frozen=True, slots=True)
class EarlyMoveInputs:
    direction: str | None
    day_return: float | None
    daily_sigma20: float | None
    oi_change_30m_pct: float | None
    current_price: float | None
    price_15m_ago: float | None
    atr14_5m: float | None
    current_volume_15m: float | None
    baseline_volume_15m: float | None
    unavailable_reasons: tuple[tuple[str, str], ...] = ()


def unavailable_early_move(reason: str) -> EarlyMoveResult:
    names = ("OI_30m", "Mom_15m", "Burst_15m", "RunPenalty")
    return EarlyMoveResult(False, None, {name: None for name in names},
                           {name: reason for name in names}, reason)


def _finite(value: float | None, name: str) -> ComponentResult | None:
    if value is None:
        return ComponentResult(False, None, f"missing_{name}")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ComponentResult(False, None, f"invalid_{name}_type")
    try:
        valid = isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        return ComponentResult(False, None, f"invalid_{name}_non_finite")
    return None


def calculate_momentum_15m(current_price: float | None,
                           price_15m_ago: float | None,
                           atr14_5m: float | None,
                           direction: str | None) -> ComponentResult:
    for value, name in ((current_price, "current_price"),
                        (price_15m_ago, "price_15m_ago"),
                        (atr14_5m, "atr14_5m")):
        invalid = _finite(value, name)
        if invalid:
            return invalid
    if current_price <= 0 or price_15m_ago <= 0:
        return ComponentResult(False, None, "prices_must_be_positive")
    if atr14_5m <= 0:
        return ComponentResult(False, None, "atr14_5m_must_be_positive")
    if direction not in ("bullish", "bearish"):
        return ComponentResult(False, None, "missing_direction")
    delta = current_price - price_15m_ago
    aligned = delta > 0 if direction == "bullish" else delta < 0
    if not aligned or delta == 0:
        return ComponentResult(True, 0.0, context="movement_not_aligned")
    return ComponentResult(True, min(abs(delta) / atr14_5m, 1.0))


def calculate_burst_15m(current_volume: float | None,
                        baseline_volume: float | None) -> ComponentResult:
    for value, name in ((current_volume, "current_volume_15m"),
                        (baseline_volume, "baseline_volume_15m")):
        invalid = _finite(value, name)
        if invalid:
            return invalid
    if current_volume < 0:
        return ComponentResult(False, None, "current_volume_15m_must_be_nonnegative")
    if baseline_volume <= 0:
        return ComponentResult(False, None, "baseline_volume_15m_must_be_positive")
    ratio = current_volume / baseline_volume
    return ComponentResult(True, min(1.0, max(0.0, (ratio - 1.0))))


def calculate_run_penalty(day_return: float | None,
                          daily_sigma20: float | None) -> ComponentResult:
    invalid = _finite(day_return, "day_return")
    if invalid:
        return invalid
    invalid = _finite(daily_sigma20, "daily_sigma20")
    if invalid:
        return invalid
    if daily_sigma20 <= 0:
        return ComponentResult(False, None, "daily_sigma20_must_be_positive")
    extension = abs(day_return) / daily_sigma20
    if extension <= 1.5:
        penalty = 0.0
    elif extension >= 3.0:
        penalty = 0.6
    else:
        penalty = 0.6 * (extension - 1.5) / 1.5
    return ComponentResult(True, penalty)


def calculate_early_move(data: EarlyMoveInputs) -> EarlyMoveResult:
    """Calculate Early-Move Score without modifying Strength Score inputs/results."""
    reasons = dict(data.unavailable_reasons)
    oi = calculate_oi_component(data.day_return, data.oi_change_30m_pct, data.direction)
    if not oi.available and oi.reason in reasons:
        oi = ComponentResult(False, None, reasons[oi.reason])
    momentum = calculate_momentum_15m(data.current_price, data.price_15m_ago,
                                     data.atr14_5m, data.direction)
    if not momentum.available and momentum.reason in reasons:
        momentum = ComponentResult(False, None, reasons[momentum.reason])
    burst = calculate_burst_15m(data.current_volume_15m,
                                data.baseline_volume_15m)
    if not burst.available and burst.reason in reasons:
        burst = ComponentResult(False, None, reasons[burst.reason])
    penalty = calculate_run_penalty(data.day_return, data.daily_sigma20)
    if not penalty.available and penalty.reason in reasons:
        penalty = ComponentResult(False, None, reasons[penalty.reason])

    results = {"OI_30m": oi, "Mom_15m": momentum,
               "Burst_15m": burst, "RunPenalty": penalty}
    components = {key: value.value if value.available else None
                  for key, value in results.items()}
    unavailable = {key: value.reason or "input_unavailable"
                   for key, value in results.items() if not value.available}
    if unavailable:
        return EarlyMoveResult(False, None, components, unavailable,
                               "required_component_unavailable")
    score = (100.0 * fsum(WEIGHTS[key] * components[key] for key in WEIGHTS)
             * (1.0 - penalty.value))
    return EarlyMoveResult(True, min(100.0, max(0.0, score)), components, {})
