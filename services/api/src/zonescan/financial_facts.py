"""Financial facts persistence schema, boundary validation, and repository.

Implements the persistence boundary for Financial Intelligence (Workspace 2),
strictly enforcing provenance, metadata completeness, and separation of
synthetic and real factual data.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

VALID_EVIDENCE_STATUSES = frozenset({
    "disclosed",
    "verified",
    "inferred",
    "unconfirmed",
    "unavailable",
})

VALID_STATEMENT_SCOPES = frozenset({
    "consolidated",
    "standalone",
})


class FactValidationError(ValueError):
    """Raised when a financial fact violates persistence boundary constraints."""
    pass


@dataclass(frozen=True, slots=True)
class FinancialFact:
    """An individual, traceable financial fact with explicit provenance."""
    fact_id: str
    company_id: str
    metric: str
    value: float
    unit: str
    financial_period: str
    statement_scope: str = "consolidated"
    source_document: str = ""
    source_url: str | None = None
    page_note_table_reference: str | None = None
    document_date: date | None = None
    retrieval_timestamp: datetime | None = None
    extraction_method: str = "manual_audited_filing_extract"
    evidence_status: str = "disclosed"
    is_synthetic: bool = False
    verification_notes: str | None = None
    created_at: datetime | None = None


def validate_financial_fact(fact: FinancialFact) -> None:
    """Validate fact boundary constraints before persistence.

    Enforces mandatory presence of company identity, metric, unit, period,
    source document, source date, and evidence status.
    """
    if not isinstance(fact, FinancialFact):
        raise FactValidationError(f"Expected FinancialFact instance, got {type(fact).__name__}")

    # 1. Company identity
    if not fact.company_id or not fact.company_id.strip():
        raise FactValidationError("company_id is mandatory and cannot be empty")

    # 2. Metric name
    if not fact.metric or not fact.metric.strip():
        raise FactValidationError("metric is mandatory and cannot be empty")

    # 3. Numeric value
    if not isinstance(fact.value, (int, float)) or not isfinite(fact.value):
        raise FactValidationError(f"value must be a finite numeric float, got {fact.value!r}")

    # 4. Unit of measurement
    if not fact.unit or not fact.unit.strip():
        raise FactValidationError("unit is mandatory and cannot be empty")

    # 5. Financial reporting period
    if not fact.financial_period or not fact.financial_period.strip():
        raise FactValidationError("financial_period is mandatory and cannot be empty")

    # 6. Statement scope
    if fact.statement_scope not in VALID_STATEMENT_SCOPES:
        raise FactValidationError(
            f"statement_scope must be one of {sorted(VALID_STATEMENT_SCOPES)}, got {fact.statement_scope!r}"
        )

    # 7. Source document
    if not fact.source_document or not fact.source_document.strip():
        raise FactValidationError("source_document is mandatory and cannot be empty")

    # 8. Source document date
    if fact.document_date is None or not isinstance(fact.document_date, date):
        raise FactValidationError(
            f"document_date is mandatory and must be a date instance, got {fact.document_date!r}"
        )

    # 9. Evidence status
    if fact.evidence_status not in VALID_EVIDENCE_STATUSES:
        raise FactValidationError(
            f"evidence_status must be one of {sorted(VALID_EVIDENCE_STATUSES)}, got {fact.evidence_status!r}"
        )

    # 10. Retrieval timestamp
    if fact.retrieval_timestamp is None:
        raise FactValidationError("retrieval_timestamp is mandatory")
    if fact.retrieval_timestamp.tzinfo is None or fact.retrieval_timestamp.utcoffset() is None:
        raise FactValidationError("retrieval_timestamp must be timezone-aware")


class FinancialFactStore:
    """SQLite-backed persistence repository for financial facts with strict constraints."""

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
        """Initialize the financial_facts relational schema with check constraints."""
        with self._conn:
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS financial_facts (
                    fact_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    financial_period TEXT NOT NULL,
                    statement_scope TEXT NOT NULL CHECK (statement_scope IN ('consolidated', 'standalone')),
                    source_document TEXT NOT NULL,
                    source_url TEXT,
                    page_note_table_reference TEXT,
                    document_date TEXT NOT NULL,
                    retrieval_timestamp TEXT NOT NULL,
                    extraction_method TEXT NOT NULL,
                    evidence_status TEXT NOT NULL CHECK (evidence_status IN ('disclosed', 'verified', 'inferred', 'unconfirmed', 'unavailable')),
                    is_synthetic INTEGER NOT NULL DEFAULT 0 CHECK (is_synthetic IN (0, 1)),
                    verification_notes TEXT,
                    created_at TEXT NOT NULL,
                    CHECK (length(trim(company_id)) > 0),
                    CHECK (length(trim(metric)) > 0),
                    CHECK (length(trim(unit)) > 0),
                    CHECK (length(trim(financial_period)) > 0),
                    CHECK (length(trim(source_document)) > 0),
                    CHECK (length(trim(document_date)) > 0),
                    CHECK (length(trim(evidence_status)) > 0)
                );
                """
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_facts_company_period ON financial_facts (company_id, financial_period);"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_facts_metric ON financial_facts (metric);"
            )
            self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_facts_synthetic ON financial_facts (is_synthetic);"
            )

    def insert_fact(self, fact: FinancialFact) -> str:
        """Validate and persist a financial fact.

        Raises FactValidationError if boundary validation fails or SQLite integrity error occurs.
        """
        # Boundary validation (Python level)
        validate_financial_fact(fact)

        created_at_dt = fact.created_at or datetime.now(IST)
        created_at_str = created_at_dt.isoformat()
        doc_date_str = fact.document_date.isoformat() if fact.document_date else ""
        retrieval_ts_str = fact.retrieval_timestamp.isoformat() if fact.retrieval_timestamp else ""

        try:
            with self._conn:
                self._conn.execute(
                    """
                    INSERT INTO financial_facts (
                        fact_id, company_id, metric, value, unit,
                        financial_period, statement_scope, source_document,
                        source_url, page_note_table_reference, document_date,
                        retrieval_timestamp, extraction_method, evidence_status,
                        is_synthetic, verification_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        fact.fact_id,
                        fact.company_id.strip(),
                        fact.metric.strip(),
                        fact.value,
                        fact.unit.strip(),
                        fact.financial_period.strip(),
                        fact.statement_scope,
                        fact.source_document.strip(),
                        fact.source_url,
                        fact.page_note_table_reference,
                        doc_date_str,
                        retrieval_ts_str,
                        fact.extraction_method,
                        fact.evidence_status,
                        1 if fact.is_synthetic else 0,
                        fact.verification_notes,
                        created_at_str,
                    ),
                )
        except sqlite3.IntegrityError as err:
            raise FactValidationError(f"Database constraint violation on fact insertion: {err}") from err

        return fact.fact_id

    def get_fact(self, fact_id: str) -> FinancialFact | None:
        """Retrieve an individual fact by its primary identifier."""
        cursor = self._conn.execute(
            """
            SELECT fact_id, company_id, metric, value, unit, financial_period,
                   statement_scope, source_document, source_url,
                   page_note_table_reference, document_date, retrieval_timestamp,
                   extraction_method, evidence_status, is_synthetic,
                   verification_notes, created_at
            FROM financial_facts
            WHERE fact_id = ?
            """,
            (fact_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return self._row_to_fact(row)

    def get_facts_for_company(
        self,
        company_id: str,
        financial_period: str | None = None,
        is_synthetic: bool | None = None,
    ) -> list[FinancialFact]:
        """Query facts by company with optional period and synthetic filters."""
        query = "SELECT * FROM financial_facts WHERE company_id = ?"
        params: list[object] = [company_id]

        if financial_period is not None:
            query += " AND financial_period = ?"
            params.append(financial_period)

        if is_synthetic is not None:
            query += " AND is_synthetic = ?"
            params.append(1 if is_synthetic else 0)

        query += " ORDER BY document_date DESC, metric ASC"
        cursor = self._conn.execute(query, params)
        return [self._row_to_fact(row) for row in cursor.fetchall()]

    def count_facts(self, is_synthetic: bool | None = None) -> int:
        """Count total persisted facts, optionally filtering by synthetic flag."""
        if is_synthetic is None:
            cursor = self._conn.execute("SELECT COUNT(*) FROM financial_facts")
        else:
            cursor = self._conn.execute(
                "SELECT COUNT(*) FROM financial_facts WHERE is_synthetic = ?",
                (1 if is_synthetic else 0,),
            )
        return int(cursor.fetchone()[0])

    def seed_bharat_forge_pilot_fact(self) -> FinancialFact:
        """Seed the genuine, individually traceable pilot fact from Bharat Forge Annual Report FY24.

        Source: BSE Statutory Filing / Audited Consolidated Financial Statements
        URL: https://www.bseindia.com/bseplus/AnnualReport/500493/73255500493.pdf
        Page: 218, Note 23 (Revenue from Operations)
        Audit Date: 2024-05-08
        """
        fact = FinancialFact(
            fact_id="fact-bf-rev-fy24",
            company_id="L25209PN1961PLC012046",
            metric="revenue_from_operations",
            value=15682.07,
            unit="INR_CRORES",
            financial_period="FY2023-24",
            statement_scope="consolidated",
            source_document="Annual Report FY 2023-24",
            source_url="https://www.bseindia.com/bseplus/AnnualReport/500493/73255500493.pdf",
            page_note_table_reference="Consolidated Statement of Profit & Loss, Page 218, Note 23",
            document_date=date(2024, 5, 8),
            retrieval_timestamp=datetime(2026, 10, 30, 10, 0, tzinfo=IST),
            extraction_method="manual_audited_filing_extract",
            evidence_status="disclosed",
            is_synthetic=False,
            verification_notes=(
                "Audited line item: Invoiced sales of forged & machined components "
                "less trade discounts and GST."
            ),
        )
        self.insert_fact(fact)
        return fact

    @staticmethod
    def _row_to_fact(row: sqlite3.Row) -> FinancialFact:
        doc_date = date.fromisoformat(row["document_date"])
        retrieval_ts = datetime.fromisoformat(row["retrieval_timestamp"])
        created_at_val = datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        return FinancialFact(
            fact_id=row["fact_id"],
            company_id=row["company_id"],
            metric=row["metric"],
            value=float(row["value"]),
            unit=row["unit"],
            financial_period=row["financial_period"],
            statement_scope=row["statement_scope"],
            source_document=row["source_document"],
            source_url=row["source_url"],
            page_note_table_reference=row["page_note_table_reference"],
            document_date=doc_date,
            retrieval_timestamp=retrieval_ts,
            extraction_method=row["extraction_method"],
            evidence_status=row["evidence_status"],
            is_synthetic=bool(row["is_synthetic"]),
            verification_notes=row["verification_notes"],
            created_at=created_at_val,
        )
