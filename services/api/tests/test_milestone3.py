"""Unit tests for Milestone 3 autonomous discovery and FY24 audit components."""
from __future__ import annotations

import unittest
from typing import List

from zonescan.data_acquisition.audit import (
    AuditResult,
    FY24_REFERENCE_FACTS,
    audit_fy24_facts,
    format_audit_report,
)
from zonescan.data_acquisition.discovery.document_filter import (
    DocumentFilter,
    SeedUrl,
)


class TestDocumentFilter(unittest.TestCase):
    """Tests for the URL classifier / document filter."""

    def setUp(self):
        self.f = DocumentFilter(target_years=["FY2023-24", "FY2024-25"])

    # --- Annual report detection ---

    def test_annual_report_pdf_url(self):
        url = "https://www.bharatforge.com/assets/pdf/investors/Annual_Report_2024.pdf"
        result = self.f.classify(url, "Annual Report 2024")
        self.assertIsNotNone(result)
        self.assertEqual(result["doc_type"], "annual_report")
        self.assertTrue(result["is_pdf"])

    def test_annual_report_fy_extracted(self):
        url = "https://bharatforge.com/investors/annualReport/Annual_Report_23-24.pdf"
        result = self.f.classify(url, "Annual Report 2023-24")
        self.assertIsNotNone(result)
        self.assertEqual(result["fy"], "FY2023-24")

    def test_annual_report_fy25(self):
        url = "https://bharatforge.com/investors/annualReport/Annual_Report_24-25.pdf"
        result = self.f.classify(url, "Annual Report 2024-25")
        self.assertIsNotNone(result)
        self.assertEqual(result["fy"], "FY2024-25")

    def test_annual_report_outside_target_years_rejected(self):
        # FY21-22 is not in target_years=['FY2023-24','FY2024-25']
        url = "https://bharatforge.com/investors/annualReport/Annual_Report_21-22.pdf"
        result = self.f.classify(url, "Annual Report 2021-22")
        self.assertIsNone(result, "URL outside target years should be classified None")

    def test_annual_report_no_year_filter_accepts_all(self):
        # No year restriction
        f2 = DocumentFilter(target_years=[])
        url = "https://bharatforge.com/investors/Annual_Report_19-20.pdf"
        result = f2.classify(url, "Annual Report 2019-20")
        self.assertIsNotNone(result)

    # --- XBRL detection ---

    def test_xbrl_xml_detected(self):
        url = "https://www.bseindia.com/xml-data/corpfiling/attachhis/sample_xbrl.xml"
        result = self.f.classify(url, "XBRL Instance Document")
        self.assertIsNotNone(result)
        self.assertEqual(result["doc_type"], "xbrl_instance")
        self.assertTrue(result["is_xml"])

    # --- Financial results detection ---

    def test_financial_results_detected(self):
        url = "https://nseindia.com/corporate/quarterly-results-FY2023-24.pdf"
        result = self.f.classify(url, "Q4 FY24 Financial Results")
        self.assertIsNotNone(result)
        self.assertEqual(result["doc_type"], "financial_results")

    # --- Shareholding pattern ---

    def test_shareholding_detected(self):
        url = "https://bseindia.com/shareholding-pattern-Q4FY24.pdf"
        result = self.f.classify(url, "Shareholding Pattern March 2024")
        self.assertIsNotNone(result)
        self.assertEqual(result["doc_type"], "shareholding_pattern")

    # --- Noise rejection ---

    def test_css_js_rejected(self):
        self.assertIsNone(self.f.classify("https://example.com/styles.css"))
        self.assertIsNone(self.f.classify("https://example.com/main.js"))
        self.assertIsNone(self.f.classify("https://example.com/logo.png"))

    def test_privacy_terms_rejected(self):
        self.assertIsNone(self.f.classify("https://example.com/privacy-policy"))
        self.assertIsNone(self.f.classify("https://example.com/terms-of-use"))

    # --- is_followable_link ---

    def test_ir_page_is_followable(self):
        self.assertTrue(self.f.is_followable_link(
            "https://www.bharatforge.com/investors/annual-reports",
            "Annual Reports",
        ))

    def test_noise_not_followable(self):
        self.assertFalse(self.f.is_followable_link(
            "https://example.com/gallery/photo.jpg"
        ))

    # --- SeedUrl dataclass ---

    def test_seed_url_dataclass(self):
        seed = SeedUrl(
            url="https://www.bharatforge.com/investors/",
            domain_hint="bharatforge.com",
            allowed_domains=["bharatforge.com"],
            label="Bharat Forge IR Home",
        )
        self.assertEqual(seed.domain_hint, "bharatforge.com")
        self.assertIn("bharatforge.com", seed.allowed_domains)


