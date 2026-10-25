from dataclasses import replace
from datetime import date, datetime, timedelta
import unittest
from zoneinfo import ZoneInfo

from zonescan.early_move import (EarlyMoveInputs, calculate_burst_15m,
                                 calculate_early_move, calculate_momentum_15m,
                                 calculate_run_penalty)
from zonescan.models import Candle, ReplayBar, TradingSession
from zonescan.replay import replay
from tests.test_replay_scoring import scoring_session

IST = ZoneInfo("Asia/Kolkata")


class EarlyMoveFormulaTests(unittest.TestCase):
    def test_weighted_score_with_component_breakdown(self):
        result = calculate_early_move(EarlyMoveInputs(
            direction="bullish", day_return=.02, daily_sigma20=.02,
            oi_change_30m_pct=.025, current_price=110, price_15m_ago=100,
            atr14_5m=5, current_volume_15m=400, baseline_volume_15m=200))
        self.assertTrue(result.available)
        self.assertEqual(80.0, result.score)
        self.assertEqual({"OI_30m": .5, "Mom_15m": 1.0,
                          "Burst_15m": 1.0, "RunPenalty": 0.0}, result.components)

    def test_momentum_alignment_and_clipping(self):
        self.assertEqual(1.0, calculate_momentum_15m(120, 100, 5, "bullish").value)
        self.assertEqual(0.0, calculate_momentum_15m(90, 100, 5, "bullish").value)
        self.assertEqual(0.0, calculate_momentum_15m(100, 100, 5, "bearish").value)
        self.assertEqual("missing_direction",
                         calculate_momentum_15m(101, 100, 5, None).reason)

    def test_burst_normalization_boundaries_and_invalid_denominator(self):
        cases = ((100, 100, 0.0), (150, 100, .5), (200, 100, 1.0),
                 (500, 100, 1.0))
        for current, baseline, expected in cases:
            with self.subTest(current=current):
                self.assertEqual(expected,
                                 calculate_burst_15m(current, baseline).value)
        self.assertEqual("baseline_volume_15m_must_be_positive",
                         calculate_burst_15m(100, 0).reason)

    def test_run_penalty_boundaries_and_linear_midpoint(self):
        sigma = .02
        self.assertEqual(0, calculate_run_penalty(.03, sigma).value)
        self.assertAlmostEqual(.3, calculate_run_penalty(.045, sigma).value)
        self.assertEqual(.6, calculate_run_penalty(.06, sigma).value)
        self.assertEqual(.6, calculate_run_penalty(-.06, sigma).value)
        self.assertEqual("daily_sigma20_must_be_positive",
                         calculate_run_penalty(.01, 0).reason)

    def test_missing_required_inputs_remain_unavailable_with_reasons(self):
        cases = (
            ("oi_change_30m_pct",), ("day_return",), ("current_price",), ("price_15m_ago",),
            ("atr14_5m",), ("current_volume_15m",),
            ("baseline_volume_15m",), ("daily_sigma20",),
        )
        values = dict(direction="bullish", day_return=.02, daily_sigma20=.02,
                      oi_change_30m_pct=.01, current_price=101, price_15m_ago=100,
                      atr14_5m=2, current_volume_15m=200, baseline_volume_15m=100)
        for (missing,) in cases:
            with self.subTest(missing=missing):
                test_values = dict(values)
                test_values[missing] = None
                result = calculate_early_move(EarlyMoveInputs(**test_values))
                self.assertFalse(result.available)
                self.assertIsNone(result.score)
                self.assertTrue(result.component_reasons)
                self.assertIsNone(result.components[
                    {"oi_change_30m_pct": "OI_30m", "current_price": "Mom_15m",
                     "price_15m_ago": "Mom_15m", "atr14_5m": "Mom_15m",
                     "current_volume_15m": "Burst_15m",
                     "baseline_volume_15m": "Burst_15m",
                     "daily_sigma20": "RunPenalty", "day_return": "RunPenalty"}[missing]])


