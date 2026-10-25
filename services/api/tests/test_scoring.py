from dataclasses import replace
import unittest

from zonescan.models import ScoreInputs, Zone
from zonescan.scoring import (
    WEIGHTS,
    calculate_move_component,
    calculate_oi_change_pct,
    calculate_oi_component,
    calculate_sector_component,
    calculate_strength,
    calculate_trend_component,
    calculate_volume_component,
    calculate_zone_component,
)


def zone(*, side="bullish", low=108.0, high=109.0, state="fresh", active=True):
    return Zone("zone-1", "TEST", side, low, high, "5m", None, None,
                state=state, active=active)


def inputs(**overrides):
    values = dict(
        day_return=.01,
        daily_sigma20=.02,
        rvol=3.0,
        oi_change_daily_pct=.05,
        direction="bullish",
        price_above_vwap=True,
        price_above_ema20=True,
        structure="bullish",
        sector="bullish",
        current_price=110.0,
        atr=1.0,
        nearest_zone=zone(),
    )
    values.update(overrides)
    return ScoreInputs(**values)


class MoveAndVolumeTests(unittest.TestCase):
    def test_move_component_thresholds(self):
        sigma = .02
        self.assertEqual(0.0, calculate_move_component(0.0, sigma).value)
        self.assertAlmostEqual(1 / 3, calculate_move_component(.5 * sigma, sigma).value)
        self.assertEqual(1.0, calculate_move_component(1.5 * sigma, sigma).value)
        self.assertEqual(1.0, calculate_move_component(2.0 * sigma, sigma).value)
        self.assertEqual(1.0, calculate_move_component(-2.0 * sigma, sigma).value)

    def test_move_component_distinguishes_missing_zero_invalid_and_nonfinite(self):
        self.assertEqual("missing_daily_sigma20", calculate_move_component(.01, None).reason)
        for sigma in (0.0, -0.01):
            self.assertFalse(calculate_move_component(.01, sigma).available)
        for invalid in (float("nan"), float("inf"), -float("inf")):
            result = calculate_move_component(.01, invalid)
            self.assertFalse(result.available)
            self.assertIn("non_finite", result.reason)
            self.assertFalse(calculate_move_component(invalid, .02).available)
        self.assertEqual(0.0, calculate_move_component(0.0, .02).value)

    def test_volume_component_boundaries(self):
        expected = {0.0: 0.0, 1.0: 0.0, 1.5: .25, 2.0: .5,
                    3.0: 1.0, 4.0: 1.0}
        for rvol, value in expected.items():
            with self.subTest(rvol=rvol):
                self.assertEqual(value, calculate_volume_component(rvol).value)
        self.assertEqual("missing_rvol", calculate_volume_component(None).reason)
        for invalid in (-.1, float("nan"), float("inf"), -float("inf")):
            self.assertFalse(calculate_volume_component(invalid).available)


class OpenInterestTests(unittest.TestCase):
    def test_oi_change_percent_requires_positive_reference(self):
        self.assertEqual(.025, calculate_oi_change_pct(102.5, 100).value)
        self.assertEqual(-.025, calculate_oi_change_pct(97.5, 100).value)
        self.assertFalse(calculate_oi_change_pct(100, 0).available)
        self.assertFalse(calculate_oi_change_pct(100, -1).available)
        self.assertFalse(calculate_oi_change_pct(None, 100).available)
        self.assertFalse(calculate_oi_change_pct(float("nan"), 100).available)
        self.assertFalse(calculate_oi_change_pct(1e308, 1e-308).available)
        self.assertEqual(-1.0, calculate_oi_change_pct(0, 100).value)

    def test_oi_magnitude_and_all_four_interpretations(self):
        cases = [
            (.01, .025, "bullish", .5, "long_buildup"),
            (.01, -.025, "bullish", .25, "short_covering"),
            (-.01, .025, "bearish", .5, "short_buildup"),
            (-.01, -.025, "bearish", .25, "long_unwinding"),
            (.01, .05, "bullish", 1.0, "long_buildup"),
            (-.01, .05, "bearish", 1.0, "short_buildup"),
            (.01, -.05, "bullish", .5, "short_covering"),
            (-.01, -.05, "bearish", .5, "long_unwinding"),
            (.01, .10, "bullish", 1.0, "long_buildup"),
            (.01, 0.0, "bullish", 0.0, "no_oi_change"),
        ]
        for day_return, oi_pct, direction, expected, context in cases:
            with self.subTest(day_return=day_return, oi_pct=oi_pct):
                result = calculate_oi_component(day_return, oi_pct, direction)
                self.assertTrue(result.available)
                self.assertAlmostEqual(expected, result.value)
                self.assertEqual(context, result.context)

    def test_oi_unavailable_contexts_are_not_imputed(self):
        self.assertEqual("missing_oi_change_daily_pct",
                         calculate_oi_component(.01, None, "bullish").reason)
        self.assertFalse(calculate_oi_component(.01, float("nan"), "bullish").available)
        self.assertEqual("price_direction_unavailable_for_oi_context",
                         calculate_oi_component(0.0, .025, "bullish").reason)
        self.assertEqual("price_direction_mismatch",
                         calculate_oi_component(.01, .025, "bearish").reason)
        self.assertEqual(0.0, calculate_oi_component(None, 0.0, None).value)


