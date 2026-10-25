"""Optional read-only FastAPI boundary over the deterministic synthetic engine."""
from __future__ import annotations

from functools import lru_cache
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .analytics_service import AnalyticsService, versions
from .fixtures import SyntheticFixtureProvider

app = FastAPI(title="ZoneScan API", version="0.1.0")
provider = SyntheticFixtureProvider()
IST = ZoneInfo("Asia/Kolkata")


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    """Construct the chronological fixture replay once per process."""
    return AnalyticsService()


def _error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {
        "code": code, "message": message, "request_id": f"req_{uuid4().hex}"}})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return _error(400, "INVALID_REQUEST", "Request parameters are invalid.")


def _indicator(value, *, unavailable_reason: str | None = None):
    if value is None:
        return {"available": False, "value": None,
                "reason": unavailable_reason or "missing_input"}
    return {"available": True, "value": value, "reason": None}


def _score_payload(score):
    if score is None:
        return {"available": False, "strength": None, "components": {},
                "unavailable_reasons": {"score": "score_not_available_at_snapshot"}}
    result = score.result
    return {
        "available": result.available,
        "strength": result.strength,
        "components": result.components,
        "component_reasons": result.component_reasons or {},
        "component_contexts": result.component_contexts or {},
        "unavailable_reason": result.reason,
        "direction": score.direction,
        "filtered_strength": score.filtered_strength,
        "smoothed_strength": score.smoothed_strength,
        "choppy": None if score.choppy is None else {
            "available": score.choppy.available,
            "is_choppy": score.choppy.is_choppy,
            "conditions": score.choppy.condition_values,
            "unavailable_reasons": score.choppy.unavailable_reasons,
            "reason": score.choppy.reason,
        },
        "early_move": None if score.early_move is None else {
            "available": score.early_move.available,
            "score": score.early_move.score,
            "components": score.early_move.components,
            "component_reasons": score.early_move.component_reasons,
            "reason": score.early_move.reason,
            "algorithm_version": score.early_move.algorithm_version,
            "parameter_version": score.early_move.parameter_version,
        },
    }


def _zone_payload(zone):
    return {"zone_id": zone.zone_id, "side": zone.side, "low": zone.low,
            "high": zone.high, "timeframe": zone.timeframe,
            "formed_at": zone.formed_at.isoformat(),
            "recognized_at": zone.recognized_at.isoformat(),
            "state": zone.state, "active": zone.active}


def _level_payload(level):
    return {"level_id": level.level_id, "kind": level.kind, "side": level.side,
            "price": level.price, "timeframe": level.timeframe, "state": level.state,
            "formed_at": level.formed_at.isoformat(),
            "confirmed_at": level.confirmed_at.isoformat(),
            "swept_at": level.swept_at.isoformat() if level.swept_at else None,
            "unavailable_reason": level.unavailable_reason}


def _metadata(service: AnalyticsService):
    snap = service.snapshot
    return {"as_of": snap.as_of.isoformat(), "data_as_of": snap.data_as_of.isoformat(),
            "data_source": snap.data_source, "data_mode": snap.data_mode,
            "data_status": snap.data_status, "market_state": snap.market_state,
            "settling": snap.settling, "settling_reason": snap.settling_reason,
            **versions()}


@app.get("/health")
def health():
    return {"status": "ok", "data_mode": provider.data_mode}


@app.get("/api/v1/market/status")
def market_status(service: AnalyticsService = Depends(get_analytics_service)):
    snap = service.snapshot
    return {**_metadata(service), "session_open_at": None, "session_close_at": None,
            "received_at": None, "delay_seconds": None,
            "universe_expected": snap.universe_expected,
            "universe_eligible": snap.universe_eligible,
            "symbols_excluded": snap.symbols_excluded,
            "exclusion_summary": snap.exclusion_summary}


