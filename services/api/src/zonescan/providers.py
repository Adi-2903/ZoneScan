from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from .models import HistoricalCandleBatch, MarketSnapshot


class MarketDataProvider(Protocol):
    """Provider-neutral read boundary; concrete vendors stay outside the engine."""

    @property
    def data_mode(self) -> str: ...

    def snapshot(self, as_of: datetime) -> MarketSnapshot: ...


class HistoricalCandleProvider(Protocol):
    """Read-only historical boundary, separate from the live snapshot protocol."""

    @property
    def data_mode(self) -> str: ...

    def fetch_one_minute(self, instrument_key: str, from_date: date | str,
                         to_date: date | str, *, include_open_interest: bool = False,
                         symbol: str | None = None) -> HistoricalCandleBatch: ...
