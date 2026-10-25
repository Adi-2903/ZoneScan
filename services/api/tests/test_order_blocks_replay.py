from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
import unittest

from zonescan.models import Candle, ReplayBar, Swing, Zone
from zonescan.order_blocks import (OrderBlockParameters, detect_order_blocks,
                                  resolve_zone_overlap, update_zone_lifecycle)
from zonescan.replay import replay


BASE = datetime(2026, 1, 5, 4, 0, tzinfo=timezone.utc)  # 09:30 Asia/Kolkata


def candle(index, open_, high, low, close, *, day=0, instrument="X", complete=True):
    timestamp = BASE + timedelta(days=day, minutes=index * 5)
    return Candle(instrument, timestamp, open_, high, low, close, 1000,
                  complete=complete)


def bullish_setup():
    specs = [
        (9, 11, 8, 10), (10, 12, 9, 11), (11, 13, 10, 12),
        (19, 21, 18, 20), (11, 13, 10, 12), (10, 12, 9, 11),
        (9, 11, 8, 10), (10.5, 12, 9, 10), (10, 32, 9, 31),
    ]
    return [ReplayBar(candle(i, *spec), 5.0, 1.5) for i, spec in enumerate(specs)]


def bearish_setup():
    specs = [
        (12, 13, 10, 11), (11, 12, 9, 10), (10, 11, 8, 9),
        (3, 4, 2, 3), (10, 11, 8, 9), (11, 12, 9, 10),
        (12, 13, 10, 11), (10, 12, 9, 11), (11, 12, 1, 1.5),
    ]
    return [ReplayBar(candle(i, *spec), 5.0, 1.5) for i, spec in enumerate(specs)]


class OrderBlockTests(unittest.TestCase):
    def confirmed_setup_swings(self, bars):
        from zonescan.structure import confirmed_swings
        return confirmed_swings(tuple(bar.candle for bar in bars), decision_time=bars[-1].candle.timestamp)

    def detect_last(self, bars, swing_override=None):
        swings = swing_override if swing_override is not None else self.confirmed_setup_swings(bars[:7])
        return detect_order_blocks(tuple(bars), swings, bars[-1].candle.timestamp)

    def test_valid_bullish_zone_and_preceding_bearish_candle(self):
        bars = bullish_setup()
        zones = self.detect_last(bars)
        self.assertEqual(1, len(zones))
        zone = zones[0]
        self.assertEqual("bullish", zone.side)
        self.assertEqual((9, 12), (zone.low, zone.high))
        self.assertEqual(bars[8].candle.timestamp, zone.formed_at)
        self.assertEqual(bars[8].candle.timestamp, zone.recognized_at)

    def test_valid_bearish_zone_and_preceding_bullish_candle(self):
        bars = bearish_setup()
        zones = self.detect_last(bars)
        self.assertEqual(1, len(zones))
        self.assertEqual("bearish", zones[0].side)
        self.assertEqual((9, 12), (zones[0].low, zones[0].high))

    def test_three_candle_fair_value_gap_confirmation(self):
        bars = bullish_setup()
        bars[-1:] = [
            ReplayBar(candle(8, 10, 12, 9, 11), 5, 1.5),
            ReplayBar(candle(9, 13, 16, 13, 15), 5, 1.5),
            ReplayBar(candle(10, 17, 32, 17, 31), 5, 1.5),
        ]
        zones = self.detect_last(bars)
        self.assertEqual(1, len(zones))
        self.assertTrue(zones[0].has_fvg)

    def test_insufficient_displacement_volume_swing_and_missing_inputs_block(self):
        bars = bullish_setup()
        self.assertEqual((), self.detect_last([*bars[:8], replace(bars[8], atr=20)]))
        self.assertEqual((), self.detect_last([*bars[:8], replace(bars[8], rvol=1.19)]))
        self.assertEqual((), self.detect_last([*bars[:8], replace(bars[8], atr=None)]))
        self.assertEqual((), self.detect_last([*bars[:8], replace(bars[8], rvol=None)]))
        self.assertEqual((), self.detect_last(bars, swing_override=()))
        no_break = Swing(3, bars[3].candle.timestamp, 40, "high",
                         bars[6].candle.timestamp)
        self.assertEqual((), self.detect_last(bars, swing_override=(no_break,)))

    def test_unfinished_candle_cannot_form_zone(self):
        bars = bullish_setup()
        bars[-1] = replace(bars[-1], candle=replace(bars[-1].candle, complete=False))
        self.assertEqual((), self.detect_last(bars))

    def test_missing_opposite_candle_blocks_zone(self):
        bars = bullish_setup()
        bars[7] = replace(bars[7], candle=replace(bars[7].candle, close=11.5))
        self.assertEqual((), self.detect_last(bars))

    def test_repeated_processing_is_idempotent(self):
        bars = bullish_setup()
        first, second = self.detect_last(bars), self.detect_last(bars)
        self.assertEqual(first, second)
        self.assertEqual(first[0].zone_id, second[0].zone_id)

    def test_zone_lifecycle_fresh_tested_mitigated_and_no_reactivation(self):
        zone = Zone("z", "X", "bullish", 9, 12, "5m", BASE, BASE)
        fresh = update_zone_lifecycle(zone, ReplayBar(candle(1, 13, 14, 12.5, 13), 1, 1), 0, 0)
        self.assertEqual("fresh", fresh.state)
        tested = update_zone_lifecycle(fresh, ReplayBar(candle(2, 13, 13.5, 10, 12.5), 1, 1), 0, 0)
        self.assertEqual("tested", tested.state)
        self.assertEqual(candle(2, 13, 13.5, 10, 12.5).timestamp, tested.last_touched_at)
        mitigated = update_zone_lifecycle(tested, ReplayBar(candle(3, 10, 10, 8, 8.5), 1, 1), 0, 0)
        self.assertEqual("mitigated", mitigated.state)
        unchanged = update_zone_lifecycle(mitigated, ReplayBar(candle(4, 10, 13, 8, 12), 1, 1), 0, 0)
        self.assertEqual(mitigated, unchanged)

    def test_bearish_mitigation_and_gap_through_zone(self):
        zone = Zone("z", "X", "bearish", 9, 12, "5m", BASE, BASE)
        mitigated = update_zone_lifecycle(zone, ReplayBar(candle(1, 13, 14, 12.5, 13.5), 1, 1), 0, 0)
        self.assertEqual("mitigated", mitigated.state)

    def test_expiry_counts_observed_trading_sessions_not_calendar_days(self):
        zone = Zone("z", "X", "bullish", 9, 12, "5m", BASE, BASE)
        # Four subsequent observed sessions; calendar gaps do not add phantom sessions.
        still_fresh = update_zone_lifecycle(zone, ReplayBar(candle(1, 13, 14, 13, 13, day=6), 1, 1), 0, 4)
        self.assertEqual("fresh", still_fresh.state)
        expired = update_zone_lifecycle(zone, ReplayBar(candle(1, 13, 14, 13, 13, day=7), 1, 1), 0, 5)
        self.assertEqual("expired", expired.state)
        self.assertFalse(expired.active)

    def test_overlap_prefers_15m_and_active_cap_is_deterministic(self):
        old_5m = Zone("5", "X", "bullish", 10, 14, "5m", BASE, BASE)
        new_15m = Zone("15", "X", "bullish", 12, 16, "15m", BASE+timedelta(minutes=1), BASE+timedelta(minutes=1))
        zones, accepted = resolve_zone_overlap((old_5m,), new_15m)
        self.assertIsNotNone(accepted)
        self.assertFalse(zones[0].active)
        self.assertTrue(zones[1].active)
        self.assertIsNone(resolve_zone_overlap(zones, old_5m)[1])
        params = OrderBlockParameters(maximum_active_per_side=2)
        third = replace(new_15m, zone_id="3", timeframe="5m", formed_at=BASE+timedelta(minutes=2))
        capped, _ = resolve_zone_overlap((replace(old_5m, low=30, high=31),
                                           replace(new_15m, low=40, high=41)), third, params)
        self.assertLessEqual(sum(z.active for z in capped), 2)


