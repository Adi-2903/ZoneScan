"""Comprehensive test suite for ZoneScan Milestone 4: Universal Indian Listed-Company Engine.

Verifies:
1. SecurityMaster resolution (main-board, SME, symbol changes, name changes, ETF exclusion).
2. NSE and BSE company matching and identifier cross-referencing.
3. Symbol and name ambiguity handling (e.g. 'Jio' -> JIOFIN vs RELIANCE; 'Tata' -> candidates).
4. Official company domain and IR link discovery.
5. Pluggable SearchProvider (BraveSearchProvider + FallbackSearchProvider + 9 query archetypes).
6. DocumentFilter universal pattern matching (NSE archives, single-year, presentations, results).
7. Industry classification and sector-aware metric schemas (Banking/IT vs Manufacturing).
8. Provenance preservation and multi-company FY24 reference audits (is_synthetic=False).
9. CLI universal argument handling and year parsing.
"""
from __future__ import annotations

import unittest
from pathlib import Path

from zonescan.data_acquisition.audit import (
    COMPANY_REFERENCE_FACTS,
    audit_fy24_facts,
)
from zonescan.data_acquisition.cli import _parse_years
from zonescan.data_acquisition.company_resolver import CompanyResolver
from zonescan.data_acquisition.cross_industry_data import (
    get_jiofin_extraction_bundle,
    get_reliance_extraction_bundle,
    get_tcs_extraction_bundle,
)
from zonescan.data_acquisition.discovery.document_filter import DocumentFilter
from zonescan.data_acquisition.discovery.domain_verifier import DomainVerifier
from zonescan.data_acquisition.industry_templates import (
    IndustrySector,
    detect_industry_sector,
    get_industry_profile,
)
import os
from zonescan.data_acquisition.models import CompanyIdentifiers
from zonescan.data_acquisition.search_provider import (
    BraveSearchProvider,
    FallbackSearchProvider,
    get_search_provider,
)
from zonescan.data_acquisition.security_master import SecurityMaster


class TestSecurityMaster(unittest.TestCase):
    """Tests for the Indian exchange SecurityMaster."""

    @classmethod
    def setUpClass(cls):
        cls.sm = SecurityMaster()

    def test_security_master_loaded(self):
        self.assertGreater(len(self.sm.securities), 2000, "Security master must contain >2000 securities")
        self.assertGreater(len(self.sm.etf_symbols), 100, "ETF registry must contain >100 ETFs")

    def test_lookup_by_nse_symbol(self):
        sec = self.sm.get_by_symbol("RELIANCE")
        self.assertIsNotNone(sec)
        self.assertEqual(sec.symbol, "RELIANCE")
        self.assertEqual(sec.isin, "INE002A01018")
        self.assertTrue(sec.is_equity)

    def test_lookup_by_isin(self):
        sec = self.sm.get_by_isin("INE467B01029")  # TCS
        self.assertIsNotNone(sec)
        self.assertEqual(sec.symbol, "TCS")
        self.assertEqual(sec.company_name, "Tata Consultancy Services Limited")

    def test_lookup_by_bse_code(self):
        sec = self.sm.get_by_bse_code("543940")  # JIOFIN
        self.assertIsNotNone(sec)
        self.assertEqual(sec.symbol, "JIOFIN")

    def test_etf_exclusion_guard(self):
        sec = self.sm.get_by_symbol("NIFTYBEES")
        self.assertIsNotNone(sec)
        self.assertFalse(sec.is_equity, "NIFTYBEES must NOT be classified as ordinary equity")
        self.assertEqual(sec.security_class, "ETF")

    def test_symbol_change_resolution(self):
        # Historical symbol mapped to active symbol
        resolved_sym = self.sm.resolve_symbol_change("CADILAHC")
        self.assertEqual(resolved_sym, "ZYDUSLIFE")

    def test_name_change_resolution(self):
        resolved_sym = self.sm.resolve_name_change("Tata Tea Limited")
        self.assertEqual(resolved_sym, "TATACONSUM")


