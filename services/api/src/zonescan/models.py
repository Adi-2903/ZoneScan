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
class OpenInterestObservation:
    instrument_id: str
    timestamp: datetime
    value: float


@dataclass(frozen=True, slots=True)
class HistoricalCandleBatch:
    instrument: Instrument
    candles: tuple[Candle, ...]
    open_interest: tuple[OpenInterestObservation, ...] = ()
    missing_open_interest_at: tuple[datetime, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class TradingSession:
    instrument_id: str
    session_date: date
    opens_at: datetime
    closes_at: datetime


@dataclass(frozen=True, slots=True)
class MissingCandleInterval:
    instrument_id: str
    timeframe: str
    timestamp: datetime
    missing_timestamps: tuple[datetime, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class CandleAggregation:
    timeframe: str
    candles: tuple[Candle, ...]
    gaps: tuple[MissingCandleInterval, ...]


@dataclass(frozen=True, slots=True)
class FuturesContractMapping:
    underlying_instrument_id: str
    contract_instrument_id: str
    valid_from: date
    valid_through: date | None = None


@dataclass(frozen=True, slots=True)
class IndicatorValue:
    available: bool
    value: float | bool | None
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.available and self.value is None:
            raise ValueError("available indicator value is required")
        if not self.available and self.value is not None:
            raise ValueError("unavailable indicator cannot carry a value")
        if self.available and self.reason is not None:
            raise ValueError("available indicator cannot have an unavailable reason")
        if not self.available and not self.reason:
            raise ValueError("unavailable indicator requires a reason")
        if isinstance(self.value, bool):
            return
        if self.value is not None and (not isinstance(self.value, (int, float)) or
                                       not isfinite(self.value)):
            raise ValueError("indicator value must be finite")


@dataclass(frozen=True, slots=True)
class IndicatorFrame:
    instrument_id: str
    timestamp: datetime
    timeframe: str
    candle: Candle | None
    atr14: IndicatorValue
    daily_sigma20: IndicatorValue
    day_return: IndicatorValue
    rvol: IndicatorValue
    oi_change_daily_pct: IndicatorValue
    oi_change_30m_pct: IndicatorValue
    vwap: IndicatorValue
    price_above_vwap: IndicatorValue
    ema20: IndicatorValue
    price_above_ema20: IndicatorValue
    adx14: IndicatorValue
    missing_reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EarlyMoveResult:
    available: bool
    score: float | None
    components: dict[str, float | None]
    component_reasons: dict[str, str]
    reason: str | None = None
    algorithm_version: str = "v0.1-early-move"
    parameter_version: str = "2026-10-26.1"

    def __post_init__(self) -> None:
        if self.available:
            if self.score is None or not isfinite(self.score) or not 0 <= self.score <= 100:
                raise ValueError("available Early-Move score must be finite and in [0, 100]")
            if self.reason is not None or self.component_reasons:
                raise ValueError("available Early-Move result cannot have unavailable reasons")
            if any(value is None or not isfinite(value) for value in self.components.values()):
                raise ValueError("available Early-Move result requires finite components")
        else:
            if self.score is not None:
                raise ValueError("unavailable Early-Move result cannot carry a score")
            if not self.reason or not self.component_reasons:
                raise ValueError("unavailable Early-Move result requires reasons")


@dataclass(frozen=True, slots=True)
class ChoppyResult:
    available: bool
    is_choppy: bool | None
    condition_values: dict[str, bool | None]
    unavailable_reasons: dict[str, str]
    overlap_ratio: float | None = None
    reason: str | None = None
    satisfied_conditions: tuple[str, ...] = ()
    algorithm_version: str = "v0.1-choppy"
    parameter_version: str = "2026-10-26.1"


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
class LiquidityLevel:
    level_id: str
    instrument_id: str
    timeframe: str
    side: str
    price: float
    kind: str
    formed_at: datetime
    confirmed_at: datetime
    state: str = "unswept"
    swept_at: datetime | None = None
    invalidated_at: datetime | None = None
    unavailable_at: datetime | None = None
    expired_at: datetime | None = None
    pending_since: datetime | None = None
    pending_candles: int = 0
    source_timestamps: tuple[datetime, ...] = ()
    unavailable_reason: str | None = None
    algorithm_version: str = "v0.1-liquidity"
    parameter_version: str = "2026-10-26.1"

    def __post_init__(self) -> None:
        if not self.level_id or not self.instrument_id:
            raise ValueError("liquidity level identity is required")
        if self.timeframe not in ("5m", "15m"):
            raise ValueError("liquidity timeframe must be 5m or 15m")
        if self.side not in ("above", "below"):
            raise ValueError("liquidity side must be above or below")
        if not isfinite(self.price) or self.price <= 0:
            raise ValueError("liquidity price must be positive and finite")
        if self.state not in ("unswept", "swept", "invalidated", "expired", "unavailable"):
            raise ValueError("invalid liquidity lifecycle state")
        if self.formed_at.tzinfo is None or self.confirmed_at.tzinfo is None:
            raise ValueError("liquidity timestamps must be timezone-aware")
        if self.confirmed_at < self.formed_at:
            raise ValueError("liquidity cannot be confirmed before formation")
        if self.state == "swept" and self.swept_at is None:
            raise ValueError("swept liquidity requires swept_at")
        if self.state == "expired" and self.expired_at is None:
            raise ValueError("expired liquidity requires expired_at")
        if self.state == "unavailable" and not self.unavailable_reason:
            raise ValueError("unavailable liquidity requires a reason")


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
    adx14: float | None = None
    indicator_unavailable_reasons: tuple[tuple[str, str], ...] = ()
    symbol: str | None = None
    oi_change_30m_pct: float | None = None

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
    liquidity_level_id: str | None = None


@dataclass(frozen=True, slots=True)
class ReplayScore:
    instrument_id: str
    timestamp: datetime
    result: ScoreResult
    direction: str | None = None
    choppy: ChoppyResult | None = None
    filtered_strength: float | None = None
    smoothed_strength: float | None = None
    rvol: float | None = None
    traded_value: float | None = None
    session_date: date | None = None
    timeframe: str = "5m"
    early_move: EarlyMoveResult | None = None


@dataclass(frozen=True, slots=True)
class BoardRow:
    rank: int
    instrument_id: str
    symbol: str
    side: str
    score: ReplayScore


@dataclass(frozen=True, slots=True)
class BoardSnapshot:
    timestamp: datetime
    session_date: date
    bullish: tuple[BoardRow, ...]
    bearish: tuple[BoardRow, ...]
    algorithm_version: str = "v0.1-board"
    parameter_version: str = "2026-10-26.1"


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
