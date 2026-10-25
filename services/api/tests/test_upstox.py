from datetime import date, datetime
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from zonescan.provider_config import configured_historical_provider
from zonescan.upstox import (UpstoxAPIError, UpstoxHistoricalCandleProvider,
                             UpstoxResponseError, UpstoxSetupError, month_windows)


def payload(candles):
    return json.dumps({"status": "success", "data": {"candles": candles}}).encode()


def row(timestamp="2026-01-05T09:15:00+05:30", *, oi=12, fields=7):
    values = [timestamp, 100, 102, 99, 101, 500]
    if fields > 6:
        values.append(oi)
    return values


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


def provider_for(body_or_opener):
    opener = body_or_opener if callable(body_or_opener) else lambda *_a, **_kw: FakeResponse(body_or_opener)
    return UpstoxHistoricalCandleProvider("secret-test-token", opener=opener)


class UpstoxAdapterTests(unittest.TestCase):
    def test_parses_timestamp_ohlcv_and_keeps_futures_oi_separate(self):
        batch = provider_for(payload([row(oi=0)])).fetch_one_minute(
            "NSE_FO|TEST-FUT", "2026-01-05", "2026-01-05",
            include_open_interest=True, symbol="TEST")
        self.assertEqual("NSE_FO|TEST-FUT", batch.instrument.instrument_id)
        self.assertEqual("TEST", batch.instrument.symbol)
        self.assertEqual(datetime.fromisoformat("2026-01-05T09:15:00+05:30"),
                         batch.candles[0].timestamp)
        self.assertEqual((100, 102, 99, 101, 500),
                         (batch.candles[0].open, batch.candles[0].high,
                          batch.candles[0].low, batch.candles[0].close,
                          batch.candles[0].volume))
        self.assertEqual(0.0, batch.open_interest[0].value)
        self.assertEqual("NSE_FO|TEST-FUT", batch.open_interest[0].instrument_id)

    def test_cash_mode_does_not_treat_response_oi_as_cash_oi(self):
        batch = provider_for(payload([row(oi=999)])).fetch_one_minute(
            "NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        self.assertEqual((), batch.open_interest)
        self.assertEqual((), batch.missing_open_interest_at)
        self.assertEqual(("open_interest_not_requested",), batch.warnings)

    def test_missing_oi_is_reported_without_zero_filling(self):
        batch = provider_for(payload([row(fields=6)])).fetch_one_minute(
            "NSE_FO|TEST-FUT", "2026-01-05", "2026-01-05",
            include_open_interest=True)
        self.assertEqual((), batch.open_interest)
        self.assertEqual((batch.candles[0].timestamp,), batch.missing_open_interest_at)

    def test_sorts_and_deduplicates_identical_records(self):
        late = row("2026-01-05T09:16:00+05:30")
        early = row()
        batch = provider_for(payload([late, early, early])).fetch_one_minute(
            "NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        self.assertEqual(2, len(batch.candles))
        self.assertLess(batch.candles[0].timestamp, batch.candles[1].timestamp)

    def test_conflicting_duplicates_and_out_of_range_timestamps_are_rejected(self):
        conflict = row()
        conflict[4] = 100
        with self.assertRaisesRegex(UpstoxResponseError, "conflicting duplicate"):
            provider_for(payload([row(), conflict])).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        with self.assertRaisesRegex(UpstoxResponseError, "outside requested date range"):
            provider_for(payload([row("2026-01-06T09:15:00+05:30")])).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")

    def test_month_chunking_uses_inclusive_non_overlapping_ranges(self):
        requests = []
        def opener(request, *, timeout):
            requests.append((request, timeout))
            return FakeResponse(payload([]))
        batch = provider_for(opener).fetch_one_minute(
            "NSE_EQ|TEST", "2026-01-30", "2026-03-02")
        self.assertEqual(2, len(requests))
        self.assertIn("minutes/1/2026-02-28/2026-01-30", requests[0][0].full_url)
        self.assertIn("minutes/1/2026-03-02/2026-03-01", requests[1][0].full_url)
        self.assertIn("NSE_EQ%7CTEST", requests[0][0].full_url)
        self.assertEqual(10.0, requests[0][1])
        self.assertEqual((), batch.candles)
        self.assertEqual(((date(2026, 1, 30), date(2026, 2, 28)),
                          (date(2026, 3, 1), date(2026, 3, 2))),
                         month_windows(date(2026, 1, 30), date(2026, 3, 2)))

    def test_invalid_or_missing_fields_are_explicit_errors(self):
        with self.assertRaisesRegex(UpstoxResponseError, "expected timestamp"):
            provider_for(payload([["2026-01-05T09:15:00+05:30", 1, 2]])).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        with self.assertRaisesRegex(UpstoxResponseError, "timestamp has no timezone"):
            provider_for(payload([row("2026-01-05T09:15:00")])).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        malformed = row()
        malformed[1] = 300
        with self.assertRaisesRegex(UpstoxResponseError, "invalid OHLCV"):
            provider_for(payload([malformed])).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")

    def test_api_error_and_rate_limit_are_reported_without_secret(self):
        def forbidden(*_a, **_kw):
            raise HTTPError("https://api.upstox.com", 403, "denied", {}, None)
        with self.assertRaisesRegex(UpstoxAPIError, "HTTP 403") as raised:
            provider_for(forbidden).fetch_one_minute("NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        self.assertNotIn("secret-test-token", str(raised.exception))
        def limited(*_a, **_kw):
            raise HTTPError("https://api.upstox.com", 429, "limited", {}, None)
        with self.assertRaisesRegex(UpstoxAPIError, "rate limit"):
            provider_for(limited).fetch_one_minute("NSE_EQ|TEST", "2026-01-05", "2026-01-05")

    def test_transport_timeout_and_error_payload_are_clear(self):
        def timeout(*_a, **_kw):
            raise TimeoutError()
        with self.assertRaisesRegex(UpstoxAPIError, "timed out"):
            provider_for(timeout).fetch_one_minute("NSE_EQ|TEST", "2026-01-05", "2026-01-05")
        with self.assertRaisesRegex(UpstoxAPIError, "invalid instrument"):
            provider_for(json.dumps({"status": "error", "message": "invalid instrument"}).encode()).fetch_one_minute(
                "NSE_EQ|TEST", "2026-01-05", "2026-01-05")

    def test_missing_credentials_and_synthetic_default(self):
        self.assertIsNone(configured_historical_provider(environ={}))
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(UpstoxSetupError, "UPSTOX_ACCESS_TOKEN"):
                UpstoxHistoricalCandleProvider()
        with self.assertRaisesRegex(UpstoxSetupError, "DATA_PROVIDER=upstox"):
            configured_historical_provider(environ={"DATA_PROVIDER": "upstox"})
        provider = configured_historical_provider(environ={
            "DATA_PROVIDER": "upstox", "UPSTOX_ACCESS_TOKEN": "test-token"})
        self.assertEqual("upstox_historical", provider.data_mode)


if __name__ == "__main__":
    unittest.main()
