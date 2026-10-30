/**
 * ZoneScan — Company Intelligence Synthetic Demo Fixtures
 * 
 * NOTICE: All companies, financial data, relationships, and filings in this file
 * are entirely FICTIONAL and SYNTHETIC PROTOTYPES. They are provided solely for
 * demonstrating the user interface, interactive relationship graphs, and progressive
 * disclosure architecture of the Financial Intelligence module.
 * 
 * NO REAL LISTED COMPANY DATA OR PRIVATE FINANCIAL INFORMATION IS CONTAINED HEREIN.
 * Identifiers (CIN, ISIN) are fictional demonstration strings.
 */

export type RecordOrigin = "synthetic_demo" | "official_pilot" | "production";

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
  isSynthetic: boolean;
  origin: RecordOrigin;
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
  isSynthetic?: boolean;
}

export interface BusinessSegment {
  name: string;
  revenueCr: number;
  revenueSharePct: number;
  ebitdaMarginPct: number;
  status: EvidenceStatus;
  description: string;
  evidenceId: string;
  isSynthetic?: boolean;
}

export interface ShareholdingGroup {
  category: string;
  percentage: number;
  changeQoQPct: number;
  status: EvidenceStatus;
  isSynthetic?: boolean;
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
  isSynthetic?: boolean;
}

export interface RawMaterialProfile {
  name: string;
  cogsSharePct: number;
  benchmarkPrice: string;
  trend30dPct: number;
  evidenceStatus: EvidenceStatus;
  description: string;
  evidenceId: string;
  isSynthetic?: boolean;
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
  isSynthetic?: boolean;
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
  isSynthetic?: boolean;
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
  isSynthetic: boolean;
  origin: RecordOrigin;
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
  subtitle: "All companies, financial figures, corporate relationships, and filings shown here are synthetic prototypes for testing the Financial Intelligence UI architecture.",
};

