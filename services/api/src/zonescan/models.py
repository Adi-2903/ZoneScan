from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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
class Zone:
    zone_id: str
    instrument_id: str
    side: str
    low: float
    high: float
    timeframe: str
    formed_at: datetime
    recognized_at: datetime
    state: str = "fresh"
    has_fvg: bool = False
    last_touched_at: datetime | None = None
    expired_at: datetime | None = None
    active: bool = True
    algorithm_version: str = "v0.1-ob"
    parameter_version: str = "2026-10-26.2"


@dataclass(frozen=True, slots=True)
class ReplayBar:
    candle: Candle
    atr: float | None
    rvol: float | None
    timeframe: str = "5m"
    session_date: date | None = None
    day_return: float | None = None
    daily_sigma20: float | None = None
    oi_change_daily_pct: float | None = None
    price_above_vwap: bool | None = None
    price_above_ema20: bool | None = None
    sector_direction: str | None = None

    def __post_init__(self) -> None:
        if self.timeframe not in ("5m", "15m"):
            raise ValueError("order-block replay timeframe must be 5m or 15m")
        if self.atr is not None and (not isfinite(self.atr) or self.atr <= 0):
            raise ValueError("ATR must be positive and finite when available")
        if self.rvol is not None and (not isfinite(self.rvol) or self.rvol < 0):
            raise ValueError("RVOL must be nonnegative and finite when available")


@dataclass(frozen=True, slots=True)
class ReplayEvent:
    timestamp: datetime
    kind: str
    zone_id: str | None = None
    state: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayScore:
    instrument_id: str
    timestamp: datetime
    result: ScoreResult
    direction: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreInputs:
    day_return: float
    daily_sigma20: float | None
    rvol: float | None
    oi_change_daily_pct: float | None
    direction: str | None
    price_above_vwap: bool | None
    price_above_ema20: bool | None
    structure: str | None
    sector: str | None
    current_price: float | None
    atr: float | None
    nearest_zone: Zone | None


@dataclass(frozen=True, slots=True)
class ComponentResult:
    available: bool
    value: float | None
    reason: str | None = None
    context: str | None = None


@dataclass(frozen=True, slots=True)
class ScoreResult:
    available: bool
    strength: float | None
    components: dict[str, float | None]
    reason: str | None = None
    component_reasons: dict[str, str] | None = None
    component_contexts: dict[str, str] | None = None
    algorithm_version: str = "v0.1-score"
    parameter_version: str = "2026-10-26.3"
