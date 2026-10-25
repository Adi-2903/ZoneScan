from dataclasses import replace
from datetime import datetime, timedelta
import unittest

from zonescan.models import Candle, ReplayBar
from zonescan.replay import replay


START = datetime.fromisoformat("2026-01-05T09:15:00+05:30")


def scoring_session():
    # Two confirmed rising highs and lows become available at bar 15.
    ranges = [
        (101, 99), (103, 98), (106, 97), (110, 100),
        (106, 99), (103, 98), (105, 96), (104, 98),
        (108, 100), (112, 102), (108, 101), (105, 100),
        (109, 99), (106, 100), (105, 101), (104, 102),
    ]
    bars = []
    for index, (high, low) in enumerate(ranges):
        timestamp = START + timedelta(minutes=5 * index)
        close = low + .5
        candle = Candle("SCORE-X", timestamp, low + .2, high, low, close, 1000)
        bars.append(ReplayBar(
            candle=candle,
            atr=2.0,
            rvol=1.5,
            day_return=(close - 100) / 100,
            daily_sigma20=.02,
            oi_change_daily_pct=.025,
            price_above_vwap=True,
            price_above_ema20=True,
            sector_direction="bullish",
        ))
    return bars


class ReplayScoringTests(unittest.TestCase):
    def test_score_attached_at_candle_timestamp_with_manual_components(self):
        bars = scoring_session()
        result = replay(bars)
        self.assertEqual(len(bars), len(result.scores))
        scored = result.scores[-1]
        self.assertEqual(bars[-1].candle.timestamp, scored.timestamp)
        self.assertEqual("SCORE-X", scored.instrument_id)
        self.assertTrue(scored.result.available)
        self.assertAlmostEqual(5 / 6, scored.result.components["M"])
        self.assertEqual(.25, scored.result.components["V"])
        self.assertEqual(.5, scored.result.components["O"])
        self.assertEqual(1.0, scored.result.components["T"])
        self.assertEqual(1.0, scored.result.components["S"])
        self.assertEqual(0.0, scored.result.components["Z"])
        expected = 100 * (.25 * (5 / 6) + .15 * .25 + .20 * .5 + .20 + .10)
        self.assertAlmostEqual(expected, scored.result.strength, places=12)
        self.assertEqual("long_buildup", scored.result.component_contexts["O"])

    def test_unavailable_inputs_propagate_and_no_zone_is_valid_zero(self):
        bars = scoring_session()
        bars[-1] = replace(bars[-1], daily_sigma20=None, rvol=None,
                           oi_change_daily_pct=None, price_above_ema20=None,
                           sector_direction=None, atr=None)
        result = replay(bars).scores[-1].result
        self.assertFalse(result.available)
        self.assertIsNone(result.strength)
        self.assertEqual({"M", "V", "O", "T", "S"}, set(result.component_reasons))
        self.assertEqual("missing_daily_sigma20", result.component_reasons["M"])
        self.assertEqual("missing_rvol", result.component_reasons["V"])
        self.assertEqual("missing_oi_change_daily_pct", result.component_reasons["O"])
        self.assertEqual("missing_price_above_ema20", result.component_reasons["T"])
        self.assertEqual("missing_sector_classification", result.component_reasons["S"])
        self.assertEqual(0.0, result.components["Z"])

    def test_structure_is_unavailable_until_right_side_swings_close(self):
        bars = scoring_session()
        partial = replay(bars[:15])
        complete = replay(bars)
        preconfirmation = partial.scores[-1]
        self.assertEqual(bars[14].candle.timestamp, preconfirmation.timestamp)
        self.assertFalse(preconfirmation.result.available)
        self.assertEqual("missing_structure", preconfirmation.result.component_reasons["T"])
        self.assertTrue(complete.scores[15].result.available)
        earlier_complete = tuple(score for score in complete.scores
                                 if score.timestamp <= bars[14].candle.timestamp)
        self.assertEqual(partial.scores, earlier_complete)

    def test_future_sector_classification_does_not_change_prior_scores(self):
        bars = scoring_session()
        prefix = replay(bars[:15])
        changed_future = list(bars)
        changed_future[-1] = replace(changed_future[-1], sector_direction="bearish")
        full = replay(changed_future)
        earlier = tuple(score for score in full.scores
                        if score.timestamp <= bars[14].candle.timestamp)
        self.assertEqual(prefix.scores, earlier)

    def test_identical_replay_is_deterministic_and_unfinished_bars_are_unscored(self):
        bars = scoring_session()
        self.assertEqual(replay(bars), replay(bars))
        bars[-1] = replace(bars[-1], candle=replace(bars[-1].candle, complete=False))
        result = replay(bars).scores[-1].result
        self.assertFalse(result.available)
        self.assertEqual("incomplete_candle", result.reason)
        self.assertTrue(all(value is None for value in result.components.values()))


if __name__ == "__main__":
    unittest.main()
