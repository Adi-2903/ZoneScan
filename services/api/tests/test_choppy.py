from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import unittest

from zonescan.choppy import (CONDITIONS, candle_overlap_ratio,
                             classify_choppy)
from zonescan.models import Candle, ReplayBar, TradingSession
from zonescan.replay import replay

IST = ZoneInfo("Asia/Kolkata")


def session(day: int, bars: int) -> TradingSession:
    start = datetime(2026, 1, day, 9, 15, tzinfo=IST)
    return TradingSession("X", start.date(), start, start + timedelta(minutes=5 * bars))


def bar(s: TradingSession, index: int, high: float = 101, low: float = 99,
        close: float = 100.5, *, adx: float | None = 20, day_return: float | None = .01,
        sigma: float | None = .02, rvol: float | None = 1.1,
        complete: bool = True) -> ReplayBar:
    timestamp = s.opens_at + timedelta(minutes=5 * (index + 1))
    candle = Candle("X", timestamp, min(close, 100.5), high, low, close, 100,
                    complete=complete)
    return ReplayBar(candle, 1.0, rvol, "5m", s.session_date, day_return,
                     sigma, 0.0, True, True, "bullish", adx)


class ChoppyTests(unittest.TestCase):
    def test_overlap_ratio_known_value_and_zero_range_rule(self):
        s = session(5, 12)
        candles = [Candle("X", s.opens_at + timedelta(minutes=5 * (i + 1)),
                          100, 110, 100, 105, 10) for i in range(12)]
        ratio, reason = candle_overlap_ratio(candles)
        self.assertIsNone(reason)
        self.assertEqual(ratio, 1.0)
        candles[0] = Candle("X", candles[0].timestamp, 100, 100, 100, 100, 10)
        ratio, reason = candle_overlap_ratio(candles)
        self.assertIsNone(reason)
        self.assertAlmostEqual(ratio, 10 / 11)

    def test_missing_or_incomplete_candle_makes_overlap_unavailable(self):
        s = session(5, 12)
        candles = [Candle("X", s.opens_at + timedelta(minutes=5 * (i + 1)),
                          100, 101, 99, 100, 10) for i in range(12)]
        candles[4] = Candle("X", candles[4].timestamp, 100, 101, 99, 100, 10,
                            complete=False)
        self.assertEqual(candle_overlap_ratio(candles)[1], "incomplete_candle_in_overlap_window")
        candles[4] = Candle("X", candles[4].timestamp + timedelta(minutes=5),
                            100, 101, 99, 100, 10)
        self.assertEqual(candle_overlap_ratio(candles)[1], "missing_candle_in_overlap_window")

    def test_each_documented_condition_uses_strict_thresholds(self):
        tests = (
            (17.99, .01, .02, 1.1, .5, True, 0),
            (20, .0099, .02, 1.1, .5, True, 1),
            (20, .01, .02, .99, .5, True, 2),
            (20, .01, .02, 1.1, .7001, True, 3),
        )
        for adx, day_return, sigma, rvol, overlap, no_bos, condition_index in tests:
            with self.subTest(condition=condition_index):
                result = classify_choppy(adx, day_return, sigma, rvol, overlap, no_bos)
                self.assertTrue(result.condition_values[CONDITIONS[condition_index]])

    def test_all_cutoff_boundaries_are_not_satisfied(self):
        result = classify_choppy(18, .005, .01, 1.0, .70, True)
        self.assertTrue(result.available)
        self.assertFalse(result.is_choppy)
        self.assertEqual(tuple(result.condition_values.values()), (False, False, False, False))

    def test_exactly_two_conditions_make_choppy(self):
        result = classify_choppy(17.9, .004, .01, 1.2, .2, True)
        self.assertTrue(result.available)
        self.assertTrue(result.is_choppy)
        self.assertEqual(result.satisfied_conditions,
                         (CONDITIONS[0], CONDITIONS[1]))

    def test_bos_makes_fourth_condition_false(self):
        result = classify_choppy(20, .01, .02, 1.1, .99, False)
        self.assertFalse(result.condition_values[CONDITIONS[3]])
        self.assertTrue(result.available)
        self.assertFalse(result.is_choppy)

    def test_missing_inputs_are_unknown_not_satisfied_and_may_make_classification_unavailable(self):
        missing = classify_choppy(None, None, None, None, None, None)
        self.assertFalse(missing.available)
        self.assertIsNone(missing.is_choppy)
        self.assertEqual(len(missing.unavailable_reasons), 4)
        undetermined = classify_choppy(17, None, None, 1.2, None, None)
        self.assertFalse(undetermined.available)
        self.assertEqual(undetermined.satisfied_conditions, (CONDITIONS[0],))
        determinate_nonchoppy = classify_choppy(20, .01, .02, 1.2, None, None)
        self.assertTrue(determinate_nonchoppy.available)
        self.assertFalse(determinate_nonchoppy.is_choppy)

    def test_replay_applies_filtered_zero_preserving_score_components_and_is_deterministic(self):
        s = session(5, 14)
        highs = [100.6, 100.7, 100.8, 101.2, 100.8, 100.7, 100.6,
                 100.8, 100.9, 101.3, 100.9, 100.8, 100.7, 100.6]
        lows = [99.5, 99.4, 99.3, 99.4, 99.2, 99.1, 99.3,
                99.5, 99.4, 99.3, 99.0, 99.4, 99.6, 99.7]
        bars = [bar(s, index, high, low, adx=20, day_return=.001,
                    sigma=.01, rvol=.5)
                for index, (high, low) in enumerate(zip(highs, lows))]
        first = replay(bars, trading_sessions=[s])
        second = replay(bars, trading_sessions=[s])
        self.assertEqual(first, second)
        score = first.scores[-1]
        self.assertTrue(score.choppy.available)
        self.assertTrue(score.choppy.is_choppy)
        self.assertTrue(score.result.available)
        self.assertEqual(score.filtered_strength, 0.0)
        self.assertGreater(score.result.strength, 0.0)
        self.assertTrue(any(value is not None and value > 0
                            for value in score.result.components.values()))

    def test_incomplete_replay_candle_has_unavailable_choppy_state(self):
        s = session(5, 1)
        result = replay([bar(s, 0, complete=False)], trading_sessions=[s])
        self.assertFalse(result.scores[0].choppy.available)
        self.assertEqual(result.scores[0].choppy.reason, "incomplete_candle")
        self.assertIsNone(result.scores[0].filtered_strength)

    def test_replay_prefix_is_unchanged_by_future_bars(self):
        s = session(5, 14)
        bars = [bar(s, i, adx=20, day_return=.01, sigma=.02, rvol=1.1)
                for i in range(14)]
        full = replay(bars, trading_sessions=[s])
        prefix = replay(bars[:12], trading_sessions=[s])
        self.assertEqual(full.scores[:12], prefix.scores)


if __name__ == "__main__":
    unittest.main()
