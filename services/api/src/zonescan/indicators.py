"""Deterministic point-in-time candle aggregation and indicator calculations."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from math import isfinite, sqrt
from statistics import fmean
from zoneinfo import ZoneInfo

from .models import (Candle, CandleAggregation, FuturesContractMapping,
                     IndicatorFrame, IndicatorValue, MissingCandleInterval,
                     OpenInterestObservation, ReplayBar, TradingSession)
from .scoring import calculate_oi_change_pct

IST = ZoneInfo("Asia/Kolkata")


def _value(value: float | bool | None, reason: str | None = None) -> IndicatorValue:
    return IndicatorValue(value is not None, value, None if value is not None else reason)


def _unavailable(reason: str) -> IndicatorValue:
    return IndicatorValue(False, None, reason)


def aggregate_candles(candles: tuple[Candle, ...] | list[Candle],
                      sessions: tuple[TradingSession, ...] | list[TradingSession],
                      timeframe: str) -> CandleAggregation:
    """Aggregate complete 1m candles into completed 5m/15m session windows.

    Source candle timestamps are interval starts; output timestamps are interval ends.
    A missing or incomplete constituent suppresses that aggregate and is reported.
    """
    if timeframe not in ("5m", "15m"):
        raise ValueError("timeframe must be 5m or 15m")
    minutes = int(timeframe[:-1])
    width = timedelta(minutes=minutes)
    by_identity: dict[tuple[str, datetime], Candle] = {}
    for candle in candles:
        if candle.timestamp.second or candle.timestamp.microsecond:
            raise ValueError("1m candle timestamp must be minute-aligned")
        key = candle.instrument_id, candle.timestamp
        if key in by_identity:
            raise ValueError("duplicate 1m candle")
        by_identity[key] = candle

    session_keys: set[tuple[str, object]] = set()
    covered_minutes: set[tuple[str, datetime]] = set()
    outputs: list[Candle] = []
    gaps: list[MissingCandleInterval] = []
    for session in sorted(sessions, key=lambda x: (x.opens_at, x.instrument_id)):
        key = session.instrument_id, session.session_date
        if key in session_keys:
            raise ValueError("duplicate trading session")
        session_keys.add(key)
        if session.opens_at.tzinfo is None or session.closes_at.tzinfo is None:
            raise ValueError("session boundaries must be timezone-aware")
        if session.opens_at.astimezone(IST).date() != session.session_date:
            raise ValueError("session date must match Asia/Kolkata open date")
        if session.closes_at <= session.opens_at or (session.closes_at - session.opens_at).total_seconds() % width.total_seconds():
            raise ValueError("session duration must be positive and divisible by timeframe")
        if session.opens_at.second or session.opens_at.microsecond:
            raise ValueError("session open must be minute-aligned")
        start = session.opens_at
        while start + width <= session.closes_at:
            end = start + width
            expected = tuple(start + timedelta(minutes=i) for i in range(minutes))
            covered_minutes.update((session.instrument_id, stamp) for stamp in expected)
            bucket = [by_identity.get((session.instrument_id, stamp)) for stamp in expected]
            missing = tuple(stamp for stamp, candle in zip(expected, bucket) if candle is None)
            incomplete = tuple(stamp for stamp, candle in zip(expected, bucket)
                               if candle is not None and not candle.complete)
            if missing or incomplete:
                reason = "missing_minute_candle" if missing else "incomplete_minute_candle"
                gaps.append(MissingCandleInterval(session.instrument_id, timeframe, end,
                                                  missing or incomplete, reason))
            else:
                valid = [c for c in bucket if c is not None]
                outputs.append(Candle(session.instrument_id, end, valid[0].open,
                                      max(c.high for c in valid), min(c.low for c in valid),
                                      valid[-1].close, sum(c.volume for c in valid), True,
                                      tuple(sorted({flag for c in valid for flag in c.quality_flags}
                                                   | {f"aggregated_{timeframe}"}))))
            start = end
    outside = set(by_identity) - covered_minutes
    if outside:
        raise ValueError("1m candle is outside declared trading sessions")
    outputs.sort(key=lambda c: (c.timestamp, c.instrument_id))
    gaps.sort(key=lambda g: (g.timestamp, g.instrument_id))
    return CandleAggregation(timeframe, tuple(outputs), tuple(gaps))


def _contract_for(instrument_id: str, day, mappings: tuple[FuturesContractMapping, ...]):
    matches = [m for m in mappings if m.underlying_instrument_id == instrument_id
               and m.valid_from <= day and (m.valid_through is None or day <= m.valid_through)]
    if len(matches) > 1:
        return None
    return matches[0] if matches else None


def _change(current: float | None, reference: float | None) -> IndicatorValue:
    result = calculate_oi_change_pct(current, reference)
    return _value(result.value) if result.available else _unavailable(result.reason or "oi_change_unavailable")


def calculate_indicators(aggregation: CandleAggregation,
                         sessions: tuple[TradingSession, ...] | list[TradingSession],
                         daily_candles: tuple[Candle, ...] | list[Candle] = (),
                         open_interest: tuple[OpenInterestObservation, ...] | list[OpenInterestObservation] = (),
                         contract_mappings: tuple[FuturesContractMapping, ...] | list[FuturesContractMapping] = ()) -> tuple[IndicatorFrame, ...]:
    """Calculate indicators chronologically; all observations are causal at frame time."""
    if aggregation.timeframe not in ("5m", "15m"):
        raise ValueError("aggregation timeframe must be 5m or 15m")
    step = timedelta(minutes=int(aggregation.timeframe[:-1]))
    session_list = sorted(sessions, key=lambda s: (s.opens_at, s.instrument_id))
    candles_by_key = {(c.instrument_id, c.timestamp): c for c in aggregation.candles}
    gaps_by_key = {(g.instrument_id, g.timestamp): g for g in aggregation.gaps}
    daily: dict[str, dict[object, Candle]] = defaultdict(dict)
    for candle in daily_candles:
        day = candle.timestamp.astimezone(IST).date()
        if day in daily[candle.instrument_id]:
            raise ValueError("duplicate daily candle for instrument and session date")
        daily[candle.instrument_id][day] = candle
    oi: dict[tuple[str, datetime], float] = {}
    for observation in open_interest:
        if observation.timestamp.tzinfo is None or not isfinite(observation.value) or observation.value < 0:
            raise ValueError("OI observations require aware timestamps and finite nonnegative values")
        key = observation.instrument_id, observation.timestamp
        if key in oi:
            raise ValueError("duplicate OI observation")
        oi[key] = observation.value
    frames: list[IndicatorFrame] = []
    for session in session_list:
        source = sorted((c for c in aggregation.candles if c.instrument_id == session.instrument_id
                         and session.opens_at < c.timestamp <= session.closes_at), key=lambda c: c.timestamp)
        gap_map = {g.timestamp: g for g in aggregation.gaps if g.instrument_id == session.instrument_id
                   and session.opens_at < g.timestamp <= session.closes_at}
        source_by_time = {c.timestamp: c for c in source}
        total_windows = int((session.closes_at - session.opens_at) / step)
        cumulative_volume = 0.0
        cumulative_pv = 0.0
        session_broken = False
        first_open = source_by_time.get(session.opens_at + step)
        previous_close: float | None = None
        tr_run: list[float] = []
        atr: float | None = None
        ema_closes: list[float] = []
        ema: float | None = None
        adx_tr: list[float] = []
        adx_plus: list[float] = []
        adx_minus: list[float] = []
        dx_run: list[float] = []
        adx: float | None = None
        for slot in range(1, total_windows + 1):
            stamp = session.opens_at + step * slot
            candle = source_by_time.get(stamp)
            reasons: list[str] = []
            if candle is None:
                gap = gap_map.get(stamp)
                reason = gap.reason if gap else "missing_aggregated_candle"
                reasons.append(reason)
                session_broken = True
                previous_close = None
                tr_run.clear(); atr = None; ema_closes.clear(); ema = None
                adx_tr.clear(); adx_plus.clear(); adx_minus.clear(); dx_run.clear(); adx = None
                unavailable = lambda: _unavailable(reason)
                frames.append(IndicatorFrame(session.instrument_id, stamp, aggregation.timeframe, None,
                    unavailable(), _unavailable("missing_daily_history"), unavailable(),
                    _unavailable("missing_session_volume_history"), _unavailable("missing_oi"),
                    _unavailable("missing_oi"), unavailable(), unavailable(), unavailable(),
                    unavailable(), unavailable(), tuple(reasons)))
                continue

            # ATR and ADX use only consecutive completed bars; a gap resets their warm-up.
            tr = candle.high - candle.low if previous_close is None else max(
                candle.high - candle.low, abs(candle.high - previous_close), abs(candle.low - previous_close))
            tr_run.append(tr)
            if len(tr_run) == 14:
                atr = fmean(tr_run)
            elif len(tr_run) > 14 and atr is not None:
                atr = (atr * 13 + tr) / 14
            prev = source_by_time.get(stamp - step)
            if prev is not None:
                up = candle.high - prev.high
                down = prev.low - candle.low
                plus = up if up > down and up > 0 else 0.0
                minus = down if down > up and down > 0 else 0.0
                adx_tr.append(tr); adx_plus.append(plus); adx_minus.append(minus)
                if len(adx_tr) >= 14:
                    if len(adx_tr) == 14:
                        smooth_tr, smooth_plus, smooth_minus = sum(adx_tr), sum(adx_plus), sum(adx_minus)
                    else:
                        smooth_tr = smooth_tr - smooth_tr / 14 + tr
                        smooth_plus = smooth_plus - smooth_plus / 14 + plus
                        smooth_minus = smooth_minus - smooth_minus / 14 + minus
                    if smooth_tr > 0:
                        pdi, mdi = 100 * smooth_plus / smooth_tr, 100 * smooth_minus / smooth_tr
                        dx_denom = pdi + mdi
                        if dx_denom > 0:
                            dx = 100 * abs(pdi - mdi) / dx_denom
                            dx_run.append(dx)
                            if len(dx_run) == 14:
                                adx = fmean(dx_run)
                            elif len(dx_run) > 14 and adx is not None:
                                adx = (adx * 13 + dx) / 14
            previous_close = candle.close
            ema_closes.append(candle.close)
            if len(ema_closes) == 20:
                ema = fmean(ema_closes)
            elif len(ema_closes) > 20 and ema is not None:
                ema = ema + (2 / 21) * (candle.close - ema)
            cumulative_volume += candle.volume
            cumulative_pv += candle.close * candle.volume
            vwap = cumulative_pv / cumulative_volume if cumulative_volume > 0 else None

            # Prior completed daily closes only; 20 returns require 21 closes.
            prior_session_dates = [s.session_date for s in session_list
                                    if s.instrument_id == session.instrument_id
                                    and s.session_date < session.session_date][-21:]
            prior_closes = [daily[session.instrument_id][day].close
                            for day in prior_session_dates
                            if day in daily[session.instrument_id]]
            sigma: float | None = None
            if len(prior_session_dates) == 21 and len(prior_closes) == 21:
                returns = [prior_closes[i] / prior_closes[i - 1] - 1 for i in range(1, 21)]
                sigma = sqrt(sum((x - fmean(returns)) ** 2 for x in returns) / (len(returns) - 1))
            day_return = (candle.close - first_open.open) / first_open.open if first_open else None

            # Same elapsed slot in each of the previous 20 supplied sessions.
            prior_sessions = [s for s in session_list if s.instrument_id == session.instrument_id
                              and s.session_date < session.session_date][-20:]
            baseline_totals: list[float] = []
            if len(prior_sessions) == 20 and not session_broken:
                valid_baseline = True
                for old in prior_sessions:
                    cumulative = 0.0
                    for old_slot in range(1, slot + 1):
                        old_candle = candles_by_key.get((old.instrument_id, old.opens_at + step * old_slot))
                        if old_candle is None:
                            valid_baseline = False; break
                        cumulative += old_candle.volume
                    if not valid_baseline: break
                    baseline_totals.append(cumulative)
            rvol_value = (cumulative_volume / fmean(baseline_totals)
                          if len(baseline_totals) == 20 and fmean(baseline_totals) > 0 else None)

            mapping = _contract_for(session.instrument_id, session.session_date, tuple(contract_mappings))
            oi_id = mapping.contract_instrument_id if mapping else None
            oi_current_time = stamp - timedelta(minutes=1)
            current_oi = oi.get((oi_id, oi_current_time)) if oi_id else None
            oi_30_ref = oi.get((oi_id, oi_current_time - timedelta(minutes=30))) if oi_id else None
            oi_30 = _change(current_oi, oi_30_ref) if oi_id else _unavailable("missing_contract_mapping")
            prior_session = next((s for s in reversed(session_list)
                                  if s.instrument_id == session.instrument_id
                                  and s.session_date < session.session_date), None)
            oi_daily = _unavailable("missing_contract_mapping")
            if mapping and prior_session:
                prior_mapping = _contract_for(session.instrument_id, prior_session.session_date,
                                              tuple(contract_mappings))
                if prior_mapping is None:
                    oi_daily = _unavailable("missing_contract_mapping")
                elif prior_mapping.contract_instrument_id != mapping.contract_instrument_id:
                    oi_daily = _unavailable("futures_contract_changed")
                else:
                    ref = oi.get((oi_id, prior_session.closes_at - timedelta(minutes=1)))
                    oi_daily = _change(current_oi, ref)
            elif mapping:
                oi_daily = _unavailable("missing_prior_session_oi")
            frames.append(IndicatorFrame(session.instrument_id, stamp, aggregation.timeframe, candle,
                _value(atr, "insufficient_history"),
                _value(sigma, "missing_daily_candle" if len(prior_session_dates) == 21
                       and len(prior_closes) < 21 else "insufficient_history"),
                _value(day_return, "missing_session_open_candle"),
                _value(rvol_value, "insufficient_or_missing_session_volume_history"),
                oi_daily, oi_30, _value(vwap, "zero_session_volume"),
                _value(candle.close >= vwap if vwap is not None else None, "zero_session_volume"),
                _value(ema, "insufficient_history"),
                _value(candle.close >= ema if ema is not None else None, "insufficient_history"),
                _value(adx, "insufficient_history_or_zero_directional_movement"), tuple(reasons)))
    return tuple(sorted(frames, key=lambda f: (f.timestamp, f.instrument_id)))


def to_replay_bars(frames: tuple[IndicatorFrame, ...],
                   sector_directions: dict[tuple[str, datetime], str] | None = None) -> tuple[ReplayBar, ...]:
    """Map available indicator values into existing replay inputs without imputing gaps."""
    result: list[ReplayBar] = []
    for frame in frames:
        if frame.candle is None:
            continue
        get = lambda name: getattr(frame, name).value if getattr(frame, name).available else None
        unavailable = tuple((name, getattr(frame, name).reason or f"missing_{name}")
                            for name in ("atr14", "daily_sigma20", "day_return", "rvol", "adx14",
                                         "oi_change_30m_pct")
                            if not getattr(frame, name).available)
        result.append(ReplayBar(frame.candle, get("atr14"), get("rvol"), frame.timeframe,
            frame.timestamp.astimezone(IST).date(), get("day_return"), get("daily_sigma20"),
            get("oi_change_daily_pct"), get("price_above_vwap"), get("price_above_ema20"),
            (sector_directions or {}).get((frame.instrument_id, frame.timestamp)),
            get("adx14"), unavailable,
            oi_change_30m_pct=get("oi_change_30m_pct")))
    return tuple(result)
