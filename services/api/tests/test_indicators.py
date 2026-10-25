from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import unittest

from zonescan.indicators import (aggregate_candles, calculate_indicators,
                                 to_replay_bars)
from zonescan.models import (Candle, FuturesContractMapping, OpenInterestObservation,
                             TradingSession)
from zonescan.replay import replay

IST = ZoneInfo("Asia/Kolkata")


def session(day: int, minutes: int = 60) -> TradingSession:
    start = datetime(2026, 1, day, 9, 15, tzinfo=IST)
    return TradingSession("CASH", start.date(), start, start + timedelta(minutes=minutes))


def minute_candles(s: TradingSession, count: int | None = None, bump: float = 0.0):
    count = count or int((s.closes_at - s.opens_at).total_seconds() // 60)
    result = []
    for i in range(count):
        p = 100 + i + bump
        result.append(Candle("CASH", s.opens_at + timedelta(minutes=i), p, p + 1,
                             p - 1, p + .5, 10))
    return result


class IndicatorTests(unittest.TestCase):
    def test_aggregation_uses_completed_windows_and_session_boundaries(self):
        first, second = session(5, 10), session(6, 10)
        result = aggregate_candles(minute_candles(first) + minute_candles(second),
                                   [first, second], "5m")
        self.assertEqual([c.timestamp for c in result.candles],
                         [first.opens_at + timedelta(minutes=5), first.opens_at + timedelta(minutes=10),
                          second.opens_at + timedelta(minutes=5), second.opens_at + timedelta(minutes=10)])
        self.assertEqual((result.candles[0].open, result.candles[0].high,
                          result.candles[0].low, result.candles[0].close,
                          result.candles[0].volume), (100, 105, 99, 104.5, 50))
        self.assertFalse(result.gaps)

    def test_missing_and_incomplete_minutes_are_reported_without_aggregate(self):
        s = session(5, 10)
        source = minute_candles(s)
        source.pop(2)
        source[6] = Candle("CASH", source[6].timestamp, source[6].open,
                           source[6].high, source[6].low, source[6].close,
                           source[6].volume, complete=False)
        result = aggregate_candles(source, [s], "5m")
        self.assertEqual(len(result.candles), 0)
        self.assertEqual([g.reason for g in result.gaps],
                         ["missing_minute_candle", "incomplete_minute_candle"])

    def test_15m_aggregation_and_duplicate_rejection(self):
        s = session(5, 30)
        result = aggregate_candles(minute_candles(s), [s], "15m")
        self.assertEqual(len(result.candles), 2)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            aggregate_candles(minute_candles(s) + [minute_candles(s)[0]], [s], "5m")

    def test_atr_ema_vwap_day_return_have_expected_values_and_warmups(self):
        s = session(5, 150)
        agg = aggregate_candles(minute_candles(s), [s], "5m")
        frames = calculate_indicators(agg, [s])
        self.assertFalse(frames[0].atr14.available)
        self.assertEqual(frames[-1].atr14.value, 6.0)
        self.assertTrue(frames[-1].ema20.available)
        self.assertTrue(frames[-1].adx14.available)
        self.assertGreaterEqual(frames[-1].adx14.value, 0)
        self.assertEqual(frames[0].day_return.value, .045)
        self.assertEqual(frames[0].vwap.value, frames[0].candle.close)
        self.assertTrue(frames[0].price_above_vwap.value)

    def test_daily_sigma_uses_only_prior_21_daily_closes(self):
        historical_sessions = [session(day, 5) for day in range(1, 22)]
        s = session(27, 5)
        daily = [Candle("CASH", datetime(2026, 1, day, 16, 0, tzinfo=IST),
                        100 + day, 101 + day, 99 + day, 100 + day, 1)
                 for day in range(1, 22)]
        all_sessions = historical_sessions + [s]
        agg = aggregate_candles([c for item in all_sessions for c in minute_candles(item)],
                                all_sessions, "5m")
        result = calculate_indicators(agg, all_sessions, daily_candles=daily)
        current = [frame for frame in result if frame.timestamp.date() == s.session_date][0]
        self.assertTrue(current.daily_sigma20.available)
        self.assertGreater(current.daily_sigma20.value, 0)
        prefix = calculate_indicators(agg, all_sessions, daily_candles=daily[:10])
        current_prefix = [frame for frame in prefix if frame.timestamp.date() == s.session_date][0]
        self.assertFalse(current_prefix.daily_sigma20.available)
        self.assertEqual(current_prefix.daily_sigma20.reason, "missing_daily_candle")

    def test_rvol_requires_twenty_complete_prior_session_baselines(self):
        sessions = [session(day, 5) for day in range(1, 22)]
        all_candles = [c for s in sessions for c in minute_candles(s)]
        agg = aggregate_candles(all_candles, sessions, "5m")
        frames = calculate_indicators(agg, sessions)
        self.assertFalse(frames[0].rvol.available)
        last_session = [f for f in frames if f.timestamp.date() == date(2026, 1, 21)]
        self.assertEqual(last_session[0].rvol.value, 1.0)

    def test_oi_observations_remain_separate_and_contract_changes_are_unavailable(self):
        old, current = session(5, 35), session(6, 35)
        cash = minute_candles(old) + minute_candles(current)
        agg = aggregate_candles(cash, [old, current], "5m")
        observations = []
        for s, contract, val in ((old, "F1", 100), (current, "F2", 120)):
            observations.extend(OpenInterestObservation(contract, c.timestamp, val)
                               for c in minute_candles(s))
        mapping = [FuturesContractMapping("CASH", "F1", old.session_date, old.session_date),
                   FuturesContractMapping("CASH", "F2", current.session_date, current.session_date)]
        frames = calculate_indicators(agg, [old, current], open_interest=observations,
                                      contract_mappings=mapping)
        current_frames = [f for f in frames if f.timestamp.date() == current.session_date]
        self.assertEqual(current_frames[0].oi_change_daily_pct.reason, "futures_contract_changed")
        self.assertFalse(current_frames[0].oi_change_30m_pct.available)

    def test_same_contract_oi_changes_use_exact_daily_and_30_minute_references(self):
        old, current = session(5, 35), session(6, 35)
        sessions = [old, current]
        agg = aggregate_candles(minute_candles(old) + minute_candles(current), sessions, "5m")
        oi = [OpenInterestObservation("F1", c.timestamp, 100)
              for c in minute_candles(old)]
        oi.extend(OpenInterestObservation("F1", c.timestamp,
                                          100 + (c.timestamp - current.opens_at).total_seconds() / 60)
                  for c in minute_candles(current))
        mappings = [FuturesContractMapping("CASH", "F1", old.session_date, current.session_date)]
        frames = calculate_indicators(agg, sessions, open_interest=oi,
                                      contract_mappings=mappings)
        current_frame = [f for f in frames if f.timestamp.date() == current.session_date][-1]
        self.assertAlmostEqual(current_frame.oi_change_daily_pct.value, .34)
        self.assertAlmostEqual(current_frame.oi_change_30m_pct.value, 30 / 104)
        mapped = to_replay_bars((current_frame,))[0]
        self.assertAlmostEqual(mapped.oi_change_30m_pct, 30 / 104)

    def test_future_candles_and_oi_do_not_change_earlier_frames(self):
        s = session(5, 30)
        source = minute_candles(s)
        full = aggregate_candles(source, [s], "5m")
        short_session = TradingSession("CASH", s.session_date, s.opens_at,
                                       s.opens_at + timedelta(minutes=20))
        prefix = aggregate_candles(source[:20], [short_session], "5m")
        mapping = [FuturesContractMapping("CASH", "FUT", s.session_date, s.session_date)]
        oi = [OpenInterestObservation("FUT", c.timestamp, 100 + index)
              for index, c in enumerate(source)]
        all_frames = calculate_indicators(full, [s], open_interest=oi,
                                          contract_mappings=mapping)
        prefix_frames = calculate_indicators(prefix, [short_session], open_interest=oi,
                                             contract_mappings=mapping)
        self.assertEqual(all_frames[:3], prefix_frames[:3])
        altered = source[:20] + [Candle("CASH", c.timestamp, c.open + 50, c.high + 50,
                                        c.low + 50, c.close + 50, c.volume) for c in source[20:]]
        changed_oi = [OpenInterestObservation(o.instrument_id, o.timestamp,
                                             o.value if o.timestamp < s.opens_at + timedelta(minutes=20)
                                             else o.value + 500) for o in oi]
        altered_frames = calculate_indicators(aggregate_candles(altered, [s], "5m"), [s],
                                              open_interest=changed_oi,
                                              contract_mappings=mapping)
        self.assertEqual(all_frames[:3], altered_frames[:3])
        self.assertEqual(all_frames, calculate_indicators(full, [s], open_interest=oi,
                                                         contract_mappings=mapping))
        bars = to_replay_bars(all_frames)
        self.assertEqual(tuple(bar.candle.timestamp for bar in bars),
                         tuple(frame.timestamp for frame in all_frames))
        self.assertEqual(bars[-1].adx14, all_frames[-1].adx14.value)
        self.assertEqual(len(replay(bars).scores), len(bars))

    def test_replay_mapper_preserves_adx_unavailable_reason(self):
        s = session(5, 5)
        agg = aggregate_candles(minute_candles(s), [s], "5m")
        frame = calculate_indicators(agg, [s])[0]
        replay_bar = to_replay_bars((frame,))[0]
        self.assertIsNone(replay_bar.adx14)
        self.assertIn(("adx14", "insufficient_history_or_zero_directional_movement"),
                      replay_bar.indicator_unavailable_reasons)

    def test_missing_oi_and_zero_volume_are_explicit(self):
        s = session(5, 5)
        source = [Candle("CASH", s.opens_at + timedelta(minutes=i), 100, 101, 99, 100, 0)
                  for i in range(5)]
        agg = aggregate_candles(source, [s], "5m")
        frame = calculate_indicators(agg, [s])[0]
        self.assertEqual(frame.vwap.reason, "zero_session_volume")
        self.assertEqual(frame.oi_change_daily_pct.reason, "missing_contract_mapping")


if __name__ == "__main__":
    unittest.main()
