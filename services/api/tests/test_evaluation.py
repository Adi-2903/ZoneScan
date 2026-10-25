from dataclasses import replace
from datetime import date, datetime, timedelta
import unittest

from zonescan.evaluation import (DatasetProvenance, HistoricalDataset,
                                HistoricalSession, evaluate, validate_dataset)
from zonescan.models import Candle, ReplayBar

START = datetime.fromisoformat("2026-01-05T09:15:00+05:30")


def dataset(bars=None, *, synthetic=True, authorized=True):
    bars = tuple(bars if bars is not None else [
        ReplayBar(Candle("X", START + timedelta(minutes=5*i), 100, 102, 99, 101, 1000),
                  1.0, 1.2, session_date=date(2026, 1, 5), day_return=.01,
                  daily_sigma20=.02, oi_change_daily_pct=0.0,
                  price_above_vwap=True, price_above_ema20=True, sector_direction=None)
        for i in range(1, 16)])
    return HistoricalDataset(
        DatasetProvenance("fixture-1", "fixture", "local-fixture", "internal-fixture-permission",
                          authorized, synthetic),
        (("X", "EXAMPLE"),),
        (HistoricalSession(date(2026, 1, 5), START,
                           START + timedelta(minutes=75), ("X",)),), bars)


class EvaluationTests(unittest.TestCase):
    def test_validation_reports_gaps_and_missing_oi(self):
        source = dataset()
        bad = replace(source, bars=(source.bars[0], replace(source.bars[1],
                     oi_change_daily_pct=None), *source.bars[3:]))
        report = validate_dataset(bad)
        self.assertTrue(report.valid)
        self.assertEqual(1, report.missing_oi_count)
        self.assertTrue(report.missing_intervals)
        self.assertIn("oi_missing_for_some_bars", report.warnings)

    def test_malformed_provenance_duplicates_order_and_timezone_rejected(self):
        source = dataset()
        no_permission = replace(source, provenance=replace(source.provenance,
                                  permitted_for_internal_evaluation=False))
        self.assertIn("dataset_not_permitted_for_internal_evaluation",
                      validate_dataset(no_permission).errors)
        duplicate = replace(source, bars=(source.bars[0], source.bars[0]))
        self.assertIn("duplicate_candle", validate_dataset(duplicate).errors)
        unordered = replace(source, bars=(source.bars[1], source.bars[0]))
        self.assertIn("candle_ordering_invalid", validate_dataset(unordered).errors)
        wrong_symbol = replace(source, bars=(replace(source.bars[0], candle=replace(
            source.bars[0].candle, instrument_id="OTHER")),))
        self.assertIn("instrument_mapping_missing", validate_dataset(wrong_symbol).errors)
        with self.assertRaises(ValueError):
            Candle("X", datetime(2026, 1, 5, 9, 20), 100, 102, 99, 101, 10)

    def test_synthetic_replay_is_deterministic_and_performance_is_unavailable(self):
        data = dataset()
        first, second = evaluate(data), evaluate(data)
        self.assertEqual(first, second)
        self.assertEqual(len(data.bars), len(first.observations))
        observation = first.observations[0]
        self.assertFalse(observation.forward_return_30m.available)
        self.assertEqual("synthetic_dataset_not_performance_eligible",
                         observation.forward_return_30m.reason)
        self.assertFalse(observation.maximum_favorable_atr.available)
        # Production replay still reports its timestamped score and missing sector.
        self.assertEqual(data.bars[0].candle.timestamp, observation.timestamp)
        self.assertIn("missing_sector_classification", observation.unavailable_reasons.values())

    def test_no_future_inputs_change_prior_score(self):
        data = dataset()
        prefix = evaluate(replace(data, bars=data.bars[:8]))
        changed = list(data.bars)
        changed[-1] = replace(changed[-1], sector_direction="bullish", rvol=100.0)
        full = evaluate(replace(data, bars=tuple(changed)))
        prior = tuple(row for row in full.observations if row.timestamp <= data.bars[7].candle.timestamp)
        self.assertEqual(prefix.replay.scores, tuple(s for s in full.replay.scores
                         if s.timestamp <= data.bars[7].candle.timestamp))
        self.assertEqual(tuple(row.score for row in prefix.observations),
                         tuple(row.score for row in prior))


if __name__ == "__main__":
    unittest.main()
