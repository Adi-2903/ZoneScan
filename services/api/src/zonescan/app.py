"""Optional FastAPI boundary. Install with `pip install -e '.[api]'`."""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI

from . import ALGORITHM_VERSION, PARAMETER_VERSION
from .fixtures import SyntheticFixtureProvider

app = FastAPI(title="ZoneScan API", version="0.1.0")
provider = SyntheticFixtureProvider()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_mode": provider.data_mode}


@app.get("/api/v1/market/status")
def market_status() -> dict[str, object]:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    snapshot = provider.snapshot(now)
    return {
        "market_state": snapshot.market_state,
        "settling": True,
        "settling_reason": "development_fixture_no_session_calendar",
        "data_status": snapshot.data_status,
        "data_mode": provider.data_mode,
        "data_as_of": snapshot.data_as_of.isoformat(),
        "algorithm_version": ALGORITHM_VERSION,
        "parameter_version": PARAMETER_VERSION,
        "universe_expected": len(snapshot.instruments),
        "universe_eligible": 0,
        "symbols_excluded": len(snapshot.instruments),
        "exclusion_summary": {"fixture_board_not_implemented": len(snapshot.instruments)},
    }


@app.get("/api/v1/dev/market")
def development_market() -> dict[str, object]:
    snapshot = provider.snapshot(datetime.now(ZoneInfo("Asia/Kolkata")))
    return {
        "data_status": snapshot.data_status,
        "data_mode": provider.data_mode,
        "data_as_of": snapshot.data_as_of.isoformat(),
        "instruments": [instrument.symbol for instrument in snapshot.instruments],
        "candle_count": len(snapshot.candles),
        "quality_flags": ["synthetic"],
    }