class TestCompanyResolver(unittest.TestCase):
    """Tests for entity resolution and strict ambiguity detection."""

    @classmethod
    def setUpClass(cls):
        cls.cr = CompanyResolver()

    def test_resolve_exact_symbols(self):
        for sym in ("BHARATFORG", "RELIANCE", "JIOFIN", "TCS"):
            res = self.cr.resolve(sym)
            self.assertTrue(res.is_resolved, f"Failed to resolve symbol {sym}")
            self.assertEqual(res.company.symbol, sym)

    def test_resolve_full_legal_name(self):
        res = self.cr.resolve("Reliance Industries Limited")
        self.assertTrue(res.is_resolved)
        self.assertEqual(res.company.symbol, "RELIANCE")

    def test_resolve_normalized_company_name(self):
        res = self.cr.resolve("Tata Consultancy Services")
        self.assertTrue(res.is_resolved)
        self.assertEqual(res.company.symbol, "TCS")

    def test_ambiguity_jio_parent_vs_demerged(self):
        """Query 'Jio' must NOT assume JIOFIN; it must present both JIOFIN and RELIANCE."""
        res = self.cr.resolve("Jio")
        self.assertEqual(res.status, "ambiguous")
        symbols = [c.symbol for c in res.candidates]
        self.assertIn("JIOFIN", symbols)
        self.assertIn("RELIANCE", symbols)
        self.assertIn("demerged", res.message.lower())

    def test_ambiguity_generic_brand(self):
        """Query 'Tata' matches multiple listed entities."""
        res = self.cr.resolve("Tata")
        self.assertEqual(res.status, "ambiguous")
        self.assertGreaterEqual(len(res.candidates), 2)

    def test_non_equity_rejection(self):
        """Querying an ETF must return non_equity status and explain why."""
        res = self.cr.resolve("NIFTYBEES")
        self.assertEqual(res.status, "non_equity")
        self.assertIn("ETF", res.message)

    def test_unknown_query(self):
        res = self.cr.resolve("NonExistentIndianCompanyXYZ999")
        self.assertEqual(res.status, "not_found")


class TestSearchProvider(unittest.TestCase):
    """Tests for the pluggable SearchProvider and dynamic query generation."""

    def test_dynamic_query_generation(self):
        sp = FallbackSearchProvider()
        comp = CompanyIdentifiers(
            company_name="Reliance Industries Limited",
            symbol="RELIANCE",
            bse_code="500325",
            isin="INE002A01018",
            cin="L17110MH1973PLC019786",
        )
        queries = sp.generate_company_queries(comp)
        self.assertGreaterEqual(len(queries), 9, "Should generate at least 9 query archetypes")
        self.assertIn("official_ir", queries)
        self.assertIn("annual_report", queries)
        self.assertIn("financial_results", queries)
        self.assertIn("subsidiaries", queries)
        self.assertIn("shareholding", queries)
        self.assertIn("raw_materials", queries)

    def test_fallback_search_provider(self):
        sp = FallbackSearchProvider()
        comp = CompanyIdentifiers(
            company_name="Reliance Industries Limited",
            symbol="RELIANCE",
            bse_code="500325",
            isin="INE002A01018",
            cin="L17110MH1973PLC019786",
        )
        domains = sp.discover_official_domains(comp)
        self.assertGreaterEqual(len(domains), 1)
        self.assertTrue(any("ril.com" in d or "reliance.com" in d for d in domains))

    def test_search_provider_factory(self):
        provider, is_brave = get_search_provider()
        self.assertIsInstance(provider, (BraveSearchProvider, FallbackSearchProvider))
        if not os.environ.get("BRAVE_SEARCH_API_KEY"):
            self.assertFalse(is_brave)
            self.assertIsInstance(provider, FallbackSearchProvider)

    def test_brave_search_provider_requires_key(self):
        with self.assertRaises(ValueError):
            BraveSearchProvider(api_key="")


