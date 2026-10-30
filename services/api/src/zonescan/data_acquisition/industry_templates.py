"""Industry-aware financial statement schemas and extraction templates.

Supports specialized accounting and business intelligence metrics for:
A. Manufacturing and Industrial (e.g. Bharat Forge, Tata Steel)
B. Banking and Financial Services (e.g. Jio Financial Services, HDFC Bank, ICICI Bank)
C. IT and Software Services (e.g. Tata Consultancy Services, Infosys)
D. Energy, Oil and Gas (e.g. Reliance Industries, ONGC)
E. Pharmaceuticals and Healthcare (e.g. Sun Pharma, Cipla)
F. General Schedule III / Other Sectors
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger("zonescan.industry_templates")


class IndustrySector(str, Enum):
    MANUFACTURING = "manufacturing"
    BANKING_FINANCIAL = "banking_financial"
    IT_SERVICES = "it_services"
    ENERGY_OIL_GAS = "energy_oil_gas"
    PHARMA_HEALTHCARE = "pharma_healthcare"
    CONGLOMERATE = "conglomerate"
    GENERAL = "general"


def detect_industry_sector(
    sector: str = "",
    industry: str = "",
    company_name: str = "",
    text_sample: str = "",
) -> IndustrySector:
    """Classify company into an industry sector based on exchange metadata and keywords."""
    combined = f"{sector} {industry} {company_name} {text_sample}".lower()

    if any(k in combined for k in ("bank", "financial services", "nbfc", "lending", "credit", "asset management", "housing finance")):
        return IndustrySector.BANKING_FINANCIAL

    if any(k in combined for k in ("information technology", "software", "it services", "it consulting", "technology services", "tcs", "infosys", "wipro")):
        return IndustrySector.IT_SERVICES

    if any(k in combined for k in ("petroleum", "oil & gas", "oil and gas", "refining", "petrochemical", "crude", "energy & petrochemicals")):
        # If it's Reliance or integrated energy conglomerate, use energy/conglomerate
        return IndustrySector.ENERGY_OIL_GAS

    if any(k in combined for k in ("pharmaceutical", "healthcare", "pharma", "biotech", "drugs", "active pharmaceutical")):
        return IndustrySector.PHARMA_HEALTHCARE

    if any(k in combined for k in ("forging", "automotive", "steel", "capital goods", "metals", "engineering", "industrial", "precision components")):
        return IndustrySector.MANUFACTURING

    if any(k in combined for k in ("conglomerate", "diversified")):
        return IndustrySector.CONGLOMERATE

    return IndustrySector.GENERAL


# ---------------------------------------------------------------------------
# Canonical schemas by industry
# Each tuple: (metric_key, display_label, [regex_patterns])
# ---------------------------------------------------------------------------

# Common foundational Schedule III P&L
COMMON_PL: List[Tuple[str, str, List[str]]] = [
    ("total_income", "Total Income", [r"^total\s+income$", r"^total\s+revenue$", r"^total\s+income\s+from\s+operations"]),
    ("total_expenses", "Total Expenses", [r"^total\s+expenses$"]),
    ("revenue", "Revenue from Operations", [r"revenue\s+from\s+operations", r"^sale\s+of\s+products", r"^operating\s+revenue"]),
    ("other_income", "Other Income", [r"^other\s+income$"]),
    ("profit_before_tax", "Profit Before Tax (PBT)", [r"profit\s+(before\s+tax|\(loss\)\s+before\s+tax)"]),
    ("tax_expense", "Tax Expense", [r"^tax\s+expense$"]),
    ("current_tax", "Current Tax", [r"current\s+tax"]),
    ("deferred_tax", "Deferred Tax", [r"deferred\s+tax"]),
    ("profit_after_tax", "Profit After Tax (PAT)", [r"profit\s+for\s+the\s+(year|period)", r"profit\s+after\s+tax"]),
    ("exceptional_items", "Exceptional Items", [r"exceptional\s+items?"]),
]

# Manufacturing specific P&L items
MANUFACTURING_PL: List[Tuple[str, str, List[str]]] = COMMON_PL + [
    ("cost_of_materials", "Cost of Raw Materials Consumed", [r"cost\s+of\s+materials?\s+consumed", r"raw\s+materials?\s+consumed"]),
    ("purchases_stock_in_trade", "Purchases of Stock-in-Trade", [r"purchases?\s+of\s+stock.?in.?trade"]),
    ("changes_in_inventories", "Changes in Inventories", [r"changes?\s+in\s+inventories"]),
    ("employee_benefits", "Employee Benefit Expenses", [r"employee\s+benefits?\s+expense"]),
    ("finance_costs", "Finance Costs", [r"finance\s+costs?"]),
    ("depreciation", "Depreciation and Amortisation", [r"depreciation\s+and\s+amortis?ation"]),
    ("other_expenses", "Other Expenses", [r"other\s+expenses"]),
]

# Banking and Financial Services P&L (Interest-spread driven, Ind AS / RBI Format)
BANKING_PL: List[Tuple[str, str, List[str]]] = [
    ("interest_income", "Interest Income", [r"interest\s+income", r"interest\s+earned", r"revenue\s+from\s+interest"]),
    ("interest_expense", "Interest Expenses", [r"interest\s+expended", r"interest\s+expense", r"finance\s+charges"]),
    ("net_interest_income", "Net Interest Income (NII)", [r"net\s+interest\s+income", r"^nii$"]),
    ("fee_commission_income", "Fee and Commission Income", [r"fees?\s+and\s+commission", r"other\s+operating\s+income"]),
    ("treasury_income", "Treasury and Investment Income", [r"profit\s+on\s+sale\s+of\s+investments", r"treasury\s+income", r"net\s+gain\s+on\s+fair\s+value"]),
    ("total_income", "Total Income", [r"^total\s+income$", r"^total\s+revenue$"]),
    ("employee_benefits", "Employee Costs", [r"employee\s+benefits?\s+expense", r"staff\s+costs?"]),
    ("provisions_and_contingencies", "Provisions and Contingencies", [r"provisions?\s+(and|&)\s+contingencies", r"impairment\s+on\s+financial\s+instruments"]),
    ("operating_expenses", "Operating Expenses", [r"operating\s+expenses", r"other\s+operating\s+expenses"]),
    ("profit_before_tax", "Profit Before Tax", [r"profit\s+(before\s+tax|\(loss\)\s+before\s+tax)"]),
    ("tax_expense", "Tax Expense", [r"^tax\s+expense$"]),
    ("profit_after_tax", "Profit After Tax (PAT)", [r"profit\s+for\s+the\s+(year|period)", r"profit\s+after\s+tax"]),
]

# IT & Software Services P&L
IT_SERVICES_PL: List[Tuple[str, str, List[str]]] = [
    ("revenue", "Revenue from Software Services", [r"revenue\s+from\s+operations", r"software\s+development\s+revenue", r"revenue\s+from\s+services"]),
    ("other_income", "Other Income", [r"^other\s+income$"]),
    ("total_income", "Total Income", [r"^total\s+income$", r"^total\s+revenue$"]),
    ("employee_benefits", "Employee Benefit Expenses (Cost of Talent)", [r"employee\s+benefits?\s+expense", r"salaries\s+and\s+wages"]),
    ("subcontractor_costs", "Subcontractor and Technical Fees", [r"sub.?contractor", r"fees\s+to\s+external\s+consultants", r"technical\s+sub.?contract"]),
    ("depreciation", "Depreciation and Amortisation", [r"depreciation\s+and\s+amortis?ation"]),
    ("other_expenses", "Other Operating Expenses", [r"other\s+expenses", r"general\s+and\s+administrative"]),
    ("total_expenses", "Total Expenses", [r"^total\s+expenses$"]),
    ("profit_before_tax", "Profit Before Tax (PBT)", [r"profit\s+(before\s+tax|\(loss\)\s+before\s+tax)"]),
    ("tax_expense", "Tax Expense", [r"^tax\s+expense$"]),
    ("profit_after_tax", "Profit After Tax (PAT)", [r"profit\s+for\s+the\s+(year|period)", r"profit\s+after\s+tax"]),
]

# Energy, Oil & Gas P&L
ENERGY_PL: List[Tuple[str, str, List[str]]] = COMMON_PL + [
    ("raw_materials_and_feedstock", "Cost of Raw Materials & Crude Feedstock", [r"cost\s+of\s+materials?\s+consumed", r"crude\s+oil\s+purchases?", r"feedstock"]),
    ("purchases_stock_in_trade", "Purchases of Petroleum Products", [r"purchases?\s+of\s+stock.?in.?trade"]),
    ("refining_and_operating_costs", "Refining and Operating Expenses", [r"operating\s+costs?", r"manufacturing\s+expenses"]),
    ("excise_duty_and_taxes", "Excise Duty on Petroleum Products", [r"excise\s+duty"]),
    ("employee_benefits", "Employee Benefit Expenses", [r"employee\s+benefits?\s+expense"]),
    ("finance_costs", "Finance Costs", [r"finance\s+costs?"]),
    ("depreciation", "Depreciation and Amortisation", [r"depreciation\s+and\s+amortis?ation"]),
]

# Balance Sheet Schemas
COMMON_BS: List[Tuple[str, str, List[str]]] = [
    ("total_assets", "Total Assets", [r"^total\s+assets$"]),
    ("total_equity", "Total Equity", [r"^total\s+equity$"]),
    ("total_equity_and_liabilities", "Total Equity and Liabilities", [r"total\s+equity\s+and\s+liabilit"]),
    ("cash_and_equivalents", "Cash and Cash Equivalents", [r"cash\s+and\s+cash\s+equivalent", r"balances\s+with\s+banks"]),
]

MANUFACTURING_BS: List[Tuple[str, str, List[str]]] = COMMON_BS + [
    ("total_noncurrent_assets", "Total Non-Current Assets", [r"total\s+non.?current\s+assets"]),
    ("total_current_assets", "Total Current Assets", [r"total\s+current\s+assets"]),
    ("total_noncurrent_liabilities", "Total Non-Current Liabilities", [r"total\s+non.?current\s+liabilit"]),
    ("total_current_liabilities", "Total Current Liabilities", [r"total\s+current\s+liabilit"]),
    ("ppe", "Property, Plant and Equipment (PPE)", [r"property,?\s+plant\s+and\s+equipment"]),
    ("cwip", "Capital Work-in-Progress", [r"capital\s+work.?in.?progress"]),
    ("inventories", "Inventories", [r"^inventories$", r"^inventor"]),
    ("trade_receivables", "Trade Receivables", [r"trade\s+receivabl"]),
    ("borrowings_noncurrent", "Long-Term Borrowings", [r"long.?term\s+borrowings", r"borrowings\s+\(non.?current\)"]),
    ("borrowings_current", "Short-Term Borrowings", [r"short.?term\s+borrowings", r"borrowings\s+\(current\)"]),
]

BANKING_BS: List[Tuple[str, str, List[str]]] = COMMON_BS + [
    ("advances_loan_book", "Loans and Advances (Loan Book)", [r"^advances$", r"^loans\s+and\s+advances", r"financial\s+assets\s+loans"]),
    ("deposits", "Deposits (CASA + Term)", [r"^deposits$", r"deposits\s+from\s+customers"]),
    ("borrowings", "Borrowings (Debt Securities & Refinance)", [r"^borrowings$", r"debt\s+securities\s+issued"]),
    ("investments", "Investments (SLR & Treasury Securities)", [r"^investments$", r"investments\s+in\s+securities"]),
    ("capital_funds", "Share Capital & Reserves", [r"^capital$", r"^reserves\s+and\s+surplus"]),
]

IT_SERVICES_BS: List[Tuple[str, str, List[str]]] = COMMON_BS + [
    ("ppe", "Property, Plant and Equipment & Data Centers", [r"property,?\s+plant\s+and\s+equipment"]),
    ("intangibles_and_goodwill", "Intangibles & Goodwill", [r"goodwill", r"intangible\s+assets"]),
    ("trade_receivables", "Trade Receivables (Unbilled Revenue)", [r"trade\s+receivabl", r"unbilled\s+revenue"]),
    ("other_financial_assets", "Investments and Mutual Funds", [r"current\s+investments", r"other\s+financial\s+assets"]),
    ("borrowings", "Total Borrowings (if any)", [r"^borrowings$"]),
]


@dataclass(frozen=True, slots=True)
class IndustryExtractionProfile:
    """Configurable extraction profile for a specific industry sector."""
    sector: IndustrySector
    pl_schema: List[Tuple[str, str, List[str]]]
    bs_schema: List[Tuple[str, str, List[str]]]
    is_raw_material_applicable: bool
    is_loan_book_applicable: bool
    is_utilization_applicable: bool
    kpi_metrics: Tuple[str, ...]
    segment_dimension_hint: str


def get_industry_profile(sector: IndustrySector) -> IndustryExtractionProfile:
    """Return the extraction profile for a detected industry sector."""
    if sector == IndustrySector.BANKING_FINANCIAL:
        return IndustryExtractionProfile(
            sector=sector,
            pl_schema=BANKING_PL,
            bs_schema=BANKING_BS,
            is_raw_material_applicable=False,
            is_loan_book_applicable=True,
            is_utilization_applicable=False,
            kpi_metrics=(
                "net_interest_income",
                "interest_income",
                "advances_loan_book",
                "deposits",
                "profit_after_tax",
                "total_assets",
            ),
            segment_dimension_hint="Retail Banking / Wholesale / Treasury / SME / Consumer Lending",
        )
    elif sector == IndustrySector.IT_SERVICES:
        return IndustryExtractionProfile(
            sector=sector,
            pl_schema=IT_SERVICES_PL,
            bs_schema=IT_SERVICES_BS,
            is_raw_material_applicable=False,
            is_loan_book_applicable=False,
            is_utilization_applicable=True,
            kpi_metrics=(
                "revenue",
                "employee_benefits",
                "profit_after_tax",
                "total_assets",
                "cash_and_equivalents",
            ),
            segment_dimension_hint="Banking & Financial / Retail / Communications / Americas / Europe",
        )
    elif sector == IndustrySector.ENERGY_OIL_GAS:
        return IndustryExtractionProfile(
            sector=sector,
            pl_schema=ENERGY_PL,
            bs_schema=MANUFACTURING_BS,
            is_raw_material_applicable=True,
            is_loan_book_applicable=False,
            is_utilization_applicable=False,
            kpi_metrics=(
                "revenue",
                "raw_materials_and_feedstock",
                "profit_after_tax",
                "ppe",
                "total_assets",
                "borrowings_noncurrent",
            ),
            segment_dimension_hint="Oil to Chemicals (O2C) / Oil & Gas / Retail / Digital Services",
        )
    else:  # MANUFACTURING, CONGLOMERATE, GENERAL
        return IndustryExtractionProfile(
            sector=sector,
            pl_schema=MANUFACTURING_PL,
            bs_schema=MANUFACTURING_BS,
            is_raw_material_applicable=True,
            is_loan_book_applicable=False,
            is_utilization_applicable=False,
            kpi_metrics=(
                "revenue",
                "cost_of_materials",
                "profit_after_tax",
                "ppe",
                "total_assets",
                "total_equity",
                "cash_and_equivalents",
            ),
            segment_dimension_hint="Forgings / Automotive / Defense / Industrial / Export vs Domestic",
        )
