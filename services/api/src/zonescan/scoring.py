from __future__ import annotations

from math import fsum, isfinite
from types import MappingProxyType

from .models import ComponentResult, ScoreInputs, ScoreResult, Zone


WEIGHTS = MappingProxyType({"M": .25, "V": .15, "O": .20,
                            "T": .20, "S": .10, "Z": .10})


def _finite(value: float | None, name: str) -> ComponentResult | None:
    if value is None:
        return ComponentResult(False, None, f"missing_{name}")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return ComponentResult(False, None, f"invalid_{name}_type")
    try:
        finite = isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        return ComponentResult(False, None, f"invalid_{name}_non_finite")
    return None


def _unavailable(reason: str) -> ComponentResult:
    return ComponentResult(False, None, reason)


def calculate_move_component(day_return: float | None,
                             daily_sigma20: float | None) -> ComponentResult:
    """M = min(abs(return)/(1.5 * sigma), 1); returns and sigma are fractions."""
    invalid = _finite(day_return, "day_return")
    if invalid:
        return invalid
    invalid = _finite(daily_sigma20, "daily_sigma20")
    if invalid:
        return invalid
    if daily_sigma20 <= 0:
        return _unavailable("daily_sigma20_must_be_positive")
    return ComponentResult(True, min(abs(day_return) / (1.5 * daily_sigma20), 1.0))


def calculate_volume_component(rvol: float | None) -> ComponentResult:
    """V = clip((RVOL - 1)/2, 0, 1); RVOL is a nonnegative ratio."""
    invalid = _finite(rvol, "rvol")
    if invalid:
        return invalid
    if rvol < 0:
        return _unavailable("rvol_must_be_nonnegative")
    return ComponentResult(True, min(1.0, max(0.0, (rvol - 1.0) / 2.0)))


def calculate_oi_change_pct(current_oi: float | None,
                            reference_oi: float | None) -> ComponentResult:
    """Return fractional OI change; a zero/negative reference is not computable."""
    invalid = _finite(current_oi, "current_oi")
    if invalid:
        return invalid
    invalid = _finite(reference_oi, "reference_oi")
    if invalid:
        return invalid
    if current_oi < 0 or reference_oi <= 0:
        return _unavailable("oi_values_invalid_for_percentage_change")
    change = (current_oi - reference_oi) / reference_oi
    if not isfinite(change):
        return _unavailable("oi_percentage_change_non_finite")
    return ComponentResult(True, change)


def calculate_oi_component(day_return: float | None,
                           oi_change_daily_pct: float | None,
                           direction: str | None) -> ComponentResult:
    """O uses same-side price/OI context; OI changes are decimal fractions."""
    invalid = _finite(oi_change_daily_pct, "oi_change_daily_pct")
    if invalid:
        return invalid
    if oi_change_daily_pct == 0:
        return ComponentResult(True, 0.0, context="no_oi_change")
    invalid = _finite(day_return, "day_return")
    if invalid:
        return invalid
    if direction not in ("bullish", "bearish"):
        return _unavailable("invalid_direction")
    if day_return == 0:
        return _unavailable("price_direction_unavailable_for_oi_context")
    price_direction = "bullish" if day_return > 0 else "bearish"
    if price_direction != direction:
        return _unavailable("price_direction_mismatch")

    magnitude = min(abs(oi_change_daily_pct) / .05, 1.0)
    if oi_change_daily_pct > 0:
        context = "long_buildup" if price_direction == "bullish" else "short_buildup"
        factor = 1.0
    else:
        context = "short_covering" if price_direction == "bullish" else "long_unwinding"
        factor = .5
    return ComponentResult(True, magnitude * factor, context=context)


def calculate_trend_component(direction: str | None,
                              price_above_vwap: bool | None,
                              price_above_ema20: bool | None,
                              structure: str | None) -> ComponentResult:
    """Average VWAP side, EMA side, and documented structure alignment value."""
    for value, name in ((price_above_vwap, "price_above_vwap"),
                        (price_above_ema20, "price_above_ema20")):
        if value is None:
            return _unavailable(f"missing_{name}")
        if type(value) is not bool:
            return _unavailable(f"invalid_{name}")
    if structure is None:
        return _unavailable("missing_structure")
    if structure not in ("bullish", "bearish", "range"):
        return _unavailable("invalid_structure")
    if direction not in ("bullish", "bearish"):
        return _unavailable("invalid_direction")
    up = direction == "bullish"
    vwap = price_above_vwap == up
    ema = price_above_ema20 == up
    structure_value = 1.0 if structure == direction else (.5 if structure == "range" else 0.0)
    return ComponentResult(True, (float(vwap) + float(ema) + structure_value) / 3.0)


