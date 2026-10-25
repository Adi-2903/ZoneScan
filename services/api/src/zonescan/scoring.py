from __future__ import annotations

from .models import ScoreInputs, ScoreResult


WEIGHTS = {"M": .25, "V": .15, "O": .20, "T": .20, "S": .10, "Z": .10}


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def calculate_strength(data: ScoreInputs) -> ScoreResult:
    required = (data.daily_sigma20, data.rvol, data.oi_change_daily_pct,
                data.price_above_vwap, data.price_above_ema20, data.structure, data.sector)
    if any(value is None for value in required):
        return ScoreResult(False, None, None, "required_input_missing")
    if data.daily_sigma20 <= 0:
        return ScoreResult(False, None, None, "daily_sigma_nonpositive")
    if data.direction not in ("bullish", "bearish"):
        return ScoreResult(False, None, None, "direction_unavailable")
    bullish = data.direction == "bullish"
    price_up = data.day_return > 0
    oi_up = data.oi_change_daily_pct > 0
    oi_factor = 1.0 if price_up == oi_up else 0.5
    m = min(abs(data.day_return) / (1.5 * data.daily_sigma20), 1.0)
    v = _clip((data.rvol - 1.0) / 2.0)
    o = min(abs(data.oi_change_daily_pct) / .05, 1.0) * oi_factor
    vwap_ok = data.price_above_vwap if bullish else not data.price_above_vwap
    ema_ok = data.price_above_ema20 if bullish else not data.price_above_ema20
    expected_structure = "bullish" if bullish else "bearish"
    structure_value = 1.0 if data.structure == expected_structure else (.5 if data.structure == "range" else 0.0)
    t = (float(vwap_ok) + float(ema_ok) + structure_value) / 3.0
    sector = data.sector
    s = 1.0 if sector == data.direction else (.5 if sector in ("neutral", "mixed") else 0.0)
    d = data.zone_distance_atr
    z = 0.0 if d is None or d >= 4 else (1.0 if d <= 1 else (4.0-d)/3.0)
    components = {"M": m, "V": v, "O": o, "T": t, "S": s, "Z": z}
    total = 100.0 * sum(WEIGHTS[key] * components[key] for key in WEIGHTS)
    return ScoreResult(True, round(total, 6), components)
