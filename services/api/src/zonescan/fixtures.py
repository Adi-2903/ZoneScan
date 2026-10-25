from __future__ import annotations

from datetime import datetime, timedelta

from .models import Candle, Instrument, MarketSnapshot


class SyntheticFixtureProvider:
    """Repeatable demo data. It must never be described as a live feed."""

    @property
    def data_mode(self) -> str:
        return "synthetic"

    def snapshot(self, as_of: datetime) -> MarketSnapshot:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        symbols = (Instrument("SYN-001", "DEMO1", "Synthetic Sector"),
                   Instrument("SYN-002", "DEMO2", "Synthetic Sector"))
        candles: list[Candle] = []
        for instrument, offset in zip(symbols, (0.0, 30.0)):
            base = 100.0 + offset
            for index in range(20):
                open_price = base + index * 0.2
                close = open_price + (0.3 if index % 3 else -0.1)
                candles.append(Candle(instrument.instrument_id, as_of - timedelta(minutes=19-index),
                                      open_price, max(open_price, close) + 0.2,
                                      min(open_price, close) - 0.2, close,
                                      1000 + index * 10, complete=True,
                                      quality_flags=("synthetic",)))
        return MarketSnapshot(tuple(candles), symbols, "deterministic_fixture", "synthetic",
                              as_of, "unknown")
