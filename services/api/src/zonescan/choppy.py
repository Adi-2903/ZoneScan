"""Point-in-time evaluation of the documented Choppy conditions."""
from __future__ import annotations

from math import isfinite
from statistics import fmean
from zoneinfo import ZoneInfo

from .models import Candle, ChoppyResult

IST = ZoneInfo("Asia/Kolkata")
CONDITIONS = (
    "adx_below_18",
    "return_below_half_daily_sigma",
    "rvol_below_1",
    "overlap_above_70_without_session_bos",
)


def candle_overlap_ratio(candles: tuple[Candle, ...] | list[Candle]) -> tuple[float | None, str | None]:
    """Mean adjacent range-intersection ratio for exactly 12 complete 5m candles.

    Each pair contributes intersection length divided by the smaller candle range.
    A pair containing a zero-range candle contributes zero. Adjacent candles must be
    exactly five minutes apart and belong to the same Asia/Kolkata session date.
    """
    if len(candles) != 12:
        return None, "insufficient_12_completed_5m_candles"
    if any(not candle.complete for candle in candles):
        return None, "incomplete_candle_in_overlap_window"
    ordered = tuple(candles)
    for previous, current in zip(ordered, ordered[1:]):
        if current.instrument_id != previous.instrument_id:
            return None, "mixed_instruments_in_overlap_window"
        if current.timestamp.astimezone(IST).date() != previous.timestamp.astimezone(IST).date():
            return None, "session_boundary_in_overlap_window"
        if (current.timestamp - previous.timestamp).total_seconds() != 300:
            return None, "missing_candle_in_overlap_window"

    ratios: list[float] = []
    for previous, current in zip(ordered, ordered[1:]):
        previous_range = previous.high - previous.low
        current_range = current.high - current.low
        denominator = min(previous_range, current_range)
        if denominator <= 0:
            ratios.append(0.0)
            continue
        intersection = max(0.0, min(previous.high, current.high) - max(previous.low, current.low))
        ratios.append(min(1.0, intersection / denominator))
    return fmean(ratios), None


def unavailable_choppy(reason: str) -> ChoppyResult:
    return ChoppyResult(False, None, {name: None for name in CONDITIONS},
                        {name: reason for name in CONDITIONS}, reason=reason)


def classify_choppy(adx14: float | None, day_return: float | None,
                    daily_sigma20: float | None, rvol: float | None,
                    overlap_ratio: float | None, no_session_bos: bool | None,
                    unavailable_reasons: dict[str, str] | None = None,
                    overlap_reason: str | None = None,
                    bos_reason: str | None = None) -> ChoppyResult:
    """Apply the four strict-boundary conditions and resolve only determinate outcomes."""
    supplied_reasons = unavailable_reasons or {}
    values: dict[str, bool | None] = {}
    reasons: dict[str, str] = {}

    def metric(value: float | None, name: str, predicate, *, minimum: float | None = None,
               maximum: float | None = None, default_reason: str | None = None) -> bool | None:
        if value is None:
            reasons[name] = supplied_reasons.get(name, default_reason or f"missing_{name}")
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            reasons[name] = f"invalid_{name}"
            return None
        if (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
            reasons[name] = f"invalid_{name}_range"
            return None
        return predicate(value)

    values[CONDITIONS[0]] = metric(adx14, "adx14", lambda value: value < 18,
                                   minimum=0, maximum=100,
                                   default_reason=supplied_reasons.get("adx14"))

    invalid_return = False
    invalid_sigma = False
    if day_return is None:
        reasons[CONDITIONS[1]] = supplied_reasons.get("day_return", "missing_day_return")
        invalid_return = True
    elif isinstance(day_return, bool) or not isinstance(day_return, (int, float)) or not isfinite(day_return):
        reasons[CONDITIONS[1]] = "invalid_day_return"
        invalid_return = True
    if daily_sigma20 is None:
        reasons.setdefault(CONDITIONS[1], supplied_reasons.get("daily_sigma20", "missing_daily_sigma20"))
        invalid_sigma = True
    elif (isinstance(daily_sigma20, bool) or not isinstance(daily_sigma20, (int, float))
          or not isfinite(daily_sigma20) or daily_sigma20 < 0):
        reasons[CONDITIONS[1]] = "invalid_daily_sigma20"
        invalid_sigma = True
    values[CONDITIONS[1]] = (None if invalid_return or invalid_sigma else
                             abs(day_return) < .5 * daily_sigma20)

    values[CONDITIONS[2]] = metric(rvol, "rvol", lambda value: value < 1,
                                   minimum=0, default_reason=supplied_reasons.get("rvol"))

    overlap_condition = metric(overlap_ratio, "overlap_ratio", lambda value: value > .70,
                               minimum=0, maximum=1, default_reason=overlap_reason or "missing_overlap_ratio")
    overlap_value_reason = reasons.pop("overlap_ratio", None)
    if overlap_condition is False:
        values[CONDITIONS[3]] = False
    elif no_session_bos is False:
        values[CONDITIONS[3]] = False
    elif overlap_condition is None:
        values[CONDITIONS[3]] = None
        reasons[CONDITIONS[3]] = overlap_reason or overlap_value_reason or "overlap_unavailable"
    elif no_session_bos is None:
        values[CONDITIONS[3]] = None
        reasons[CONDITIONS[3]] = bos_reason or "session_bos_status_unavailable"
    elif type(no_session_bos) is bool:
        values[CONDITIONS[3]] = overlap_condition and no_session_bos
    else:
        values[CONDITIONS[3]] = None
        reasons[CONDITIONS[3]] = "invalid_session_bos_status"

    satisfied = tuple(name for name in CONDITIONS if values[name] is True)
    unknown_count = sum(value is None for value in values.values())
    if len(satisfied) >= 2:
        return ChoppyResult(True, True, values, reasons, overlap_ratio,
                            satisfied_conditions=satisfied)
    if len(satisfied) + unknown_count < 2:
        return ChoppyResult(True, False, values, reasons, overlap_ratio,
                            satisfied_conditions=satisfied)
    return ChoppyResult(False, None, values, reasons, overlap_ratio,
                        reason="insufficient_inputs_to_classify_choppy",
                        satisfied_conditions=satisfied)
