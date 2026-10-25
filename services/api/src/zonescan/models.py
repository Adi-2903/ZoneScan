from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite


@dataclass(frozen=True, slots=True)
class Candle:
    instrument_id: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    complete: bool = True
    quality_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.instrument_id.strip():
            raise ValueError("instrument_id is required")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        values = (self.open, self.high, self.low, self.close, self.volume)
        if not all(isfinite(value) for value in values):
            raise ValueError("candle values must be finite")
        if self.low <= 0 or self.high < self.low:
            raise ValueError("candle price range is invalid")
        if not self.low <= self.open <= self.high or not self.low <= self.close <= self.high:
            raise ValueError("open and close must be within candle range")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")


@dataclass(frozen=True, slots=True)
class Instrument:
    instrument_id: str
    symbol: str
    sector: str | None = None
    active: bool = True


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    candles: tuple[Candle, ...]
    instruments: tuple[Instrument, ...]
    source: str
    data_status: str
    data_as_of: datetime
    market_state: str


@dataclass(frozen=True, slots=True)
class Swing:
    index: int
    timestamp: datetime
    price: float
    kind: str
    confirmed_at: datetime


@dataclass(frozen=True, slots=True)
class ScoreInputs:
    day_return: float
    daily_sigma20: float | None
    rvol: float | None
    oi_change_daily_pct: float | None
    direction: str
    price_above_vwap: bool | None
    price_above_ema20: bool | None
    structure: str | None
    sector: str | None
    zone_distance_atr: float | None


@dataclass(frozen=True, slots=True)
class ScoreResult:
    available: bool
    strength: float | None
    components: dict[str, float] | None
    reason: str | None = None
