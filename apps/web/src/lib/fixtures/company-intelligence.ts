/**
 * ZoneScan — Company Intelligence Synthetic Demo Fixtures
 * 
 * NOTICE: All companies, financial data, relationships, and filings in this file
 * are entirely FICTIONAL and SYNTHETIC. They are provided solely for demonstrating
 * the user interface and progressive disclosure architecture of the Financial
 * Intelligence module.
 * 
 * NO REAL LISTED COMPANY DATA OR PRIVATE FINANCIAL INFORMATION IS CONTAINED HEREIN.
 */

export type EvidenceStatus = "disclosed" | "verified" | "inferred" | "unconfirmed" | "unavailable";

export interface EvidenceDetail {
  id: string;
  itemName: string;
  status: EvidenceStatus;
  statusExplanation: string;
  sourceDocument?: string;
  sourceSection?: string;
  sourceDate?: string;
  filingType?: string;
  formula?: string;
  verificationSource?: string;
  plainSummary: string;
  verbatimExcerpt?: string;
  missingDataReason?: string;
}

export interface FinancialMetric {
  key: string;
  name: string;
  plainName: string;
  value: number | null;
  unit: string;
  period: string;
  status: EvidenceStatus;
  yoyChangePct?: number | null;
  evidenceId: string;
}

export interface BusinessSegment {
  name: string;
  revenueCr: number;
  revenueSharePct: number;
  ebitdaMarginPct: number;
  status: EvidenceStatus;
  description: string;
  evidenceId: string;
}

export interface ShareholdingGroup {
  category: string;
  percentage: number;
  changeQoQPct: number;
  status: EvidenceStatus;
}

export interface RelationshipItem {
  id: string;
  name: string;
  ticker?: string;
  type: "supplier" | "customer" | "competitor" | "raw_material";
  roleDescription: string;
  whyItMatters: string;
  concentrationPct?: number | null;
  evidenceStatus: EvidenceStatus;
  sourceReference: string;
  evidenceId: string;
}

export interface RawMaterialProfile {
  name: string;
  cogsSharePct: number;
  benchmarkPrice: string;
  trend30dPct: number;
  evidenceStatus: EvidenceStatus;
  description: string;
  evidenceId: string;
}

export interface RegulatoryFilingItem {
  id: string;
  title: string;
  type: "results" | "contract" | "shareholding" | "governance" | "expansion";
  typeLabel: string;
  date: string;
  exchange: string;
  plainSummary: string;
  status: EvidenceStatus;
  evidenceId: string;
  syntheticDocumentUrl?: string;
}

export interface FinancialYearRow {
  label: string;
  category: "revenue" | "expense" | "profit" | "balance_sheet" | "ratio";
  unit: string;
  isHeader?: boolean;
  indent?: boolean;
  status: EvidenceStatus;
  evidenceId: string;
  fy23: number | null;
  fy24: number | null;
  fy25: number | null;
  q1fy26: number | null;
  q2fy26: number | null;
}

export interface CompanyProfile {
  id: string;
  symbol: string;
  legalName: string;
  exchange: string;
  cin: string;
  isin: string;
  sector: string;
  industry: string;
  incorporatedYear: number;
  headquarters: string;
  marketCapCr: number;
  enterpriseValueCr: number;
  peRatio: number;
  pbRatio: number;
  oneLineDescription: string;
  plainLanguageOverview: string;
  primaryRevenueEngine: string;
  keySensitivityWarning: string;
  evidenceStatus: EvidenceStatus;
  evidenceId: string;
  headlineKPIs: FinancialMetric[];
  segments: BusinessSegment[];
  shareholding: {
    promoter: ShareholdingGroup;
    dii: ShareholdingGroup;
    fii: ShareholdingGroup;
    retail: ShareholdingGroup;
    pledgedPct: number;
    asOfDate: string;
    evidenceId: string;
  };
  financialStatements: FinancialYearRow[];
  relationships: RelationshipItem[];
  rawMaterials: RawMaterialProfile[];
  filings: RegulatoryFilingItem[];
}

export const SYNTHETIC_DATA_BANNER = {
  title: "SYNTHETIC DEMO FIXTURE · NOT REAL MARKET DATA",
  subtitle: "All financial figures, corporate relationships, and regulatory filings shown here are synthetic prototypes for testing the Financial Intelligence UI architecture.",
};

