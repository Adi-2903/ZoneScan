from datetime import datetime, timedelta, timezone
import unittest

from zonescan.fixtures import SyntheticFixtureProvider
from zonescan.models import Candle, ScoreInputs
from zonescan.scoring import calculate_strength
from zonescan.structure import confirmed_swings


class FoundationTests(unittest.TestCase):
    def test_invalid_candle_rejected(self):
        with self.assertRaises(ValueError):
            Candle("x", datetime.now(timezone.utc), 10, 9, 8, 9, 1)

    def test_swing_only_visible_after_right_candles_close(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        highs = [21, 22, 23, 30, 23, 22, 21]
        bars = tuple(Candle("x", start + timedelta(minutes=i), h-1, h, h-2, h-1, 10)
                     for i, h in enumerate(highs))
        self.assertEqual((), confirmed_swings(bars[:6]))
        swings = confirmed_swings(bars)
        self.assertEqual(1, len(swings))
        self.assertEqual("high", swings[0].kind)
        self.assertEqual(bars[6].timestamp, swings[0].confirmed_at)

    def test_synthetic_fixture_is_deterministic_and_marked(self):
        as_of = datetime(2026, 1, 1, tzinfo=timezone.utc)
        provider = SyntheticFixtureProvider()
        first, second = provider.snapshot(as_of), provider.snapshot(as_of)
        self.assertEqual(first, second)
        self.assertEqual("synthetic", first.data_status)
        self.assertTrue(all("synthetic" in c.quality_flags for c in first.candles))

    def test_strength_missing_required_input_is_unavailable(self):
        result = calculate_strength(ScoreInputs(.01, .02, 1.5, .01, "bullish",
                                                 True, True, "bullish", "bullish", 1.0))
        self.assertTrue(result.available)
        self.assertIsNotNone(result.strength)
        missing = calculate_strength(ScoreInputs(.01, .02, None, .01, "bullish",
                                                  True, True, "bullish", "bullish", 1.0))
        self.assertFalse(missing.available)
        self.assertEqual("required_input_missing", missing.reason)


if __name__ == "__main__":
    unittest.main()
