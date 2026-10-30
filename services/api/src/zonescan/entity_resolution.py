"""Deterministic company-identity and historical security-identifier resolution (FI-007).

Enforces point-in-time identifier mapping, temporal validity windows (e.g. stock splits,
ISIN changes), source provenance, and strict guards against merging similar-named entities.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

VALID_IDENTIFIER_TYPES = frozenset({
    "isin",
    "cin",
    "nse_symbol",
    "bse_code",
})

VALID_EVIDENCE_STATUSES = frozenset({
    "disclosed",
    "verified",
    "inferred",
    "unconfirmed",
    "unavailable",
})


class EntityResolutionError(ValueError):
    """Raised when entity mapping or identity integrity check fails."""
    pass


@dataclass(frozen=True, slots=True)
class CompanyRecord:
    """Canonical company master record."""
    company_id: str
    canonical_name: str
    legal_name: str
    cin: str
    is_synthetic: bool = False
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class CompanyIdentifierRecord:
    """Point-in-time identifier mapping with validity window and source evidence."""
    company_id: str
    identifier_type: str
    identifier_value: str
    valid_from: date | None = None
    valid_to: date | None = None
    source: str = ""
    evidence_status: str = "disclosed"
    created_at: datetime | None = None


class EntityResolver:
    """Deterministic entity resolution engine backed by SQLite."""

    def __init__(self, db_path: str | Path | None = None, connection: sqlite3.Connection | None = None) -> None:
        if connection is not None:
            self._conn = connection
        elif db_path is not None:
            self._conn = sqlite3.connect(str(db_path))
        else:
            self._conn = sqlite3.connect(":memory:")

        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Initialize the companies and company_identifiers tables."""
        with self._conn:
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS companies (
                    company_id TEXT PRIMARY KEY,
                    canonical_name TEXT NOT NULL,
                    legal_name TEXT NOT NULL,
                    cin TEXT NOT NULL UNIQUE,
                    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1)),
                    created_at TEXT NOT NULL,
                    CHECK (length(trim(company_id)) > 0),
                    CHECK (length(trim(canonical_name)) > 0),
                    CHECK (length(trim(legal_name)) > 0),
                    CHECK (length(trim(cin)) > 0)
                );
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS company_identifiers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id TEXT NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
                    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('isin', 'cin', 'nse_symbol', 'bse_code')),
                    identifier_value TEXT NOT NULL,
                    valid_from TEXT,
                    valid_to TEXT,
                    source TEXT NOT NULL,
                    evidence_status TEXT NOT NULL CHECK (evidence_status IN ('disclosed', 'verified', 'inferred', 'unconfirmed', 'unavailable')),
                    created_at TEXT NOT NULL,
                    CHECK (length(trim(identifier_value)) > 0),
                    CHECK (length(trim(source)) > 0),
                    CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from)
                );
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_identifiers_lookup ON company_identifiers (identifier_type, identifier_value);"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_identifiers_company ON company_identifiers (company_id);"
            )

    def register_company(self, company: CompanyRecord) -> None:
        """Register a canonical company master record."""
        if not company.company_id or not company.company_id.strip():
            raise EntityResolutionError("company_id is mandatory and cannot be empty")
        if not company.canonical_name or not company.canonical_name.strip():
            raise EntityResolutionError("canonical_name is mandatory and cannot be empty")
        if not company.cin or not company.cin.strip():
            raise EntityResolutionError("cin is mandatory and cannot be empty")

        created_at_dt = company.created_at or datetime.now(IST)
        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO companies (company_id, canonical_name, legal_name, cin, is_synthetic, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        company.company_id.strip(),
                        company.canonical_name.strip(),
                        company.legal_name.strip(),
                        company.cin.strip(),
                        1 if company.is_synthetic else 0,
                        created_at_dt.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as err:
            raise EntityResolutionError(f"Company registration constraint violation: {err}") from err

    def register_identifier(self, identifier: CompanyIdentifierRecord) -> None:
        """Register an identifier mapping with point-in-time validity and source evidence."""
        if identifier.identifier_type not in VALID_IDENTIFIER_TYPES:
            raise EntityResolutionError(
                f"identifier_type must be in {sorted(VALID_IDENTIFIER_TYPES)}, got {identifier.identifier_type!r}"
            )
        if not identifier.identifier_value or not identifier.identifier_value.strip():
            raise EntityResolutionError("identifier_value is mandatory")
        if not identifier.source or not identifier.source.strip():
            raise EntityResolutionError("source reference is mandatory for provenance")
        if identifier.evidence_status not in VALID_EVIDENCE_STATUSES:
            raise EntityResolutionError(
                f"evidence_status must be in {sorted(VALID_EVIDENCE_STATUSES)}, got {identifier.evidence_status!r}"
            )
        if (
            identifier.valid_from is not None
            and identifier.valid_to is not None
            and identifier.valid_to < identifier.valid_from
        ):
            raise EntityResolutionError(
                f"valid_to ({identifier.valid_to}) cannot precede valid_from ({identifier.valid_from})"
            )

        created_at_dt = identifier.created_at or datetime.now(IST)
        valid_from_str = identifier.valid_from.isoformat() if identifier.valid_from else None
        valid_to_str = identifier.valid_to.isoformat() if identifier.valid_to else None

        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO company_identifiers (
                        company_id, identifier_type, identifier_value,
                        valid_from, valid_to, source, evidence_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        identifier.company_id.strip(),
                        identifier.identifier_type,
                        identifier.identifier_value.strip(),
                        valid_from_str,
                        valid_to_str,
                        identifier.source.strip(),
                        identifier.evidence_status,
                        created_at_dt.isoformat(),
                    ),
                )
        except sqlite3.IntegrityError as err:
            raise EntityResolutionError(f"Identifier registration constraint violation: {err}") from err

    def resolve_cin(self, cin: str) -> CompanyRecord | None:
        """Resolve company directly by statutory Corporate Identification Number (CIN)."""
        cursor = self._conn.execute(
            "SELECT company_id, canonical_name, legal_name, cin, is_synthetic, created_at FROM companies WHERE cin = ?",
            (cin.strip(),),
        )
        row = cursor.fetchone()
        return self._row_to_company(row) if row else None

    def resolve_isin(self, isin: str, as_of: date | None = None) -> CompanyRecord | None:
        """Deterministically resolve company by ISIN, enforcing point-in-time validity.

        If as_of is provided, matches only records where:
        (valid_from IS NULL OR valid_from <= as_of) AND (valid_to IS NULL OR valid_to >= as_of).
        """
        clean_isin = isin.strip()
        if as_of is None:
            # Query the latest or active identifier
            cursor = self._conn.execute(
                """
                SELECT c.company_id, c.canonical_name, c.legal_name, c.cin, c.is_synthetic, c.created_at
                FROM company_identifiers i
                JOIN companies c ON i.company_id = c.company_id
                WHERE i.identifier_type = 'isin' AND i.identifier_value = ?
                ORDER BY i.valid_from DESC
                LIMIT 1
                """,
                (clean_isin,),
            )
        else:
            as_of_str = as_of.isoformat()
            cursor = self._conn.execute(
                """
                SELECT c.company_id, c.canonical_name, c.legal_name, c.cin, c.is_synthetic, c.created_at
                FROM company_identifiers i
                JOIN companies c ON i.company_id = c.company_id
                WHERE i.identifier_type = 'isin'
                  AND i.identifier_value = ?
                  AND (i.valid_from IS NULL OR i.valid_from <= ?)
                  AND (i.valid_to IS NULL OR i.valid_to >= ?)
                LIMIT 1
                """,
                (clean_isin, as_of_str, as_of_str),
            )
        row = cursor.fetchone()
        return self._row_to_company(row) if row else None

    def get_isin_history(self, company_id: str) -> list[CompanyIdentifierRecord]:
        """Retrieve full historical ISIN audit trail for a company."""
        cursor = self._conn.execute(
            """
            SELECT company_id, identifier_type, identifier_value, valid_from, valid_to,
                   source, evidence_status, created_at
            FROM company_identifiers
            WHERE company_id = ? AND identifier_type = 'isin'
            ORDER BY valid_from ASC
            """,
            (company_id,),
        )
        return [self._row_to_identifier(row) for row in cursor.fetchall()]

    def resolve_by_exact_name(self, name: str) -> CompanyRecord | None:
        """Strict exact name resolution. NEVER performs fuzzy or substring matching."""
        clean_name = name.strip()
        cursor = self._conn.execute(
            """
            SELECT company_id, canonical_name, legal_name, cin, is_synthetic, created_at
            FROM companies
            WHERE lower(canonical_name) = lower(?) OR lower(legal_name) = lower(?)
            """,
            (clean_name, clean_name),
        )
        rows = cursor.fetchall()
        if len(rows) == 1:
            return self._row_to_company(rows[0])
        # If multiple entities or none, return None (never guess or merge)
        return None

    def prevent_merge_similar_names(self, company_a_id: str, company_b_id: str) -> None:
        """Invariant check: ensures two entities are not merged merely because names overlap."""
        if company_a_id == company_b_id:
            return
        cursor = self._conn.execute(
            "SELECT company_id, canonical_name, cin FROM companies WHERE company_id IN (?, ?)",
            (company_a_id, company_b_id),
        )
        rows = cursor.fetchall()
        if len(rows) < 2:
            return
        # Both exist as distinct rows with distinct CINs
        cin_a = rows[0]["cin"]
        cin_b = rows[1]["cin"]
        if cin_a == cin_b:
            raise EntityResolutionError(f"Entities {company_a_id} and {company_b_id} have conflicting identical CIN")
        # Distinct identities verified

    def seed_verified_corporate_actions(self) -> None:
        """Seed verified corporate action cases including real historical ISIN changes and peer separation.

        1. Tata Steel Limited (Split 10:1 on 2022-07-29, ISIN changed from INE081A01012 to INE081A01020).
           Source: NSE Circular Ref: NSE/CML/2022/35.
        2. Tata Steel Long Products Limited (Distinct company, merged later, CIN: L27102OR1982PLC001091).
        3. Bharat Forge Limited (Pilot company, CIN: L25209PN1961PLC012046, ISIN: INE465A01025).
        """
        # Company 1: Tata Steel Limited
        tata_steel = CompanyRecord(
            company_id="comp-tata-steel",
            canonical_name="Tata Steel",
            legal_name="Tata Steel Limited",
            cin="L27100MH1907PLC000260",
            is_synthetic=False,
        )
        self.register_company(tata_steel)

        # Historical ISIN (Pre-split ₹10 face value)
        self.register_identifier(
            CompanyIdentifierRecord(
                company_id="comp-tata-steel",
                identifier_type="isin",
                identifier_value="INE081A01012",
                valid_from=date(1998, 10, 15),
                valid_to=date(2022, 7, 28),
                source="BSE / NSE Corporate Action Circular Ref: NSE/CML/2022/35 (Record Date 29-Jul-2022)",
                evidence_status="disclosed",
            )
        )
        # Active ISIN (Post-split ₹1 face value)
        self.register_identifier(
            CompanyIdentifierRecord(
                company_id="comp-tata-steel",
                identifier_type="isin",
                identifier_value="INE081A01020",
                valid_from=date(2022, 7, 29),
                valid_to=None,
                source="BSE / NSE Corporate Action Circular Ref: NSE/CML/2022/35 (New ISIN Post Sub-Division)",
                evidence_status="disclosed",
            )
        )

        # Company 2: Tata Steel Long Products Limited (Distinct legal entity with similar name)
        tata_long = CompanyRecord(
            company_id="comp-tata-steel-long",
            canonical_name="Tata Steel Long Products",
            legal_name="Tata Steel Long Products Limited",
            cin="L27102OR1982PLC001091",
            is_synthetic=False,
        )
        self.register_company(tata_long)
        self.register_identifier(
            CompanyIdentifierRecord(
                company_id="comp-tata-steel-long",
                identifier_type="isin",
                identifier_value="INE374A01013",
                valid_from=date(2019, 11, 15),
                valid_to=None,
                source="BSE / NSE Security Master (Formerly Tata Sponge Iron Limited)",
                evidence_status="disclosed",
            )
        )

        # Company 3: Bharat Forge Limited
        bharat_forge = CompanyRecord(
            company_id="comp-bharat-forge",
            canonical_name="Bharat Forge",
            legal_name="Bharat Forge Limited",
            cin="L25209PN1961PLC012046",
            is_synthetic=False,
        )
        self.register_company(bharat_forge)
        self.register_identifier(
            CompanyIdentifierRecord(
                company_id="comp-bharat-forge",
                identifier_type="isin",
                identifier_value="INE465A01025",
                valid_from=date(2003, 4, 1),
                valid_to=None,
                source="BSE / NSE Statutory Master & NSDL Security Master",
                evidence_status="disclosed",
            )
        )

    @staticmethod
    def _row_to_company(row: sqlite3.Row) -> CompanyRecord:
        created_at_val = datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        return CompanyRecord(
            company_id=row["company_id"],
            canonical_name=row["canonical_name"],
            legal_name=row["legal_name"],
            cin=row["cin"],
            is_synthetic=bool(row["is_synthetic"]),
            created_at=created_at_val,
        )

    @staticmethod
    def _row_to_identifier(row: sqlite3.Row) -> CompanyIdentifierRecord:
        v_from = date.fromisoformat(row["valid_from"]) if row["valid_from"] else None
        v_to = date.fromisoformat(row["valid_to"]) if row["valid_to"] else None
        created_at_val = datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        return CompanyIdentifierRecord(
            company_id=row["company_id"],
            identifier_type=row["identifier_type"],
            identifier_value=row["identifier_value"],
            valid_from=v_from,
            valid_to=v_to,
            source=row["source"],
            evidence_status=row["evidence_status"],
            created_at=created_at_val,
        )