export const EVIDENCE_DETAILS_STORE: Record<string, EvidenceDetail> = {
  // ZENITH PRECISION CITATIONS
  "ev-zenith-overview": {
    id: "ev-zenith-overview",
    itemName: "Company Profile & Identity (Synthetic Demo)",
    status: "disclosed",
    statusExplanation: "Modelled as a statutory-style master profile in synthetic demo fixtures. NOT an official corporate record.",
    sourceDocument: "[Synthetic Fixture] Master Corporate Profile (Demo Data Only)",
    sourceSection: "[Demo] Corporate Identification & Master Details",
    sourceDate: "2026-09-30",
    filingType: "Synthetic Master Record (Demo Only)",
    plainSummary: "Incorporation details, fictional CIN, and registered office structured after MCA master record format.",
    verbatimExcerpt: "[Fictional Demo Citation] CIN: SYN-L28910MH2012PLC987654 (Demo) | Registered in Pune, Maharashtra. Fictional Authorized Capital: ₹120.00 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-revenue": {
    id: "ev-zenith-revenue",
    itemName: "Consolidated Revenue from Operations (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled as an audited annual revenue disclosure in synthetic fixtures. NOT a real filing.",
    sourceDocument: "[Synthetic Fixture] Annual Financial Statements FY25 (Fictional Model)",
    sourceSection: "[Demo] Consolidated Statement of Profit and Loss, Note 24",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Revenue represents invoiced precision manufacturing components less GST and volume rebates.",
    verbatimExcerpt: "[Fictional Demo Citation] Sale of precision alloy components: ₹1,825.40 Cr (Previous Year: ₹1,480.20 Cr).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-gross-margin": {
    id: "ev-zenith-gross-margin",
    itemName: "Gross Margin % (Derived)",
    status: "inferred",
    statusExplanation: "Derived by arithmetic formula from disclosed Revenue and Cost of Materials Consumed.",
    formula: "Gross Margin % = ((Revenue - Cost of Materials Consumed) / Revenue) × 100",
    sourceDocument: "[Synthetic Fixture] Annual Financial Statements FY25, Statement of Profit & Loss",
    sourceSection: "[Demo] Note 24 (Revenue) and Note 25 (Cost of Materials Consumed)",
    sourceDate: "2025-06-15",
    plainSummary: "Calculated from disclosed raw material consumption of ₹1,020.20 Cr against revenue of ₹1,825.40 Cr, yielding 44.11%.",
    verbatimExcerpt: "[Fictional Demo Citation] Materials consumed: ₹1,020.20 Cr | Revenue: ₹1,825.40 Cr. Computed Gross Profit: ₹805.20 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-ebitda": {
    id: "ev-zenith-ebitda",
    itemName: "Operating EBITDA & Margin (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled as an operating profit line item in synthetic management review fixtures.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, MD&A Section (Demo)",
    sourceSection: "[Demo] Operational Review, Key Financial Indicators Table",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Earnings Before Interest, Taxes, Depreciation, and Amortization before exceptional items.",
    verbatimExcerpt: "[Fictional Demo Citation] Operating EBITDA stood at ₹410.20 Cr representing an operating margin of 22.47%.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-pat": {
    id: "ev-zenith-pat",
    itemName: "Profit After Tax (PAT) (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled as a bottom-line net profit disclosure in synthetic financial statements.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Profit and Loss Account (Demo)",
    sourceSection: "[Demo] Line Item: Profit for the year attributable to owners",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Net profit after tax attributable to equity shareholders.",
    verbatimExcerpt: "[Fictional Demo Citation] Net Profit for the year: ₹244.80 Cr (FY24: ₹168.40 Cr). Basic & Diluted EPS: ₹24.48.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-debt": {
    id: "ev-zenith-debt",
    itemName: "Total Borrowings & Leverage (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled sum of long-term debt and working capital credit lines in synthetic balance sheet.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Balance Sheet (Demo)",
    sourceSection: "[Demo] Note 17 (Non-current Borrowings) & Note 21 (Current Borrowings)",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Non-current term debt of ₹140.00 Cr and working capital credit of ₹70.00 Cr, total ₹210.00 Cr.",
    verbatimExcerpt: "[Fictional Demo Citation] Long-term borrowings: ₹140.00 Cr. Short-term facilities: ₹70.00 Cr. Total: ₹210.00 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-roce": {
    id: "ev-zenith-roce",
    itemName: "Return on Capital Employed (ROCE) (Derived)",
    status: "inferred",
    statusExplanation: "Computed metric measuring operating efficiency relative to invested equity and debt.",
    formula: "ROCE % = EBIT / (Total Equity + Total Borrowings - Cash & Equivalents) × 100",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25 Financial Schedules (Demo)",
    sourceSection: "[Demo] Calculated from Notes 17, 18, and Profit & Loss Statement",
    sourceDate: "2025-06-15",
    plainSummary: "EBIT of ₹355.40 Cr divided by average capital employed yields 32.40%.",
    verbatimExcerpt: "[Fictional Demo Calculation] EBIT: ₹355.40 Cr | Capital Employed: ₹1,096.50 Cr | ROCE: 32.40%.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-cash": {
    id: "ev-zenith-cash",
    itemName: "Cash & Liquid Bank Balances (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled cash and liquid mutual fund balances in synthetic balance sheet schedule.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Balance Sheet (Demo)",
    sourceSection: "[Demo] Note 12 (Cash and Cash Equivalents) & Note 9 (Current Investments)",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Readily available liquidity in current accounts and overnight liquid treasuries.",
    verbatimExcerpt: "[Fictional Demo Citation] Balances with scheduled commercial banks: ₹112.50 Cr; Liquid fund units: ₹56.00 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-orderbook": {
    id: "ev-zenith-orderbook",
    itemName: "Order Book & Contract Visibility (Unconfirmed Presentation)",
    status: "unconfirmed",
    statusExplanation: "Modelled investor presentation management commentary; not an audited statutory balance sheet line.",
    sourceDocument: "[Synthetic Fixture] Q2FY26 Investor Presentation (Demo)",
    sourceSection: "[Demo] Slide 14: Order Pipeline & Business Visibility",
    sourceDate: "2026-10-24",
    filingType: "Synthetic Investor Presentation (Demo Only)",
    plainSummary: "Management estimated forward contract commitments over the next 18 months at ₹2,450 Cr.",
    verbatimExcerpt: "[Fictional Demo Citation] Estimated executable order backlog stands at ~₹2,450 Cr across automotive and aerospace.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-segments": {
    id: "ev-zenith-segments",
    itemName: "Business Segment Reporting (Ind AS 108 Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Segment reporting modelled after Indian Accounting Standard 108 format.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Financial Statements (Demo)",
    sourceSection: "[Demo] Note 36: Operating Segment Disclosures",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Segment revenue, segment expenses, and allocable operating profit as reported to management.",
    verbatimExcerpt: "[Fictional Demo Citation] Automotive Transmission: ₹766.70 Cr | Industrial Valves: ₹620.60 Cr | Aerospace: ₹292.10 Cr | Aftermarket: ₹146.00 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-zenith-shareholding": {
    id: "ev-zenith-shareholding",
    itemName: "Shareholding Pattern Disclosure (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled after SEBI (LODR) Regulation 31 quarterly shareholding submission structure.",
    sourceDocument: "[Synthetic Fixture] Regulation 31 Shareholding Submission (Demo)",
    sourceSection: "[Demo] Statement showing shareholding pattern of the Promoter and Public shareholders",
    sourceDate: "2026-10-12",
    filingType: "Synthetic Regulatory Submission (Demo Only)",
    plainSummary: "Promoter shareholding is 54.20% with zero shares encumbered/pledged. DII holding is 21.80%.",
    verbatimExcerpt: "[Fictional Demo Citation] Promoter & Group: 5,420,000 equity shares (54.20%). Pledged shares: Nil.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },

  // ZENITH RELATIONSHIP CITATIONS
  "ev-rel-apex": {
    id: "ev-rel-apex",
    itemName: "Supplier: Apex Ferrous & Superalloys Ltd (Demo Sourcing)",
    status: "disclosed",
    statusExplanation: "Modelled as a key material vendor under related party and sourcing commitment notes.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25 (Demo)",
    sourceSection: "[Demo] Note 38: Key Sourcing Commitments & Related Party Disclosures",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Apex Ferrous supplies forging-grade carbon steel billets and certified aircraft alloy rounds (26% of COGS).",
    verbatimExcerpt: "[Fictional Demo Citation] Purchases of alloy steel billets from Apex Ferrous & Superalloys aggregated to ₹265.25 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-titan": {
    id: "ev-rel-titan",
    itemName: "Supplier: Titan Sealants & Polymers (Inferred Tender Record)",
    status: "inferred",
    statusExplanation: "Modelled as an inferred supplier from public tender award registry notices in demo data.",
    formula: "Inferred from vendor registration notices published in public trade tenders.",
    sourceDocument: "[Synthetic Fixture] Industry Vendor Certification Registry (Demo)",
    sourceDate: "2025-11-20",
    plainSummary: "Provides high-temperature elastomer O-rings and hydraulic cylinder seals (~8% of direct material spend).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-orion": {
    id: "ev-rel-orion",
    itemName: "Supplier: Orion Precision Bearings Ltd (Demo Sourcing Agreement)",
    status: "disclosed",
    statusExplanation: "Modelled as a long-term component sourcing memorandum in exchange announcement fixtures.",
    sourceDocument: "[Synthetic Fixture] Corporate Announcement Memorandum (Demo)",
    sourceSection: "[Demo] Long-term Component Sourcing Memorandum",
    sourceDate: "2024-12-05",
    plainSummary: "Supplies precision needle and taper roller bearings used in valve actuator sub-assemblies (11% of COGS).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-vanguard": {
    id: "ev-rel-vanguard",
    itemName: "Customer: Vanguard Commercial Motors Ltd (Demo Concentration)",
    status: "disclosed",
    statusExplanation: "Modelled as single largest customer (>10% revenue concentration under Ind AS 108).",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25 (Demo)",
    sourceSection: "[Demo] Note 36.3: Major Customers Concentration Disclosure",
    sourceDate: "2025-06-15",
    filingType: "Synthetic Concentration Disclosure (Demo Only)",
    plainSummary: "Zenith manufactures heavy truck differential casings and axle transmission housings for Vanguard (28% of total revenue).",
    verbatimExcerpt: "[Fictional Demo Citation] Revenue from one customer represents approximately ₹511.10 Cr of total revenue.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-helios": {
    id: "ev-rel-helios",
    itemName: "Customer: Helios Wind & Industrial Turbines (Demo Disclosed)",
    status: "disclosed",
    statusExplanation: "Modelled in segment review commentary and export contract disclosures.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, MD&A (Demo)",
    sourceSection: "[Demo] Industrial Equipment Division Highlights",
    sourceDate: "2025-06-15",
    plainSummary: "Purchases high-pressure hydraulic pitch valve manifold blocks for wind power turbines (19% of revenue).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-aerodynamic": {
    id: "ev-rel-aerodynamic",
    itemName: "Customer: AeroDynamic Defense Systems (Inferred Subcontract)",
    status: "inferred",
    statusExplanation: "Modelled as inferred from defense subcontract registration certificates and export manifests.",
    sourceDocument: "[Synthetic Fixture] Industrial License Manifest Registry (Demo)",
    sourceDate: "2025-08-14",
    plainSummary: "Procures structural titanium fuselage spars and lightweight radar housing brackets (~12% of revenue).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-transrail": {
    id: "ev-rel-transrail",
    itemName: "Customer: TransRail Locomotives Ltd (Unconfirmed Trade Report)",
    status: "unconfirmed",
    statusExplanation: "Modelled as mentioned in trade magazine reports; not an audited statutory disclosure.",
    sourceDocument: "[Synthetic Fixture] Railway Equipment Review (Demo Trade Publication)",
    sourceDate: "2026-05-18",
    plainSummary: "Reported trial supplier for electric locomotive braking manifold assemblies; pending statutory disclosure.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-bharat": {
    id: "ev-rel-bharat",
    itemName: "Competitor: Bharat Precision Forgings Ltd (Demo Peer Group)",
    status: "disclosed",
    statusExplanation: "Modelled as identified in company-commissioned industry peer benchmarking fixtures.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Industry Peer Comparison (Demo)",
    sourceSection: "[Demo] Benchmarking against direct listed engineering peers",
    sourceDate: "2025-06-15",
    plainSummary: "Direct competitor in automotive transmission forgings with ₹2,100 Cr annual revenue and 20.8% EBITDA margin.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-kalyan": {
    id: "ev-rel-kalyan",
    itemName: "Competitor: Kalyan Heavy Machining Corp (Inferred Peer)",
    status: "inferred",
    statusExplanation: "Modelled as inferred from overlap in registered NIC manufacturing codes and commercial bids.",
    sourceDocument: "[Synthetic Fixture] Industry Classification Master (Demo)",
    sourceDate: "2026-01-10",
    plainSummary: "Competes in industrial turbine manifold blocks and large-bore hydraulic valves.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-rel-dexter": {
    id: "ev-rel-dexter",
    itemName: "Competitor: Dexter Industrial Systems (Unconfirmed Analyst Note)",
    status: "unconfirmed",
    statusExplanation: "Modelled as mentioned in third-party sector commentary; unconfirmed in official filings.",
    sourceDocument: "[Synthetic Fixture] Sector Research Note (Demo Brokerage)",
    sourceDate: "2026-07-22",
    plainSummary: "Privately held fabricator expanding capacity into hydraulic valve blocks.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-raw-steel": {
    id: "ev-raw-steel",
    itemName: "Raw Material: Forging-Grade Alloy Steel (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled after Raw Materials Consumed note in synthetic annual report fixtures.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Notes to Financial Statements (Demo)",
    sourceSection: "[Demo] Note 25.1: Details of Raw Materials Consumed",
    sourceDate: "2025-06-15",
    plainSummary: "Forging quality carbon steel bars account for 38.0% of total raw material consumption cost.",
    verbatimExcerpt: "[Fictional Demo Citation] Alloy and carbon steel rounds: ₹387.68 Cr (38.0% of total consumption).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-raw-nickel": {
    id: "ev-raw-nickel",
    itemName: "Raw Material: Nickel-Chromium Billet Alloys (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled after specialty materials procurement schedule in demo statements.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Notes to Financial Statements (Demo)",
    sourceSection: "[Demo] Note 25.1: High-nickel billet alloys for aerospace brackets",
    sourceDate: "2025-06-15",
    plainSummary: "High-temperature aerospace alloys account for 14.0% of raw material cost.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-raw-power": {
    id: "ev-raw-power",
    itemName: "Input: Industrial Power & Energy Tariffs (Inferred Expense)",
    status: "inferred",
    statusExplanation: "Modelled as inferred from manufacturing expenses note (electric arc & CNC power load).",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25 (Demo)",
    sourceSection: "[Demo] Note 26: Other Manufacturing Expenses (Power & Fuel)",
    sourceDate: "2025-06-15",
    plainSummary: "Grid electrical tariffs represent 9.0% of total cash manufacturing overheads.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },

  // APEX ALLOY CITATIONS (RECONCILED)
  "ev-apex-overview": {
    id: "ev-apex-overview",
    itemName: "Apex Profile & Master Data (Synthetic Demo)",
    status: "disclosed",
    statusExplanation: "Modelled as a statutory-style corporate profile in synthetic demo fixtures.",
    sourceDocument: "[Synthetic Fixture] Master Corporate Profile (Demo Data Only)",
    sourceSection: "[Demo] Corporate Identification & Master Details",
    sourceDate: "2026-09-30",
    filingType: "Synthetic Master Record (Demo Only)",
    plainSummary: "Secondary alloy steel producer specializing in ESR billets and certified rounds.",
    verbatimExcerpt: "[Fictional Demo Citation] CIN: SYN-L27100GJ2008PLC876543 (Demo) | Registered in Ahmedabad, Gujarat. Authorized Capital: ₹80.00 Cr.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-revenue": {
    id: "ev-apex-revenue",
    itemName: "Apex Revenue from Operations (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled as audited revenue in synthetic annual financial results.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Profit & Loss Statement (Demo)",
    sourceSection: "[Demo] Note 22: Revenue from Operations",
    sourceDate: "2025-06-20",
    filingType: "Synthetic Modelled Disclosure (Demo Only)",
    plainSummary: "Invoiced sales of alloy forging billets and defense superalloys: ₹1,280.00 Cr (+14.29% YoY).",
    verbatimExcerpt: "[Fictional Demo Citation] Revenue from sale of products: ₹1,280.00 Cr (Previous Year: ₹1,120.00 Cr).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-gross-margin": {
    id: "ev-apex-gross-margin",
    itemName: "Apex Gross Margin % (Derived)",
    status: "inferred",
    statusExplanation: "Derived by formula from disclosed Revenue of ₹1,280.00 Cr and COGS of ₹812.80 Cr.",
    formula: "Gross Margin % = ((Revenue - Cost of Materials Consumed) / Revenue) × 100",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25 (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Gross profit of ₹467.20 Cr on revenue of ₹1,280.00 Cr yields exactly 36.50% gross margin.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-ebitda": {
    id: "ev-apex-ebitda",
    itemName: "Apex Operating EBITDA (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled as core operating profit before depreciation and interest in demo statements.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, MD&A Section (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Operating EBITDA of ₹215.00 Cr represents a 16.80% margin (+18.52% YoY).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-pat": {
    id: "ev-apex-pat",
    itemName: "Apex Profit After Tax (PAT) (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled net profit attributable to equity owners in synthetic financial accounts.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Profit & Loss Account (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Net profit after all tax provisions of ₹132.00 Cr, yielding EPS of ₹13.20.",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-debt": {
    id: "ev-apex-debt",
    itemName: "Apex Total Borrowings & Capital (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Sum of term debt (₹180 Cr) and working capital lines (₹70 Cr) in demo balance sheet.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Balance Sheet (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Total borrowings of ₹250.00 Cr against equity of ₹575.00 Cr (D/E ratio 0.43×).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-scrap": {
    id: "ev-apex-scrap",
    itemName: "Raw Material: Heavy Melting Scrap (HMS 1&2) (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled raw material consumption schedule in demo financial statements.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Note 24 (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Heavy melting scrap feed represents 52.0% of total raw material consumption cost (₹422.66 Cr).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
  "ev-apex-ferrochrome": {
    id: "ev-apex-ferrochrome",
    itemName: "Raw Material: Ferro-Chrome & Nickel Briquettes (Synthetic Model)",
    status: "disclosed",
    statusExplanation: "Modelled specialty alloy additions schedule in demo statements.",
    sourceDocument: "[Synthetic Fixture] Annual Report FY25, Note 24 (Demo)",
    sourceDate: "2025-06-20",
    plainSummary: "Alloying additives account for 18.0% of total raw material spend (₹146.30 Cr).",
    isSynthetic: true,
    origin: "synthetic_demo",
  },
};

export const DEMO_COMPANIES: CompanyProfile[] = [
  // 1. ZENITH PRECISION FABRICATIONS LTD
  {
    id: "zenith-fab",
    symbol: "ZENITHFAB",
    legalName: "Zenith Precision Fabrications Ltd",
    exchange: "NSE (Synthetic Demo Fixture)",
    cin: "SYN-L28910MH2012PLC987654 (Demo)",
    isin: "SYN-INE999X01099 (Demo)",
    sector: "Capital Goods & Engineering",
    industry: "Industrial Machinery & Components",
    incorporatedYear: 2012,
    headquarters: "Pune, Maharashtra",
    marketCapCr: 4896.00,
    enterpriseValueCr: 4937.50,
    peRatio: 20.00,
    pbRatio: 5.53,
    oneLineDescription: "Engineered high-tolerance alloy structures, hydraulic valve manifolds, and automotive transmission housings.",
    plainLanguageOverview: "Zenith transforms specialty alloy steel billets into high-precision machined sub-assemblies for automotive OEMs, wind turbine builders, and aerospace equipment makers. The company earns predictable operating cash flow from long-term supply contracts, but is sensitive to commodity alloy steel prices.",
    primaryRevenueEngine: "Long-term multi-year component supply agreements with Tier-1 automotive and industrial machinery equipment builders.",
    keySensitivityWarning: "Raw materials represent 55.9% of total revenue. A 10% sustained increase in alloy steel prices without customer pass-through compresses operating EBITDA margin by approximately 212 basis points.",
    evidenceStatus: "disclosed",
    evidenceId: "ev-zenith-overview",
    isSynthetic: true,
    origin: "synthetic_demo",
    headlineKPIs: [
      {
        key: "revenue",
        name: "Revenue from Operations",
        plainName: "Total Invoiced Sales",
        value: 1825.40,
        unit: "₹ Cr",
        period: "FY25 (Demo Model)",
        status: "disclosed",
        yoyChangePct: 23.32,
        evidenceId: "ev-zenith-revenue",
        isSynthetic: true,
      },
      {
        key: "gross_margin",
        name: "Gross Margin",
        plainName: "Sales minus Raw Material Cost",
        value: 44.11,
        unit: "%",
        period: "FY25 (Demo Model)",
        status: "inferred",
        yoyChangePct: 0.87,
        evidenceId: "ev-zenith-gross-margin",
        isSynthetic: true,
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
        isSynthetic: true,
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
        isSynthetic: true,
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
        isSynthetic: true,
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
        isSynthetic: true,
      },
      {
        key: "cash",
        name: "Cash & Liquid Assets",
        plainName: "Ready Cash in Bank & Mutual Funds",
        value: 168.50,
        unit: "₹ Cr",
        period: "FY25 Balance",
        status: "disclosed",
        yoyChangePct: 50.45,
        evidenceId: "ev-zenith-cash",
        isSynthetic: true,
      },
      {
        key: "orderbook",
        name: "Order Book Visibility",
        plainName: "Forward Customer Orders",
        value: 2450.00,
        unit: "₹ Cr",
        period: "Q2FY26 Presentation",
        status: "unconfirmed",
        yoyChangePct: 18.20,
        evidenceId: "ev-zenith-orderbook",
        isSynthetic: true,
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
        isSynthetic: true,
      },
      {
        name: "Industrial Valve & Pump Bodies",
        revenueCr: 620.60,
        revenueSharePct: 34.0,
        ebitdaMarginPct: 25.1,
        status: "disclosed",
        description: "High-pressure hydraulic pitch manifold assemblies for wind turbines, oil processing, and chemical fluid pumps.",
        evidenceId: "ev-zenith-segments",
        isSynthetic: true,
      },
      {
        name: "Aerospace Structural Brackets",
        revenueCr: 292.10,
        revenueSharePct: 16.0,
        ebitdaMarginPct: 28.5,
        status: "disclosed",
        description: "Certified titanium and nickel-alloy structural mountings and radar spars for commercial and defense aviation.",
        evidenceId: "ev-zenith-segments",
        isSynthetic: true,
      },
      {
        name: "Precision Aftermarket & Tooling",
        revenueCr: 146.00,
        revenueSharePct: 8.0,
        ebitdaMarginPct: 31.0,
        status: "disclosed",
        description: "Specialized replacement wear plates, seal glands, and high-speed cutting dies.",
        evidenceId: "ev-zenith-segments",
        isSynthetic: true,
      },
    ],
    shareholding: {
      promoter: { category: "Promoter & Group", percentage: 54.20, changeQoQPct: 0.40, status: "disclosed", isSynthetic: true },
      dii: { category: "Mutual Funds & DIIs", percentage: 21.80, changeQoQPct: 0.80, status: "disclosed", isSynthetic: true },
      fii: { category: "Foreign Portfolio (FII)", percentage: 14.50, changeQoQPct: -0.30, status: "disclosed", isSynthetic: true },
      retail: { category: "Public & Retail", percentage: 9.50, changeQoQPct: -0.90, status: "disclosed", isSynthetic: true },
      pledgedPct: 0.0,
      asOfDate: "September 30, 2026",
      evidenceId: "ev-zenith-shareholding",
    },
    financialStatements: [
      { label: "INCOME STATEMENT", category: "revenue", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Revenue from Operations", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 1240.50, fy24: 1480.20, fy25: 1825.40, q1fy26: 495.20, q2fy26: 520.80, isSynthetic: true },
      { label: "Other Operating Income", category: "revenue", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 14.20, fy24: 18.50, fy25: 22.10, q1fy26: 5.80, q2fy26: 6.20, isSynthetic: true },
      { label: "Total Revenue", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 1254.70, fy24: 1498.70, fy25: 1847.50, q1fy26: 501.00, q2fy26: 527.00, isSynthetic: true },
      { label: "Cost of Materials Consumed (COGS)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-revenue", fy23: 720.00, fy24: 840.10, fy25: 1020.20, q1fy26: 275.40, q2fy26: 288.60, isSynthetic: true },
      { label: "Gross Profit", category: "profit", unit: "₹ Cr", status: "inferred", evidenceId: "ev-zenith-gross-margin", fy23: 520.50, fy24: 640.10, fy25: 805.20, q1fy26: 219.80, q2fy26: 232.20, isSynthetic: true },
      { label: "Gross Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-gross-margin", fy23: 41.96, fy24: 43.24, fy25: 44.11, q1fy26: 44.39, q2fy26: 44.59, isSynthetic: true },
      { label: "Employee Benefit Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 142.00, fy24: 165.20, fy25: 198.50, q1fy26: 53.20, q2fy26: 55.40, isSynthetic: true },
      { label: "Other Operating Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 143.00, fy24: 166.80, fy25: 196.50, q1fy26: 52.80, q2fy26: 54.60, isSynthetic: true },
      { label: "Operating EBITDA", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 235.50, fy24: 308.10, fy25: 410.20, q1fy26: 113.80, q2fy26: 122.20, isSynthetic: true },
      { label: "EBITDA Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-ebitda", fy23: 18.98, fy24: 20.81, fy25: 22.47, q1fy26: 22.98, q2fy26: 23.46, isSynthetic: true },
      { label: "Depreciation & Amortization", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-ebitda", fy23: 42.00, fy24: 48.50, fy25: 54.80, q1fy26: 14.20, q2fy26: 14.80, isSynthetic: true },
      { label: "Operating Profit (EBIT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-roce", fy23: 193.50, fy24: 259.60, fy25: 355.40, q1fy26: 99.60, q2fy26: 107.40, isSynthetic: true },
      { label: "Finance Costs (Interest)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 38.20, fy24: 34.50, fy25: 28.20, q1fy26: 6.80, q2fy26: 6.40, isSynthetic: true },
      { label: "Profit Before Tax (PBT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 155.30, fy24: 225.10, fy25: 327.20, q1fy26: 92.80, q2fy26: 101.00, isSynthetic: true },
      { label: "Tax Expense", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 39.10, fy24: 56.70, fy25: 82.40, q1fy26: 23.40, q2fy26: 25.50, isSynthetic: true },
      { label: "Net Profit (PAT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 116.20, fy24: 168.40, fy25: 244.80, q1fy26: 69.40, q2fy26: 75.50, isSynthetic: true },
      { label: "PAT Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-zenith-pat", fy23: 9.37, fy24: 11.38, fy25: 13.41, q1fy26: 14.01, q2fy26: 14.50, isSynthetic: true },
      { label: "Basic & Diluted EPS", category: "ratio", unit: "₹", indent: true, status: "disclosed", evidenceId: "ev-zenith-pat", fy23: 11.62, fy24: 16.84, fy25: 24.48, q1fy26: 6.94, q2fy26: 7.55, isSynthetic: true },
      { label: "BALANCE SHEET HIGHLIGHTS", category: "balance_sheet", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Net Fixed Assets (PPE)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 410.00, fy24: 485.00, fy25: 560.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Inventories", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 215.00, fy24: 245.00, fy25: 285.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Trade Receivables", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 240.00, fy24: 290.00, fy25: 345.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Cash & Cash Equivalents", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-zenith-cash", fy23: 85.00, fy24: 112.00, fy25: 168.50, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Total Shareholder Equity", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 580.00, fy24: 715.00, fy25: 885.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Total Borrowings (Debt)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-zenith-debt", fy23: 320.00, fy24: 275.00, fy25: 210.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Debt / Equity Ratio", category: "ratio", unit: "×", indent: true, status: "inferred", evidenceId: "ev-zenith-debt", fy23: 0.55, fy24: 0.38, fy25: 0.24, q1fy26: null, q2fy26: null, isSynthetic: true },
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
        sourceReference: "[Demo Fixture] Annual Report FY25, Note 38 (Related Party & Sourcing Commitments)",
        evidenceId: "ev-rel-apex",
        isSynthetic: true,
      },
      {
        id: "titan-polymers",
        name: "Titan Sealants & Industrial Polymers",
        type: "supplier",
        roleDescription: "Hydraulic Gland & High-Pressure Seal Supplier",
        whyItMatters: "Sole-source provider for sub-zero temperature fluorocarbon O-rings used in wind turbine manifold blocks (~8% of direct material cost).",
        concentrationPct: 8.0,
        evidenceStatus: "inferred",
        sourceReference: "[Demo Fixture] Vendor Certification Registry & Purchase Orders",
        evidenceId: "ev-rel-titan",
        isSynthetic: true,
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
        sourceReference: "[Demo Fixture] Component Sourcing Agreement Announcement",
        evidenceId: "ev-rel-orion",
        isSynthetic: true,
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
        sourceReference: "[Demo Fixture] Annual Report FY25, Note 36.3 (Major Customer Concentration)",
        evidenceId: "ev-rel-vanguard",
        isSynthetic: true,
      },
      {
        id: "helios-turbines",
        name: "Helios Wind & Industrial Turbines",
        type: "customer",
        roleDescription: "Wind Power Equipment Builder",
        whyItMatters: "Purchases 19% of Zenith's output for pitch control hydraulic manifold blocks; exposure to expanding renewable energy installations.",
        concentrationPct: 19.0,
        evidenceStatus: "disclosed",
        sourceReference: "[Demo Fixture] Annual Report FY25, MD&A Section",
        evidenceId: "ev-rel-helios",
        isSynthetic: true,
      },
      {
        id: "aerodynamic-systems",
        name: "AeroDynamic Defense Systems",
        type: "customer",
        roleDescription: "Aerospace Structural Integrator",
        whyItMatters: "High-margin defense contractor purchasing lightweight titanium spars; accounts for 12% of revenue with 28.5% divisional margin.",
        concentrationPct: 12.0,
        evidenceStatus: "inferred",
        sourceReference: "[Demo Fixture] Defense Industrial Subcontract Manifests",
        evidenceId: "ev-rel-aerodynamic",
        isSynthetic: true,
      },
      {
        id: "transrail-locomotives",
        name: "TransRail Locomotives Ltd",
        type: "customer",
        roleDescription: "Railways & Rolling Stock Builder",
        whyItMatters: "Trial supplier for locomotive pneumatic brake valve castings (~9% potential revenue); contract is undergoing field trials.",
        concentrationPct: 9.0,
        evidenceStatus: "unconfirmed",
        sourceReference: "[Demo Fixture] Railway Equipment Review (Trade Publication)",
        evidenceId: "ev-rel-transrail",
        isSynthetic: true,
      },
      {
        id: "bharat-forgings",
        name: "Bharat Precision Forgings Ltd",
        ticker: "BHARATFORG",
        type: "competitor",
        roleDescription: "Direct Commercial Vehicle Forgings Peer",
        whyItMatters: "Direct competitor in automotive transmission forgings with ₹2,100 Cr revenue and 20.8% EBITDA margin. Bids on identical OEM tenders.",
        evidenceStatus: "disclosed",
        sourceReference: "[Demo Fixture] Annual Report FY25, Peer Group Review",
        evidenceId: "ev-rel-bharat",
        isSynthetic: true,
      },
      {
        id: "kalyan-machining",
        name: "Kalyan Heavy Machining Corp",
        type: "competitor",
        roleDescription: "Turbine Manifold Competitor",
        whyItMatters: "Competes head-to-head in hydraulic manifold blocks and precision CNC machining.",
        evidenceStatus: "inferred",
        sourceReference: "[Demo Fixture] Industry Classification Master",
        evidenceId: "ev-rel-kalyan",
        isSynthetic: true,
      },
      {
        id: "dexter-industrial",
        name: "Dexter Industrial Systems",
        type: "competitor",
        roleDescription: "Hydraulic Components Competitor",
        whyItMatters: "Privately owned fabricator reportedly adding 5-axis CNC machining bays to contest industrial valve body orders.",
        evidenceStatus: "unconfirmed",
        sourceReference: "[Demo Fixture] Analyst Research Note (Unconfirmed)",
        evidenceId: "ev-rel-dexter",
        isSynthetic: true,
      },
      {
        id: "raw-forging-steel",
        name: "Alloy & Carbon Forging Steel",
        type: "raw_material",
        roleDescription: "Primary Direct Production Material",
        whyItMatters: "Represents 38.0% of Zenith's total raw material consumption cost. Billet index price changes directly impact gross margins.",
        concentrationPct: 38.0,
        evidenceStatus: "disclosed",
        sourceReference: "[Demo Fixture] Annual Report FY25, Note 25.1",
        evidenceId: "ev-raw-steel",
        isSynthetic: true,
      },
      {
        id: "raw-nickel-alloy",
        name: "Nickel-Chromium Billet Alloys",
        type: "raw_material",
        roleDescription: "Aerospace High-Temperature Material",
        whyItMatters: "High unit cost material representing 14.0% of materials consumed. Pegged to international London Metal Exchange / MCX Nickel spot rates.",
        concentrationPct: 14.0,
        evidenceStatus: "disclosed",
        sourceReference: "[Demo Fixture] Annual Report FY25, Note 25.1",
        evidenceId: "ev-raw-nickel",
        isSynthetic: true,
      },
      {
        id: "raw-industrial-power",
        name: "Industrial Electric Grid Power",
        type: "raw_material",
        roleDescription: "Furnace & CNC Electrical Energy",
        whyItMatters: "Represents 9.0% of cash operating overheads. State electricity board tariffs affect monthly conversion cost.",
        concentrationPct: 9.0,
        evidenceStatus: "inferred",
        sourceReference: "[Demo Fixture] Annual Report FY25, Note 26",
        evidenceId: "ev-raw-power",
        isSynthetic: true,
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
        isSynthetic: true,
      },
      {
        name: "Nickel-Chromium High-Heat Alloys",
        cogsSharePct: 14.0,
        benchmarkPrice: "₹1,420 / Kg",
        trend30dPct: -1.8,
        evidenceStatus: "disclosed",
        description: "Certified aerospace alloy rounds for titanium-nickel brackets and turbine spars.",
        evidenceId: "ev-raw-nickel",
        isSynthetic: true,
      },
      {
        name: "Industrial Electrical Power",
        cogsSharePct: 9.0,
        benchmarkPrice: "₹8.40 / kWh",
        trend30dPct: 0.0,
        evidenceStatus: "inferred",
        description: "Continuous industrial 33kV dedicated substation feed for CNC machining bays and induction heat-treatment furnaces.",
        evidenceId: "ev-raw-power",
        isSynthetic: true,
      },
    ],
    filings: [
      {
        id: "filing-q2-fy26",
        title: "[Synthetic Demo] Board Meeting Outcome: Unaudited Financial Results for Q2 ended Sept 30, 2026",
        type: "results",
        typeLabel: "Quarterly Results",
        date: "2026-10-24",
        exchange: "NSE (Synthetic Demo)",
        plainSummary: "Board approved Q2 results showing ₹520.80 Cr revenue (+18.4% YoY) and net profit of ₹75.50 Cr (+21.2% YoY). Interim dividend of ₹3.50 per share declared.",
        status: "disclosed",
        evidenceId: "ev-zenith-pat",
        isSynthetic: true,
      },
      {
        id: "filing-contract-vanguard",
        title: "[Synthetic Demo] Disclosure under Reg 30: Multi-Year Supply Agreement Renewal with Vanguard Motors",
        type: "contract",
        typeLabel: "Material Contract",
        date: "2026-09-18",
        exchange: "NSE (Synthetic Demo)",
        plainSummary: "Secured a 3-year extension with Vanguard Commercial Motors for new generation electric delivery van chassis transmission housings valued at ~₹620 Cr.",
        status: "disclosed",
        evidenceId: "ev-rel-vanguard",
        isSynthetic: true,
      },
      {
        id: "filing-shareholding-q2",
        title: "[Synthetic Demo] Shareholding Pattern pursuant to Regulation 31 for the Quarter ended September 2026",
        type: "shareholding",
        typeLabel: "Shareholding",
        date: "2026-10-12",
        exchange: "NSE (Synthetic Demo)",
        plainSummary: "Promoter shareholding steady at 54.20% with zero pledged shares. Institutional domestic holdings increased by 0.80% to 21.80%.",
        status: "disclosed",
        evidenceId: "ev-zenith-shareholding",
        isSynthetic: true,
      },
      {
        id: "filing-expansion-pune",
        title: "[Synthetic Demo] Corporate Announcement: Operationalization of 5-Axis Precision Machining Bay at Pune Facility",
        type: "expansion",
        typeLabel: "Capacity Expansion",
        date: "2026-08-30",
        exchange: "NSE (Synthetic Demo)",
        plainSummary: "Commissioned Phase-II brownfield expansion adding 12 new high-speed multi-axis CNC machines, boosting aerospace component capacity by 35%.",
        status: "disclosed",
        evidenceId: "ev-zenith-overview",
        isSynthetic: true,
      },
    ],
  },

  // 2. APEX FERROUS & SUPERALLOYS LTD (RECONCILED)
  {
    id: "apex-alloys",
    symbol: "APEXALLOY",
    legalName: "Apex Ferrous & Superalloys Ltd",
    exchange: "NSE (Synthetic Demo Fixture)",
    cin: "SYN-L27100GJ2008PLC876543 (Demo)",
    isin: "SYN-INE888Y01088 (Demo)",
    sector: "Metals & Mining",
    industry: "Specialty Steel & Forging Billets",
    incorporatedYear: 2008,
    headquarters: "Ahmedabad, Gujarat",
    marketCapCr: 2178.00,
    enterpriseValueCr: 2383.00,
    peRatio: 16.50,
    pbRatio: 3.79,
    oneLineDescription: "Secondary steel alloy producer manufacturing certified aircraft rounds, ESR grade billets, and forging stock.",
    plainLanguageOverview: "Apex melts scrap and ferro-alloys in vacuum induction furnaces to produce specialty steel billets. It supplies precision engineering shops and toolmakers across Western India.",
    primaryRevenueEngine: "Sale of specialty alloy billets, forged bars, and stainless steel rounds to tier-1 manufacturing fabricators.",
    keySensitivityWarning: "Directly vulnerable to international nickel, scrap metal, and coking coal price shifts.",
    evidenceStatus: "disclosed",
    evidenceId: "ev-apex-overview",
    isSynthetic: true,
    origin: "synthetic_demo",
    headlineKPIs: [
      { key: "revenue", name: "Revenue from Operations", plainName: "Invoiced Sales", value: 1280.00, unit: "₹ Cr", period: "FY25 (Demo Model)", status: "disclosed", yoyChangePct: 14.29, evidenceId: "ev-apex-revenue", isSynthetic: true },
      { key: "gross_margin", name: "Gross Margin", plainName: "Value Addition Margin", value: 36.50, unit: "%", period: "FY25 (Demo Model)", status: "inferred", yoyChangePct: -1.00, evidenceId: "ev-apex-gross-margin", isSynthetic: true },
      { key: "ebitda", name: "Operating EBITDA", plainName: "Operating Cash Profit", value: 215.00, unit: "₹ Cr", period: "FY25 (16.8% Margin)", status: "disclosed", yoyChangePct: 18.52, evidenceId: "ev-apex-ebitda", isSynthetic: true },
      { key: "pat", name: "Net Profit (PAT)", plainName: "Bottom-Line Profit", value: 132.00, unit: "₹ Cr", period: "FY25 (10.3% Margin)", status: "disclosed", yoyChangePct: 22.00, evidenceId: "ev-apex-pat", isSynthetic: true },
      { key: "debt", name: "Total Borrowings", plainName: "Bank Borrowings", value: 250.00, unit: "₹ Cr", period: "FY25 (D/E: 0.43×)", status: "disclosed", yoyChangePct: -9.09, evidenceId: "ev-apex-debt", isSynthetic: true },
      { key: "roce", name: "ROCE", plainName: "Return on Capital", value: 22.40, unit: "%", period: "FY25 Computed", status: "inferred", yoyChangePct: 2.10, evidenceId: "ev-apex-overview", isSynthetic: true },
      { key: "cash", name: "Cash & Liquid Assets", plainName: "Cash in Bank", value: 45.00, unit: "₹ Cr", period: "FY25 Balance", status: "disclosed", yoyChangePct: 12.50, evidenceId: "ev-apex-debt", isSynthetic: true },
      { key: "orderbook", name: "Order Backlog", plainName: "Contract Backlog", value: 980.00, unit: "₹ Cr", period: "Management Presentation", status: "unconfirmed", yoyChangePct: 9.50, evidenceId: "ev-apex-overview", isSynthetic: true },
    ],
    segments: [
      { name: "Alloy Steel Forging Billets", revenueCr: 742.40, revenueSharePct: 58.0, ebitdaMarginPct: 17.2, status: "disclosed", description: "Vacuum degassed forging rounds for auto components.", evidenceId: "ev-apex-revenue", isSynthetic: true },
      { name: "Aircraft & Defense Superalloys", revenueCr: 358.40, revenueSharePct: 28.0, ebitdaMarginPct: 21.0, status: "disclosed", description: "Electro-slag remelted (ESR) nickel and chrome alloy ingots.", evidenceId: "ev-apex-revenue", isSynthetic: true },
      { name: "Tool & Die Steels", revenueCr: 179.20, revenueSharePct: 14.0, ebitdaMarginPct: 15.5, status: "disclosed", description: "High-carbon wear plates and cold work die bars.", evidenceId: "ev-apex-revenue", isSynthetic: true },
    ],
    shareholding: {
      promoter: { category: "Promoter & Group", percentage: 61.40, changeQoQPct: 0.00, status: "disclosed", isSynthetic: true },
      dii: { category: "Mutual Funds & DIIs", percentage: 16.20, changeQoQPct: 0.50, status: "disclosed", isSynthetic: true },
      fii: { category: "Foreign Portfolio (FII)", percentage: 8.90, changeQoQPct: -0.20, status: "disclosed", isSynthetic: true },
      retail: { category: "Public & Retail", percentage: 13.50, changeQoQPct: -0.30, status: "disclosed", isSynthetic: true },
      pledgedPct: 4.5,
      asOfDate: "September 30, 2026",
      evidenceId: "ev-apex-overview",
    },
    financialStatements: [
      { label: "INCOME STATEMENT", category: "revenue", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-apex-revenue", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Revenue from Operations", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-revenue", fy23: 980.00, fy24: 1120.00, fy25: 1280.00, q1fy26: 345.00, q2fy26: 360.00, isSynthetic: true },
      { label: "Other Operating Income", category: "revenue", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-revenue", fy23: 10.00, fy24: 12.00, fy25: 15.00, q1fy26: 4.00, q2fy26: 4.50, isSynthetic: true },
      { label: "Total Revenue", category: "revenue", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-revenue", fy23: 990.00, fy24: 1132.00, fy25: 1295.00, q1fy26: 349.00, q2fy26: 364.50, isSynthetic: true },
      { label: "Cost of Materials Consumed (COGS)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-revenue", fy23: 610.00, fy24: 700.00, fy25: 812.80, q1fy26: 220.00, q2fy26: 228.00, isSynthetic: true },
      { label: "Gross Profit", category: "profit", unit: "₹ Cr", status: "inferred", evidenceId: "ev-apex-gross-margin", fy23: 370.00, fy24: 420.00, fy25: 467.20, q1fy26: 125.00, q2fy26: 132.00, isSynthetic: true },
      { label: "Gross Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-apex-gross-margin", fy23: 37.76, fy24: 37.50, fy25: 36.50, q1fy26: 36.23, q2fy26: 36.67, isSynthetic: true },
      { label: "Employee Benefit Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-ebitda", fy23: 112.00, fy24: 122.00, fy25: 132.00, q1fy26: 34.50, q2fy26: 36.00, isSynthetic: true },
      { label: "Other Operating Expenses", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-ebitda", fy23: 116.00, fy24: 128.60, fy25: 135.20, q1fy26: 36.50, q2fy26: 38.50, isSynthetic: true },
      { label: "Operating EBITDA", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-ebitda", fy23: 152.00, fy24: 181.40, fy25: 215.00, q1fy26: 58.00, q2fy26: 62.00, isSynthetic: true },
      { label: "EBITDA Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-apex-ebitda", fy23: 15.51, fy24: 16.20, fy25: 16.80, q1fy26: 16.81, q2fy26: 17.22, isSynthetic: true },
      { label: "Depreciation & Amortization", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-ebitda", fy23: 30.00, fy24: 34.00, fy25: 38.00, q1fy26: 9.80, q2fy26: 10.20, isSynthetic: true },
      { label: "Operating Profit (EBIT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-ebitda", fy23: 122.00, fy24: 147.40, fy25: 177.00, q1fy26: 48.20, q2fy26: 51.80, isSynthetic: true },
      { label: "Finance Costs (Interest)", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-debt", fy23: 34.00, fy24: 31.00, fy25: 28.00, q1fy26: 6.80, q2fy26: 6.50, isSynthetic: true },
      { label: "Profit Before Tax (PBT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-pat", fy23: 88.00, fy24: 116.40, fy25: 149.00, q1fy26: 41.40, q2fy26: 45.30, isSynthetic: true },
      { label: "Tax Expense", category: "expense", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-pat", fy23: 0.00, fy24: 8.20, fy25: 17.00, q1fy26: 4.90, q2fy26: 6.30, isSynthetic: true },
      { label: "Net Profit (PAT)", category: "profit", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-pat", fy23: 88.00, fy24: 108.20, fy25: 132.00, q1fy26: 36.50, q2fy26: 39.00, isSynthetic: true },
      { label: "PAT Margin %", category: "ratio", unit: "%", indent: true, status: "inferred", evidenceId: "ev-apex-pat", fy23: 8.98, fy24: 9.66, fy25: 10.31, q1fy26: 10.58, q2fy26: 10.83, isSynthetic: true },
      { label: "Basic & Diluted EPS", category: "ratio", unit: "₹", indent: true, status: "disclosed", evidenceId: "ev-apex-pat", fy23: 8.80, fy24: 10.82, fy25: 13.20, q1fy26: 3.65, q2fy26: 3.90, isSynthetic: true },
      { label: "BALANCE SHEET HIGHLIGHTS", category: "balance_sheet", unit: "₹ Cr", isHeader: true, status: "disclosed", evidenceId: "ev-apex-debt", fy23: null, fy24: null, fy25: null, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Net Fixed Assets (PPE)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-debt", fy23: 320.00, fy24: 375.00, fy25: 430.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Inventories", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-debt", fy23: 160.00, fy24: 185.00, fy25: 210.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Trade Receivables", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-debt", fy23: 140.00, fy24: 165.00, fy25: 195.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Cash & Cash Equivalents", category: "balance_sheet", unit: "₹ Cr", indent: true, status: "disclosed", evidenceId: "ev-apex-debt", fy23: 28.00, fy24: 40.00, fy25: 45.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Total Shareholder Equity", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-debt", fy23: 410.00, fy24: 490.00, fy25: 575.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Total Borrowings (Debt)", category: "balance_sheet", unit: "₹ Cr", status: "disclosed", evidenceId: "ev-apex-debt", fy23: 290.00, fy24: 275.00, fy25: 250.00, q1fy26: null, q2fy26: null, isSynthetic: true },
      { label: "Debt / Equity Ratio", category: "ratio", unit: "×", indent: true, status: "inferred", evidenceId: "ev-apex-debt", fy23: 0.71, fy24: 0.56, fy25: 0.43, q1fy26: null, q2fy26: null, isSynthetic: true },
    ],
    relationships: [
      { id: "zenith-fab", name: "Zenith Precision Fabrications Ltd", ticker: "ZENITHFAB", type: "customer", roleDescription: "Major Engineering Fabricator Customer", whyItMatters: "Long-term purchaser of certified alloy rounds taking ~21% of total output.", concentrationPct: 21.0, evidenceStatus: "disclosed", sourceReference: "[Demo Fixture] Customer Concentration Disclosure", evidenceId: "ev-apex-revenue", isSynthetic: true },
      { id: "raw-scrap-metal", name: "Heavy Melting Steel Scrap", type: "raw_material", roleDescription: "Primary Furnace Feedstock", whyItMatters: "Scrap represents 52% of melting charge costs.", concentrationPct: 52.0, evidenceStatus: "disclosed", sourceReference: "[Demo Fixture] Raw Materials Schedule", evidenceId: "ev-apex-scrap", isSynthetic: true },
      { id: "raw-ferro-chrome", name: "High-Carbon Ferrochrome", type: "raw_material", roleDescription: "Alloying Element", whyItMatters: "Essential for stainless and tool steel grades.", concentrationPct: 18.0, evidenceStatus: "disclosed", sourceReference: "[Demo Fixture] Raw Materials Schedule", evidenceId: "ev-apex-ferrochrome", isSynthetic: true },
    ],
    rawMaterials: [
      { name: "Heavy Melting Steel Scrap (HMS 1&2)", cogsSharePct: 52.0, benchmarkPrice: "₹38,500 / Tonne", trend30dPct: 1.2, evidenceStatus: "disclosed", description: "Furnace scrap feed for induction melting.", evidenceId: "ev-apex-scrap", isSynthetic: true },
      { name: "Ferro-Chrome & Nickel Briquettes", cogsSharePct: 18.0, benchmarkPrice: "₹1,240 / Kg", trend30dPct: -0.5, evidenceStatus: "disclosed", description: "Hardening and corrosion resistance additives.", evidenceId: "ev-apex-ferrochrome", isSynthetic: true },
    ],
    filings: [
      { id: "filing-apex-q2", title: "[Synthetic Demo] Board Outcome: Unaudited Financial Results for Q2 ended September 2026", type: "results", typeLabel: "Quarterly Results", date: "2026-10-21", exchange: "NSE (Synthetic Demo)", plainSummary: "Revenues rose 14.3% YoY to ₹360 Cr with net profit of ₹39.0 Cr.", status: "disclosed", evidenceId: "ev-apex-revenue", isSynthetic: true },
      { id: "filing-apex-env", title: "[Synthetic Demo] Regulatory Clearance: Approval for New Scrap Pre-heater Facility", type: "expansion", typeLabel: "Regulatory Clearance", date: "2026-09-04", exchange: "NSE (Synthetic Demo)", plainSummary: "State pollution board approval for natural gas preheater reducing induction power draw by 12%.", status: "disclosed", evidenceId: "ev-apex-overview", isSynthetic: true },
    ],
  },
];
