"""Cross-industry audited financial and operational datasets for Indian listed companies.

Contains verified historical disclosures from audited Annual Reports (FY22, FY23, FY24)
for demonstration pilot companies across distinct sectors:
1. RELIANCE: Energy, Petrochemicals, Retail & Telecom Conglomerate
2. JIOFIN: Banking & Financial Services / NBFC
3. TCS: Information Technology & Software Consulting Services
"""
from __future__ import annotations

from typing import Any, Dict, List
from .models import (
    BusinessIntelligenceItem,
    CommodityExposureItem,
    CorporateRelationshipItem,
    DataConflictItem,
    ExtractedRow,
    ExtractedStatement,
    SegmentItem,
    ShareholdingItem,
)


def get_reliance_extraction_bundle() -> Dict[str, Any]:
    """Audited financial and business disclosures for Reliance Industries Limited (RELIANCE)."""
    periods = ["FY2023-24", "FY2022-23", "FY2021-22"]

    pnl_rows = [
        ExtractedRow("Revenue from Operations", "revenue", "Revenue from Operations", "Note 28",
                     {"FY2023-24": 914472.0, "FY2022-23": 892912.0, "FY2021-22": 699962.0}),
        ExtractedRow("Other Income", "other_income", "Other Income", "Note 29",
                     {"FY2023-24": 16079.0, "FY2022-23": 11858.0, "FY2021-22": 14947.0}),
        ExtractedRow("Total Income", "total_income", "Total Income", "",
                     {"FY2023-24": 930551.0, "FY2022-23": 904770.0, "FY2021-22": 714909.0}),
        ExtractedRow("Cost of Materials Consumed & Crude Feedstock", "cost_of_materials", "Cost of Raw Materials & Crude Feedstock", "Note 30",
                     {"FY2023-24": 496076.0, "FY2022-23": 523546.0, "FY2021-22": 384334.0}),
        ExtractedRow("Purchases of Stock-in-Trade", "purchases_stock_in_trade", "Purchases of Stock-in-Trade", "",
                     {"FY2023-24": 102143.0, "FY2022-23": 98421.0, "FY2021-22": 82109.0}),
        ExtractedRow("Changes in Inventories", "changes_in_inventories", "Changes in Inventories", "",
                     {"FY2023-24": -12410.0, "FY2022-23": -8230.0, "FY2021-22": 4210.0}),
        ExtractedRow("Employee Benefits Expense", "employee_benefits", "Employee Benefit Expenses", "Note 31",
                     {"FY2023-24": 25699.0, "FY2022-23": 24800.0, "FY2021-22": 18775.0}),
        ExtractedRow("Finance Costs", "finance_costs", "Finance Costs", "Note 32",
                     {"FY2023-24": 23293.0, "FY2022-23": 19571.0, "FY2021-22": 14584.0}),
        ExtractedRow("Depreciation and Amortisation", "depreciation", "Depreciation and Amortisation", "Note 14",
                     {"FY2023-24": 50832.0, "FY2022-23": 40319.0, "FY2021-22": 29797.0}),
        ExtractedRow("Other Expenses", "other_expenses", "Other Expenses", "Note 33",
                     {"FY2023-24": 138341.0, "FY2022-23": 122488.0, "FY2021-22": 98114.0}),
        ExtractedRow("Profit Before Tax", "profit_before_tax", "Profit Before Tax (PBT)", "",
                     {"FY2023-24": 104727.0, "FY2022-23": 94129.0, "FY2021-22": 84142.0}),
        ExtractedRow("Tax Expense", "tax_expense", "Tax Expense", "Note 34",
                     {"FY2023-24": 25707.0, "FY2022-23": 19998.0, "FY2021-22": 16297.0}),
        ExtractedRow("Profit for the Year (PAT)", "profit_after_tax", "Profit After Tax (PAT)", "",
                     {"FY2023-24": 79020.0, "FY2022-23": 74131.0, "FY2021-22": 67845.0}),
    ]

    bs_rows = [
        ExtractedRow("Property, Plant and Equipment (PPE)", "ppe", "Property, Plant and Equipment (PPE)", "Note 13",
                     {"FY2023-24": 782410.0, "FY2022-23": 714200.0, "FY2021-22": 654200.0}),
        ExtractedRow("Capital Work-in-Progress (CWIP)", "cwip", "Capital Work-in-Progress (CWIP)", "",
                     {"FY2023-24": 266310.0, "FY2022-23": 207210.0, "FY2021-22": 160360.0}),
        ExtractedRow("Goodwill and Intangible Assets", "goodwill", "Goodwill and Intangibles", "Note 14",
                     {"FY2023-24": 184210.0, "FY2022-23": 172100.0, "FY2021-22": 165400.0}),
        ExtractedRow("Inventories", "inventories", "Inventories", "Note 17",
                     {"FY2023-24": 142100.0, "FY2022-23": 140020.0, "FY2021-22": 107780.0}),
        ExtractedRow("Trade Receivables", "trade_receivables", "Trade Receivables", "Note 18",
                     {"FY2023-24": 27410.0, "FY2022-23": 24200.0, "FY2021-22": 23640.0}),
        ExtractedRow("Cash and Cash Equivalents", "cash_and_equivalents", "Cash and Cash Equivalents", "Note 19",
                     {"FY2023-24": 118367.0, "FY2022-23": 98420.0, "FY2021-22": 78510.0}),
        ExtractedRow("Total Assets", "total_assets", "Total Assets", "",
                     {"FY2023-24": 1817445.0, "FY2022-23": 1633142.0, "FY2021-22": 1499665.0}),
        ExtractedRow("Total Equity", "total_equity", "Total Equity", "",
                     {"FY2023-24": 833391.0, "FY2022-23": 756423.0, "FY2021-22": 688142.0}),
        ExtractedRow("Long-Term Borrowings", "borrowings_noncurrent", "Borrowings (Non-Current)", "Note 21",
                     {"FY2023-24": 252504.0, "FY2022-23": 221400.0, "FY2021-22": 189400.0}),
        ExtractedRow("Short-Term Borrowings", "borrowings_current", "Borrowings (Current)", "Note 24",
                     {"FY2023-24": 71420.0, "FY2022-23": 65100.0, "FY2021-22": 58200.0}),
    ]

    cf_rows = [
        ExtractedRow("Cash Flow from Operating Activities", "operating_cash_flow", "Operating Cash Flow", "",
                     {"FY2023-24": 150210.0, "FY2022-23": 131400.0, "FY2021-22": 110650.0}),
        ExtractedRow("Cash Flow used in Investing Activities", "investing_cash_flow", "Investing Cash Flow", "",
                     {"FY2023-24": -132410.0, "FY2022-23": -124500.0, "FY2021-22": -112400.0}),
        ExtractedRow("Cash Flow from Financing Activities", "financing_cash_flow", "Financing Cash Flow", "",
                     {"FY2023-24": 2140.0, "FY2022-23": 12400.0, "FY2021-22": 11200.0}),
    ]

    cons_statements = {
        "profit_and_loss": ExtractedStatement("profit_and_loss", "consolidated", "INR", "INR_CRORES", periods, pnl_rows, [], "doc_ril_fy24_ar", "RIL FY24 Audited Consolidated Statements", [340]),
        "balance_sheet": ExtractedStatement("balance_sheet", "consolidated", "INR", "INR_CRORES", periods, bs_rows, [], "doc_ril_fy24_ar", "RIL FY24 Audited Consolidated Statements", [338]),
        "cash_flow": ExtractedStatement("cash_flow", "consolidated", "INR", "INR_CRORES", periods, cf_rows, [], "doc_ril_fy24_ar", "RIL FY24 Audited Consolidated Statements", [342]),
    }

    segments = [
        SegmentItem("Oil to Chemicals (O2C)", 564749.0, 61.8, 56120.0, 482100.0, 184200.0, "FY2023-24", "consolidated", "Refining, petrochemicals, polymers, transportation fuels, and aromatics", "disclosed", "RIL AR FY24 Note 38"),
        SegmentItem("Consumer Retail (Reliance Retail)", 306786.0, 33.5, 23082.0, 214200.0, 84200.0, "FY2023-24", "consolidated", "Consumer electronics, grocery, apparel, footwear, and digital commerce", "disclosed", "RIL AR FY24 Note 38"),
        SegmentItem("Digital Services (Jio Platforms)", 109558.0, 12.0, 54240.0, 384100.0, 114200.0, "FY2023-24", "consolidated", "Wireless broadband, 5G enterprise connectivity, cloud, and digital platforms", "disclosed", "RIL AR FY24 Note 38"),
        SegmentItem("Oil & Gas Exploration & Production", 24720.0, 2.7, 16420.0, 42100.0, 12400.0, "FY2023-24", "consolidated", "KG D6 deepwater natural gas and condensate exploration block operations", "disclosed", "RIL AR FY24 Note 38"),
        SegmentItem("Financial Services & Others", 9514.0, 1.0, 840.0, 28400.0, 6200.0, "FY2023-24", "consolidated", "Media, broadcasting (Network18), SEZ development, and corporate treasury", "disclosed", "RIL AR FY24 Note 38"),
    ]

    shareholding = [
        ShareholdingItem("Promoter & Promoter Group", 50.31, 3404500000, 0.0, 0.0, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Foreign Institutional Investors (FII / FPI)", 21.65, 1464800000, 0.0, -0.42, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Domestic Institutional Investors (Mutual Funds & Insurance)", 16.32, 1104200000, 0.0, 0.54, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Non-Institutional / Public Retail", 11.72, 793100000, 0.0, -0.12, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
    ]

    relationships = [
        CorporateRelationshipItem("Jio Platforms Limited", "subsidiary", 66.48, "India", "Consolidated digital services holding company (Jio)", 109558.0, "FY2023-24", "disclosed", "Note 42"),
        CorporateRelationshipItem("Reliance Retail Ventures Limited", "subsidiary", 83.56, "India", "Consolidated consumer retail operations holding company", 306786.0, "FY2023-24", "disclosed", "Note 42"),
        CorporateRelationshipItem("Reliance O2C Limited", "subsidiary", 100.0, "India", "Refining, petrochemicals, and marketing operations subsidiary", 564749.0, "FY2023-24", "disclosed", "Note 42"),
        CorporateRelationshipItem("bp Exploration (Alpha) Limited", "joint_venture", 50.0, "United Kingdom", "KG D6 deepwater exploration & production joint venture partner", 14200.0, "FY2023-24", "disclosed", "Note 43"),
    ]

    commodities = [
        CommodityExposureItem("Crude Oil Feedstock", 43.2, 496076.0, "Brent Crude / Platts Dubai", "Domestic (KG Basin) & Middle East Import Mix", "Forward derivatives and operational crack spread hedging", "High sensitivity to global crude benchmarks and refining crack margins", "disclosed", "RIL AR FY24 Note 30"),
        CommodityExposureItem("Natural Gas & Condensate", 6.8, 78420.0, "JKM / Henry Hub / Domestic APM", "100% Domestic Offshore (KG D6)", "Government domestic gas pricing formula and long-term contracts", "Exposure to international LNG import parity and regulated ceilings", "disclosed", "RIL AR FY24 Note 30"),
        CommodityExposureItem("Petrochemical Polymers (PP, PE, PVC)", 12.4, 142000.0, "ICIS Asia Polymer Benchmarks", "70% Domestic / 30% Export", "Price pass-through mechanism to industrial and packaging consumers", "Polymer crack spread margin fluctuations relative to crude/naphtha", "disclosed", "RIL AR FY24 Note 30"),
    ]

    business_intel = [
        BusinessIntelligenceItem("division", "Jamnagar Refining & Petrochemical Complex", "World's largest integrated single-site refinery with 1.4 million bpd capacity and high Nelson Complexity Index (NCI 21.1)", "FY2023-24", "RIL MD&A"),
        BusinessIntelligenceItem("division", "Jio True 5G Nationwide Infrastructure", "Deployment of pan-India Standalone 5G network across 700MHz, 3300MHz, and 26GHz spectrum bands covering 100M+ users", "FY2023-24", "RIL MD&A"),
        BusinessIntelligenceItem("capex", "Dhirubhai Ambani Green Energy Giga Complex", "Commenced construction of multi-gigawatt facilities for Solar PV, Green Hydrogen electrolyzers, and Energy Storage at Jamnagar", "FY2023-24", "RIL MD&A"),
    ]

    return {
        "company_name": "Reliance Industries Limited",
        "symbol": "RELIANCE",
        "cin": "L17110MH1973PLC019786",
        "isin": "INE002A01018",
        "industry_sector": "energy_oil_gas",
        "consolidated_statements": cons_statements,
        "standalone_statements": cons_statements,  # mirrored structure for demonstration
        "segments": segments,
        "shareholding": shareholding,
        "relationships": relationships,
        "commodities": commodities,
        "business_intel": business_intel,
        "conflicts": [],
    }


def get_jiofin_extraction_bundle() -> Dict[str, Any]:
    """Audited financial and business disclosures for Jio Financial Services Limited (JIOFIN)."""
    periods = ["FY2023-24", "FY2022-23"]

    pnl_rows = [
        ExtractedRow("Interest Income", "interest_income", "Interest Income", "Note 18",
                     {"FY2023-24": 938.45, "FY2022-23": 38.20}),
        ExtractedRow("Net Gain on Fair Value / Dividends", "treasury_income", "Treasury and Investment Income", "Note 19",
                     {"FY2023-24": 886.12, "FY2022-23": 6.64}),
        ExtractedRow("Fees and Commission Income", "fee_commission_income", "Fee and Commission Income", "",
                     {"FY2023-24": 30.70, "FY2022-23": 0.00}),
        ExtractedRow("Total Income", "total_income", "Total Income", "",
                     {"FY2023-24": 1855.27, "FY2022-23": 44.84}),
        ExtractedRow("Employee Benefits Expense", "employee_benefits", "Employee Costs", "Note 21",
                     {"FY2023-24": 114.28, "FY2022-23": 1.25}),
        ExtractedRow("Other Operating Expenses", "operating_expenses", "Operating Expenses", "Note 22",
                     {"FY2023-24": 62.44, "FY2022-23": 1.84}),
        ExtractedRow("Depreciation and Amortisation", "depreciation", "Depreciation", "",
                     {"FY2023-24": 18.40, "FY2022-23": 0.15}),
        ExtractedRow("Total Expenses", "total_expenses", "Total Expenses", "",
                     {"FY2023-24": 195.12, "FY2022-23": 3.24}),
        ExtractedRow("Profit Before Tax", "profit_before_tax", "Profit Before Tax (PBT)", "",
                     {"FY2023-24": 1660.15, "FY2022-23": 41.60}),
        ExtractedRow("Tax Expense", "tax_expense", "Tax Expense", "",
                     {"FY2023-24": 55.60, "FY2022-23": 10.35}),
        ExtractedRow("Profit After Tax (PAT)", "profit_after_tax", "Profit After Tax (PAT)", "",
                     {"FY2023-24": 1604.55, "FY2022-23": 31.25}),
    ]

    bs_rows = [
        ExtractedRow("Cash and Bank Balances", "cash_and_equivalents", "Cash and Cash Equivalents", "Note 4",
                     {"FY2023-24": 2642.18, "FY2022-23": 840.15}),
        ExtractedRow("Investments (Treasury & Strategic)", "investments", "Investments in Financial Assets", "Note 5",
                     {"FY2023-24": 136412.00, "FY2022-23": 113200.00}),
        ExtractedRow("Loans and Advances (Loan Book)", "advances_loan_book", "Loans and Advances (Loan Book)", "Note 6",
                     {"FY2023-24": 540.25, "FY2022-23": 120.00}),
        ExtractedRow("Other Financial Assets", "other_noncurrent_assets", "Other Financial Assets", "",
                     {"FY2023-24": 194.00, "FY2022-23": 79.95}),
        ExtractedRow("Total Assets", "total_assets", "Total Assets", "",
                     {"FY2023-24": 139788.42, "FY2022-23": 114240.10}),
        ExtractedRow("Total Equity and Net Worth", "total_equity", "Total Equity", "",
                     {"FY2023-24": 138924.16, "FY2022-23": 114180.20}),
        ExtractedRow("Total Borrowings & Liabilities", "borrowings", "Borrowings and Liabilities", "",
                     {"FY2023-24": 864.26, "FY2022-23": 59.90}),
    ]

    cf_rows = [
        ExtractedRow("Cash Flow from Operating Activities", "cash_from_operations", "Operating Cash Flow", "CF Stmt",
                     {"FY2023-24": 1420.50, "FY2022-23": 25.10}),
        ExtractedRow("Cash Flow from Investing Activities", "cash_from_investing", "Investing Cash Flow", "CF Stmt",
                     {"FY2023-24": -1850.20, "FY2022-23": -12.40}),
        ExtractedRow("Cash Flow from Financing Activities", "cash_from_financing", "Financing Cash Flow", "CF Stmt",
                     {"FY2023-24": 512.40, "FY2022-23": 0.00}),
        ExtractedRow("Net Increase in Cash and Cash Equivalents", "net_change_cash", "Net Change in Cash", "CF Stmt",
                     {"FY2023-24": 82.70, "FY2022-23": 12.70}),
    ]

    cons_statements = {
        "profit_and_loss": ExtractedStatement("profit_and_loss", "consolidated", "INR", "INR_CRORES", periods, pnl_rows, [], "doc_jiofin_fy24_ar", "JFS FY24 Audited Consolidated Statements", [48]),
        "balance_sheet": ExtractedStatement("balance_sheet", "consolidated", "INR", "INR_CRORES", periods, bs_rows, [], "doc_jiofin_fy24_ar", "JFS FY24 Audited Consolidated Statements", [46]),
        "cash_flow": ExtractedStatement("cash_flow", "consolidated", "INR", "INR_CRORES", periods, cf_rows, [], "doc_jiofin_fy24_ar", "JFS FY24 Audited Consolidated Statements", [50]),
    }

    segments = [
        SegmentItem("Investment & Financing Activities", 1812.35, 97.7, 1642.10, 139200.0, 780.0, "FY2023-24", "consolidated", "Treasury investments, strategic holdings, and commercial lending", "disclosed", "JFS AR FY24 Note 26"),
        SegmentItem("Payment Solutions", 32.18, 1.7, 12.40, 420.0, 64.0, "FY2023-24", "consolidated", "Jio Payment Solutions: Soundbox, merchant POS, and payment aggregator services", "disclosed", "JFS AR FY24 Note 26"),
        SegmentItem("Insurance Broking & Other Services", 10.74, 0.6, 5.65, 168.0, 20.0, "FY2023-24", "consolidated", "Digital insurance distribution partnerships across health, motor, and life", "disclosed", "JFS AR FY24 Note 26"),
    ]

    shareholding = [
        ShareholdingItem("Promoter & Promoter Group", 47.12, 2993800000, 0.0, 0.0, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Foreign Institutional Investors (FII / FPI)", 19.53, 1240800000, 0.0, -0.65, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Domestic Institutional Investors (Mutual Funds & LIC)", 13.88, 881800000, 0.0, 0.82, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Non-Institutional / Public Retail", 19.47, 1237000000, 0.0, -0.17, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
    ]

    relationships = [
        CorporateRelationshipItem("Jio Finance Limited", "subsidiary", 100.0, "India", "Wholly owned core NBFC lending subsidiary", 540.25, "FY2023-24", "disclosed", "Note 29"),
        CorporateRelationshipItem("Jio Payment Solutions Limited", "subsidiary", 100.0, "India", "Payment aggregator and merchant acceptance network", 32.18, "FY2023-24", "disclosed", "Note 29"),
        CorporateRelationshipItem("Jio Insurance Broking Limited", "subsidiary", 100.0, "India", "Direct insurance broking corporate agent license", 10.74, "FY2023-24", "disclosed", "Note 29"),
        CorporateRelationshipItem("Jio BlackRock Asset Management Pvt Ltd", "joint_venture", 50.0, "India", "50:50 Joint Venture with BlackRock Inc. for digital-first Indian AMC", 150.0, "FY2023-24", "disclosed", "Note 30"),
    ]

    # Explicitly records Not Applicable for manufacturing raw materials
    commodities = [
        CommodityExposureItem(
            material_name="Physical Raw Materials (Not Applicable)",
            share_of_cogs_pct=0.0,
            annual_expenditure_cr=0.0,
            benchmark_index="Not Applicable",
            domestic_import_mix="Not Applicable",
            hedging_policy="Not Applicable",
            risk_summary="Non-banking financial institution with zero physical raw material consumption. Operational risk is driven by credit quality, liquidity, and regulatory capital adequacy.",
            evidence_status="disclosed",
            source_ref="JFS Statutory Note 32",
        ),
    ]

    business_intel = [
        BusinessIntelligenceItem("corporate_action", "Demerger and Separate Exchange Listing", "Completed demerger of financial services undertaking from Reliance Industries Limited in July 2023, listing on NSE and BSE on August 21, 2023", "FY2023-24", "JFS AR Director's Report"),
        BusinessIntelligenceItem("partnership", "Strategic Joint Venture with BlackRock", "Formed 50:50 Joint Venture with BlackRock Inc. to enter asset management and wealth management markets in India", "FY2023-24", "JFS AR Director's Report"),
        BusinessIntelligenceItem("product_launch", "Digital Lending & Device Financing Rollout", "Launched pilot products including Loan Against Mutual Funds, Home Loans, and digital device merchant financing", "FY2023-24", "JFS MD&A"),
    ]

    return {
        "company_name": "Jio Financial Services Limited",
        "symbol": "JIOFIN",
        "cin": "L65990MH1999PLC120918",
        "isin": "INE758E01017",
        "industry_sector": "banking_financial",
        "consolidated_statements": cons_statements,
        "standalone_statements": cons_statements,
        "segments": segments,
        "shareholding": shareholding,
        "relationships": relationships,
        "commodities": commodities,
        "business_intel": business_intel,
        "conflicts": [],
    }


def get_tcs_extraction_bundle() -> Dict[str, Any]:
    """Audited financial and business disclosures for Tata Consultancy Services Limited (TCS)."""
    periods = ["FY2023-24", "FY2022-23", "FY2021-22"]

    pnl_rows = [
        ExtractedRow("Revenue from Software Services", "revenue", "Revenue from Operations", "Note 24",
                     {"FY2023-24": 240893.0, "FY2022-23": 225458.0, "FY2021-22": 191754.0}),
        ExtractedRow("Other Income", "other_income", "Other Income", "Note 25",
                     {"FY2023-24": 8241.0, "FY2022-23": 6488.0, "FY2021-22": 5618.0}),
        ExtractedRow("Total Income", "total_income", "Total Income", "",
                     {"FY2023-24": 249134.0, "FY2022-23": 231946.0, "FY2021-22": 197372.0}),
        ExtractedRow("Employee Benefit Expenses", "employee_benefits", "Employee Benefit Expenses (Cost of Talent)", "Note 26",
                     {"FY2023-24": 136897.0, "FY2022-23": 127522.0, "FY2021-22": 107453.0}),
        ExtractedRow("Fees to External Consultants / Subcontractors", "purchases_stock_in_trade", "Fees to Subcontractors", "",
                     {"FY2023-24": 19836.0, "FY2022-23": 18520.0, "FY2021-22": 16420.0}),
        ExtractedRow("Depreciation and Amortisation", "depreciation", "Depreciation", "Note 13",
                     {"FY2023-24": 4987.0, "FY2022-23": 5022.0, "FY2021-22": 4604.0}),
        ExtractedRow("Other Operating Expenses", "other_expenses", "Other Operating Expenses", "Note 27",
                     {"FY2023-24": 19845.0, "FY2022-23": 15223.0, "FY2021-22": 14036.0}),
        ExtractedRow("Total Expenses", "total_expenses", "Total Expenses", "",
                     {"FY2023-24": 181565.0, "FY2022-23": 166287.0, "FY2021-22": 142513.0}),
        ExtractedRow("Operating Profit (EBIT)", "operating_profit", "Operating Profit (EBIT)", "",
                     {"FY2023-24": 59328.0, "FY2022-23": 59171.0, "FY2021-22": 49241.0}),
        ExtractedRow("Profit Before Tax", "profit_before_tax", "Profit Before Tax (PBT)", "",
                     {"FY2023-24": 61540.0, "FY2022-23": 56907.0, "FY2021-22": 51687.0}),
        ExtractedRow("Tax Expense", "tax_expense", "Tax Expense", "Note 28",
                     {"FY2023-24": 15441.0, "FY2022-23": 14604.0, "FY2021-22": 13238.0}),
        ExtractedRow("Profit for the Year (PAT)", "profit_after_tax", "Profit After Tax (PAT)", "",
                     {"FY2023-24": 46099.0, "FY2022-23": 42303.0, "FY2021-22": 38449.0}),
    ]

    bs_rows = [
        ExtractedRow("Property, Plant and Equipment & Data Centers", "ppe", "Property, Plant and Equipment (PPE)", "Note 12",
                     {"FY2023-24": 21412.0, "FY2022-23": 20840.0, "FY2021-22": 20120.0}),
        ExtractedRow("Goodwill and Intangible Assets", "goodwill", "Goodwill and Intangibles", "",
                     {"FY2023-24": 5120.0, "FY2022-23": 4980.0, "FY2021-22": 4850.0}),
        ExtractedRow("Cash, Bank Balances and Current Investments", "cash_and_equivalents", "Cash, Bank & Investments", "Note 16",
                     {"FY2023-24": 48829.0, "FY2022-23": 45120.0, "FY2021-22": 42800.0}),
        ExtractedRow("Trade Receivables and Unbilled Revenue", "trade_receivables", "Trade Receivables & Unbilled", "Note 17",
                     {"FY2023-24": 41512.0, "FY2022-23": 39410.0, "FY2021-22": 36200.0}),
        ExtractedRow("Total Assets", "total_assets", "Total Assets", "",
                     {"FY2023-24": 144834.0, "FY2022-23": 141614.0, "FY2021-22": 141514.0}),
        ExtractedRow("Total Equity", "total_equity", "Total Equity", "",
                     {"FY2023-24": 90488.0, "FY2022-23": 90424.0, "FY2021-22": 89139.0}),
        ExtractedRow("Total Borrowings (Debt-Free)", "borrowings_noncurrent", "Borrowings", "",
                     {"FY2023-24": 0.0, "FY2022-23": 0.0, "FY2021-22": 0.0}),
    ]

    cf_rows = [
        ExtractedRow("Cash Flow from Operating Activities", "cash_from_operations", "Operating Cash Flow", "CF Stmt",
                     {"FY2023-24": 44282.0, "FY2022-23": 41965.0, "FY2021-22": 39949.0}),
        ExtractedRow("Cash Flow from Investing Activities", "cash_from_investing", "Investing Cash Flow", "CF Stmt",
                     {"FY2023-24": -5210.0, "FY2022-23": -4820.0, "FY2021-22": -4510.0}),
        ExtractedRow("Cash Flow from Financing Activities", "cash_from_financing", "Financing Cash Flow", "CF Stmt",
                     {"FY2023-24": -36840.0, "FY2022-23": -35210.0, "FY2021-22": -33420.0}),
        ExtractedRow("Net Increase in Cash and Cash Equivalents", "net_change_cash", "Net Change in Cash", "CF Stmt",
                     {"FY2023-24": 2232.0, "FY2022-23": 1935.0, "FY2021-22": 2019.0}),
    ]

    cons_statements = {
        "profit_and_loss": ExtractedStatement("profit_and_loss", "consolidated", "INR", "INR_CRORES", periods, pnl_rows, [], "doc_tcs_fy24_ar", "TCS FY24 Audited Consolidated Statements", [246]),
        "balance_sheet": ExtractedStatement("balance_sheet", "consolidated", "INR", "INR_CRORES", periods, bs_rows, [], "doc_tcs_fy24_ar", "TCS FY24 Audited Consolidated Statements", [244]),
        "cash_flow": ExtractedStatement("cash_flow", "consolidated", "INR", "INR_CRORES", periods, cf_rows, [], "doc_tcs_fy24_ar", "TCS FY24 Audited Consolidated Statements", [248]),
    }

    segments = [
        SegmentItem("Banking, Financial Services & Insurance (BFSI)", 76845.0, 31.9, 19825.0, 34200.0, 11400.0, "FY2023-24", "consolidated", "Core banking modernization, cloud migrations, payments and capital markets IT", "disclosed", "TCS AR FY24 Segment Note"),
        SegmentItem("Consumer Business & Retail", 38061.0, 15.8, 9591.0, 16800.0, 5200.0, "FY2023-24", "consolidated", "Omnichannel commerce, supply chain visibility, and consumer goods IT", "disclosed", "TCS AR FY24 Segment Note"),
        SegmentItem("Life Sciences & Healthcare", 26980.0, 11.2, 7662.0, 12400.0, 3800.0, "FY2023-24", "consolidated", "Clinical trials digital transformation, regulatory compliance, and medtech platforms", "disclosed", "TCS AR FY24 Segment Note"),
        SegmentItem("Manufacturing & Industrial", 23607.0, 9.8, 6161.0, 10500.0, 3200.0, "FY2023-24", "consolidated", "Smart factory, IoT automation, and enterprise ERP integration", "disclosed", "TCS AR FY24 Segment Note"),
        SegmentItem("Technology & Services", 21439.0, 8.9, 5252.0, 9400.0, 2900.0, "FY2023-24", "consolidated", "Product engineering and AI platform integration for global tech majors", "disclosed", "TCS AR FY24 Segment Note"),
        SegmentItem("Communications, Media & Information Services", 16380.0, 6.8, 3407.0, 7800.0, 2400.0, "FY2023-24", "consolidated", "5G network slicing, digital OTT media platforms, and telecom OSS/BSS", "disclosed", "TCS AR FY24 Segment Note"),
    ]

    shareholding = [
        ShareholdingItem("Tata Sons & Promoter Entities", 71.77, 2596800000, 0.0, 0.0, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Foreign Institutional Investors (FII / FPI)", 12.72, 460200000, 0.0, -0.21, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Domestic Institutional Investors (Mutual Funds & LIC)", 10.51, 380300000, 0.0, 0.35, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
        ShareholdingItem("Non-Institutional / Public Retail", 5.00, 180900000, 0.0, -0.14, "FY2023-24", "2024-03-31", "disclosed", "NSE Reg 31 Filing"),
    ]

    relationships = [
        CorporateRelationshipItem("Tata Sons Private Limited", "promoter", 71.77, "India", "Ultimate holding entity of Tata Group", 0.0, "FY2023-24", "disclosed", "Note 32"),
        CorporateRelationshipItem("Tata Consultancy Services Netherlands B.V.", "subsidiary", 100.0, "Netherlands", "European operating hub subsidiary", 42100.0, "FY2023-24", "disclosed", "Note 34"),
        CorporateRelationshipItem("Tata America International Corporation", "subsidiary", 100.0, "United States", "North American customer contracting entity", 120900.0, "FY2023-24", "disclosed", "Note 34"),
    ]

    commodities = [
        CommodityExposureItem(
            material_name="Physical Raw Materials (Not Applicable)",
            share_of_cogs_pct=0.0,
            annual_expenditure_cr=0.0,
            benchmark_index="Not Applicable",
            domestic_import_mix="Not Applicable",
            hedging_policy="Not Applicable",
            risk_summary="Pure-play IT software services provider with zero physical raw material exposure. Primary operating cost is employee compensation (56.8% of revenue). Operating risk exposure is currency fluctuation (USD, GBP, EUR).",
            evidence_status="disclosed",
            source_ref="TCS Statutory Note 36",
        ),
    ]

    business_intel = [
        BusinessIntelligenceItem("workforce", "Global Talent & Diversity Metrics", "Global workforce of 601,546 employees representing 152 nationalities; 35.6% women representation; LTM IT services attrition rate of 12.5%", "FY2023-24", "TCS Annual Report Integrated Review"),
        BusinessIntelligenceItem("strategy", "AI and Generative AI Practice", "Over 300,000 employees trained in foundational AI/GenAI competencies; launched TCS AI WisdomNext and partnership with AWS, Azure, Google Cloud, and NVIDIA", "FY2023-24", "TCS MD&A"),
        BusinessIntelligenceItem("order_book", "Annual Total Contract Value (TCV)", "All-time high annual contract bookings (TCV) of $42.7 billion in FY24, including $13.2 billion Q4 TCV", "FY2023-24", "TCS Investor Release"),
    ]

    return {
        "company_name": "Tata Consultancy Services Limited",
        "symbol": "TCS",
        "cin": "L22210MH1995PLC084781",
        "isin": "INE467B01029",
        "industry_sector": "it_services",
        "consolidated_statements": cons_statements,
        "standalone_statements": cons_statements,
        "segments": segments,
        "shareholding": shareholding,
        "relationships": relationships,
        "commodities": commodities,
        "business_intel": business_intel,
        "conflicts": [],
    }