@app.get("/api/v1/board")
def board(side: str = Query(...), service: AnalyticsService = Depends(get_analytics_service)):
    if side not in ("bull", "bear"):
        return _error(400, "INVALID_SIDE", "side must be 'bull' or 'bear'.")
    rows = []
    for row in service.board_rows(side):
        score = row.score
        bar = service.latest_bar(row.instrument_id)
        instrument = service.instrument(row.instrument_id)
        zones = [zone for zone in service.zones_for(row.instrument_id)
                 if zone.active and zone.state in ("fresh", "tested")]
        zone = min(zones, key=lambda item: abs((item.low + item.high) / 2 - bar.candle.close)) if zones and bar else None
        rows.append({
            "rank": row.rank, "symbol": row.symbol,
            "price": bar.candle.close if bar else None,
            "change_pct": bar.day_return * 100 if bar and bar.day_return is not None else None,
            "strength": score.result.strength,
            "filtered_strength": score.filtered_strength,
            "smoothed_strength": score.smoothed_strength,
            "early_move": _score_payload(score)["early_move"],
            "score_breakdown": _score_payload(score),
            "sector": instrument.sector,
            "sector_badge": "unavailable" if instrument.sector is None else "fixture_input",
            "zone": _zone_payload(zone) if zone else {"available": False, "reason": "no_active_zone"},
            "levels": [_level_payload(level) for level in service.liquidity_for(row.instrument_id)],
            "trend": score.direction,
            "quality_flags": sorted(set(bar.candle.quality_flags)) if bar else [],
        })
    return {**_metadata(service), "side": side, "rows": rows}


@app.get("/api/v1/stocks/{symbol}")
def stock(symbol: str, service: AnalyticsService = Depends(get_analytics_service)):
    instrument_id = service.instrument_id_for_symbol(symbol)
    if instrument_id is None:
        return _error(404, "UNKNOWN_SYMBOL", f"Unknown symbol: {symbol}.")
    instrument = service.instrument(instrument_id)
    bar = service.latest_bar(instrument_id)
    score = service.latest_score(instrument_id)
    if bar is None:
        indicators = {"available": False, "reason": "no_completed_5m_bar"}
    else:
        reasons = dict(bar.indicator_unavailable_reasons)
        indicators = {
            "atr": _indicator(bar.atr, unavailable_reason=reasons.get("atr")),
            "rvol": _indicator(bar.rvol, unavailable_reason=reasons.get("rvol")),
            "day_return": _indicator(bar.day_return, unavailable_reason=reasons.get("day_return")),
            "daily_sigma20": _indicator(bar.daily_sigma20, unavailable_reason=reasons.get("daily_sigma20")),
            "oi_change_daily_pct": _indicator(bar.oi_change_daily_pct, unavailable_reason=reasons.get("oi_change_daily_pct")),
            "oi_change_30m_pct": _indicator(bar.oi_change_30m_pct, unavailable_reason=reasons.get("oi_change_30m_pct")),
            "price_above_vwap": _indicator(bar.price_above_vwap, unavailable_reason=reasons.get("price_above_vwap")),
            "price_above_ema20": _indicator(bar.price_above_ema20, unavailable_reason=reasons.get("price_above_ema20")),
            "adx14": _indicator(bar.adx14, unavailable_reason=reasons.get("adx14")),
        }
    return {**_metadata(service), "symbol": instrument.symbol,
            "instrument_id": instrument.instrument_id,
            "price": bar.candle.close if bar else None,
            "quality_flags": sorted(set(bar.candle.quality_flags)) if bar else [],
            "sector": instrument.sector,
            "indicators": indicators,
            "strength": _score_payload(score),
            "zones": [_zone_payload(zone) for zone in service.zones_for(instrument_id)],
            "liquidity_levels": [_level_payload(level) for level in service.liquidity_for(instrument_id)]}


@app.get("/api/v1/dev/market")
def development_market():
    from datetime import datetime
    snapshot = provider.snapshot(datetime.now(IST))
    return {"data_status": snapshot.data_status, "data_mode": provider.data_mode,
            "data_as_of": snapshot.data_as_of.isoformat(),
            "instruments": [item.symbol for item in snapshot.instruments],
            "candle_count": len(snapshot.candles),
            "quality_flags": sorted({flag for candle in snapshot.candles
                                     for flag in candle.quality_flags})}
