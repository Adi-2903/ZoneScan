"""Run: python examples/replay_synthetic.py (from services/api). All values are synthetic."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from zonescan.models import Candle, ReplayBar
from zonescan.replay import replay


start = datetime(2026, 1, 5, 9, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
ohlc = [
    (9, 11, 8, 10), (10, 12, 9, 11), (11, 13, 10, 12),
    (19, 21, 18, 20), (11, 13, 10, 12), (10, 12, 9, 11),
    (9, 11, 8, 10), (10.5, 12, 9, 10), (10, 32, 9, 31),
    (13, 13.5, 10, 12.5), (10, 10.5, 8, 8.5),
]
bars = []
for index, (open_, high, low, close) in enumerate(ohlc):
    candle = Candle("SYNTHETIC-X", start + timedelta(minutes=5 * index),
                    open_, high, low, close, 1000, quality_flags=("synthetic",))
    bars.append(ReplayBar(candle, atr=5.0, rvol=1.5, timeframe="5m"))

result = replay(bars)
print("data_mode=synthetic")
for event in result.events:
    print(event.timestamp.isoformat(), event.kind, event.zone_id or "", event.state or "", event.detail or "")
for zone in result.zones:
    print("zone", zone.side, zone.low, zone.high, zone.state, zone.active,
          "formed_at", zone.formed_at.isoformat(), "recognized_at", zone.recognized_at.isoformat())