def replay_fixture():
    template = scoring_session()
    sessions = []
    bars = []
    for day_number in range(1, 22):
        session_day = date(2026, 1, day_number)
        opens_at = datetime(2026, 1, day_number, 9, 15, tzinfo=IST)
        closes_at = opens_at + timedelta(minutes=85 if day_number == 21 else 80)
        sessions.append(TradingSession("EM-X", session_day, opens_at, closes_at))
        for index, source in enumerate(template):
            stamp = opens_at + timedelta(minutes=5 * (index + 1))
            volume = 400 if day_number == 21 and index in (12, 13, 14) else 200
            candle = Candle("EM-X", stamp, source.candle.open, source.candle.high,
                            source.candle.low, source.candle.close, volume)
            bars.append(ReplayBar(candle, 2.0, 1.5, "5m", session_day,
                                  .02, .02, .01, True, True, "bullish", 25,
                                  symbol="EM-X", oi_change_30m_pct=.025))
            if day_number == 21 and index == 15:
                future_time = stamp + timedelta(minutes=5)
                future_candle = Candle("EM-X", future_time, 150, 160, 149, 159, 5000)
                bars.append(ReplayBar(
                    future_candle, 2.0, 10.0, "5m", session_day, .5, .02, .5,
                    True, True, "bearish", 50, symbol="EM-X", oi_change_30m_pct=-.5))
    bars.sort(key=lambda bar: (bar.candle.timestamp, bar.timeframe))
    return bars, sessions


class EarlyMoveReplayTests(unittest.TestCase):
    def test_replay_attaches_timestamped_score_and_repeats_deterministically(self):
        bars, sessions = replay_fixture()
        first = replay(bars, trading_sessions=sessions)
        again = replay(bars, trading_sessions=sessions)
        target_time = sessions[-1].opens_at + timedelta(minutes=80)
        result = next(score.early_move for score in first.scores
                      if score.instrument_id == "EM-X" and score.timeframe == "5m"
                      and score.timestamp == target_time)
        self.assertEqual(first, again)
        self.assertIsNotNone(result)
        self.assertTrue(result.available, result.component_reasons)
        self.assertAlmostEqual(80.0, result.score, places=8)

    def test_future_bars_do_not_change_an_earlier_early_move_result(self):
        bars, sessions = replay_fixture()
        target_time = sessions[-1].opens_at + timedelta(minutes=80)
        prefix = [bar for bar in bars if bar.candle.timestamp <= target_time]
        changed = [replace(bar, candle=replace(
            bar.candle, open=bar.candle.open + 30, high=bar.candle.high + 30,
            low=bar.candle.low + 30, close=bar.candle.close + 30, volume=9000),
                           oi_change_30m_pct=-.75, day_return=-.3)
                   if bar.candle.timestamp > target_time else bar for bar in bars]
        full = replay(changed, trading_sessions=sessions)
        partial = replay(prefix, trading_sessions=sessions)
        expected = next(score.early_move for score in partial.scores
                        if score.timeframe == "5m" and score.timestamp == target_time)
        actual = next(score.early_move for score in full.scores
                      if score.timeframe == "5m" and score.timestamp == target_time)
        self.assertEqual(expected, actual)

    def test_five_minute_score_has_explicit_early_move_unavailable_state(self):
        stamp = datetime.fromisoformat("2026-01-05T09:30:00+05:30")
        bar = ReplayBar(Candle("EM-X", stamp, 100, 101, 99, 100, 100),
                        2, 1, "15m")
        score = replay([bar]).scores[0]
        self.assertFalse(score.early_move.available)
        self.assertEqual("early_move_requires_5m_replay", score.early_move.reason)

    def test_insufficient_baseline_history_is_explicit_in_replay(self):
        source = scoring_session()
        session_day = date(2026, 1, 5)
        opens_at = datetime(2026, 1, 5, 9, 15, tzinfo=IST)
        session = TradingSession("EM-X", session_day, opens_at,
                                 opens_at + timedelta(minutes=80))
        bars = []
        for index, item in enumerate(source):
            stamp = opens_at + timedelta(minutes=5 * (index + 1))
            candle = Candle("EM-X", stamp, item.candle.open, item.candle.high,
                            item.candle.low, item.candle.close, 100)
            bars.append(ReplayBar(candle, 2, 1.2, "5m", session_day,
                                  .02, .02, .01, True, True, "bullish", 25,
                                  oi_change_30m_pct=.02))
        bars.sort(key=lambda item: (item.candle.timestamp, item.timeframe))
        result = replay(bars, trading_sessions=[session])
        last = next(item for item in result.scores
                    if item.timeframe == "5m" and item.timestamp == bars[-1].candle.timestamp)
        self.assertFalse(last.early_move.available)
        self.assertEqual("insufficient_20_prior_sessions",
                         last.early_move.component_reasons["Burst_15m"])


if __name__ == "__main__":
    unittest.main()
