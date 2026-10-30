"""FY24 financial fact auditor for Bharat Forge Limited.

Compares extracted facts against the independently verified audited FY24
reference values from the official Annual Report 2023-24. Flags discrepancies
and provides corrected canonical records.

Reference values (Consolidated, INR Crores, FY2023-24):
  Revenue from Operations : 15,682.071 Cr
  Raw Materials Consumed  :  7,138.381 Cr
  Total PAT (Group)       :    910.159 Cr   ← total = attributable to parent + minority
  PAT (Parent)            :    951.128 Cr   ← attributable to owners of the parent
  Total Assets            : 19,349.118 Cr
  Total Equity            :  7,165.309 Cr
  Cash & Equivalents      :  1,315.310 Cr

Important accounting distinctions:
  - Revenue ≠ Other Income. "Revenue from Operations" is operating revenue only.
  - PAT (Group) ≠ PAT (Parent). Group PAT includes minority interest deduction.
    PAT attributable to owners of the parent is the standalone-equivalent parent figure.
  - Raw Materials Consumed ≠ Total COGS (which includes purchases, changes in inventory, etc.)

Evidence status: Disclosed (from publicly filed audited annual report).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("zonescan.audit")

# ---------------------------------------------------------------------------
# Reference dataset — FY24 Consolidated (INR Crores)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReferenceRecord:
    """A single audited reference fact."""
    canonical_key: str
    canonical_label: str
    statement_type: str          # profit_and_loss, balance_sheet, cash_flow
    statement_scope: str         # consolidated, standalone
    reporting_period: str
    reference_value_cr: float
    note: str = ""
    evidence_status: str = "Disclosed"


FY24_REFERENCE_FACTS: List[ReferenceRecord] = [
    ReferenceRecord(
        canonical_key="revenue",
        canonical_label="Revenue from Operations",
        statement_type="profit_and_loss",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=15_682.071,
        note="Operating revenue only; excludes other income",
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="cost_of_materials",
        canonical_label="Raw Materials Consumed",
        statement_type="profit_and_loss",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=7_138.381,
        note="Raw materials consumed; NOT total COGS",
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="profit_after_tax",
        canonical_label="Profit After Tax — Group (Total)",
        statement_type="profit_and_loss",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=910.159,
        note="Group PAT = attributable to parent + minority interest deduction",
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="profit_after_tax_parent",
        canonical_label="PAT Attributable to Owners of Parent",
        statement_type="profit_and_loss",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=951.128,
        note=(
            "PAT attributable to equity holders of Bharat Forge Limited; "
            "Net profit including minority interest share excluded. "
            "Do NOT combine with group PAT."
        ),
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="total_assets",
        canonical_label="Total Assets",
        statement_type="balance_sheet",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=19_349.118,
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="total_equity",
        canonical_label="Total Equity",
        statement_type="balance_sheet",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=7_165.309,
        evidence_status="Disclosed",
    ),
    ReferenceRecord(
        canonical_key="cash_and_equivalents",
        canonical_label="Cash and Cash Equivalents",
        statement_type="balance_sheet",
        statement_scope="consolidated",
        reporting_period="FY2023-24",
        reference_value_cr=1_315.310,
        evidence_status="Disclosed",
    ),
]

COMPANY_REFERENCE_FACTS: Dict[str, List[ReferenceRecord]] = {
    "BHARATFORG": FY24_REFERENCE_FACTS,
    "RELIANCE": [
        ReferenceRecord("revenue", "Revenue from Operations", "profit_and_loss", "consolidated", "FY2023-24", 914_472.0, "Consolidated operating revenue Note 28"),
        ReferenceRecord("profit_after_tax", "Profit After Tax (PAT)", "profit_and_loss", "consolidated", "FY2023-24", 79_020.0, "Consolidated PAT"),
        ReferenceRecord("total_assets", "Total Assets", "balance_sheet", "consolidated", "FY2023-24", 1_817_445.0, "Total Consolidated Assets"),
        ReferenceRecord("total_equity", "Total Equity", "balance_sheet", "consolidated", "FY2023-24", 833_391.0, "Total Equity & NCI"),
        ReferenceRecord("cash_and_equivalents", "Cash and Cash Equivalents", "balance_sheet", "consolidated", "FY2023-24", 118_367.0, "Cash & Equivalents Note 19"),
    ],
    "JIOFIN": [
        ReferenceRecord("total_income", "Total Income", "profit_and_loss", "consolidated", "FY2023-24", 1_855.27, "Consolidated Total Income"),
        ReferenceRecord("profit_after_tax", "Profit After Tax (PAT)", "profit_and_loss", "consolidated", "FY2023-24", 1_604.55, "Consolidated PAT"),
        ReferenceRecord("total_assets", "Total Assets", "balance_sheet", "consolidated", "FY2023-24", 139_832.0, "Total Balance Sheet Assets"),
        ReferenceRecord("total_equity", "Total Equity", "balance_sheet", "consolidated", "FY2023-24", 139_141.0, "Total Net Worth / Equity"),
        ReferenceRecord("cash_and_equivalents", "Cash and Cash Equivalents", "balance_sheet", "consolidated", "FY2023-24", 1_940.0, "Cash & Bank Balances"),
    ],
    "TCS": [
        ReferenceRecord("revenue", "Revenue from Software Services", "profit_and_loss", "consolidated", "FY2023-24", 240_893.0, "Consolidated Revenue Note 24"),
        ReferenceRecord("profit_after_tax", "Profit After Tax (PAT)", "profit_and_loss", "consolidated", "FY2023-24", 46_099.0, "Consolidated PAT"),
        ReferenceRecord("total_assets", "Total Assets", "balance_sheet", "consolidated", "FY2023-24", 144_834.0, "Total Consolidated Assets Note 12-18"),
        ReferenceRecord("total_equity", "Total Equity", "balance_sheet", "consolidated", "FY2023-24", 90_488.0, "Total Equity / Net Worth"),
        ReferenceRecord("cash_and_equivalents", "Cash and Cash Equivalents", "balance_sheet", "consolidated", "FY2023-24", 48_829.0, "Cash, Bank & Investments Note 16"),
    ],
}

# Tolerance for considering values "matching" — ±0.5 Crores (rounding)
_MATCH_TOLERANCE_CR = 0.5
# Tolerance for flagging as "suspect" — >2% deviation
_SUSPECT_THRESHOLD_PCT = 2.0


@dataclass
class AuditFlag:
    """A single discrepancy found during FY24 audit."""
    canonical_key: str
    reporting_period: str
    statement_scope: str
    reference_value_cr: float
    extracted_value_cr: Optional[float]
    discrepancy_cr: float
    discrepancy_pct: float
    severity: str                   # "match", "rounding", "suspect", "missing"
    recommendation: str


@dataclass
class AuditResult:
    """Full audit result for one company-period."""
    symbol: str
    reporting_period: str
    flags: List[AuditFlag] = field(default_factory=list)

    @property
    def n_matches(self) -> int:
        return sum(1 for f in self.flags if f.severity == "match")

    @property
    def n_suspect(self) -> int:
        return sum(1 for f in self.flags if f.severity == "suspect")

    @property
    def n_missing(self) -> int:
        return sum(1 for f in self.flags if f.severity == "missing")


def audit_fy24_facts(
    extracted_facts: List[Dict[str, Any]],
    symbol: str = "BHARATFORG",
) -> AuditResult:
    """Compare extracted facts against FY24 reference values.

    Args:
        extracted_facts: List of dicts from FinancialFactStore or normalizer output.
            Expected keys: canonical_key, statement_type, statement_scope,
            reporting_period, value_cr (or value_numeric + unit).
        symbol: Company symbol for reporting.

    Returns:
        AuditResult with per-metric flags.
    """
    # Index extracted facts for fast lookup
    # key: (canonical_key, statement_scope, reporting_period)
    extracted_index: Dict[tuple, float] = {}
    for fact in extracted_facts:
        # Support both dataclass (FinancialFact) and plain dict
        if isinstance(fact, dict):
            ck = fact.get("canonical_key") or fact.get("metric_key", "")
            scope = fact.get("statement_scope", "")
            period = fact.get("reporting_period", "") or fact.get("financial_period", "")
            val = fact.get("value_cr") or fact.get("value_numeric")
            unit = fact.get("unit", "INR_CRORES")
        else:
            # FinancialFact dataclass: fields are metric, value, unit, financial_period, statement_scope
            ck = getattr(fact, "metric", None) or getattr(fact, "canonical_key", "")
            scope = getattr(fact, "statement_scope", "")
            period = getattr(fact, "financial_period", "") or getattr(fact, "reporting_period", "")
            val = getattr(fact, "value", None)
            unit = getattr(fact, "unit", "INR_CRORES") or "INR_CRORES"

        if ck and scope and period and val is not None:
            # Normalise to Crores
            try:
                v = float(val)
                if unit == "INR_LAKHS":
                    v = v / 100.0
                elif unit == "INR":
                    v = v / 10_000_000.0
                extracted_index[(ck, scope, period)] = v
            except (ValueError, TypeError):
                pass

    result = AuditResult(symbol=symbol, reporting_period="FY2023-24")

    ref_records = COMPANY_REFERENCE_FACTS.get(symbol.upper(), FY24_REFERENCE_FACTS if symbol.upper() == "BHARATFORG" else [])
    for ref in ref_records:
        lookup_key = (ref.canonical_key, ref.statement_scope, ref.reporting_period)
        extracted_val = extracted_index.get(lookup_key)

        if extracted_val is None:
            result.flags.append(AuditFlag(
                canonical_key=ref.canonical_key,
                reporting_period=ref.reporting_period,
                statement_scope=ref.statement_scope,
                reference_value_cr=ref.reference_value_cr,
                extracted_value_cr=None,
                discrepancy_cr=ref.reference_value_cr,
                discrepancy_pct=100.0,
                severity="missing",
                recommendation=(
                    f"No extracted value found for {ref.canonical_label} "
                    f"({ref.statement_scope}, {ref.reporting_period}). "
                    f"Reference: {ref.reference_value_cr:,.3f} Cr. {ref.note}"
                ),
            ))
            continue

        diff = abs(extracted_val - ref.reference_value_cr)
        pct = (diff / ref.reference_value_cr) * 100.0 if ref.reference_value_cr else 0.0

        if diff <= _MATCH_TOLERANCE_CR:
            severity = "match"
            recommendation = "Values match within rounding tolerance."
        elif pct <= _SUSPECT_THRESHOLD_PCT:
            severity = "rounding"
            recommendation = (
                f"Minor deviation ({pct:.2f}%) — likely rounding/unit difference. "
                f"Extracted: {extracted_val:,.3f}, Reference: {ref.reference_value_cr:,.3f} Cr."
            )
        else:
            severity = "suspect"
            recommendation = (
                f"Significant deviation ({pct:.2f}%). "
                f"Extracted: {extracted_val:,.3f}, Reference: {ref.reference_value_cr:,.3f} Cr. "
                f"{ref.note} — Verify extraction against original document."
            )

        result.flags.append(AuditFlag(
            canonical_key=ref.canonical_key,
            reporting_period=ref.reporting_period,
            statement_scope=ref.statement_scope,
            reference_value_cr=ref.reference_value_cr,
            extracted_value_cr=extracted_val,
            discrepancy_cr=diff,
            discrepancy_pct=pct,
            severity=severity,
            recommendation=recommendation,
        ))
        logger.info(
            "AUDIT [%s] %s: extracted=%.3f ref=%.3f diff=%.3f (%.2f%%) [%s]",
            ref.statement_scope, ref.canonical_key, extracted_val,
            ref.reference_value_cr, diff, pct, severity.upper(),
        )

    return result


def format_audit_report(result: AuditResult) -> str:
    """Render an AuditResult as a markdown string suitable for embedding in reports."""
    lines = [
        f"## FY24 Reference Audit — {result.symbol} ({result.reporting_period})",
        "",
        "| Metric | Scope | Reference (Cr) | Extracted (Cr) | Δ | Δ% | Status |",
        "|--------|-------|---------------:|---------------:|--:|---:|--------|",
    ]
    for f in result.flags:
        ext_str = f"{f.extracted_value_cr:,.3f}" if f.extracted_value_cr is not None else "MISSING"
        lines.append(
            f"| {f.canonical_key} | {f.statement_scope} "
            f"| {f.reference_value_cr:,.3f} | {ext_str} "
            f"| {f.discrepancy_cr:,.3f} | {f.discrepancy_pct:.2f}% | {f.severity.upper()} |"
        )

    lines += [
        "",
        f"**Summary:** {result.n_matches} match | {result.n_suspect} suspect | {result.n_missing} missing",
        "",
        "### Notes",
        "- **Revenue ≠ Total Income.** Reference revenue is *Revenue from Operations* only. Other income is excluded.",
        "- **Group PAT ≠ Parent PAT.** Group PAT = 910.159 Cr includes minority interest deduction.",
        "  PAT attributable to owners = 951.128 Cr. These are different line items; do not combine.",
        "- **Raw Materials Consumed ≠ Total COGS.** Reference RM consumed: 7,138.381 Cr.",
        "  Total cost of materials (incl. purchases + inventory changes) is a different figure.",
        "- Evidence status: **Disclosed** (sourced from audited Annual Report 2023-24, Bharat Forge Limited).",
    ]
    return "\n".join(lines)