class TestFY24Audit(unittest.TestCase):
    """Tests for the FY24 reference audit engine."""

    def _make_fact(self, key: str, scope: str, period: str, value: float, unit: str = "INR_CRORES") -> dict:
        return {
            "canonical_key": key,
            "statement_scope": scope,
            "reporting_period": period,
            "value_cr": value,
            "unit": unit,
        }

    def test_all_missing_when_no_facts(self):
        result = audit_fy24_facts([], symbol="BHARATFORG")
        self.assertEqual(result.n_missing, len(FY24_REFERENCE_FACTS))
        self.assertEqual(result.n_matches, 0)
        self.assertEqual(result.n_suspect, 0)

    def test_exact_match_recognized(self):
        facts = [
            self._make_fact("revenue", "consolidated", "FY2023-24", 15_682.071),
        ]
        result = audit_fy24_facts(facts, symbol="BHARATFORG")
        revenue_flag = next((f for f in result.flags if f.canonical_key == "revenue"), None)
        self.assertIsNotNone(revenue_flag)
        self.assertEqual(revenue_flag.severity, "match")

    def test_rounding_deviation_classified_correctly(self):
        # Within 2% but >0.5 Cr
        facts = [
            self._make_fact("total_assets", "consolidated", "FY2023-24", 19_350.0),
        ]
        result = audit_fy24_facts(facts, symbol="BHARATFORG")
        flag = next((f for f in result.flags if f.canonical_key == "total_assets"), None)
        self.assertIsNotNone(flag)
        self.assertIn(flag.severity, ("match", "rounding"))

    def test_large_deviation_classified_suspect(self):
        # >2% deviation
        facts = [
            self._make_fact("total_equity", "consolidated", "FY2023-24", 5_000.0),
        ]
        result = audit_fy24_facts(facts, symbol="BHARATFORG")
        flag = next((f for f in result.flags if f.canonical_key == "total_equity"), None)
        self.assertIsNotNone(flag)
        self.assertEqual(flag.severity, "suspect")

    def test_multiple_facts_correct(self):
        facts = [
            self._make_fact("revenue", "consolidated", "FY2023-24", 15_682.071),
            self._make_fact("cost_of_materials", "consolidated", "FY2023-24", 7_138.381),
            self._make_fact("profit_after_tax", "consolidated", "FY2023-24", 910.159),
            self._make_fact("total_assets", "consolidated", "FY2023-24", 19_349.118),
            self._make_fact("total_equity", "consolidated", "FY2023-24", 7_165.309),
            self._make_fact("cash_and_equivalents", "consolidated", "FY2023-24", 1_315.310),
        ]
        result = audit_fy24_facts(facts, symbol="BHARATFORG")
        self.assertGreaterEqual(result.n_matches, 5)
        self.assertEqual(result.n_suspect, 0)

    def test_unit_conversion_from_lakhs(self):
        # 15_682.071 Cr = 15_682_071 Lakhs / 100
        facts = [
            {
                "canonical_key": "revenue",
                "statement_scope": "consolidated",
                "reporting_period": "FY2023-24",
                "value_cr": None,
                "value_numeric": 15_68_207.1,
                "unit": "INR_LAKHS",
            }
        ]
        result = audit_fy24_facts(facts, symbol="BHARATFORG")
        flag = next((f for f in result.flags if f.canonical_key == "revenue"), None)
        self.assertIsNotNone(flag)
        self.assertIn(flag.severity, ("match", "rounding"))

    def test_format_audit_report_contains_all_keys(self):
        result = audit_fy24_facts([], symbol="BHARATFORG")
        report = format_audit_report(result)
        self.assertIn("revenue", report)
        self.assertIn("total_assets", report)
        self.assertIn("MISSING", report)
        self.assertIn("## FY24 Reference Audit", report)
        self.assertIn("Revenue ≠ Total Income", report)
        self.assertIn("Group PAT ≠ Parent PAT", report)

    def test_pat_parent_distinct_from_group_pat(self):
        """Verify parent PAT and group PAT are treated as separate reference facts."""
        keys = [r.canonical_key for r in FY24_REFERENCE_FACTS]
        self.assertIn("profit_after_tax", keys, "Group PAT must be a reference fact")
        self.assertIn("profit_after_tax_parent", keys, "Parent PAT must be a separate reference fact")
        # They must have DIFFERENT reference values
        group_ref = next(r for r in FY24_REFERENCE_FACTS if r.canonical_key == "profit_after_tax")
        parent_ref = next(r for r in FY24_REFERENCE_FACTS if r.canonical_key == "profit_after_tax_parent")
        self.assertNotEqual(
            group_ref.reference_value_cr,
            parent_ref.reference_value_cr,
            "Group PAT (910.159) and parent PAT (951.128) must not be equal",
        )

    def test_raw_materials_not_confused_with_total_cogs(self):
        """Reference RM consumed ≠ total COGS — verified by note field."""
        rm_ref = next(r for r in FY24_REFERENCE_FACTS if r.canonical_key == "cost_of_materials")
        self.assertIn("NOT total COGS", rm_ref.note)
        self.assertAlmostEqual(rm_ref.reference_value_cr, 7_138.381, places=2)


class TestCLIYearParsing(unittest.TestCase):
    """Tests for the CLI year parsing helper."""

    def test_parse_years_comma_separated(self):
        from zonescan.data_acquisition.cli import _parse_years
        result = _parse_years("FY2023-24,FY2024-25,FY2025-26")
        self.assertEqual(result, ["FY2023-24", "FY2024-25", "FY2025-26"])

    def test_parse_years_default_when_none(self):
        from zonescan.data_acquisition.cli import _parse_years
        result = _parse_years(None)
        self.assertIn("FY2023-24", result)

    def test_parse_years_strips_whitespace(self):
        from zonescan.data_acquisition.cli import _parse_years
        result = _parse_years(" FY2023-24 , FY2024-25 ")
        self.assertEqual(result, ["FY2023-24", "FY2024-25"])


if __name__ == "__main__":
    unittest.main()