export const EVIDENCE_DETAILS_STORE: Record<string, EvidenceDetail> = {
  "ev-zenith-overview": {
    id: "ev-zenith-overview",
    itemName: "Company Profile & Identity",
    status: "disclosed",
    statusExplanation: "Directly disclosed in synthetic regulatory filings and corporate master data.",
    sourceDocument: "Ministry of Corporate Affairs (MCA21) & Exchange Master Data (Synthetic)",
    sourceSection: "Corporate Identification & Master Details",
    sourceDate: "2026-09-30",
    filingType: "Corporate Master Record",
    plainSummary: "Incorporation details, CIN, and registered office verified against statutory database records.",
    verbatimExcerpt: "CIN: L28910MH2012PLC987654 | Registered in Pune, Maharashtra. Authorized Capital: ₹120.00 Cr.",
  },
  "ev-zenith-revenue": {
    id: "ev-zenith-revenue",
    itemName: "Consolidated Revenue from Operations",
    status: "disclosed",
    statusExplanation: "Audited revenue directly extracted from the annual financial statements.",
    sourceDocument: "Annual Report FY2024-25 (Synthetic Fixture)",
    sourceSection: "Consolidated Statement of Profit and Loss, Note 24 (Revenue from Operations)",
    sourceDate: "2025-06-15",
    filingType: "Audited Annual Financial Results",
    plainSummary: "Revenue represents invoiced precision manufacturing components less GST and volume rebates.",
    verbatimExcerpt: "Sale of manufactured high-precision alloy components: ₹1,825.40 Cr (Previous Year: ₹1,480.20 Cr).",
  },
  "ev-zenith-gross-margin": {
    id: "ev-zenith-gross-margin",
    itemName: "Gross Margin %",
    status: "inferred",
    statusExplanation: "Derived by arithmetic formula from disclosed Revenue and Cost of Goods Sold.",
    formula: "Gross Margin = ((Revenue - Cost of Materials Consumed) / Revenue) × 100",
    sourceDocument: "Annual Report FY2024-25, Statement of Profit & Loss",
    sourceSection: "Note 24 (Revenue) and Note 25 (Cost of Materials Consumed)",
    sourceDate: "2025-06-15",
    plainSummary: "Calculated from disclosed raw material consumption of ₹1,020.20 Cr against revenue of ₹1,825.40 Cr, yielding 44.11%.",
    verbatimExcerpt: "Materials consumed: ₹1,020.20 Cr | Revenue: ₹1,825.40 Cr. Computed Gross Profit: ₹805.20 Cr.",
  },
  "ev-zenith-ebitda": {
    id: "ev-zenith-ebitda",
    itemName: "Operating EBITDA & Margin",
    status: "disclosed",
    statusExplanation: "Extracted from disclosure in Management Discussion and Analysis (MD&A) and Profit & Loss statement.",
    sourceDocument: "Annual Report FY2024-25, MD&A Section",
    sourceSection: "Operational Review, Key Financial Indicators Table, Page 42",
    sourceDate: "2025-06-15",
    filingType: "Annual Report Disclosures",
    plainSummary: "Earnings Before Interest, Taxes, Depreciation, and Amortization before exceptional items.",
    verbatimExcerpt: "Operating EBITDA stood at ₹410.20 Cr representing an operating margin of 22.47%.",
  },
  "ev-zenith-pat": {
    id: "ev-zenith-pat",
    itemName: "Profit After Tax (PAT)",
    status: "disclosed",
    statusExplanation: "Audited Net Profit after all finance costs and income tax provisions.",
    sourceDocument: "Annual Report FY2024-25, Profit and Loss Account",
    sourceSection: "Line Item: Profit for the year attributable to owners",
    sourceDate: "2025-06-15",
    filingType: "Audited Financial Statements",
    plainSummary: "Net profit after tax attributable to equity shareholders.",
    verbatimExcerpt: "Net Profit for the year: ₹244.80 Cr (FY24: ₹168.40 Cr). Basic & Diluted EPS: ₹24.48.",
  },
  "ev-zenith-debt": {
    id: "ev-zenith-debt",
    itemName: "Total Borrowings & Leverage",
    status: "disclosed",
    statusExplanation: "Sum of long-term term loans and working capital credit facilities.",
    sourceDocument: "Annual Report FY2024-25, Balance Sheet",
    sourceSection: "Note 17 (Non-current Borrowings) & Note 21 (Current Borrowings)",
    sourceDate: "2025-06-15",
    filingType: "Audited Balance Sheet",
    plainSummary: "Non-current term debt of ₹140.00 Cr and working capital credit of ₹70.00 Cr, total ₹210.00 Cr.",
    verbatimExcerpt: "Long-term borrowings from consortium banks: ₹140.00 Cr. Short-term facilities: ₹70.00 Cr.",
  },
  "ev-zenith-roce": {
    id: "ev-zenith-roce",
    itemName: "Return on Capital Employed (ROCE)",
    status: "inferred",
    statusExplanation: "Computed metric measuring operating efficiency relative to invested equity and debt.",
    formula: "ROCE = EBIT / (Total Equity + Total Borrowings - Cash & Equivalents) × 100",
    sourceDocument: "Annual Report FY2024-25 Financial Schedules",
    sourceSection: "Calculated from Notes 17, 18, and Profit & Loss Statement",
    sourceDate: "2025-06-15",
    plainSummary: "EBIT of ₹355.40 Cr divided by average capital employed yields 32.4%.",
  },
  "ev-zenith-cash": {
    id: "ev-zenith-cash",
    itemName: "Cash & Liquid Bank Balances",
    status: "disclosed",
    statusExplanation: "Audited cash, bank balances, and liquid mutual fund investments.",
    sourceDocument: "Annual Report FY2024-25, Balance Sheet",
    sourceSection: "Note 12 (Cash and Cash Equivalents) & Note 9 (Current Investments)",
    sourceDate: "2025-06-15",
    filingType: "Audited Balance Sheet",
    plainSummary: "Readily available liquidity in current accounts and overnight liquid treasuries.",
    verbatimExcerpt: "Balances with scheduled commercial banks in current accounts: ₹112.50 Cr; Liquid fund units: ₹56.00 Cr.",
  },
  "ev-zenith-orderbook": {
    id: "ev-zenith-orderbook",
    itemName: "Order Book & Contract Visibility",
    status: "unconfirmed",
    statusExplanation: "Stated in investor presentation management commentary; not an audited statutory balance sheet line.",
    sourceDocument: "Q2FY26 Investor Presentation (Synthetic)",
    sourceSection: "Slide 14: Order Pipeline & Business Visibility",
    sourceDate: "2026-10-24",
    filingType: "Investor Presentation",
    plainSummary: "Management estimated forward contract commitments over the next 18 months at ₹2,450 Cr.",
    verbatimExcerpt: "Estimated executable order backlog across automotive and aerospace divisions stands at ~₹2,450 Cr.",
  },
  "ev-zenith-segments": {
    id: "ev-zenith-segments",
    itemName: "Business Segment Reporting (Ind AS 108)",
    status: "disclosed",
    statusExplanation: "Statutory segment reporting audited under Indian Accounting Standard 108.",
    sourceDocument: "Annual Report FY2024-25, Financial Statements",
    sourceSection: "Note 36: Operating Segment Disclosures",
    sourceDate: "2025-06-15",
    filingType: "Segment Disclosures",
    plainSummary: "Segment revenue, segment expenses, and allocable operating profit as reported to the Chief Operating Decision Maker.",
    verbatimExcerpt: "Automotive Transmission: ₹766.7 Cr | Industrial Valves: ₹620.6 Cr | Aerospace Brackets: ₹292.1 Cr | Aftermarket: ₹146.0 Cr.",
  },
  "ev-zenith-shareholding": {
    id: "ev-zenith-shareholding",
    itemName: "Shareholding Pattern Disclosure",
    status: "disclosed",
    statusExplanation: "Statutory quarterly disclosure submitted under Regulation 31 of SEBI (LODR) Regulations.",
    sourceDocument: "SEBI LODR Regulation 31 Quarterly Filing (Synthetic)",
    sourceSection: "Statement showing shareholding pattern of the Promoter and Public shareholders",
    sourceDate: "2026-10-12",
    filingType: "Regulatory Shareholding Submission",
    plainSummary: "Promoter shareholding is 54.20% with zero shares encumbered/pledged. DII holding is 21.80%.",
    verbatimExcerpt: "Promoter & Promoter Group: 5,420,000 equity shares (54.20%). Pledged shares: Nil.",
  },
  "ev-rel-apex": {
    id: "ev-rel-apex",
    itemName: "Supplier: Apex Ferrous & Superalloys Ltd",
    status: "disclosed",
    statusExplanation: "Disclosed in annual report as a key material vendor under Related Party and Material Supply agreements.",
    sourceDocument: "Annual Report FY2024-25",
    sourceSection: "Note 38: Key Sourcing Commitments & Related Party Disclosures",
    sourceDate: "2025-06-15",
    filingType: "Audited Annual Report Note",
    plainSummary: "Apex Ferrous supplies forging-grade carbon steel billets and certified aircraft alloy rounds (26% of COGS).",
    verbatimExcerpt: "Purchases of alloy steel billets from Apex Ferrous & Superalloys during the period aggregated to ₹265.25 Cr.",
  },
  "ev-rel-titan": {
    id: "ev-rel-titan",
    itemName: "Supplier: Titan Sealants & Polymers",
    status: "inferred",
    statusExplanation: "Inferred from purchase order tender awards and industrial certification filings.",
    formula: "Inferred from vendor registration notices published in public trade tenders.",
    sourceDocument: "Industry Vendor Certification Registry (Synthetic)",
    sourceDate: "2025-11-20",
    plainSummary: "Provides high-temperature elastomer O-rings and hydraulic cylinder seals (~8% of direct material spend).",
  },
  "ev-rel-orion": {
    id: "ev-rel-orion",
    itemName: "Supplier: Orion Precision Bearings Ltd",
    status: "disclosed",
    statusExplanation: "Disclosed in supply agreement announcements filed with the exchange.",
    sourceDocument: "BSE Corporate Announcement (Synthetic)",
    sourceSection: "Long-term Component Sourcing Memorandum",
    sourceDate: "2024-12-05",
    plainSummary: "Supplies precision needle and taper roller bearings used in valve actuator sub-assemblies (11% of COGS).",
  },
  "ev-rel-vanguard": {
    id: "ev-rel-vanguard",
    itemName: "Customer: Vanguard Commercial Motors Ltd",
    status: "disclosed",
    statusExplanation: "Disclosed as single largest customer (>10% revenue concentration threshold under Ind AS 108).",
    sourceDocument: "Annual Report FY2024-25",
    sourceSection: "Note 36.3: Major Customers Concentration Disclosure",
    sourceDate: "2025-06-15",
    filingType: "Statutory Concentration Disclosure",
    plainSummary: "Zenith manufactures heavy truck differential casings and axle transmission housings for Vanguard (28% of total revenue).",
    verbatimExcerpt: "Revenue from one customer of the Automotive Transmission segment represents approximately ₹511.10 Cr of total revenue.",
  },
  "ev-rel-helios": {
    id: "ev-rel-helios",
    itemName: "Customer: Helios Wind & Industrial Turbines",
    status: "disclosed",
    statusExplanation: "Disclosed in segment commentary and export contract disclosures.",
    sourceDocument: "Annual Report FY2024-25, MD&A",
    sourceSection: "Industrial Equipment Division Highlights",
    sourceDate: "2025-06-15",
    plainSummary: "Purchases high-pressure hydraulic pitch valve manifold blocks for wind power turbines (19% of revenue).",
  },
  "ev-rel-aerodynamic": {
    id: "ev-rel-aerodynamic",
    itemName: "Customer: AeroDynamic Defense Systems",
    status: "inferred",
    statusExplanation: "Inferred from defense subcontract registration certificates and export shipping manifests.",
    sourceDocument: "Directorate of Industrial Licenses Disclosures (Synthetic)",
    sourceDate: "2025-08-14",
    plainSummary: "Procures structural titanium fuselage spars and lightweight radar housing brackets (~12% of revenue).",
  },
  "ev-rel-transrail": {
    id: "ev-rel-transrail",
    itemName: "Customer: TransRail Locomotives Ltd",
    status: "unconfirmed",
    statusExplanation: "Mentioned in trade magazine reports regarding freight locomotive bogie frame contracts.",
    sourceDocument: "Railway Equipment Journal (Synthetic Trade Publication)",
    sourceDate: "2026-05-18",
    plainSummary: "Reported trial supplier for electric locomotive braking manifold assemblies; pending statutory disclosure.",
  },
  "ev-rel-bharat": {
    id: "ev-rel-bharat",
    itemName: "Competitor: Bharat Precision Forgings Ltd",
    status: "disclosed",
    statusExplanation: "Identified in company-commissioned industry benchmarking report included in regulatory prospectus.",
    sourceDocument: "Annual Report FY2024-25, Industry Peer Comparison",
    sourceSection: "Benchmarking against direct listed engineering peers",
    sourceDate: "2025-06-15",
    plainSummary: "Direct competitor in automotive transmission forgings with ₹2,100 Cr annual revenue and 20.8% EBITDA margin.",
  },
  "ev-rel-kalyan": {
    id: "ev-rel-kalyan",
    itemName: "Competitor: Kalyan Heavy Machining Corp",
    status: "inferred",
    statusExplanation: "Inferred from overlap in registered NIC manufacturing codes and commercial bids.",
    sourceDocument: "BSE Industry Classification Master (Synthetic)",
    sourceDate: "2026-01-10",
    plainSummary: "Competes in industrial turbine manifold blocks and large-bore hydraulic valves.",
  },
  "ev-rel-dexter": {
    id: "ev-rel-dexter",
    itemName: "Competitor: Dexter Industrial Systems",
    status: "unconfirmed",
    statusExplanation: "Mentioned by brokerage sector analysis note; not verified in company statutory filings.",
    sourceDocument: "Sector Research Note (Synthetic Brokerage)",
    sourceDate: "2026-07-22",
    plainSummary: "Privately held fabricator expanding capacity into hydraulic valve blocks.",
  },
  "ev-raw-steel": {
    id: "ev-raw-steel",
    itemName: "Raw Material: Forging-Grade Alloy Steel",
    status: "disclosed",
    statusExplanation: "Disclosed in Annual Report Raw Materials Consumption note.",
    sourceDocument: "Annual Report FY2024-25, Notes to Financial Statements",
    sourceSection: "Note 25.1: Details of Raw Materials Consumed",
    sourceDate: "2025-06-15",
    plainSummary: "Forging quality carbon steel bars account for 38% of total raw material consumption cost.",
    verbatimExcerpt: "Alloy and carbon steel rounds: ₹387.68 Cr (38.0% of total consumption).",
  },
  "ev-raw-nickel": {
    id: "ev-raw-nickel",
    itemName: "Raw Material: Nickel-Chromium Billet Alloys",
    status: "disclosed",
    statusExplanation: "Disclosed in specialty materials procurement schedule.",
    sourceDocument: "Annual Report FY2024-25, Notes to Financial Statements",
    sourceSection: "Note 25.1: High-nickel billet alloys for aerospace brackets",
    sourceDate: "2025-06-15",
    plainSummary: "High-temperature aerospace alloys account for 14% of raw material cost.",
  },
  "ev-raw-power": {
    id: "ev-raw-power",
    itemName: "Input: Industrial Power & Energy Tariffs",
    status: "inferred",
    statusExplanation: "Inferred from Manufacturing Expenses note; electric arc furnaces & CNC heating load.",
    sourceDocument: "Annual Report FY2024-25",
    sourceSection: "Note 26: Other Manufacturing Expenses (Power & Fuel)",
    sourceDate: "2025-06-15",
    plainSummary: "Grid electrical tariffs represent 9% of total cash manufacturing overheads.",
  },
};

