"use client";

import React, { useState } from "react";
import {
  DEMO_COMPANIES,
  EVIDENCE_DETAILS_STORE,
  SYNTHETIC_DATA_BANNER,
  type CompanyProfile,
} from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";
import { SourcePanel } from "./SourcePanel";
import { KPICard } from "./KPICard";
import { MetricSparkline } from "./MetricSparkline";
import { FinancialTable } from "./FinancialTable";
import { ShareholdingBar } from "./ShareholdingBar";
import { SegmentChart } from "./SegmentChart";
import { RelationshipMap } from "./RelationshipMap";
import { SupplyChainSimulator } from "./SupplyChainSimulator";
import { FilingList } from "./FilingList";

type CompanyTab = "overview" | "financials" | "relationships" | "supply_chain" | "filings";

interface CompanyIntelligenceProps {
  initialCompanyId?: string;
  onNavigateToBoard?: () => void;
}

export function CompanyIntelligence({
  initialCompanyId = "zenith-fab",
  onNavigateToBoard,
}: CompanyIntelligenceProps) {
  const [selectedCompanyId, setSelectedCompanyId] = useState(initialCompanyId);
  const [activeTab, setActiveTab] = useState<CompanyTab>("overview");
  const [inspectingEvidenceId, setInspectingEvidenceId] = useState<string | null>(null);

  const company: CompanyProfile =
    DEMO_COMPANIES.find((c) => c.id === selectedCompanyId) ?? DEMO_COMPANIES[0];

  const handleInspectSource = (evidenceId: string) => {
    setInspectingEvidenceId(evidenceId);
  };

  const handleCloseSource = () => {
    setInspectingEvidenceId(null);
  };

  const activeEvidenceDetail = inspectingEvidenceId
    ? EVIDENCE_DETAILS_STORE[inspectingEvidenceId] ?? {
        id: inspectingEvidenceId,
        itemName: "Statutory Citation Detail",
        status: "disclosed",
        statusExplanation: "Information verified against statutory disclosures.",
        plainSummary: "Detailed evidence reference verified in statutory company filings.",
      }
    : null;

  // Margin sparkline data points
  const marginPoints = [
    { period: "FY23", gross: 41.96, ebitda: 18.98, pat: 9.37 },
    { period: "FY24", gross: 43.24, ebitda: 20.81, pat: 11.38 },
    { period: "FY25", gross: 44.11, ebitda: 22.47, pat: 13.41 },
    { period: "Q1FY26", gross: 44.39, ebitda: 22.98, pat: 14.01 },
    { period: "Q2FY26", gross: 44.59, ebitda: 23.46, pat: 14.50 },
  ];

  return (
    <div className="company-intelligence-workspace">
      {onNavigateToBoard && (
        <button
          type="button"
          className="back-link"
          onClick={onNavigateToBoard}
          style={{ marginBottom: "12px", display: "inline-block" }}
        >
          ← Back to Market board
        </button>
      )}

      {/* Top Banner: Explicit Synthetic Fixture Warning */}
      <div className="ci-synthetic-banner" role="status">
        <span className="banner-dot" aria-hidden="true" />
        <strong>{SYNTHETIC_DATA_BANNER.title}</strong>
        <span>— {SYNTHETIC_DATA_BANNER.subtitle}</span>
      </div>

      {/* Company Header Card */}
      <header className="company-header-card">
        <div className="company-header-top">
          <div className="company-identity-group">
            <div className="company-symbol-row">
              <span className="company-monogram">{company.symbol.slice(0, 2)}</span>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="company-title">{company.legalName}</h1>
                  <EvidenceBadge
                    status={company.evidenceStatus}
                    size="sm"
                    interactive
                    onClick={() => handleInspectSource(company.evidenceId)}
                  />
                </div>
                <div className="company-code-pills">
                  <span className="code-pill symbol-pill">{company.symbol}</span>
                  <span className="code-pill">{company.exchange}</span>
                  <span className="code-pill">CIN: {company.cin}</span>
                  <span className="code-pill">ISIN: {company.isin}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Demo Switcher */}
          <div className="company-switcher-wrap">
            <label htmlFor="company-select" className="switcher-label">
              Select Demo Company:
            </label>
            <select
              id="company-select"
              className="terminal-select"
              value={selectedCompanyId}
              onChange={(e) => {
                setSelectedCompanyId(e.target.value);
                setActiveTab("overview");
              }}
            >
              {DEMO_COMPANIES.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.symbol} · {c.legalName}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Company Attributes Bar */}
        <div className="company-meta-bar">
          <div className="meta-item">
            <span className="meta-label">SECTOR / INDUSTRY</span>
            <strong className="meta-val">{company.sector}</strong>
            <small className="meta-sub">{company.industry}</small>
          </div>
          <div className="meta-item">
            <span className="meta-label">HEADQUARTERS</span>
            <strong className="meta-val">{company.headquarters}</strong>
            <small className="meta-sub">Inc. {company.incorporatedYear}</small>
          </div>
          <div className="meta-item">
            <span className="meta-label">MARKET VALUATION</span>
            <strong className="meta-val">₹{company.marketCapCr.toLocaleString("en-IN")} Cr</strong>
            <small className="meta-sub">EV: ₹{company.enterpriseValueCr.toLocaleString("en-IN")} Cr</small>
          </div>
          <div className="meta-item">
            <span className="meta-label">VALUATION MULTIPLES</span>
            <strong className="meta-val">P/E: {company.peRatio}×</strong>
            <small className="meta-sub">P/B: {company.pbRatio}×</small>
          </div>
        </div>

        {/* Plain-Language Business Description Box */}
        <div className="plain-description-box">
          <div className="description-main">
            <span className="box-eyebrow">PLAIN-LANGUAGE BUSINESS PROFILE</span>
            <p className="description-text">{company.plainLanguageOverview}</p>
          </div>
          <div className="economic-engine-box">
            <strong>Primary Economic Engine:</strong>
            <p>{company.primaryRevenueEngine}</p>
            <div className="sensitivity-callout">
              <strong>Key Exposure Note:</strong>
              <p>{company.keySensitivityWarning}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Five Main Workspaces Navigation Tabs */}
      <nav className="company-tabs-nav" aria-label="Company Intelligence Workspace Navigation">
        <button
          type="button"
          className={`tab-item ${activeTab === "overview" ? "active" : ""}`}
          onClick={() => setActiveTab("overview")}
          aria-selected={activeTab === "overview"}
          role="tab"
        >
          <span className="tab-icon">▦</span>
          Overview &amp; KPIs
        </button>
        <button
          type="button"
          className={`tab-item ${activeTab === "financials" ? "active" : ""}`}
          onClick={() => setActiveTab("financials")}
          aria-selected={activeTab === "financials"}
          role="tab"
        >
          <span className="tab-icon">▤</span>
          Financial Statements
        </button>
        <button
          type="button"
          className={`tab-item ${activeTab === "relationships" ? "active" : ""}`}
          onClick={() => setActiveTab("relationships")}
          aria-selected={activeTab === "relationships"}
          role="tab"
        >
          <span className="tab-icon">☊</span>
          Relationship Graph
          <span className="tab-badge">{company.relationships.length}</span>
        </button>
        <button
          type="button"
          className={`tab-item ${activeTab === "supply_chain" ? "active" : ""}`}
          onClick={() => setActiveTab("supply_chain")}
          aria-selected={activeTab === "supply_chain"}
          role="tab"
        >
          <span className="tab-icon">⚡</span>
          Supply Chain &amp; Scenarios
        </button>
        <button
          type="button"
          className={`tab-item ${activeTab === "filings" ? "active" : ""}`}
          onClick={() => setActiveTab("filings")}
          aria-selected={activeTab === "filings"}
          role="tab"
        >
          <span className="tab-icon">📄</span>
          Filings &amp; Disclosures
          <span className="tab-badge">{company.filings.length}</span>
        </button>
      </nav>

      {/* Main Tab Content */}
      <main className="tab-content-area" role="tabpanel">
        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="tab-overview-grid">
            <section className="overview-section">
              <div className="section-title-row">
                <div>
                  <h2 className="section-title">Headline Financial KPIs</h2>
                  <p className="section-subtitle">
                    Core audited figures with clear reporting units and evidence classification
                  </p>
                </div>
                <div className="evidence-legend-compact">
                  <EvidenceBadge status="disclosed" size="xs" />
                  <EvidenceBadge status="inferred" size="xs" />
                  <EvidenceBadge status="unconfirmed" size="xs" />
                </div>
              </div>

              <div className="kpi-cards-grid">
                {company.headlineKPIs.map((kpi) => (
                  <KPICard
                    key={kpi.key}
                    metric={kpi}
                    onInspectSource={handleInspectSource}
                  />
                ))}
              </div>
            </section>

            <div className="overview-two-col">
              <SegmentChart
                segments={company.segments}
                onInspectSource={handleInspectSource}
              />
              <ShareholdingBar
                shareholding={company.shareholding}
                onInspectSource={handleInspectSource}
              />
            </div>
          </div>
        )}

        {/* TAB 2: FINANCIAL STATEMENTS */}
        {activeTab === "financials" && (
          <div className="tab-financials-layout">
            <section className="margin-trends-section">
              <div className="section-title-row">
                <div>
                  <h2 className="section-title">Operating Margin Evolution (3-Year Trend)</h2>
                  <p className="section-subtitle">
                    Progression across gross, cash operating, and net profitability
                  </p>
                </div>
                <EvidenceBadge status="inferred" size="xs" />
              </div>

              <div className="sparklines-grid">
                <MetricSparkline
                  title="Gross Margin"
                  unit="%"
                  color="#38bdf8"
                  points={marginPoints.map((p) => ({ period: p.period, value: p.gross }))}
                  summaryText="Value-addition expanded +263 bps from FY23 to Q2FY26"
                />
                <MetricSparkline
                  title="Operating EBITDA Margin"
                  unit="%"
                  color="#44ce9a"
                  points={marginPoints.map((p) => ({ period: p.period, value: p.ebitda }))}
                  summaryText="Operating leverage drove +448 bps cash margin improvement"
                />
                <MetricSparkline
                  title="Net PAT Margin"
                  unit="%"
                  color="#818cf8"
                  points={marginPoints.map((p) => ({ period: p.period, value: p.pat }))}
                  summaryText="Bottom-line net margin climbed from 9.4% to 14.5%"
                />
              </div>
            </section>

            <section className="statement-table-section">
              <div className="section-title-row">
                <div>
                  <h2 className="section-title">Audited Financial Statements</h2>
                  <p className="section-subtitle">
                    Multi-period statutory income statement and balance sheet schedules
                  </p>
                </div>
              </div>

              <FinancialTable
                rows={company.financialStatements}
                onInspectSource={handleInspectSource}
              />
            </section>
          </div>
        )}

        {/* TAB 3: RELATIONSHIP INTELLIGENCE (CYTOSCAPE GRAPH) */}
        {activeTab === "relationships" && (
          <div className="tab-relationships-layout">
            <RelationshipMap
              company={company}
              relationships={company.relationships}
              onInspectSource={handleInspectSource}
            />
          </div>
        )}

        {/* TAB 4: SUPPLY CHAIN & COMMODITIES */}
        {activeTab === "supply_chain" && (
          <div className="tab-supply-chain-layout">
            <SupplyChainSimulator
              company={company}
              rawMaterials={company.rawMaterials}
              onInspectSource={handleInspectSource}
            />
          </div>
        )}

        {/* TAB 5: FILINGS & DISCLOSURES */}
        {activeTab === "filings" && (
          <div className="tab-filings-layout">
            <FilingList
              filings={company.filings}
              onInspectSource={handleInspectSource}
            />
          </div>
        )}
      </main>

      {/* Global Level 3 Progressive Disclosure Drawer / Modal */}
      <SourcePanel
        detail={activeEvidenceDetail}
        isOpen={inspectingEvidenceId !== null}
        onClose={handleCloseSource}
      />
    </div>
  );
}
