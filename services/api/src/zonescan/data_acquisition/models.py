"""Data contracts and schemas for the ZoneScan Data Acquisition & Extraction pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


@dataclass(frozen=True, slots=True)
class CompanyIdentifiers:
    """Master identity identifiers for a target company."""
    company_name: str
    symbol: str
    bse_code: str
    isin: str
    cin: str
    sector: str = ""
    industry: str = ""
    incorporation_year: int = 1961
    registered_office: str = ""


@dataclass
class DocumentMetadata:
    """Detailed provenance metadata for a collected corporate document."""
    doc_id: str
    company_id: str
    symbol: str
    title: str
    source_url: str
    source_website: str
    document_type: str                  # annual_report, financial_results, xbrl_instance, shareholding, rpt, announcement
    reporting_period: str               # e.g. FY2023-24, FY2022-23, FY2021-22
    publication_date: Optional[date] = None
    download_timestamp: Optional[datetime] = None
    file_type: str = "pdf"              # pdf, xml, json, html, zip
    local_path: str = ""
    sha256_hash: str = ""
    file_size_bytes: int = 0
    extraction_status: str = "pending"  # pending, extracted, partial, failed, skipped
    error_message: Optional[str] = None


@dataclass
class ExtractedRow:
    """An individual line item from a financial statement table."""
    raw_label: str
    normalized_key: Optional[str] = None
    normalized_label: Optional[str] = None
    note_reference: Optional[str] = None
    values: Dict[str, Optional[float]] = field(default_factory=dict)  # period (e.g. FY2023-24) -> value


@dataclass
class ExtractedStatement:
    """A parsed and structured financial statement table."""
    statement_type: str                 # profit_and_loss, balance_sheet, cash_flow
    statement_scope: str                # consolidated, standalone
    reported_currency: str = "INR"
    reported_unit: str = "INR_CRORES"   # INR_CRORES, INR_LAKHS, INR
    periods: List[str] = field(default_factory=list)
    rows: List[ExtractedRow] = field(default_factory=list)
    unmapped_rows: List[ExtractedRow] = field(default_factory=list)
    source_doc_id: str = ""
    source_title: str = ""
    page_numbers: List[int] = field(default_factory=list)
    extraction_engine: str = "arx_pdfplumber"


@dataclass
class SegmentItem:
    """Operating business or geographic segment disclosure (Ind AS 108)."""
    segment_name: str
    revenue_cr: float
    revenue_share_pct: float
    operating_profit_cr: Optional[float] = None
    assets_cr: Optional[float] = None
    liabilities_cr: Optional[float] = None
    reporting_period: str = "FY2023-24"
    statement_scope: str = "consolidated"
    plain_description: str = ""
    evidence_status: str = "disclosed"
    source_ref: str = ""


@dataclass
class ShareholdingItem:
    """Shareholding category from SEBI Reg 31 filing."""
    category: str
    holding_pct: float
    shares_count: int
    pledged_pct: float = 0.0
    qoq_shift_pct: Optional[float] = None
    reporting_period: str = "FY2023-24"
    as_of_date: str = "2024-03-31"
    evidence_status: str = "disclosed"
    source_ref: str = ""


@dataclass
class CorporateRelationshipItem:
    """Connected corporate entity, subsidiary, customer, supplier, or JV."""
    entity_name: str
    relationship_type: str              # subsidiary, associate, joint_venture, customer, supplier, competitor
    ownership_pct: Optional[float] = None
    country: str = "India"
    nature_of_transaction: str = ""
    transaction_amount_cr: Optional[float] = None
    reporting_period: str = "FY2023-24"
    evidence_status: str = "disclosed"
    source_ref: str = ""


@dataclass
class CommodityExposureItem:
    """Raw material dependency and benchmark sensitivity."""
    material_name: str
    share_of_cogs_pct: float
    annual_expenditure_cr: float
    benchmark_index: str
    domestic_import_mix: str
    hedging_policy: str = ""
    risk_summary: str = ""
    evidence_status: str = "disclosed"
    source_ref: str = ""


@dataclass
class BusinessIntelligenceItem:
    """Qualitative operational disclosure: divisions, capex, risks, management commentary."""
    category: str                       # division, location, capex, risk_factor, commentary
    title: str
    details: str
    reporting_period: str = "FY2023-24"
    source_ref: str = ""


@dataclass
class DataConflictItem:
    """Discrepancy between filings, comparative restatements, or reporting periods."""
    metric: str
    reporting_period: str
    statement_scope: str
    source_primary: str
    value_primary: float
    source_secondary: str
    value_secondary: float
    discrepancy_pct: float
    reason: str


@dataclass
class ExtractionIssueItem:
    """Recorded extraction or source accessibility issue."""
    source_url: str
    issue_type: str                     # access_restriction, ocr_quality, parse_ambiguity, missing_disclosure
    description: str
    impact: str
    remediation: str
