"""Unit and integration test suite for the corporate data acquisition & extraction pipeline."""
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from zoneinfo import ZoneInfo

import openpyxl

from zonescan.data_acquisition.collector import DEFAULT_BHARAT_FORGE, DocumentCollector
from zonescan.data_acquisition.extractor import (
    CompanyReportExtractor,
    match_canonical_metric,
    parse_indian_number,
)
from zonescan.data_acquisition.models import (
    CompanyIdentifiers,
    DocumentMetadata,
    ExtractionIssueItem,
)
from zonescan.data_acquisition.normalizer import FinancialNormalizer
from zonescan.data_acquisition.report_generator import ReportGenerator
from zonescan.financial_facts import FinancialFactStore

IST = ZoneInfo("Asia/Kolkata")


class DataAcquisitionPipelineTests(unittest.TestCase):
    """Test suite for pipeline components, offline fixtures, and boundary constraints."""

    def setUp(self):
        self.company = DEFAULT_BHARAT_FORGE
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_company_identifiers_integrity(self):
        """Verify Bharat Forge pilot identifiers adhere to regulatory masters."""
        self.assertEqual(self.company.symbol, "BHARATFORG")
        self.assertEqual(self.company.bse_code, "500493")
        self.assertEqual(self.company.isin, "INE465A01025")
        self.assertEqual(self.company.cin, "L25209PN1961PLC012046")
        self.assertEqual(self.company.incorporation_year, 1961)

    def test_indian_number_parsing(self):
        """Verify parsing of Indian numbering conventions, brackets, and nil indicators."""
        self.assertEqual(parse_indian_number("15,682.07"), 15682.07)
        self.assertEqual(parse_indian_number("(1,234.56)"), -1234.56)
        self.assertEqual(parse_indian_number("₹ 6,684.32 Cr"), 6684.32)
        self.assertEqual(parse_indian_number("57.38%"), 57.38)
        self.assertIsNone(parse_indian_number("-"))
        self.assertIsNone(parse_indian_number("–"))
        self.assertIsNone(parse_indian_number("nil"))
        self.assertIsNone(parse_indian_number("N.A."))
        self.assertIsNone(parse_indian_number(None))

    def test_canonical_metric_mapping(self):
        """Verify Schedule III / Ind AS pattern matching for core financial lines."""
        key, label = match_canonical_metric("Revenue from Operations", "profit_and_loss")
        self.assertEqual(key, "revenue")
        self.assertEqual(label, "Revenue from Operations")

        key, label = match_canonical_metric("Cost of raw materials consumed", "profit_and_loss")
        self.assertEqual(key, "cost_of_materials")

        key, label = match_canonical_metric("Property, Plant and Equipment", "balance_sheet")
        self.assertEqual(key, "ppe")

        key, label = match_canonical_metric("Total Equity and Liabilities", "balance_sheet")
        self.assertEqual(key, "total_equity_and_liabilities")

        key, label = match_canonical_metric("Net cash flows from operating activities", "cash_flow")
        self.assertEqual(key, "operating_cash_flow")

    def test_extractor_statement_separation(self):
        """Verify standalone and consolidated statements are strictly separated."""
        extractor = CompanyReportExtractor(raw_dir=self.base_dir / "raw", extracted_dir=self.base_dir / "extracted")
        bundle = extractor.extract_all()

        cons_pnl = bundle["consolidated_statements"]["profit_and_loss"]
        stan_pnl = bundle["standalone_statements"]["profit_and_loss"]

        self.assertEqual(cons_pnl.statement_scope, "consolidated")
        self.assertEqual(stan_pnl.statement_scope, "standalone")

        # Consolidated revenue (₹15,682.07 Cr) must be distinct from Standalone revenue (₹8,959.50 Cr)
        cons_rev_row = next(r for r in cons_pnl.rows if r.normalized_key == "revenue")
        stan_rev_row = next(r for r in stan_pnl.rows if r.normalized_key == "revenue")

        self.assertEqual(cons_rev_row.values["FY2023-24"], 15682.07)
        self.assertEqual(stan_rev_row.values["FY2023-24"], 8959.50)
        self.assertNotEqual(cons_rev_row.values["FY2023-24"], stan_rev_row.values["FY2023-24"])

    def test_extractor_intelligence_categories(self):
        """Verify extraction of segments, shareholding, relationships, commodities, and business intel."""
        extractor = CompanyReportExtractor(raw_dir=self.base_dir / "raw", extracted_dir=self.base_dir / "extracted")
        bundle = extractor.extract_all()

        # Segments
        self.assertEqual(len(bundle["segments"]), 4)
        segment_names = {s.segment_name for s in bundle["segments"]}
        self.assertIn("Commercial Vehicles (CV)", segment_names)
        self.assertIn("Defence & Aerospace", segment_names)

        # Shareholding
        self.assertEqual(len(bundle["shareholding"]), 4)
        promoter_holding = next(sh for sh in bundle["shareholding"] if "Promoter" in sh.category)
        self.assertEqual(promoter_holding.holding_pct, 45.25)
        self.assertEqual(promoter_holding.pledged_pct, 0.0)

        # Relationships
        self.assertGreaterEqual(len(bundle["relationships"]), 8)
        rel_types = {r.relationship_type for r in bundle["relationships"]}
        self.assertIn("subsidiary", rel_types)
        self.assertIn("customer", rel_types)

        # Commodities
        self.assertEqual(len(bundle["commodities"]), 4)
        steel = next(c for c in bundle["commodities"] if "Steel" in c.material_name)
        self.assertEqual(steel.share_of_cogs_pct, 62.4)

    def test_normalizer_persists_real_facts(self):
        """Verify normalizer writes non-synthetic facts conforming to persistence schema."""
        fact_store = FinancialFactStore(":memory:")
        normalizer = FinancialNormalizer(fact_store=fact_store)

        extractor = CompanyReportExtractor(raw_dir=self.base_dir / "raw", extracted_dir=self.base_dir / "extracted")
        bundle = extractor.extract_all()

        facts = normalizer.normalize_and_persist(self.company, bundle)
        self.assertGreater(len(facts), 100)

        # Verify all facts carry is_synthetic = False
        for f in facts:
            self.assertFalse(f.is_synthetic, f"Fact {f.fact_id} must have is_synthetic=False")
            self.assertEqual(f.company_id, self.company.cin)
            self.assertEqual(f.unit, "INR_CRORES")

        # Verify facts count in repository
        count_real = fact_store.count_facts(is_synthetic=False)
        count_synth = fact_store.count_facts(is_synthetic=True)
        self.assertEqual(count_real, len(facts))
        self.assertEqual(count_synth, 0)

    def test_report_generator_worksheets_and_json(self):
        """Verify 17-sheet Excel generation, JSON payload, and Markdown research report."""
        docs = [
            DocumentMetadata(
                doc_id="test_doc",
                company_id=self.company.cin,
                symbol=self.company.symbol,
                title="Bharat Forge Test Annual Report",
                source_url="https://example.com/ar.pdf",
                source_website="IR",
                document_type="annual_report",
                reporting_period="FY2023-24",
                file_type="pdf",
                local_path="raw/test.pdf",
                sha256_hash="abcdef1234567890",
                file_size_bytes=1000,
                extraction_status="downloaded",
            )
        ]
        issues = [
            ExtractionIssueItem(
                source_url="https://example.com/bse",
                issue_type="access_restriction",
                description="Test 403 error",
                impact="Minor",
                remediation="Use IR mirror",
            )
        ]

        reporter = ReportGenerator(
            company=self.company,
            base_dir=self.base_dir,
            documents=docs,
            issues=issues,
        )

        extractor = CompanyReportExtractor(raw_dir=self.base_dir / "raw", extracted_dir=self.base_dir / "extracted")
        bundle = extractor.extract_all()
        normalizer = FinancialNormalizer(fact_store=FinancialFactStore(":memory:"))
        payload = normalizer.build_normalized_payload(self.company, bundle)

        deliverables = reporter.generate_all(bundle, payload)

        # 1. JSON file exists and has correct keys
        self.assertTrue(deliverables["json"].exists())
        self.assertGreater(deliverables["json"].stat().st_size, 5000)

        # 2. Markdown report exists and contains required sections
        self.assertTrue(deliverables["markdown"].exists())
        md_text = deliverables["markdown"].read_text(encoding="utf-8")
        self.assertIn("Bharat Forge Limited", md_text)
        self.assertIn("Operating Business Segments", md_text)
        self.assertIn("Raw Material Dependencies", md_text)

        # 3. Excel workbook exists and has exactly 17 worksheets
        self.assertTrue(deliverables["xlsx"].exists())
        wb = openpyxl.load_workbook(deliverables["xlsx"])
        self.assertEqual(len(wb.sheetnames), 17)

        expected_sheets = [
            "Company Profile",
            "Consolidated Financials",
            "Standalone Financials",
            "Profit and Loss",
            "Balance Sheet",
            "Cash Flow",
            "Segment Information",
            "Shareholding",
            "Related Party Transactions",
            "Subsidiaries and Relationships",
            "Raw Materials & Commodities",
            "Business and Operations",
            "Risk Factors",
            "Source Register",
            "Extraction Issues",
            "Data Conflicts",
            "Unmapped Financial Items",
        ]
        for name in expected_sheets:
            self.assertIn(name, wb.sheetnames, f"Expected sheet '{name}' in workbook")


if __name__ == "__main__":
    unittest.main()
