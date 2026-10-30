import math
import sqlite3
import unittest
from datetime import date, datetime
from zoneinfo import ZoneInfo

from zonescan.financial_facts import (
    FactValidationError,
    FinancialFact,
    FinancialFactStore,
    validate_financial_fact,
)

IST = ZoneInfo("Asia/Kolkata")


class FinancialFactsTests(unittest.TestCase):
    """Test suite for financial_facts persistence, provenance, and boundary validation."""

    def setUp(self):
        self.store = FinancialFactStore(":memory:")

    def test_schema_and_indexes_are_created(self):
        """Verify the relational schema, check constraints, and indexes exist."""
        cursor = self.store._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='financial_facts'"
        )
        self.assertIsNotNone(cursor.fetchone(), "Table 'financial_facts' must exist")

        cursor = self.store._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='financial_facts'"
        )
        index_names = {row[0] for row in cursor.fetchall()}
        self.assertIn("idx_facts_company_period", index_names)
        self.assertIn("idx_facts_metric", index_names)
        self.assertIn("idx_facts_synthetic", index_names)

    def test_genuine_traceable_fact_persists_successfully(self):
        """Verify writing and retrieving a genuine traceable fact from an official permitted source."""
        # Genuine fact: Bharat Forge Ltd Audited Consolidated Revenue FY2023-24
        # Source: BSE Filing / Annual Report FY 2023-24, Page 218, Note 23
        fact = self.store.seed_bharat_forge_pilot_fact()

        self.assertEqual(fact.fact_id, "fact-bf-rev-fy24")
        self.assertEqual(fact.company_id, "L25209PN1961PLC012046")
        self.assertEqual(fact.metric, "revenue_from_operations")
        self.assertAlmostEqual(fact.value, 15682.07, places=2)
        self.assertEqual(fact.unit, "INR_CRORES")
        self.assertEqual(fact.financial_period, "FY2023-24")
        self.assertEqual(fact.statement_scope, "consolidated")
        self.assertEqual(fact.evidence_status, "disclosed")
        self.assertFalse(fact.is_synthetic)
        self.assertIn("Page 218, Note 23", fact.page_note_table_reference)
        self.assertEqual(fact.document_date, date(2024, 5, 8))
        self.assertEqual(
            fact.source_url,
            "https://www.bseindia.com/bseplus/AnnualReport/500493/73255500493.pdf",
        )

        # Retrieve and verify round-trip
        retrieved = self.store.get_fact("fact-bf-rev-fy24")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.company_id, "L25209PN1961PLC012046")
        self.assertEqual(retrieved.metric, "revenue_from_operations")
        self.assertAlmostEqual(retrieved.value, 15682.07, places=2)
        self.assertEqual(retrieved.document_date, date(2024, 5, 8))
        self.assertEqual(retrieved.evidence_status, "disclosed")
        self.assertFalse(retrieved.is_synthetic)

    def test_ingestion_validation_rejects_missing_mandatory_fields(self):
        """Boundary validation must reject writes missing any required provenance or identity field."""
        valid_args = dict(
            fact_id="fact-test-01",
            company_id="L25209PN1961PLC012046",
            metric="operating_ebitda",
            value=2608.20,
            unit="INR_CRORES",
            financial_period="FY2023-24",
            statement_scope="consolidated",
            source_document="Annual Report FY 2023-24",
            source_url="https://www.bseindia.com/test.pdf",
            page_note_table_reference="Page 42",
            document_date=date(2024, 5, 8),
            retrieval_timestamp=datetime(2026, 10, 30, 10, 0, tzinfo=IST),
            extraction_method="manual_audited_filing_extract",
            evidence_status="disclosed",
            is_synthetic=False,
        )

        # 1. Missing company identity
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "company_id": ""}))
        self.assertIn("company_id is mandatory", str(ctx.exception))

        with self.assertRaises(FactValidationError):
            self.store.insert_fact(FinancialFact(**{**valid_args, "company_id": "   "}))

        # 2. Missing metric
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "metric": ""}))
        self.assertIn("metric is mandatory", str(ctx.exception))

        # 3. Missing unit
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "unit": ""}))
        self.assertIn("unit is mandatory", str(ctx.exception))

        # 4. Missing financial period
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "financial_period": ""}))
        self.assertIn("financial_period is mandatory", str(ctx.exception))

        # 5. Missing source document
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "source_document": ""}))
        self.assertIn("source_document is mandatory", str(ctx.exception))

        # 6. Missing source date
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "document_date": None}))
        self.assertIn("document_date is mandatory", str(ctx.exception))

        # 7. Missing or invalid evidence status
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "evidence_status": ""}))
        self.assertIn("evidence_status must be one of", str(ctx.exception))

        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "evidence_status": "fabricated"}))
        self.assertIn("evidence_status must be one of", str(ctx.exception))

        # 8. Non-finite values (NaN / Inf)
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "value": float("nan")}))
        self.assertIn("value must be a finite numeric float", str(ctx.exception))

        with self.assertRaises(FactValidationError):
            self.store.insert_fact(FinancialFact(**{**valid_args, "value": float("inf")}))

        # 9. Invalid statement scope
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(FinancialFact(**{**valid_args, "statement_scope": "hypothetical"}))
        self.assertIn("statement_scope must be one of", str(ctx.exception))

        # 10. Naive (non-timezone aware) retrieval timestamp
        with self.assertRaises(FactValidationError) as ctx:
            self.store.insert_fact(
                FinancialFact(
                    **{**valid_args, "retrieval_timestamp": datetime(2026, 10, 30, 10, 0)}
                )
            )
        self.assertIn("retrieval_timestamp must be timezone-aware", str(ctx.exception))

    def test_database_constraints_reject_direct_sql_violations(self):
        """Verify that direct raw SQL insert bypassing the Python validator triggers DB-level rejection."""
        # Test 1: Empty company_id violating CHECK constraint
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._conn:
                self.store._conn.execute(
                    """
                    INSERT INTO financial_facts (
                        fact_id, company_id, metric, value, unit, financial_period,
                        statement_scope, source_document, document_date,
                        retrieval_timestamp, extraction_method, evidence_status, created_at
                    ) VALUES ('raw-01', '', 'metric_a', 100.0, 'INR', 'FY24', 'consolidated', 'doc_a', '2024-05-08', '2026-10-30T10:00:00+05:30', 'manual', 'disclosed', '2026-10-30T10:00:00+05:30')
                    """
                )

        # Test 2: Invalid evidence status violating CHECK constraint
        with self.assertRaises(sqlite3.IntegrityError):
            with self.store._conn:
                self.store._conn.execute(
                    """
                    INSERT INTO financial_facts (
                        fact_id, company_id, metric, value, unit, financial_period,
                        statement_scope, source_document, document_date,
                        retrieval_timestamp, extraction_method, evidence_status, created_at
                    ) VALUES ('raw-02', 'COMP123', 'metric_a', 100.0, 'INR', 'FY24', 'consolidated', 'doc_a', '2024-05-08', '2026-10-30T10:00:00+05:30', 'manual', 'unverified_rumor', '2026-10-30T10:00:00+05:30')
                    """
                )

    def test_strict_separation_of_synthetic_and_real_facts(self):
        """Ensure real factual records are strictly partitioned from synthetic prototypes."""
        # Insert real fact
        self.store.seed_bharat_forge_pilot_fact()

        # Insert synthetic fact
        synthetic_fact = FinancialFact(
            fact_id="fact-syn-rev-01",
            company_id="SYN-COMP-01",
            metric="revenue_from_operations",
            value=1825.40,
            unit="INR_CRORES",
            financial_period="FY25 (Demo Model)",
            statement_scope="consolidated",
            source_document="[Synthetic Fixture] Annual Report FY25 (Demo)",
            source_url=None,
            page_note_table_reference="[Demo] Note 24",
            document_date=date(2025, 6, 15),
            retrieval_timestamp=datetime(2026, 10, 30, 10, 0, tzinfo=IST),
            extraction_method="synthetic_prototype",
            evidence_status="disclosed",
            is_synthetic=True,
            verification_notes="Synthetic demonstration record.",
        )
        self.store.insert_fact(synthetic_fact)

        self.assertEqual(self.store.count_facts(), 2)
        self.assertEqual(self.store.count_facts(is_synthetic=False), 1)
        self.assertEqual(self.store.count_facts(is_synthetic=True), 1)

        # Querying real company returns only real fact
        real_facts = self.store.get_facts_for_company(
            "L25209PN1961PLC012046", is_synthetic=False
        )
        self.assertEqual(len(real_facts), 1)
        self.assertEqual(real_facts[0].fact_id, "fact-bf-rev-fy24")
        self.assertFalse(real_facts[0].is_synthetic)

        # Querying synthetic company returns only synthetic fact
        syn_facts = self.store.get_facts_for_company("SYN-COMP-01", is_synthetic=True)
        self.assertEqual(len(syn_facts), 1)
        self.assertEqual(syn_facts[0].fact_id, "fact-syn-rev-01")
        self.assertTrue(syn_facts[0].is_synthetic)


if __name__ == "__main__":
    unittest.main()
