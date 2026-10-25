from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import unittest

from zonescan.liquidity import equal_level_for_swing
from zonescan.models import Candle, ReplayBar, Swing, TradingSession
from zonescan.replay import replay

IST = ZoneInfo("Asia/Kolkata")


def ts(day: int, minute: int) -> datetime:
    return datetime(2026, 1, day, 9, 15, tzinfo=IST) + timedelta(minutes=minute)


def session(day: int, minutes: int) -> TradingSession:
    start = ts(day, 0)
    return TradingSession("X", start.date(), start, start + timedelta(minutes=minutes))


def bar(day: int, minute: int, high: float, low: float, close: float,
        *, atr: float | None = 1.0, complete: bool = True) -> ReplayBar:
    timestamp = ts(day, minute)
    candle = Candle("X", timestamp, close, high, low, close, 100, complete=complete)
    return ReplayBar(candle, atr, 1.0, "5m", date(2026, 1, day))


def prior_day_bars():
    return [bar(5, 5, 110, 90, 100), bar(5, 10, 108, 92, 100)]


class LiquidityTests(unittest.TestCase):
    def test_equal_high_low_tolerance_uses_outer_cluster_extreme(self):
        high_a = Swing(1, ts(5, 5), 100.0, "high", ts(5, 15))
        high_b = Swing(2, ts(5, 10), 100.9, "high", ts(5, 20))
        high, reason = equal_level_for_swing("X", "5m", high_b, (high_a, high_b), 10.0)
        self.assertIsNone(reason)
        self.assertEqual((high.kind, high.side, high.price), ("equal_high", "above", 100.9))
        low_a = Swing(3, ts(5, 25), 90.0, "low", ts(5, 35))
        low_b = Swing(4, ts(5, 30), 89.1, "low", ts(5, 40))
        low, _ = equal_level_for_swing("X", "5m", low_b, (low_a, low_b), 10.0)
        self.assertEqual((low.kind, low.side, low.price), ("equal_low", "below", 89.1))
        self.assertEqual(equal_level_for_swing("X", "5m", high_b, (high_a, high_b), None)[1],
                         "equal_levels_require_positive_atr14_5m")

    def test_confirmed_swing_levels_appear_only_at_confirmation_timestamp(self):
        highs = [5, 6, 7, 10, 7, 6, 5]
        bars = []
        for index, high in enumerate(highs):
            timestamp = ts(5, 5 * (index + 1))
            candle = Candle("X", timestamp, high - 1, high, high - 2, high - 1, 100)
            bars.append(ReplayBar(candle, 1.0, 1.0, "5m", date(2026, 1, 5)))
        prefix = replay(bars[:6])
        complete = replay(bars)
        swing_levels = [level for level in complete.liquidity_levels if level.kind == "swing_high"]
        self.assertFalse(swing_levels[:-1])
        self.assertEqual(len(swing_levels), 1)
        self.assertEqual(swing_levels[0].formed_at, bars[3].candle.timestamp)
        self.assertEqual(swing_levels[0].confirmed_at, bars[-1].candle.timestamp)
        self.assertFalse(any(level.kind == "swing_high" for level in prefix.liquidity_levels))

    def test_replay_forms_equal_high_pool_only_when_second_swing_is_confirmed(self):
        highs = [100, 101, 102, 110, 102, 101, 100, 101, 102, 110.05, 102, 101, 100]
        bars = []
        for index, high in enumerate(highs):
            timestamp = ts(5, 5 * (index + 1))
            candle = Candle("X", timestamp, high - 1, high, high - 2, high - 1, 100)
            bars.append(ReplayBar(candle, 1.0, 1.0, "5m", date(2026, 1, 5)))
        before_confirmation = replay(bars[:12])
        after_confirmation = replay(bars)
        self.assertFalse(any(level.kind == "equal_high" for level in before_confirmation.liquidity_levels))
        equal = [level for level in after_confirmation.liquidity_levels if level.kind == "equal_high"]
        self.assertEqual(len(equal), 1)
        self.assertEqual(equal[0].price, 110.05)
        self.assertEqual(equal[0].confirmed_at, bars[-1].candle.timestamp)

    def test_previous_week_extremes_require_prior_week_session_history(self):
        prior_sessions = [session(day, 5) for day in range(5, 10)]
        current = session(12, 10)
        bars = []
        for index, prior in enumerate(prior_sessions):
            bars.append(bar(prior.session_date.day, 5, 100 + index, 90 - index, 95))
        bars.extend([bar(12, 5, 105, 85, 95), bar(12, 10, 104, 86, 95)])
        result = replay(bars, trading_sessions=prior_sessions + [current])
        levels = {level.kind: level.price for level in result.liquidity_levels}
        self.assertEqual(levels["pwh"], 104)
        self.assertEqual(levels["pwl"], 86)

    def test_prior_day_levels_expire_when_they_are_no_longer_previous_day(self):
        day5, day6, day7 = session(5, 10), session(6, 10), session(7, 10)
        bars = prior_day_bars() + [bar(6, 5, 105, 95, 100), bar(6, 10, 106, 94, 100),
                                   bar(7, 5, 105, 95, 100)]
        result = replay(bars, trading_sessions=[day5, day6, day7])
        yesterday_level = next(level for level in result.liquidity_levels
                               if level.kind == "pdh" and level.confirmed_at.date() == date(2026, 1, 6))
        self.assertEqual(yesterday_level.state, "expired")
        self.assertEqual(yesterday_level.expired_at, day7.opens_at)

    def test_previous_day_levels_and_bull_bear_sweeps_emit_chronologically(self):
        previous, current = session(5, 10), session(6, 20)
        bars = prior_day_bars() + [
            bar(6, 5, 111, 89, 100),  # crosses both prior levels, returns inside
            bar(6, 10, 105, 95, 100),
            bar(6, 15, 106, 94, 100),
            bar(6, 20, 107, 93, 100),
        ]
        result = replay(bars, trading_sessions=[previous, current])
        levels = {level.kind: level for level in result.liquidity_levels}
        self.assertEqual(levels["pdh"].state, "swept")
        self.assertEqual(levels["pdl"].state, "swept")
        sweeps = [event for event in result.events if event.kind == "liquidity_swept"]
        self.assertEqual(len(sweeps), 2)
        self.assertTrue(all(event.timestamp == ts(6, 5) for event in sweeps))

    def test_sweep_can_confirm_within_three_completed_candles(self):
        previous, current = session(5, 10), session(6, 25)
        bars = prior_day_bars() + [bar(6, 5, 111, 100, 111),
                                    bar(6, 10, 112, 105, 111),
                                    bar(6, 15, 110, 100, 109)]
        result = replay(bars, trading_sessions=[previous, current])
        pdh = next(level for level in result.liquidity_levels if level.kind == "pdh")
        self.assertEqual(pdh.state, "swept")
        self.assertEqual(pdh.swept_at, ts(6, 15))

    def test_unreturned_excursion_invalidates_after_three_bars(self):
        previous, current = session(5, 10), session(6, 25)
        bars = prior_day_bars() + [bar(6, 5, 111, 100, 111),
                                    bar(6, 10, 112, 105, 111),
                                    bar(6, 15, 113, 106, 112)]
        result = replay(bars, trading_sessions=[previous, current])
        pdh = next(level for level in result.liquidity_levels if level.kind == "pdh")
        self.assertEqual(pdh.state, "invalidated")
        self.assertEqual(pdh.invalidated_at, ts(6, 15))

    def test_missing_candle_breaks_pending_sweep_window_explicitly(self):
        previous, current = session(5, 10), session(6, 25)
        bars = prior_day_bars() + [bar(6, 5, 111, 100, 111),
                                    bar(6, 15, 110, 100, 109)]
        result = replay(bars, trading_sessions=[previous, current])
        pdh = next(level for level in result.liquidity_levels if level.kind == "pdh")
        self.assertEqual(pdh.state, "unavailable")
        self.assertEqual(pdh.unavailable_reason, "missing_candle_during_sweep_window")
        self.assertTrue(any(e.kind == "data_gap" for e in result.events))

    def test_first_fifteen_minute_levels_wait_for_range_close_and_are_causal(self):
        current = session(6, 30)
        bars = [bar(6, 5, 101, 99, 100), bar(6, 10, 104, 98, 101),
                bar(6, 15, 103, 97, 102), bar(6, 20, 105, 96, 104),
                bar(6, 25, 106, 95, 105), bar(6, 30, 107, 94, 106)]
        prefix = replay(bars[:2], trading_sessions=[current])
        full = replay(bars, trading_sessions=[current])
        self.assertFalse(any(level.kind.startswith("opening_range") for level in prefix.liquidity_levels))
        opening = [level for level in full.liquidity_levels if level.kind.startswith("opening_range")]
        self.assertEqual({level.kind: level.price for level in opening},
                         {"opening_range_high": 104, "opening_range_low": 97})
        self.assertEqual({level.formed_at for level in opening}, {ts(6, 0)})
        self.assertEqual({level.confirmed_at for level in opening}, {ts(6, 15)})
        self.assertEqual(prefix.events, tuple(e for e in full.events if e.timestamp <= ts(6, 10)))

    def test_missing_session_calendar_reports_period_levels_unavailable(self):
        result = replay([bar(6, 5, 105, 95, 100)])
        self.assertTrue(any(event.kind == "liquidity_unavailable" and
                            event.detail == "trading_session_calendar_missing"
                            for event in result.events))

    def test_incomplete_prior_session_does_not_create_day_levels(self):
        previous, current = session(5, 10), session(6, 10)
        result = replay([bar(5, 5, 110, 90, 100), bar(6, 5, 105, 95, 100)],
                        trading_sessions=[previous, current])
        self.assertFalse(any(level.kind in ("pdh", "pdl") for level in result.liquidity_levels))
        self.assertTrue(any(event.detail == "previous_day_history_incomplete"
                            for event in result.events))

    def test_incomplete_candle_during_pending_sweep_marks_unavailable(self):
        previous, current = session(5, 10), session(6, 20)
        bars = prior_day_bars() + [bar(6, 5, 111, 100, 111),
                                    bar(6, 10, 112, 100, 111, complete=False)]
        result = replay(bars, trading_sessions=[previous, current])
        pdh = next(level for level in result.liquidity_levels if level.kind == "pdh")
        self.assertEqual(pdh.state, "unavailable")
        self.assertEqual(pdh.unavailable_reason, "incomplete_candle_during_sweep_window")

    def test_replay_is_deterministic_and_levels_remain_outside_score_inputs(self):
        previous, current = session(5, 10), session(6, 20)
        bars = prior_day_bars() + [bar(6, 5, 111, 89, 100), bar(6, 10, 105, 95, 100),
                                   bar(6, 15, 106, 94, 100), bar(6, 20, 107, 93, 100)]
        first = replay(bars, trading_sessions=[previous, current])
        second = replay(bars, trading_sessions=[previous, current])
        self.assertEqual(first, second)
        self.assertEqual(len(first.scores), len(bars))
        self.assertEqual(first.scores, replay(bars).scores)


if __name__ == "__main__":
    unittest.main()
