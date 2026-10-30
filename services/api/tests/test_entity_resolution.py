import sqlite3
import unittest
from datetime import date

from zonescan.entity_resolution import (
    CompanyIdentifierRecord,
    CompanyRecord,
    EntityResolutionError,
    EntityResolver,
)


class EntityResolutionTests(unittest.TestCase):
    """Test suite for deterministic entity resolution, point-in-time ISIN mapping, and merge guards (FI-007)."""

    def setUp(self):
        self.resolver = EntityResolver(":memory:")
        self.resolver.seed_verified_corporate_actions()

    def test_schema_and_constraints_exist(self):
        """Verify companies and company_identifiers tables and constraints exist."""
        cursor = self.resolver._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('companies', 'company_identifiers')"
        )
        table_names = {row[0] for row in cursor.fetchall()}
        self.assertEqual(table_names, {"companies", "company_identifiers"})

    def test_real_isin_change_regression_tata_steel_split(self):
        """Regression test on independently verified real ISIN change case:

        Tata Steel Limited (CIN: L27100MH1907PLC000260) underwent a 10:1 stock split
        with record date July 29, 2022 (NSE Circular Ref: NSE/CML/2022/35).
        - Pre-split ISIN: INE081A01012 (valid until 2022-07-28)
        - Post-split ISIN: INE081A01020 (valid from 2022-07-29)
        """
        pre_split_date = date(2022, 6, 15)
        record_date = date(2022, 7, 29)
        post_split_date = date(2023, 1, 10)

        # 1. On pre-split date:
        # Pre-split ISIN resolves to Tata Steel
        company_pre = self.resolver.resolve_isin("INE081A01012", as_of=pre_split_date)
        self.assertIsNotNone(company_pre)
        self.assertEqual(company_pre.company_id, "comp-tata-steel")
        self.assertEqual(company_pre.cin, "L27100MH1907PLC000260")
        self.assertEqual(company_pre.canonical_name, "Tata Steel")

        # Post-split ISIN did not exist yet as of pre_split_date -> must resolve to None
        company_not_yet = self.resolver.resolve_isin("INE081A01020", as_of=pre_split_date)
        self.assertIsNone(company_not_yet, "Post-split ISIN must not resolve prior to its valid_from date")

        # 2. On post-split date:
        # Post-split ISIN resolves to Tata Steel
        company_post = self.resolver.resolve_isin("INE081A01020", as_of=post_split_date)
        self.assertIsNotNone(company_post)
        self.assertEqual(company_post.company_id, "comp-tata-steel")
        self.assertEqual(company_post.cin, "L27100MH1907PLC000260")

        # Old pre-split ISIN expired as of 2022-07-28 -> must resolve to None as of post_split_date
        company_expired = self.resolver.resolve_isin("INE081A01012", as_of=post_split_date)
        self.assertIsNone(company_expired, "Pre-split ISIN must not resolve as active after its valid_to date")

        # 3. Exact boundary on Record Date (2022-07-29)
        company_boundary = self.resolver.resolve_isin("INE081A01020", as_of=record_date)
        self.assertIsNotNone(company_boundary)
        self.assertEqual(company_boundary.company_id, "comp-tata-steel")

        # 4. Audit trail: Both ISINs exist in company ISIN history with evidence and validity dates
        history = self.resolver.get_isin_history("comp-tata-steel")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].identifier_value, "INE081A01012")
        self.assertEqual(history[0].valid_to, date(2022, 7, 28))
        self.assertIn("NSE/CML/2022/35", history[0].source)
        self.assertEqual(history[0].evidence_status, "disclosed")

        self.assertEqual(history[1].identifier_value, "INE081A01020")
        self.assertEqual(history[1].valid_from, date(2022, 7, 29))
        self.assertIsNone(history[1].valid_to)

    def test_similar_names_are_never_merged(self):
        """Invariant: Never merge companies simply because their names look similar (FI-007).

        "Tata Steel Limited" and "Tata Steel Long Products Limited" share words
        and parentage, but are distinct legal corporate entities with different CINs and ISINs.
        """
        # Resolve by CIN
        tata_steel = self.resolver.resolve_cin("L27100MH1907PLC000260")
        tata_long = self.resolver.resolve_cin("L27102OR1982PLC001091")

        self.assertIsNotNone(tata_steel)
        self.assertIsNotNone(tata_long)
        self.assertNotEqual(tata_steel.company_id, tata_long.company_id)
        self.assertNotEqual(tata_steel.cin, tata_long.cin)
        self.assertNotEqual(tata_steel.canonical_name, tata_long.canonical_name)

        # Invariant check prevents merging them
        self.resolver.prevent_merge_similar_names(tata_steel.company_id, tata_long.company_id)

        # Resolve by exact ISIN
        comp_by_isin1 = self.resolver.resolve_isin("INE081A01020")
        comp_by_isin2 = self.resolver.resolve_isin("INE374A01013")
        self.assertEqual(comp_by_isin1.company_id, "comp-tata-steel")
        self.assertEqual(comp_by_isin2.company_id, "comp-tata-steel-long")
        self.assertNotEqual(comp_by_isin1.company_id, comp_by_isin2.company_id)

    def test_exact_name_matching_rejects_fuzzy_merge(self):
        """Fuzzy or ambiguous names must never return a merged or guessed entity."""
        # Exact match works
        exact = self.resolver.resolve_by_exact_name("Tata Steel Limited")
        self.assertIsNotNone(exact)
        self.assertEqual(exact.company_id, "comp-tata-steel")

        exact_long = self.resolver.resolve_by_exact_name("Tata Steel Long Products Limited")
        self.assertIsNotNone(exact_long)
        self.assertEqual(exact_long.company_id, "comp-tata-steel-long")

        # Incomplete / ambiguous substring must return None (never guess or merge)
        ambiguous = self.resolver.resolve_by_exact_name("Tata")
        self.assertIsNone(ambiguous)

        fuzzy = self.resolver.resolve_by_exact_name("Tata Steel Ltd.")
        # Does not match exact canonical/legal name
        self.assertIsNone(fuzzy)

    def test_registration_validation_rules(self):
        """Validate boundary checks on company and identifier registration."""
        # Empty company ID
        with self.assertRaises(EntityResolutionError):
            self.resolver.register_company(
                CompanyRecord(
                    company_id="",
                    canonical_name="Invalid",
                    legal_name="Invalid Ltd",
                    cin="L12345MH2020PLC123456",
                )
            )

        # Duplicate CIN constraint violation
        with self.assertRaises(EntityResolutionError):
            self.resolver.register_company(
                CompanyRecord(
                    company_id="comp-dup-cin",
                    canonical_name="Duplicate CIN Corp",
                    legal_name="Duplicate CIN Corp Ltd",
                    cin="L27100MH1907PLC000260",  # Same as Tata Steel
                )
            )

        # Inverted validity dates (valid_to < valid_from)
        with self.assertRaises(EntityResolutionError) as ctx:
            self.resolver.register_identifier(
                CompanyIdentifierRecord(
                    company_id="comp-tata-steel",
                    identifier_type="isin",
                    identifier_value="INE999A01099",
                    valid_from=date(2023, 1, 1),
                    valid_to=date(2022, 1, 1),  # Invalid inverted window
                    source="Test Circular",
                    evidence_status="disclosed",
                )
            )
        self.assertIn("cannot precede valid_from", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