def calculate_sector_component(direction: str | None,
                               sector: str | None) -> ComponentResult:
    if sector is None:
        return _unavailable("missing_sector_classification")
    if direction not in ("bullish", "bearish"):
        return _unavailable("invalid_direction")
    if sector in ("neutral", "mixed"):
        return ComponentResult(True, .5)
    if sector not in ("bullish", "bearish"):
        return _unavailable("invalid_sector_classification")
    return ComponentResult(True, 1.0 if sector == direction else 0.0)


def classify_direction(day_return: float | None, structure: str | None,
                       price_above_vwap: bool | None) -> str | None:
    """Classify using signed return plus structure; neutral differs from unavailable."""
    if _finite(day_return, "day_return") is not None:
        return None
    if structure not in ("bullish", "bearish", "range"):
        return None
    if price_above_vwap is not None and type(price_above_vwap) is not bool:
        return None
    if day_return > 0 and (structure == "bullish" or
                           (structure == "range" and price_above_vwap is True)):
        return "bullish"
    if day_return < 0 and (structure == "bearish" or
                           (structure == "range" and price_above_vwap is False)):
        return "bearish"
    if structure == "range" and price_above_vwap is None:
        return None
    return "neutral"


def calculate_zone_component(direction: str | None,
                             current_price: float | None,
                             atr: float | None,
                             zone: Zone | None) -> ComponentResult:
    """Score the nearest active supporting zone; no eligible zone contributes zero."""
    if zone is None:
        return ComponentResult(True, 0.0, context="no_qualifying_zone")
    if direction not in ("bullish", "bearish"):
        return _unavailable("invalid_direction")
    if not zone.active or zone.state not in ("fresh", "tested"):
        return ComponentResult(True, 0.0, context="zone_not_active")
    if zone.side != direction:
        return ComponentResult(True, 0.0, context="zone_direction_mismatch")
    invalid = _finite(zone.low, "zone_low")
    if invalid:
        return invalid
    invalid = _finite(zone.high, "zone_high")
    if invalid:
        return invalid
    if zone.low <= 0 or zone.high < zone.low:
        return _unavailable("invalid_zone_bounds")
    invalid = _finite(current_price, "current_price")
    if invalid:
        return invalid
    invalid = _finite(atr, "atr")
    if invalid:
        return invalid
    if current_price <= 0:
        return _unavailable("current_price_must_be_positive")
    if atr <= 0:
        return _unavailable("atr_must_be_positive")

    if zone.low <= current_price <= zone.high:
        distance_atr = 0.0
    elif direction == "bullish":
        if zone.high > current_price:
            return ComponentResult(True, 0.0, context="zone_not_below_or_containing_price")
        distance_atr = (current_price - zone.high) / atr
    else:
        if zone.low < current_price:
            return ComponentResult(True, 0.0, context="zone_not_above_or_containing_price")
        distance_atr = (zone.low - current_price) / atr

    if distance_atr <= 1.0:
        value = 1.0
    elif distance_atr >= 4.0:
        value = 0.0
    else:
        value = (4.0 - distance_atr) / 3.0
    return ComponentResult(True, value)


def calculate_strength(data: ScoreInputs) -> ScoreResult:
    """Calculate the fixed-weight score or preserve each unavailable component."""
    results = {
        "M": calculate_move_component(data.day_return, data.daily_sigma20),
        "V": calculate_volume_component(data.rvol),
        "O": calculate_oi_component(data.day_return, data.oi_change_daily_pct,
                                     data.direction),
        "T": calculate_trend_component(data.direction, data.price_above_vwap,
                                        data.price_above_ema20, data.structure),
        "S": calculate_sector_component(data.direction, data.sector),
        "Z": calculate_zone_component(data.direction, data.current_price,
                                      data.atr, data.nearest_zone),
    }
    components = {name: result.value if result.available else None
                  for name, result in results.items()}
    reasons = {name: result.reason for name, result in results.items()
               if not result.available and result.reason is not None}
    contexts = {name: result.context for name, result in results.items()
                if result.context is not None}
    if reasons:
        return ScoreResult(False, None, components,
                           "required_component_unavailable", reasons, contexts)
    raw = 100.0 * fsum(WEIGHTS[name] * components[name] for name in WEIGHTS)
    # Clip only binary floating-point boundary noise; all component values remain raw.
    score = min(100.0, max(0.0, raw))
    return ScoreResult(True, score, components, component_contexts=contexts)
