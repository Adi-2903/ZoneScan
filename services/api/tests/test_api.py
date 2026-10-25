from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from zonescan.app import app, get_analytics_service


class AnalyticalApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_synthetic_default_status_and_legacy_routes(self):
        self.assertEqual(self.client.get("/health").json()["data_mode"], "synthetic")
        response = self.client.get("/api/v1/market/status")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["data_mode"], "synthetic")
        self.assertEqual(payload["data_status"], "synthetic")
        self.assertEqual(payload["data_source"], "deterministic_synthetic_fixture")
        self.assertTrue(payload["as_of"].endswith("+05:30"))
        self.assertEqual(self.client.get("/api/v1/dev/market").status_code, 200)

    def test_bull_and_bear_board_responses(self):
        for side, symbol in (("bull", "SYNBULL"), ("bear", "SYNBEAR")):
            response = self.client.get("/api/v1/board", params={"side": side})
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertEqual(body["side"], side)
            self.assertEqual(body["data_mode"], "synthetic")
            self.assertEqual(body["rows"][0]["symbol"], symbol)
            row = body["rows"][0]
            self.assertEqual(row["score_breakdown"]["available"], True)
            self.assertEqual(row["score_breakdown"]["direction"],
                             "bullish" if side == "bull" else "bearish")
            self.assertTrue(row["quality_flags"])
            self.assertIn("as_of", body)

    def test_invalid_side_and_unknown_symbol_use_error_envelope(self):
        invalid = self.client.get("/api/v1/board", params={"side": "flat"})
        self.assertEqual(invalid.status_code, 400)
        self.assertEqual(invalid.json()["error"]["code"], "INVALID_SIDE")
        missing = self.client.get("/api/v1/board")
        self.assertEqual(missing.status_code, 400)
        self.assertEqual(missing.json()["error"]["code"], "INVALID_REQUEST")
        unknown = self.client.get("/api/v1/stocks/NOTREAL")
        self.assertEqual(unknown.status_code, 404)
        self.assertEqual(unknown.json()["error"]["code"], "UNKNOWN_SYMBOL")

    def test_stock_detail_and_deterministic_repeated_reads(self):
        first = self.client.get("/api/v1/stocks/synbull")
        second = self.client.get("/api/v1/stocks/SYNBULL")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), second.json())
        body = first.json()
        self.assertEqual(body["symbol"], "SYNBULL")
        self.assertEqual(body["data_mode"], "synthetic")
        self.assertIn("components", body["strength"])
        self.assertIn("atr", body["indicators"])
        self.assertIn("zones", body)
        self.assertIn("liquidity_levels", body)

    def test_candles_endpoint_uses_fixture_and_validates_timeframe(self):
        response = self.client.get("/api/v1/stocks/SYNBULL/candles", params={"tf": "5m"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["data_mode"], "synthetic")
        self.assertEqual(body["timeframe"], "5m")
        self.assertTrue(body["candles"])
        self.assertEqual(body["candles"][0]["quality_flags"] and
                         "aggregated_5m" in body["candles"][0]["quality_flags"], True)
        invalid = self.client.get("/api/v1/stocks/SYNBULL/candles", params={"tf": "2m"})
        self.assertEqual(invalid.status_code, 400)

    def test_missing_analytical_inputs_stay_unavailable(self):
        from dataclasses import replace
        from zonescan.analytics_service import AnalyticsService
        from zonescan.synthetic_analytics import build_synthetic_analytics_dataset

        fixture = replace(build_synthetic_analytics_dataset(), open_interest=(),
                          sector_directions={})
        service = AnalyticsService(fixture)
        app.dependency_overrides[get_analytics_service] = lambda: service
        try:
            response = self.client.get("/api/v1/stocks/SYNBULL")
            body = response.json()
            self.assertFalse(body["indicators"]["oi_change_daily_pct"]["available"])
            self.assertIsNone(body["indicators"]["oi_change_daily_pct"]["value"])
            self.assertFalse(body["strength"]["available"])
            self.assertIn("S", body["strength"]["component_reasons"])
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    unittest.main()