class AlignmentAndZoneTests(unittest.TestCase):
    def test_trend_alignment_documented_combinations(self):
        self.assertEqual(1.0, calculate_trend_component("bullish", True, True, "bullish").value)
        self.assertEqual(0.0, calculate_trend_component("bullish", False, False, "bearish").value)
        self.assertAlmostEqual(2 / 3,
                               calculate_trend_component("bullish", True, False, "bullish").value)
        self.assertEqual(.5, calculate_trend_component("bullish", True, False, "range").value)
        self.assertEqual(1.0, calculate_trend_component("bearish", False, False, "bearish").value)
        self.assertEqual(0.0, calculate_trend_component("bearish", True, True, "bullish").value)
        self.assertEqual(.5, calculate_trend_component("bearish", False, True, "range").value)

    def test_trend_missing_and_invalid_indicators(self):
        self.assertEqual("missing_price_above_vwap",
                         calculate_trend_component("bullish", None, True, "bullish").reason)
        self.assertEqual("missing_price_above_ema20",
                         calculate_trend_component("bullish", True, None, "bullish").reason)
        self.assertEqual("missing_structure",
                         calculate_trend_component("bullish", True, True, None).reason)
        self.assertFalse(calculate_trend_component("bullish", 1, True, "bullish").available)
        self.assertFalse(calculate_trend_component("bullish", True, True, "sideways").available)

    def test_sector_values_and_missing_state(self):
        self.assertEqual(1.0, calculate_sector_component("bullish", "bullish").value)
        self.assertEqual(.5, calculate_sector_component("bullish", "neutral").value)
        self.assertEqual(.5, calculate_sector_component("bearish", "mixed").value)
        self.assertEqual(0.0, calculate_sector_component("bullish", "bearish").value)
        self.assertEqual("missing_sector_classification",
                         calculate_sector_component("bullish", None).reason)
        self.assertEqual("missing_sector_classification",
                         calculate_sector_component(None, None).reason)
        self.assertFalse(calculate_sector_component("bullish", "unknown").available)

    def test_zone_distance_interpolation_and_edges(self):
        expected = {0.0: 1.0, 1.0: 1.0, 2.0: 2 / 3,
                    2.5: .5, 4.0: 0.0, 5.0: 0.0}
        for distance, component in expected.items():
            test_zone = zone(low=110.0 - distance - 1.0,
                             high=110.0 - distance)
            result = calculate_zone_component("bullish", 110.0, 1.0, test_zone)
            with self.subTest(distance=distance):
                self.assertTrue(result.available)
                self.assertAlmostEqual(component, result.value)
        self.assertEqual(1.0, calculate_zone_component("bearish", 100, 1,
                                                       zone(side="bearish", low=100, high=101)).value)

    def test_zone_missing_atr_invalidated_and_wrong_side(self):
        supporting = zone()
        self.assertEqual(0.0, calculate_zone_component("bullish", None, None, None).value)
        self.assertEqual(0.0, calculate_zone_component(None, None, None, None).value)
        self.assertEqual("missing_atr", calculate_zone_component("bullish", 110, None,
                                                                  supporting).reason)
        self.assertEqual("missing_current_price", calculate_zone_component("bullish", None, 1,
                                                                            supporting).reason)
        self.assertEqual("atr_must_be_positive", calculate_zone_component("bullish", 110, 0,
                                                                           supporting).reason)
        for state in ("mitigated", "expired"):
            invalidated = zone(state=state, active=False)
            self.assertEqual(0.0, calculate_zone_component("bullish", None, None,
                                                           invalidated).value)
        wrong_direction = zone(side="bearish")
        self.assertEqual("zone_direction_mismatch",
                         calculate_zone_component("bullish", None, None,
                                                  wrong_direction).context)
        wrong_location = zone(low=120, high=121)
        self.assertEqual("zone_not_below_or_containing_price",
                         calculate_zone_component("bullish", 110, 1,
                                                  wrong_location).context)
        self.assertFalse(calculate_zone_component("bullish", float("inf"), 1,
                                                   supporting).available)
        invalid_bounds = zone(low=120, high=119)
        self.assertEqual("invalid_zone_bounds",
                         calculate_zone_component("bullish", 110, 1,
                                                  invalid_bounds).reason)


