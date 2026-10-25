"""Fetch one explicitly configured historical sample; never scans a universe.

Run from services/api after setting DATA_PROVIDER=upstox,
UPSTOX_ACCESS_TOKEN, UPSTOX_INSTRUMENT_KEY, UPSTOX_FROM_DATE and
UPSTOX_TO_DATE in the environment.
"""
import os

from zonescan.provider_config import configured_historical_provider


provider = configured_historical_provider()
if provider is None:
    raise SystemExit("Set DATA_PROVIDER=upstox to opt into historical retrieval")

instrument_key = os.environ.get("UPSTOX_INSTRUMENT_KEY", "").strip()
from_date = os.environ.get("UPSTOX_FROM_DATE", "").strip()
to_date = os.environ.get("UPSTOX_TO_DATE", "").strip()
if not instrument_key or not from_date or not to_date:
    raise SystemExit(
        "Set UPSTOX_INSTRUMENT_KEY, UPSTOX_FROM_DATE and UPSTOX_TO_DATE")

batch = provider.fetch_one_minute(instrument_key, from_date, to_date)
print(f"source=upstox_historical instrument={batch.instrument.instrument_id}")
print(f"candles={len(batch.candles)}")
if batch.candles:
    first, last = batch.candles[0], batch.candles[-1]
    print(f"first={first.timestamp.isoformat()} last={last.timestamp.isoformat()}")
print("Open interest was not requested; fetch a futures key separately with include_open_interest=True.")