class ReplayTests(unittest.TestCase):
    def test_zone_emitted_only_after_swing_and_displacement_are_known(self):
        bars = bullish_setup()
        early = replay(bars[:8])
        self.assertFalse(any(event.kind == "zone_created" for event in early.events))
        full = replay(bars)
        created = [event for event in full.events if event.kind == "zone_created"]
        self.assertEqual(1, len(created))
        self.assertEqual(bars[-1].candle.timestamp, created[0].timestamp)
        self.assertEqual(bars[-1].candle.timestamp, full.zones[0].recognized_at)
        swing_event = next(event for event in full.events if event.kind == "swing_confirmed")
        self.assertLess(swing_event.timestamp, created[0].timestamp)

    def test_future_candle_does_not_change_earlier_events(self):
        bars = bullish_setup()
        prefix = replay(bars[:8])
        full = replay(bars)
        self.assertEqual(prefix.events, tuple(event for event in full.events
                                               if event.timestamp <= bars[7].candle.timestamp))

    def test_replay_is_deterministic_and_missing_history_is_explicitly_insufficient(self):
        bars = bullish_setup()
        self.assertEqual(replay(bars), replay(bars))
        self.assertFalse(replay(bars[:6]).zones)
        missing = [*bars[:8], replace(bars[8], atr=None)]
        self.assertFalse(replay(missing).zones)

    def test_replay_rejects_unordered_and_duplicate_bars(self):
        bars = bullish_setup()
        with self.assertRaisesRegex(ValueError, "ordered"):
            replay([bars[1], bars[0]])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            replay([bars[0], bars[0]])

    def test_missing_same_session_candles_emit_gap_without_backfill(self):
        bars = bullish_setup()
        result = replay([bars[0], bars[2]])
        gaps = [event for event in result.events if event.kind == "data_gap"]
        self.assertEqual(1, len(gaps))
        self.assertEqual((), result.swings)
        self.assertEqual((), result.zones)

    def test_replay_tracks_test_and_mitigation_events(self):
        bars = bullish_setup()
        zone_created = bars[-1].candle.timestamp
        bars.extend([
            ReplayBar(candle(9, 13, 13.5, 10, 12.5), 5, 1.5),
            ReplayBar(candle(10, 10, 10.5, 8, 8.5), 5, 1.5),
        ])
        result = replay(bars)
        changes = [event.state for event in result.events if event.kind == "zone_state_changed"]
        self.assertEqual(["tested", "mitigated"], changes)
        self.assertEqual("mitigated", result.zones[0].state)
        self.assertGreater(zone_created, bars[7].candle.timestamp)
        self.assertEqual(len(bars), len(result.scores))
        score_timestamps = {item.timestamp for item in result.scores}
        self.assertTrue(all(event.timestamp in score_timestamps
                            for event in result.events
                            if event.kind in ("zone_created", "zone_state_changed")))


if __name__ == "__main__":
    unittest.main()