class WeightedScoreTests(unittest.TestCase):
    def test_component_weights_minimum_and_maximum_scores(self):
        self.assertEqual(1.0, sum(WEIGHTS.values()))
        with self.assertRaises(TypeError):
            WEIGHTS["M"] = 0.0
        minimum = inputs(day_return=0.0, rvol=0.0, oi_change_daily_pct=0.0,
                        price_above_vwap=False, price_above_ema20=False,
                        structure="bearish", sector="bearish",
                        nearest_zone=zone(side="bearish"))
        minimum_result = calculate_strength(minimum)
        self.assertTrue(minimum_result.available)
        self.assertEqual(0.0, minimum_result.strength)
        self.assertEqual({"M": 0.0, "V": 0.0, "O": 0.0, "T": 0.0, "S": 0.0, "Z": 0.0},
                         minimum_result.components)

        maximum = inputs(day_return=.045, daily_sigma20=.02, rvol=4.0,
                         oi_change_daily_pct=.10)
        maximum_result = calculate_strength(maximum)
        self.assertTrue(maximum_result.available)
        self.assertEqual(100.0, maximum_result.strength)
        self.assertTrue(all(value == 1.0 for value in maximum_result.components.values()))

    def test_manually_calculated_nontrivial_score_and_no_early_rounding(self):
        result = calculate_strength(inputs(
            rvol=1.5, oi_change_daily_pct=-.025,
            price_above_vwap=True, price_above_ema20=False,
            structure="range", sector="neutral",
            nearest_zone=zone(low=106.5, high=107.5),
        ))
        expected = 100 * (.25 * (1 / 3) + .15 * .25 + .20 * .25
                          + .20 * .5 + .10 * .5 + .10 * .5)
        self.assertTrue(result.available)
        self.assertAlmostEqual(expected, result.strength, places=12)
        self.assertAlmostEqual(1 / 3, result.components["M"], places=15)
        self.assertEqual("short_covering", result.component_contexts["O"])
        self.assertEqual("v0.1-score", result.algorithm_version)
        self.assertEqual("2026-10-26.3", result.parameter_version)

    def test_each_component_has_its_documented_weight(self):
        baseline = inputs(day_return=0, rvol=1, oi_change_daily_pct=0,
                          price_above_vwap=False, price_above_ema20=False,
                          structure="bearish", sector="bearish",
                          nearest_zone=zone(side="bearish"))
        base_score = calculate_strength(baseline).strength
        variants = [
            replace(baseline, day_return=.03),
            replace(baseline, rvol=3),
            replace(baseline, day_return=.001, oi_change_daily_pct=.05),
            replace(baseline, price_above_vwap=True, price_above_ema20=True,
                    structure="bullish"),
            replace(baseline, sector="bullish"),
            replace(baseline, nearest_zone=zone(low=109, high=110)),
        ]
        for name, variant in zip(WEIGHTS, variants):
            with self.subTest(component=name):
                reference = baseline
                if name == "O":
                    reference = replace(baseline, day_return=.001)
                increase = calculate_strength(variant).strength - calculate_strength(reference).strength
                self.assertAlmostEqual(WEIGHTS[name] * 100, increase)

    def test_missing_and_invalid_components_preserve_unavailable_reasons(self):
        missing = calculate_strength(inputs(rvol=None))
        self.assertFalse(missing.available)
        self.assertIsNone(missing.strength)
        self.assertIsNone(missing.components["V"])
        self.assertEqual("missing_rvol", missing.component_reasons["V"])
        self.assertEqual(0.0, calculate_strength(inputs(rvol=0)).components["V"])

        cases = [
            inputs(daily_sigma20=0), inputs(rvol=float("nan")),
            inputs(oi_change_daily_pct=float("inf")),
            inputs(current_price=float("nan")), inputs(atr=-1),
        ]
        for case in cases:
            with self.subTest(case=case):
                self.assertFalse(calculate_strength(case).available)

    def test_repeated_calculation_is_identical(self):
        data = inputs(rvol=1.5, oi_change_daily_pct=-.025,
                      nearest_zone=zone(low=107.5, high=108.5))
        self.assertEqual(calculate_strength(data), calculate_strength(data))


if __name__ == "__main__":
    unittest.main()
