"""Read-only adapter for Upstox Historical Candle Data V3."""
from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
import json
import os
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .models import (Candle, HistoricalCandleBatch, Instrument,
                     OpenInterestObservation)

BASE_URL = "https://api.upstox.com/v3/historical-candle"


class UpstoxError(RuntimeError):
    """Base error for configuration, transport, and response failures."""


class UpstoxSetupError(UpstoxError):
    pass


class UpstoxResponseError(UpstoxError):
    pass


class UpstoxAPIError(UpstoxError):
    pass


def _as_date(value: date | str, name: str) -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{name} must be a date, not a datetime")
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must use YYYY-MM-DD format") from exc


def _next_month(start: date) -> date:
    year = start.year + (start.month == 12)
    month = 1 if start.month == 12 else start.month + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def month_windows(start: date, end: date) -> tuple[tuple[date, date], ...]:
    """Create inclusive, non-overlapping windows no longer than one calendar month."""
    if end < start:
        raise ValueError("to_date must be on or after from_date")
    windows: list[tuple[date, date]] = []
    cursor = start
    while cursor <= end:
        window_end = min(end, _next_month(cursor))
        windows.append((cursor, window_end))
        cursor = window_end + timedelta(days=1)
    return tuple(windows)


def _number(value: object, field: str, row: int) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UpstoxResponseError(f"candle row {row}: {field} is missing or not numeric")
    try:
        numeric = float(value)
    except (OverflowError, ValueError) as exc:
        raise UpstoxResponseError(f"candle row {row}: {field} is invalid") from exc
    if numeric != numeric or numeric in (float("inf"), float("-inf")):
        raise UpstoxResponseError(f"candle row {row}: {field} is not finite")
    return numeric


def _timestamp(value: object, row: int) -> datetime:
    # Upstox V3 examples encode the candle-start timestamp as ISO-8601 with +05:30.
    # The field table's declared numeric type conflicts with those examples; fail
    # clearly on an unrecognized timestamp instead of guessing an epoch unit.
    if not isinstance(value, str):
        raise UpstoxResponseError(f"candle row {row}: timestamp must be ISO-8601 text")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise UpstoxResponseError(f"candle row {row}: timestamp is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise UpstoxResponseError(f"candle row {row}: timestamp has no timezone")
    return parsed


def _error_detail(body: bytes) -> str:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "provider returned a non-JSON error body"
    if not isinstance(payload, dict):
        return "provider returned an invalid error body"
    message = payload.get("message") or payload.get("errors") or payload.get("error")
    return str(message)[:300] if message else "provider returned an API error"


class UpstoxHistoricalCandleProvider:
    """Fetch one instrument's one-minute candles; never places orders or streams live data."""

    def __init__(self, access_token: str | None = None, *, timeout_seconds: float = 10.0,
                 opener: Callable = urlopen) -> None:
        token = access_token if access_token is not None else os.getenv("UPSTOX_ACCESS_TOKEN")
        if not token or not token.strip():
            raise UpstoxSetupError(
                "Upstox mode requires UPSTOX_ACCESS_TOKEN in the environment")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._access_token = token.strip()
        self._timeout = timeout_seconds
        self._opener = opener

    @property
    def data_mode(self) -> str:
        return "upstox_historical"

    def fetch_one_minute(self, instrument_key: str, from_date: date | str,
                         to_date: date | str, *, include_open_interest: bool = False,
                         symbol: str | None = None) -> HistoricalCandleBatch:
        if not instrument_key or not instrument_key.strip():
            raise ValueError("instrument_key is required")
        start, end = _as_date(from_date, "from_date"), _as_date(to_date, "to_date")
        windows = month_windows(start, end)
        rows: list[tuple[object, date, date]] = []
        encoded_key = quote(instrument_key.strip(), safe="")
        for window_start, window_end in windows:
            url = (f"{BASE_URL}/{encoded_key}/minutes/1/"
                   f"{window_end.isoformat()}/{window_start.isoformat()}")
            request = Request(url, headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._access_token}",
            }, method="GET")
            try:
                with self._opener(request, timeout=self._timeout) as response:
                    body = response.read()
            except HTTPError as exc:
                detail = _error_detail(exc.read())
                if exc.code == 429:
                    raise UpstoxAPIError("Upstox rate limit reached (HTTP 429); retry later") from None
                raise UpstoxAPIError(f"Upstox API request failed (HTTP {exc.code}): {detail}") from None
            except (TimeoutError, URLError, OSError) as exc:
                if isinstance(exc, URLError) and isinstance(exc.reason, TimeoutError):
                    detail = "request timed out"
                elif isinstance(exc, TimeoutError):
                    detail = "request timed out"
                else:
                    detail = "network request failed"
                raise UpstoxAPIError(f"Upstox historical request failed: {detail}") from None
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise UpstoxResponseError("Upstox response is not valid JSON") from exc
            if not isinstance(payload, dict) or payload.get("status") != "success":
                raise UpstoxAPIError(f"Upstox returned an API error: {_error_detail(body)}")
            data = payload.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("candles"), list):
                raise UpstoxResponseError("Upstox response is missing data.candles array")
            rows.extend((row, window_start, window_end) for row in data["candles"])

        instrument = Instrument(instrument_key.strip(), symbol or instrument_key.strip())
        by_timestamp: dict[datetime, tuple[Candle, float | None]] = {}
        missing_oi: set[datetime] = set()
        oi_points: dict[datetime, OpenInterestObservation] = {}
        for index, (row, window_start, window_end) in enumerate(rows):
            if not isinstance(row, (list, tuple)) or len(row) < 6:
                raise UpstoxResponseError(
                    f"candle row {index}: expected timestamp, OHLC and volume fields")
            timestamp = _timestamp(row[0], index)
            if not window_start <= timestamp.date() <= window_end:
                raise UpstoxResponseError(
                    f"candle row {index}: timestamp falls outside requested date range")
            values = [_number(row[column], field, index) for column, field in
                      ((1, "open"), (2, "high"), (3, "low"), (4, "close"), (5, "volume"))]
            try:
                candle = Candle(instrument.instrument_id, timestamp, *values,
                                quality_flags=("upstox_historical", "one_minute"))
            except ValueError as exc:
                raise UpstoxResponseError(f"candle row {index}: invalid OHLCV: {exc}") from exc
            oi_value: float | None = None
            if include_open_interest:
                if len(row) <= 6 or row[6] is None:
                    missing_oi.add(timestamp)
                else:
                    oi_value = _number(row[6], "open_interest", index)
                    if oi_value < 0:
                        raise UpstoxResponseError(f"candle row {index}: open_interest cannot be negative")
                    oi_points[timestamp] = OpenInterestObservation(
                        instrument.instrument_id, timestamp, oi_value)
            prior = by_timestamp.get(timestamp)
            current = (candle, oi_value)
            if prior is not None:
                if prior != current:
                    raise UpstoxResponseError(
                        f"conflicting duplicate candle at {timestamp.isoformat()}")
                continue
            by_timestamp[timestamp] = current

        candles = tuple(pair[0] for _, pair in sorted(by_timestamp.items()))
        ordered_oi = tuple(oi_points[key] for key in sorted(oi_points))
        return HistoricalCandleBatch(
            instrument, candles, ordered_oi, tuple(sorted(missing_oi)),
            ("open_interest_not_requested",) if not include_open_interest else ())
