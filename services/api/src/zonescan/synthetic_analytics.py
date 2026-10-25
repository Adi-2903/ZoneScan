"""Deterministic synthetic history for the local analytical API only."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from math import pi, sin
from zoneinfo import ZoneInfo

from .models import (Candle, FuturesContractMapping, Instrument,
                     OpenInterestObservation, TradingSession)


IST = ZoneInfo("Asia/Kolkata")
FIXTURE_AS_OF = datetime(2026, 10, 26, 15, 30, tzinfo=IST)


@dataclass(frozen=True, slots=True)
class SyntheticAnalyticsDataset:
    instruments: tuple[Instrument, ...]
    one_minute_candles: tuple[Candle, ...]
    daily_candles: tuple[Candle, ...]
    sessions: tuple[TradingSession, ...]
    open_interest: tuple[OpenInterestObservation, ...]
    contract_mappings: tuple[FuturesContractMapping, ...]
    sector_directions: dict[tuple[str, datetime], str]
    source: str = "deterministic_synthetic_fixture"
    data_status: str = "synthetic"


def _fixture_dates(count: int = 22) -> tuple[date, ...]:
    days: list[date] = []
    day = FIXTURE_AS_OF.date()
    while len(days) < count:
        if day.weekday() < 5:
            days.append(day)
        day -= timedelta(days=1)
    return tuple(reversed(days))


def build_synthetic_analytics_dataset() -> SyntheticAnalyticsDataset:
    """Create complete, visibly synthetic sessions with opposing directional paths.

    This is a hand-authored demo fixture. Its generated observations do not describe
    actual exchange prices, OI, sector data, or historical performance.
    """
    instruments = (
        Instrument("SYN-BULL", "SYNBULL", "Synthetic Fixture Sector"),
        Instrument("SYN-BEAR", "SYNBEAR", "Synthetic Fixture Sector"),
    )
    dates = _fixture_dates()
    minute_candles: list[Candle] = []
    daily_candles: list[Candle] = []
    sessions: list[TradingSession] = []
    oi_observations: list[OpenInterestObservation] = []
    mappings: list[FuturesContractMapping] = []
    sectors: dict[tuple[str, datetime], str] = {}

    for instrument, direction, initial_price in (
            (instruments[0], 1.0, 100.0), (instruments[1], -1.0, 200.0)):
        previous_close = initial_price
        previous_oi_close = 100_000.0
        contract_id = f"{instrument.instrument_id}-FUT"
        mappings.append(FuturesContractMapping(instrument.instrument_id, contract_id,
                                               dates[0], dates[-1]))
        for session_index, session_day in enumerate(dates):
            opens_at = datetime.combine(session_day, time(9, 15), IST)
            closes_at = opens_at + timedelta(minutes=375)
            session = TradingSession(instrument.instrument_id, session_day,
                                     opens_at, closes_at)
            sessions.append(session)
            daily_fraction = direction * (0.0025 + 0.00035 * (session_index % 5))
            if session_index == len(dates) - 1:
                daily_fraction = direction * 0.008
            oi_daily_factor = 1.003 + 0.0002 * (session_index % 3)
            oi_start = previous_oi_close * oi_daily_factor
            final_close = previous_close
            last_center = previous_close
            for minute_index in range(375):
                timestamp = opens_at + timedelta(minutes=minute_index)
                progress = (minute_index + 1) / 375
                trend_fraction = daily_fraction * progress
                wave_fraction = 0.00065 * sin(2 * pi * minute_index / 24)
                center = previous_close * (1 + trend_fraction + wave_fraction)
                candle_open = last_center
                candle_close = center
                wick = previous_close * 0.00018
                high = max(candle_open, candle_close) + wick
                low = min(candle_open, candle_close) - wick
                volume = 140.0 if session_index == len(dates) - 1 else 100.0
                minute_candles.append(Candle(
                    instrument.instrument_id, timestamp, candle_open, high, low,
                    candle_close, volume, quality_flags=("synthetic",)))
                oi_value = oi_start * (1 + 0.000004 * minute_index)
                oi_observations.append(OpenInterestObservation(
                    contract_id, timestamp, oi_value))
                final_close = candle_close
                last_center = candle_close

            daily_candles.append(Candle(
                instrument.instrument_id, closes_at, previous_close,
                max(previous_close, final_close) * 1.001,
                min(previous_close, final_close) * 0.999,
                final_close, 1.0, quality_flags=("synthetic", "daily_fixture")))
            previous_close = final_close
            previous_oi_close = oi_start * (1 + 0.000004 * 374)

    for session in sessions:
        # Sector direction is an explicit categorical fixture input. This does not
        # implement sector aggregation or resolve the outstanding sector decision.
        for minute in range(5, 376, 5):
            stamp = session.opens_at + timedelta(minutes=minute)
            sectors[(session.instrument_id, stamp)] = "neutral"

    return SyntheticAnalyticsDataset(
        instruments=instruments,
        one_minute_candles=tuple(minute_candles),
        daily_candles=tuple(daily_candles),
        sessions=tuple(sessions),
        open_interest=tuple(oi_observations),
        contract_mappings=tuple(mappings),
        sector_directions=sectors,
    )