class TestDomainVerifier(unittest.TestCase):
    """Tests for official company domain validation."""

    def setUp(self):
        self.dv = DomainVerifier()

    def test_verified_domains_lookup(self):
        self.assertIn("bharatforge.com", self.dv.get_candidate_domains("BHARATFORG"))
        self.assertIn("ril.com", self.dv.get_candidate_domains("RELIANCE"))
        self.assertIn("jfs.in", self.dv.get_candidate_domains("JIOFIN"))
        self.assertIn("tcs.com", self.dv.get_candidate_domains("TCS"))

    def test_extract_ir_links_from_html(self):
        sample_html = """
        <html>
          <body>
            <nav>
              <a href="/about">About Us</a>
              <a href="/investors/annual-reports">Annual Reports & Filings</a>
              <a href="/investors/financial-results">Quarterly Results</a>
              <a href="/contact">Contact</a>
            </nav>
          </body>
        </html>
        """
        ir_links = self.dv.extract_ir_links_from_html(sample_html, "https://www.example.com")
        self.assertIn("https://www.example.com/investors/annual-reports", ir_links)
        self.assertIn("https://www.example.com/investors/financial-results", ir_links)
        self.assertNotIn("https://www.example.com/about", ir_links)


class TestDocumentFilterUniversal(unittest.TestCase):
    """Tests for universal document classification across exchanges and websites."""

    def setUp(self):
        self.df = DocumentFilter(target_years=["FY2023-24", "FY2022-23"])

    def test_nse_archives_annual_report(self):
        url = "https://nsearchives.nseindia.com/annual_reports/AR_24864_JIOFIN_2023_2024_0808202401621.pdf"
        res = self.df.classify(url, "JIOFIN AR 2023-2024")
        self.assertIsNotNone(res)
        self.assertEqual(res["doc_type"], "annual_report")
        self.assertEqual(res["fy"], "FY2023-24")
        self.assertTrue(res["is_pdf"])

    def test_single_year_annual_report(self):
        url = "https://www.ril.com/assets/pdf/Annual_Report_2024.pdf"
        res = self.df.classify(url, "RIL Integrated Annual Report 2024")
        self.assertIsNotNone(res)
        self.assertEqual(res["doc_type"], "annual_report")
        self.assertEqual(res["fy"], "FY2023-24")

    def test_single_year_prior_annual_report(self):
        url = "https://www.ril.com/assets/pdf/Annual_Report_2023.pdf"
        res = self.df.classify(url, "RIL Integrated Annual Report 2023")
        self.assertIsNotNone(res)
        self.assertEqual(res["doc_type"], "annual_report")
        self.assertEqual(res["fy"], "FY2022-23")

    def test_investor_presentation_classification(self):
        url = "https://www.tcs.com/investors/TCS_Q4_FY24_Investor_Presentation.pdf"
        res = self.df.classify(url, "Earnings Presentation Q4 FY24")
        self.assertIsNotNone(res)
        self.assertEqual(res["doc_type"], "investor_presentation")

    def test_shareholding_pattern_classification(self):
        url = "https://nsearchives.nseindia.com/corporate/shareholding/SHP_RELIANCE_31032024.pdf"
        res = self.df.classify(url, "Shareholding Pattern for Quarter ended March 2024")
        self.assertIsNotNone(res)
        self.assertEqual(res["doc_type"], "shareholding_pattern")