export const DEMO_COMPANIES: CompanyProfile[] = [
  {
    id: "zenith-fab",
    symbol: "ZENITHFAB",
    legalName: "Zenith Precision Fabrications Ltd",
    exchange: "NSE (Synthetic Fixture)",
    cin: "L28910MH2012PLC987654",
    isin: "INE999X01099",
    sector: "Capital Goods & Engineering",
    industry: "Industrial Machinery & Components",
    incorporatedYear: 2012,
    headquarters: "Pune, Maharashtra",
    marketCapCr: 4896.00,
    enterpriseValueCr: 4937.50,
    peRatio: 20.0,
    pbRatio: 5.53,
    oneLineDescription: "Engineered high-tolerance alloy structures, hydraulic valve manifolds, and automotive transmission housings.",
    plainLanguageOverview: "Zenith transforms specialty alloy steel billets into high-precision machined sub-assemblies for automotive OEMs, wind turbine builders, and aerospace equipment makers. The company earns predictable operating cash flow from long-term supply contracts, but is sensitive to commodity alloy steel prices.",
    primaryRevenueEngine: "Long-term multi-year component supply agreements with Tier-1 automotive and industrial machinery equipment builders.",
    keySensitivityWarning: "Raw materials represent 55.9% of total revenue. A 10% sustained increase in alloy steel prices without customer pass-through compresses operating EBITDA margin by approximately 212 basis points.",
    evidenceStatus: "disclosed",
    evidenceId: "ev-zenith-overview",
    headlineKPIs: [
      {
        key: "revenue",
        name: "Revenue from Operations",
        plainName: "Total Invoiced Sales",
        value: 1825.40,
        unit: "₹ Cr",
        period: "FY25 Audited",
        status: "disclosed",
        yoyChangePct: 23.32,
        evidenceId: "ev-zenith-revenue",
      },
      {
        key: "gross_margin",
        name: "Gross Margin",
        plainName: "Sales minus Raw Material Cost",
        value: 44.11,
        unit: "%",
        period: "FY25 Computed",
        status: "inferred",
        yoyChangePct: 0.91,
        evidenceId: "ev-zenith-gross-margin",
      },
      {
        key: "ebitda",
        name: "Operating EBITDA",
        plainName: "Core Cash Operating Profit",
        value: 410.20,
        unit: "₹ Cr",
        period: "FY25 (22.5% Margin)",
        status: "disclosed",
        yoyChangePct: 33.14,
        evidenceId: "ev-zenith-ebitda",
      },
      {
        key: "pat",
        name: "Net Profit (PAT)",
        plainName: "Bottom-Line Profit after Taxes",
        value: 244.80,
        unit: "₹ Cr",
        period: "FY25 (13.4% Margin)",
        status: "disclosed",
        yoyChangePct: 45.37,
        evidenceId: "ev-zenith-pat",
      },
      {
        key: "debt",
        name: "Total Borrowings",
        plainName: "Bank Loans & Credit Lines",
        value: 210.00,
        unit: "₹ Cr",
        period: "FY25 (D/E: 0.24×)",
        status: "disclosed",
        yoyChangePct: -23.64,
        evidenceId: "ev-zenith-debt",
      },
      {
        key: "roce",
        name: "Return on Capital (ROCE)",
        plainName: "Efficiency on Invested Money",
        value: 32.40,
        unit: "%",
        period: "FY25 Computed",
        status: "inferred",
        yoyChangePct: 4.80,
        evidenceId: "ev-zenith-roce",
      },
      {
        key: "cash",
        name: "Cash & Liquid Assets",
        plainName: "Ready Cash in Bank & Mutual Funds",
        value: 168.50,
        unit: "₹ Cr",
        period: "FY25 Liquid Balance",
        status: "disclosed",
        yoyChangePct: 50.45,
        evidenceId: "ev-zenith-cash",
      },
      {
        key: "orderbook",
        name: "Order Book Visibility",
        plainName: "Confirmed Forward Customer Orders",
        value: 2450.00,
        unit: "₹ Cr",
        period: "Q2FY26 Presentation",
        status: "unconfirmed",
        yoyChangePct: 18.20,
        evidenceId: "ev-zenith-orderbook",
      },
    ],
    segments: [
      {
        name: "Automotive Transmission Housings",
        revenueCr: 766.70,
        revenueSharePct: 42.0,
        ebitdaMarginPct: 23.4,
        status: "disclosed",
        description: "Heavy commercial vehicle transmission blocks and differential gear casings supplied to truck manufacturers.",
        evidenceId: "ev-zenith-segments",
      },
      {
        name: "Industrial Valve & Pump Bodies",
        revenueCr: 620.60,
        revenueSharePct: 34.0,
        ebitdaMarginPct: 25.1,
        status: "disclosed",
        description: "High-pressure hydraulic pitch manifold assemblies for wind turbines, oil processing, and chemical fluid pumps.",
        evidenceId: "ev-zenith-segments",
      },
      {
        name: "Aerospace Structural Brackets",
        revenueCr: 292.10,
        revenueSharePct: 16.0,
        ebitdaMarginPct: 28.5,
        status: "disclosed",
        description: "Certified titanium and nickel-alloy structural mountings and radar spars for commercial and defense aviation.",
        evidenceId: "ev-zenith-segments",
      },
      {
        name: "Precision Aftermarket & Tooling",
        revenueCr: 146.00,
        revenueSharePct: 8.0,
        ebitdaMarginPct: 31.0,
        status: "disclosed",
        description: "Specialized replacement wear plates, seal glands, and high-speed cutting dies.",
        evidenceId: "ev-zenith-segments",
      },
    ],
    shareholding: {
      promoter: { category: "Promoter & Group", percentage: 54.20, changeQoQPct: 0.40, status: "disclosed" },
      dii: { category: "Mutual Funds & DIIs", percentage: 21.80, changeQoQPct: 0.80, status: "disclosed" },
      fii: { category: "Foreign Portfolio (FII)", percentage: 14.50, changeQoQPct: -0.30, status: "disclosed" },
      retail: { category: "Public & Retail", percentage: 9.50, changeQoQPct: -0.90, status: "disclosed" },
      pledgedPct: 0.0,
      asOfDate: "September 30, 2026",
      evidenceId: "ev-zenith-shareholding",
    },
    financialStatements: [
      { label: "INCOME STATEMENT", category: "revenue", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null },
      { label: "Revenue from Operations", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 1240.50, fy24: 1480.20, fy25: 1825.40, q1fy26: 495.20, q2fy26: 520.80 },
      { label: "Other Operating Income", category: "revenue", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 14.20, fy24: 18.50, fy25: 22.10, q1fy26: 5.80, q2fy26: 6.20 },
      { label: "Total Revenue", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 1254.70, fy24: 1498.70, fy25: 1847.50, q1fy26: 501.00, q2fy26: 527.00 },
      { label: "Cost of Materials Consumed (COGS)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 720.00, fy24: 840.10, fy25: 1020.20, q1fy26: 275.40, q2fy26: 288.60 },
      { label: "Gross Profit", category: "profit", unit: "₹ Cr", status: "inferred", evidenceId: "ev-zenith-gross-margin", fy23: 520.50, fy24: 640.10, fy25: 805.20, q1fy26: 219.80, q2fy26: 232.20 },
      { label: "Gross Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-gross-margin", fy23: 41.96, fy24: 43.24, fy25: 44.11, q1fy26: 44.39, q2fy26: 44.59 },
      { label: "Employee Benefit Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 142.00, fy24: 165.20, fy25: 198.50, q1fy26: 53.20, q2fy26: 55.40 },
      { label: "Other Operating Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 143.00, fy24: 166.80, fy25: 196.50, q1fy26: 52.80, q2fy26: 54.60 },
      { label: "Operating EBITDA", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 235.50, fy24: 308.10, fy25: 410.20, q1fy26: 113.80, q2fy26: 122.20 },
      { label: "EBITDA Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-ebitda", fy23: 18.98, fy24: 20.81, fy25: 22.47, q1fy26: 22.98, q2fy26: 23.46 },
      { label: "Depreciation & Amortization", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 42.00, fy24: 48.50, fy25: 54.80, q1fy26: 14.20, q2fy26: 14.80 },
      { label: "Operating Profit (EBIT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-roce", fy23: 193.50, fy24: 259.60, fy25: 355.40, q1fy26: 99.60, q2fy26: 107.40 },
      { label: "Finance Costs (Interest)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 38.20, fy24: 34.50, fy25: 28.20, q1fy26: 6.80, q2fy26: 6.40 },
      { label: "Profit Before Tax (PBT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 155.30, fy24: 225.10, fy25: 327.20, q1fy26: 92.80, q2fy26: 101.00 },
      { label: "Tax Expense", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 39.10, fy24: 56.70, fy25: 82.40, q1fy26: 23.40, q2fy26: 25.50 },
      { label: "Net Profit (PAT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 116.20, fy24: 168.40, fy25: 244.80, q1fy26: 69.40, q2fy26: 75.50 },
      { label: "PAT Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-pat", fy23: 9.37, fy24: 11.38, fy25: 13.41, q1fy26: 14.01, q2fy26: 14.50 },
      { label: "Basic & Diluted EPS", category: "ratio", unit: "₹", indent: true, status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 11.62, fy24: 16.84, fy25: 24.48, q1fy26: 6.94, q2fy26: 7.55 },
      { label: "BALANCE SHEET HIGHLIGHTS", category: "balance_sheet", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null },
      { label: "Net Fixed Assets (PPE)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 410.00, fy24: 485.00, fy25: 560.00, q1fy26: null, q2fy26: null },
      { label: "Inventories", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 215.00, fy24: 245.00, fy25: 285.00, q1fy26: null, q2fy26: null },
      { label: "Trade Receivables", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 240.00, fy24: 290.00, fy25: 345.00, q1fy26: null, q2fy26: null },
      { label: "Cash & Cash Equivalents", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-cash", fy23: 85.00, fy24: 112.00, fy25: 168.50, q1fy26: null, q2fy26: null },
      { label: "Total Shareholder Equity", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 580.00, fy24: 715.00, fy25: 885.00, q1fy26: null, q2fy26: null },
      { label: "Total Borrowings (Debt)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 320.00, fy24: 275.00, fy25: 210.00, q1fy26: null, q2fy26: null },
      { label: "Debt / Equity Ratio", category: "ratio", unit: "×", indent: true, status: "inferred", evidenceId: "ev-zenith-debt", fy23: 0.55, fy24: 0.38, fy25: 0.24, q1fy26: null, q2fy26: null },
    ],
    relationships: [
      {
        id: "apex-alloys",
        name: "Apex Ferrous & Superalloys Ltd",
        ticker: "APEXALLOY",
        type: "supplier",
        roleDescription: "Primary Forging Billet & Bar Supplier",
        whyItMatters: "Supplies 26% of Zenith's total direct raw material spend. Zenith holds a 3-year fixed alloy-index pricing pact with Apex to mitigate sudden price spikes.",
        concentrationPct: 26.0,
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, Note 38 (Related Party & Sourcing Commitments)",
        evidenceId: "ev-rel-apex",
      },
      {
        id: "titan-polymers",
        name: "Titan Sealants & Industrial Polymers",
        type: "supplier",
        roleDescription: "Hydraulic Gland & High-Pressure Seal Supplier",
        whyItMatters: "Sole-source provider for sub-zero temperature fluorocarbon O-rings used in wind turbine manifold blocks (~8% of direct material cost).",
        concentrationPct: 8.0,
        evidenceStatus: "inferred",
        sourceReference: "Industry Vendor Certification Registry & Purchase Orders",
        evidenceId: "ev-rel-titan",
      },
      {
        id: "orion-bearings",
        name: "Orion Precision Bearings Ltd",
        ticker: "ORIONBEAR",
        type: "supplier",
        roleDescription: "Needle & Taper Roller Bearings Provider",
        whyItMatters: "Provides high-load bearings embedded inside transmission sub-assemblies (11% of direct raw materials).",
        concentrationPct: 11.0,
        evidenceStatus: "disclosed",
        sourceReference: "BSE Corporate Disclosure: Component Sourcing Agreement",
        evidenceId: "ev-rel-orion",
      },
      {
        id: "vanguard-motors",
        name: "Vanguard Commercial Motors Ltd",
        ticker: "VANGUARD",
        type: "customer",
        roleDescription: "Heavy Commercial Vehicle Manufacturer",
        whyItMatters: "Zenith's largest customer, accounting for 28% of total revenue. Contracts for differential gear and transmission housings renewed through 2029.",
        concentrationPct: 28.0,
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, Note 36.3 (Major Customer Concentration)",
        evidenceId: "ev-rel-vanguard",
      },
      {
        id: "helios-turbines",
        name: "Helios Wind & Industrial Turbines",
        type: "customer",
        roleDescription: "Wind Power Equipment Builder",
        whyItMatters: "Purchases 19% of Zenith's output for pitch control hydraulic manifold blocks; exposure to expanding renewable energy installations.",
        concentrationPct: 19.0,
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, MD&A Section",
        evidenceId: "ev-rel-helios",
      },
      {
        id: "aerodynamic-systems",
        name: "AeroDynamic Defense Systems",
        type: "customer",
        roleDescription: "Aerospace Structural Integrator",
        whyItMatters: "High-margin defense contractor purchasing lightweight titanium spars; accounts for 12% of revenue with 28.5% divisional margin.",
        concentrationPct: 12.0,
        evidenceStatus: "inferred",
        sourceReference: "Defense Industrial Subcontract Manifests",
        evidenceId: "ev-rel-aerodynamic",
      },
      {
        id: "transrail-locomotives",
        name: "TransRail Locomotives Ltd",
        type: "customer",
        roleDescription: "Railways & Rolling Stock Builder",
        whyItMatters: "Trial supplier for locomotive pneumatic brake valve castings (~9% potential revenue); contract is undergoing field trials.",
        concentrationPct: 9.0,
        evidenceStatus: "unconfirmed",
        sourceReference: "Trade Publication: Railway Equipment Review",
        evidenceId: "ev-rel-transrail",
      },
      {
        id: "bharat-forgings",
        name: "Bharat Precision Forgings Ltd",
        ticker: "BHARATFORG",
        type: "competitor",
        roleDescription: "Direct Commercial Vehicle Forgings Peer",
        whyItMatters: "Direct competitor in automotive transmission forgings with ₹2,100 Cr revenue and 20.8% EBITDA margin. Bids on identical OEM tenders.",
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, Peer Group Review",
        evidenceId: "ev-rel-bharat",
      },
      {
        id: "kalyan-machining",
        name: "Kalyan Heavy Machining Corp",
        type: "competitor",
        roleDescription: "Turbine Manifold Competitor",
        whyItMatters: "Competes head-to-head in hydraulic manifold blocks and precision CNC machining.",
        evidenceStatus: "inferred",
        sourceReference: "BSE Industry Classification Master",
        evidenceId: "ev-rel-kalyan",
      },
      {
        id: "dexter-industrial",
        name: "Dexter Industrial Systems",
        type: "competitor",
        roleDescription: "Hydraulic Components Competitor",
        whyItMatters: "Privately owned fabricator reportedly adding 5-axis CNC machining bays to contest industrial valve body orders.",
        evidenceStatus: "unconfirmed",
        sourceReference: "Analyst Research Note (Unconfirmed)",
        evidenceId: "ev-rel-dexter",
      },
      {
        id: "raw-forging-steel",
        name: "Alloy & Carbon Forging Steel",
        type: "raw_material",
        roleDescription: "Primary Direct Production Material",
        whyItMatters: "Represents 38.0% of Zenith's total raw material consumption cost. Billet index price changes directly impact gross margins.",
        concentrationPct: 38.0,
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, Note 25.1",
        evidenceId: "ev-raw-steel",
      },
      {
        id: "raw-nickel-alloy",
        name: "Nickel-Chromium Billet Alloys",
        type: "raw_material",
        roleDescription: "Aerospace High-Temperature Material",
        whyItMatters: "High unit cost material representing 14.0% of materials consumed. Pegged to international London Metal Exchange / MCX Nickel spot rates.",
        concentrationPct: 14.0,
        evidenceStatus: "disclosed",
        sourceReference: "Annual Report FY25, Note 25.1",
        evidenceId: "ev-raw-nickel",
      },
      {
        id: "raw-industrial-power",
        name: "Industrial Electric Grid Power",
        type: "raw_material",
        roleDescription: "Furnace & CNC Electrical Energy",
        whyItMatters: "Represents 9.0% of cash operating overheads. State electricity board tariffs affect monthly conversion cost.",
        concentrationPct: 9.0,
        evidenceStatus: "inferred",
        sourceReference: "Annual Report FY25, Note 26",
        evidenceId: "ev-raw-power",
      },
    ],
    rawMaterials: [
      {
        name: "Forging-Grade Carbon & Alloy Steel",
        cogsSharePct: 38.0,
        benchmarkPrice: "₹54,200 / Tonne",
        trend30dPct: 3.4,
        evidenceStatus: "disclosed",
        description: "Primary forging stock for truck transmission housings and valve bodies. Sourced under semi-annual index contracts.",
        evidenceId: "ev-raw-steel",
      },
      {
        name: "Nickel-Chromium High-Heat Alloys",
        cogsSharePct: 14.0,
        benchmarkPrice: "₹1,420 / Kg",
        trend30dPct: -1.8,
        evidenceStatus: "disclosed",
        description: "Certified aerospace alloy rounds for titanium-nickel brackets and turbine spars.",
        evidenceId: "ev-raw-nickel",
      },
      {
        name: "Industrial Electrical Power",
        cogsSharePct: 9.0,
        benchmarkPrice: "₹8.40 / kWh",
        trend30dPct: 0.0,
        evidenceStatus: "inferred",
        description: "Continuous industrial 33kV dedicated substation feed for CNC machining bays and induction heat-treatment furnaces.",
        evidenceId: "ev-raw-power",
      },
    ],
    filings: [
      {
        id: "filing-q2-fy26",
        title: "Outcome of Board Meeting: Unaudited Financial Results for Q2 ended Sept 30, 2026",
        type: "results",
        typeLabel: "Quarterly Results",
        date: "2026-10-24",
        exchange: "NSE & BSE",
        plainSummary: "Board approved Q2 results showing ₹520.80 Cr revenue (+18.4% YoY) and net profit of ₹75.50 Cr (+21.2% YoY). Interim dividend of ₹3.50 per share declared.",
        status: "disclosed",
        evidenceId: "ev-zenith-pat",
      },
      {
        id: "filing-contract-vanguard",
        title: "Disclosure under Reg 30: Multi-Year Supply Agreement Renewal with Vanguard Motors",
        type: "contract",
        typeLabel: "Material Contract",
        date: "2026-09-18",
        exchange: "NSE",
        plainSummary: "Secured a 3-year extension with Vanguard Commercial Motors for new generation electric delivery van chassis transmission housings valued at ~₹620 Cr.",
        status: "disclosed",
        evidenceId: "ev-rel-vanguard",
      },
      {
        id: "filing-shareholding-q2",
        title: "Shareholding Pattern pursuant to Regulation 31 for the Quarter ended September 2026",
        type: "shareholding",
        typeLabel: "Shareholding",
        date: "2026-10-12",
        exchange: "BSE & NSE",
        plainSummary: "Promoter shareholding steady at 54.20% with zero pledged shares. Institutional domestic holdings increased by 0.80% to 21.80%.",
        status: "disclosed",
        evidenceId: "ev-zenith-shareholding",
      },
      {
        id: "filing-expansion-pune",
        title: "Corporate Announcement: Operationalization of 5-Axis Precision Machining Bay at Pune Facility",
        type: "expansion",
        typeLabel: "Capacity Expansion",
        date: "2026-08-30",
        exchange: "NSE",
        plainSummary: "Commissioned Phase-II brownfield expansion adding 12 new high-speed multi-axis CNC machines, boosting aerospace component capacity by 35%.",
        status: "disclosed",
        evidenceId: "ev-zenith-overview",
      },
    ],
  },
  {
    id: "apex-alloys",
    symbol: "APEXALLOY",
    legalName: "Apex Ferrous & Superalloys Ltd",
    exchange: "NSE (Synthetic Fixture)",
    cin: "L27100GJ2008PLC876543",
    isin: "INE888Y01088",
    sector: "Metals & Mining",
    industry: "Specialty Steel & Forging Billets",
    incorporatedYear: 2008,
    headquarters: "Ahmedabad, Gujarat",
    marketCapCr: 3240.00,
    enterpriseValueCr: 3490.00,
    peRatio: 16.5,
    pbRatio: 3.8,
    oneLineDescription: "Secondary steel alloy producer manufacturing certified aircraft rounds, ESR grade billets, and forging stock.",
    plainLanguageOverview: "Apex melts scrap and ferro-alloys in vacuum induction furnaces to produce specialty steel billets. It supplies precision engineering shops and toolmakers across Western India.",
    primaryRevenueEngine: "Sale of specialty alloy billets, forged bars, and stainless steel rounds to tier-1 manufacturing fabricators.",
    keySensitivityWarning: "Directly vulnerable to international nickel, scrap metal, and coking coal price shifts.",
    evidenceStatus: "disclosed",
    evidenceId: "ev-rel-apex",
    headlineKPIs: [
      { key: "revenue", name: "Revenue from Operations", plainName: "Invoiced Sales", value: 1280.00, unit: "₹ Cr", period: "FY25 Audited", status: "disclosed", yoyChangePct: 14.2, evidenceId: "ev-rel-apex" },
      { key: "gross_margin", name: "Gross Margin", plainName: "Value Addition Margin", value: 36.50, unit: "%", period: "FY25 Computed", status: "inferred", yoyChangePct: -1.2, evidenceId: "ev-rel-apex" },
      { key: "ebitda", name: "Operating EBITDA", plainName: "Operating Cash Profit", value: 215.00, unit: "₹ Cr", period: "FY25 (16.8%)", status: "disclosed", yoyChangePct: 18.5, evidenceId: "ev-rel-apex" },
      { key: "pat", name: "Net Profit (PAT)", plainName: "Bottom-Line Profit", value: 132.00, unit: "₹ Cr", period: "FY25 (10.3%)", status: "disclosed", yoyChangePct: 22.0, evidenceId: "ev-rel-apex" },
      { key: "debt", name: "Total Borrowings", plainName: "Bank Borrowings", value: 250.00, unit: "₹ Cr", period: "FY25", status: "disclosed", yoyChangePct: -8.0, evidenceId: "ev-rel-apex" },
      { key: "roce", name: "ROCE", plainName: "Return on Capital", value: 22.40, unit: "%", period: "FY25 Computed", status: "inferred", yoyChangePct: 2.1, evidenceId: "ev-rel-apex" },
      { key: "cash", name: "Cash & Liquid Assets", plainName: "Cash in Bank", value: 45.00, unit: "₹ Cr", period: "FY25", status: "disclosed", yoyChangePct: 12.5, evidenceId: "ev-rel-apex" },
      { key: "orderbook", name: "Order Backlog", plainName: "Contract Backlog", value: 980.00, unit: "₹ Cr", period: "Management Disclosure", status: "unconfirmed", yoyChangePct: 9.5, evidenceId: "ev-rel-apex" },
    ],
    segments: [
      { name: "Alloy Steel Forging Billets", revenueCr: 742.40, revenueSharePct: 58.0, ebitdaMarginPct: 17.2, status: "disclosed", description: "Vacuum degassed forging rounds for auto components.", evidenceId: "ev-rel-apex" },
      { name: "Aircraft & Defense Superalloys", revenueCr: 358.40, revenueSharePct: 28.0, ebitdaMarginPct: 21.0, status: "disclosed", description: "Electro-slag remelted (ESR) nickel and chrome alloy ingots.", evidenceId: "ev-rel-apex" },
      { name: "Tool & Die Steels", revenueCr: 179.20, revenueSharePct: 14.0, ebitdaMarginPct: 15.5, status: "disclosed", description: "High-carbon wear plates and cold work die bars.", evidenceId: "ev-rel-apex" },
    ],
    shareholding: {
      promoter: { category: "Promoter & Group", percentage: 61.40, changeQoQPct: 0.0, status: "disclosed" },
      dii: { category: "Mutual Funds & DIIs", percentage: 16.20, changeQoQPct: 0.50, status: "disclosed" },
      fii: { category: "Foreign Portfolio (FII)", percentage: 8.90, changeQoQPct: -0.20, status: "disclosed" },
      retail: { category: "Public & Retail", percentage: 13.50, changeQoQPct: -0.30, status: "disclosed" },
      pledgedPct: 4.5,
      asOfDate: "September 30, 2026",
      evidenceId: "ev-rel-apex",
    },
    financialStatements: [
      { label: "INCOME STATEMENT", category: "revenue", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-rel-apex", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null },
      { label: "Revenue from Operations", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-rel-apex", fy23: 980.00, fy24: 1120.00, fy25: 1280.00, q1fy26: 345.00, q2fy26: 360.00 },
      { label: "Cost of Materials Consumed", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-rel-apex", fy23: 610.00, fy24: 700.00, fy25: 812.80, q1fy26: 220.00, q2fy26: 228.00 },
      { label: "Gross Profit", category: "profit", unit: "₹ Cr", status: "inferred", evidenceId: "ev-rel-apex", fy23: 370.00, fy24: 420.00, fy25: 467.20, q1fy26: 125.00, q2fy26: 132.00 },
      { label: "Operating EBITDA", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-rel-apex", fy23: 152.00, fy24: 181.40, fy25: 215.00, q1fy26: 58.00, q2fy26: 62.00 },
      { label: "Net Profit (PAT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-rel-apex", fy23: 88.00, fy24: 108.20, fy25: 132.00, q1fy26: 36.50, q2fy26: 39.00 },
    ],
    relationships: [
      { id: "zenith-fab", name: "Zenith Precision Fabrications Ltd", ticker: "ZENITHFAB", type: "customer", roleDescription: "Major Engineering Fabricator Customer", whyItMatters: "Long-term purchaser of certified alloy rounds taking ~21% of total output.", concentrationPct: 21.0, evidenceStatus: "disclosed", sourceReference: "Annual Report FY25, Customer Concentration", evidenceId: "ev-rel-apex" },
      { id: "raw-scrap-metal", name: "Heavy Melting Steel Scrap", type: "raw_material", roleDescription: "Primary Furnace Feedstock", whyItMatters: "Scrap represents 52% of melting charge costs.", concentrationPct: 52.0, evidenceStatus: "disclosed", sourceReference: "Annual Report FY25, Note 24", evidenceId: "ev-rel-apex" },
      { id: "raw-ferro-chrome", name: "High-Carbon Ferrochrome", type: "raw_material", roleDescription: "Alloying Element", whyItMatters: "Essential for stainless and tool steel grades.", concentrationPct: 18.0, evidenceStatus: "disclosed", sourceReference: "Annual Report FY25, Note 24", evidenceId: "ev-rel-apex" },
    ],
    rawMaterials: [
      { name: "Heavy Melting Steel Scrap (HMS 1&2)", cogsSharePct: 52.0, benchmarkPrice: "₹38,500 / Tonne", trend30dPct: 1.2, evidenceStatus: "disclosed", description: "Furnace scrap feed for induction melting.", evidenceId: "ev-rel-apex" },
      { name: "Ferro-Chrome & Nickel Briquettes", cogsSharePct: 18.0, benchmarkPrice: "₹1,240 / Kg", trend30dPct: -0.5, evidenceStatus: "disclosed", description: "Hardening and corrosion resistance additives.", evidenceId: "ev-rel-apex" },
    ],
    filings: [
      { id: "filing-apex-q2", title: "Unaudited Financial Results for Q2 ended September 2026", type: "results", typeLabel: "Quarterly Results", date: "2026-10-21", exchange: "NSE & BSE", plainSummary: "Revenues rose 15.2% to ₹360 Cr with net profit of ₹39.0 Cr.", status: "disclosed", evidenceId: "ev-rel-apex" },
      { id: "filing-apex-env", title: "Environmental Clearance Approval for New Scrap Pre-heater", type: "expansion", typeLabel: "Regulatory Clearance", date: "2026-09-04", exchange: "BSE", plainSummary: "State pollution board approval for natural gas preheater reducing induction power draw by 12%.", status: "disclosed", evidenceId: "ev-rel-apex" },
    ],
  },
];
