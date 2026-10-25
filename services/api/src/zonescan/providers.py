from __future__ import annotations

from datetime import datetime
from typing import Protocol

from .models import MarketSnapshot


class MarketDataProvider(Protocol):
    """Provider-neutral read boundary; concrete vendors stay outside the engine."""

    @property
    def data_mode(self) -> str: ...

    def snapshot(self, as_of: datetime) -> MarketSnapshot: ...