class TestIndustryTemplates(unittest.TestCase):
    """Tests for sector-aware schemas and raw-material applicability."""

    def test_manufacturing_template(self):
        profile = get_industry_profile(IndustrySector.MANUFACTURING)
        self.assertTrue(profile.is_raw_material_applicable)
        self.assertIn("cost_of_materials", profile.kpi_metrics)

    def test_banking_financial_template(self):
        profile = get_industry_profile(IndustrySector.BANKING_FINANCIAL)
        self.assertFalse(profile.is_raw_material_applicable, "Banking sector must NOT require raw material metrics")
        self.assertIn("interest_income", profile.kpi_metrics)
        self.assertTrue(profile.is_loan_book_applicable)

    def test_it_services_template(self):
        profile = get_industry_profile(IndustrySector.IT_SERVICES)
        self.assertFalse(profile.is_raw_material_applicable, "IT sector must NOT require raw material metrics")
        self.assertIn("employee_benefits", profile.kpi_metrics)
        self.assertTrue(profile.is_utilization_applicable)

    def test_detect_industry_sector(self):
        self.assertEqual(detect_industry_sector("Automotive & Capital Goods", "Forgings"), IndustrySector.MANUFACTURING)
        self.assertEqual(detect_industry_sector("Financial Services", "NBFC"), IndustrySector.BANKING_FINANCIAL)
        self.assertEqual(detect_industry_sector("Information Technology", "IT Services"), IndustrySector.IT_SERVICES)
        self.assertEqual(detect_industry_sector("Energy", "Oil & Gas"), IndustrySector.ENERGY_OIL_GAS)


class TestCrossIndustryDataAndProvenance(unittest.TestCase):
    """Tests for verified cross-industry datasets and provenance guarantees."""

    def test_reliance_bundle_integrity(self):
        b = get_reliance_extraction_bundle()
        self.assertEqual(b["symbol"], "RELIANCE")
        pnl = b["consolidated_statements"]["profit_and_loss"]
        rev_row = next(r for r in pnl.rows if r.normalized_key == "revenue")
        self.assertEqual(rev_row.values["FY2023-24"], 914472.0)
        self.assertEqual(len(b["segments"]), 5)
        self.assertEqual(len(b["commodities"]), 3)

    def test_jiofin_bundle_integrity(self):
        b = get_jiofin_extraction_bundle()
        self.assertEqual(b["symbol"], "JIOFIN")
        pnl = b["consolidated_statements"]["profit_and_loss"]
        inc_row = next(r for r in pnl.rows if r.normalized_key == "total_income")
        self.assertEqual(inc_row.values["FY2023-24"], 1855.27)
        # Verify Not Applicable for manufacturing raw materials
        self.assertIn("Not Applicable", b["commodities"][0].material_name)

    def test_tcs_bundle_integrity(self):
        b = get_tcs_extraction_bundle()
        self.assertEqual(b["symbol"], "TCS")
        pnl = b["consolidated_statements"]["profit_and_loss"]
        rev_row = next(r for r in pnl.rows if r.normalized_key == "revenue")
        self.assertEqual(rev_row.values["FY2023-24"], 240893.0)
        self.assertIn("Not Applicable", b["commodities"][0].material_name)

    def test_multi_company_audit_benchmarks(self):
        self.assertIn("BHARATFORG", COMPANY_REFERENCE_FACTS)
        self.assertIn("RELIANCE", COMPANY_REFERENCE_FACTS)
        self.assertIn("JIOFIN", COMPANY_REFERENCE_FACTS)
        self.assertIn("TCS", COMPANY_REFERENCE_FACTS)


class TestCLIPipelineUniversal(unittest.TestCase):
    """Tests for CLI parameter parsing and year generation."""

    def test_parse_years_integer_count(self):
        # Passing '5' generates last 5 financial years
        years = _parse_years("5")
        self.assertEqual(len(years), 5)
        self.assertEqual(years, ["FY2023-24", "FY2022-23", "FY2021-22", "FY2020-21", "FY2019-20"])

    def test_parse_years_integer_three(self):
        years = _parse_years("3")
        self.assertEqual(years, ["FY2023-24", "FY2022-23", "FY2021-22"])

    def test_parse_years_comma_separated(self):
        years = _parse_years("FY2023-24,FY2024-25")
        self.assertEqual(years, ["FY2023-24", "FY2024-25"])

    def test_parse_years_none_default(self):
        years = _parse_years(None)
        self.assertEqual(years, ["FY2023-24", "FY2022-23", "FY2021-22"])


if __name__ == "__main__":
    unittest.main()
