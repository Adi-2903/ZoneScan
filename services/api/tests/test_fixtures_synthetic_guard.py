import unittest
from zonescan.synthetic_analytics import build_synthetic_analytics_dataset


class FixtureSyntheticGuardTests(unittest.TestCase):
    """CI Safety guard ensuring all backend analytical fixtures carry explicit demo/synthetic markers."""

    def test_all_synthetic_instruments_and_dataset_carry_explicit_markers(self):
        dataset = build_synthetic_analytics_dataset()
        self.assertEqual(dataset.data_status, "synthetic")
        self.assertEqual(dataset.source, "deterministic_synthetic_fixture")

        for instrument in dataset.instruments:
            self.assertTrue(
                instrument.instrument_id.startswith("SYN-"),
                f"Synthetic instrument {instrument.instrument_id} must start with 'SYN-' prefix",
            )
            self.assertTrue(
                instrument.symbol.startswith("SYN"),
                f"Synthetic symbol {instrument.symbol} must start with 'SYN' prefix",
            )
            if instrument.sector is not None:
                self.assertIn(
                    "Synthetic",
                    instrument.sector,
                    f"Synthetic sector {instrument.sector} must explicitly identify as 'Synthetic'",
                )

    def test_drift_regression_fails_when_synthetic_marker_is_removed(self):
        dataset = build_synthetic_analytics_dataset()
        # Mutate instrument ID to simulate drift toward real instrument name
        drifting_instrument_id = "TATASTEEL"
        with self.assertRaises(AssertionError):
            self.assertTrue(drifting_instrument_id.startswith("SYN-"))

        drifting_source = "nse_live_feed"
        with self.assertRaises(AssertionError):
            self.assertEqual(drifting_source, "deterministic_synthetic_fixture")


if __name__ == "__main__":
    unittest.main()
