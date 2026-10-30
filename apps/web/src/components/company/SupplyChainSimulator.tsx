"use client";

import React, { useState } from "react";
import type { CompanyProfile, RawMaterialProfile } from "@/lib/fixtures/company-intelligence";
import { calculateCommodityImpact } from "@/lib/calculations/supply-chain-impact";
import { EvidenceBadge } from "./EvidenceBadge";

interface SupplyChainSimulatorProps {
  company: CompanyProfile;
  rawMaterials: RawMaterialProfile[];
  onInspectSource: (evidenceId: string) => void;
}

export function SupplyChainSimulator({
  company,
  rawMaterials,
  onInspectSource,
}: SupplyChainSimulatorProps) {
  const [selectedMatIdx, setSelectedMatIdx] = useState(0);
  const [priceChangePct, setPriceChangePct] = useState(10); // default +10% stress test

  const selectedMat = rawMaterials[selectedMatIdx] ?? rawMaterials[0];

  // Dynamic baseline extraction from typed company fixtures (FY25 Annual)
  const baselineRevenue =
    company.financialStatements.find((r) => r.label === "Revenue from Operations" && r.category === "revenue")?.fy25 ??
    company.headlineKPIs.find((k) => k.key === "revenue")?.value ??
    1825.40;

  const baselineCOGS =
    company.financialStatements.find((r) => r.label.includes("Cost of Materials Consumed"))?.fy25 ??
    (baselineRevenue * 0.55);

  // Pure deterministic mathematical calculation
  const impact = calculateCommodityImpact({
    annualRevenueCr: baselineRevenue,
    annualCogsCr: baselineCOGS,
    cogsSharePct: selectedMat.cogsSharePct,
    priceChangePct,
  });

  const {
    additionalCostCr,
    marginCompressionBps,
    modelledGrossMarginPct,
    baselineGrossMarginPct,
  } = impact;

  return (
    <div className="supply-chain-layout">
      {/* Raw Material Inventory Profile */}
      <section className="raw-material-profile-card">
        <header className="profile-header">
          <div>
            <h3 className="section-heading">Raw Material Cost Profile</h3>
            <span className="section-subheading">
              Modelled input dependency and commodity benchmarks (FY25 Synthetic Baseline)
            </span>
          </div>
          <EvidenceBadge
            status="disclosed"
            size="xs"
            interactive
            onClick={() => onInspectSource(selectedMat.evidenceId)}
          />
        </header>

        <div className="materials-grid">
          {rawMaterials.map((mat, idx) => (
            <div
              key={mat.name}
              className={`material-item-card ${selectedMatIdx === idx ? "is-selected" : ""}`}
              tabIndex={0}
              role="button"
              onClick={() => setSelectedMatIdx(idx)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  setSelectedMatIdx(idx);
                }
              }}
            >
              <div className="material-card-top">
                <span className="material-cogs-tag">{mat.cogsSharePct.toFixed(1)}% of COGS</span>
                <EvidenceBadge
                  status={mat.evidenceStatus}
                  size="xs"
                  interactive
                  onClick={() => onInspectSource(mat.evidenceId)}
                />
              </div>
              <h4 className="material-name">{mat.name}</h4>
              <p className="material-desc">{mat.description}</p>
              <div className="material-price-row">
                <div>
                  <span className="price-label">Benchmark Spot:</span>
                  <strong className="price-val">{mat.benchmarkPrice}</strong>
                </div>
                <span
                  className={`price-trend ${mat.trend30dPct >= 0 ? "trend-up" : "trend-down"}`}
                >
                  {mat.trend30dPct >= 0 ? "↗ +" : "↘ "}{mat.trend30dPct.toFixed(1)}% (30d)
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive Scenario Calculator */}
      <section className="scenario-simulator-card">
        <header className="simulator-header">
          <div className="simulator-title-group">
            <span className="eyebrow">DETERMINISTIC SIMULATION · DEMO ONLY</span>
            <h3 className="section-heading">Evidence-Based Commodity Stress Test</h3>
          </div>
          <span className="simulation-tag">Synthetic Sensitivity Heuristic</span>
        </header>

        <p className="simulator-intro">
          Model how changes in global or domestic input prices propagate into {company.legalName}&apos;s cost base and operating profitability.
        </p>

        <div className="simulator-controls-box">
          <div className="control-group">
            <label htmlFor="material-select" className="control-label">
              Stressed Commodity Input:
            </label>
            <select
              id="material-select"
              className="terminal-select"
              value={selectedMatIdx}
              onChange={(e) => setSelectedMatIdx(Number(e.target.value))}
            >
              {rawMaterials.map((mat, idx) => (
                <option key={mat.name} value={idx}>
                  {mat.name} ({mat.cogsSharePct.toFixed(1)}% of COGS)
                </option>
              ))}
            </select>
          </div>

          <div className="control-group slider-group">
            <div className="slider-label-row">
              <label htmlFor="price-slider" className="control-label">
                Hypothetical Commodity Price Shock:
              </label>
              <strong className={`slider-value-display ${priceChangePct > 0 ? "negative" : priceChangePct < 0 ? "positive" : ""}`}>
                {priceChangePct > 0 ? `+${priceChangePct}%` : `${priceChangePct}%`}
              </strong>
            </div>
            <input
              id="price-slider"
              type="range"
              min="-20"
              max="30"
              step="1"
              value={priceChangePct}
              onChange={(e) => setPriceChangePct(Number(e.target.value))}
              className="terminal-range-slider"
            />
            <div className="slider-ticks" aria-hidden="true">
              <span>-20% (Softening)</span>
              <span>0% (Baseline)</span>
              <span>+15% (Spike)</span>
              <span>+30% (Severe Shock)</span>
            </div>
          </div>
        </div>

        {/* Calculated Results Grid */}
        <div className="impact-results-grid">
          <div className="result-metric-box">
            <span className="metric-title">Cost Base Impact</span>
            <strong className={`metric-big ${additionalCostCr > 0 ? "cost-increase" : "cost-decrease"}`}>
              {additionalCostCr >= 0 ? `+₹${additionalCostCr.toFixed(1)}` : `-₹${Math.abs(additionalCostCr).toFixed(1)}`} Cr
            </strong>
            <span className="metric-sub">Annual raw material expenditure delta (FY25 Baseline)</span>
          </div>

          <div className="result-metric-box">
            <span className="metric-title">Gross Margin Compression</span>
            <strong className={`metric-big ${marginCompressionBps > 0 ? "cost-increase" : "cost-decrease"}`}>
              {marginCompressionBps >= 0 ? `-${marginCompressionBps.toFixed(0)}` : `+${Math.abs(marginCompressionBps).toFixed(0)}`} bps
            </strong>
            <span className="metric-sub">Denominator: FY25 Revenue (₹{baselineRevenue.toFixed(1)} Cr)</span>
          </div>

          <div className="result-metric-box">
            <span className="metric-title">Modelled Gross Margin</span>
            <strong className="metric-big text-accent">
              {modelledGrossMarginPct.toFixed(2)}%
            </strong>
            <span className="metric-sub">Baseline: {baselineGrossMarginPct.toFixed(2)}%</span>
          </div>
        </div>

        {/* Audit / Formula Disclosure */}
        <div className="formula-explanation-box">
          <span className="formula-label">Exact Heuristic Formula:</span>
          <code>
            Cost Impact = FY25 COGS (₹{baselineCOGS.toFixed(1)} Cr) × Share ({selectedMat.cogsSharePct.toFixed(1)}%) × Shock ({priceChangePct > 0 ? `+${priceChangePct}` : priceChangePct}%) = {additionalCostCr >= 0 ? `+₹${additionalCostCr.toFixed(2)}` : `-₹${Math.abs(additionalCostCr).toFixed(2)}`} Cr
          </code>
          <code style={{ display: "block", marginTop: "4px" }}>
            Margin Compression = ({additionalCostCr >= 0 ? `+₹${additionalCostCr.toFixed(2)}` : `-₹${Math.abs(additionalCostCr).toFixed(2)}`} Cr / Revenue ₹{baselineRevenue.toFixed(1)} Cr) × 10,000 = {marginCompressionBps.toFixed(0)} bps
          </code>
        </div>

        <div className="scenario-disclaimer">
          <strong>SYNTHETIC MODEL DISCLAIMER:</strong>
          <p>
            Illustrative scenario based on synthetic procurement weights and fictional baseline financials. Assumes unhedged purchases, static volume, and zero immediate customer pricing pass-through. This is a heuristic simulation for UI demonstration, not a financial forecast or investment advisory call.
          </p>
        </div>
      </section>

      {/* Supply Chain Disruption Signals */}
      <section className="disruption-signals-card">
        <header className="signals-header">
          <h4 className="signals-title">Supply Disruption Signals &amp; Logistics Feed</h4>
          <EvidenceBadge status="unconfirmed" size="xs" />
        </header>

        <div className="signals-list">
          <article className="signal-item">
            <div className="signal-meta">
              <span className="signal-tag">LOGISTICS &amp; PORT</span>
              <span className="signal-date">2026-10-18</span>
              <EvidenceBadge status="unconfirmed" size="xs" />
            </div>
            <h5 className="signal-headline">Western Port Bulk Freight Congestion</h5>
            <p className="signal-summary">
              Customs processing delays for imported alloy scrap at Nhava Sheva port extended dwell times by 4 days, temporarily widening local billet spot premia by 1.8%.
            </p>
            <span className="signal-source">Source: Synthetic Shipping Intelligence Report</span>
          </article>

          <article className="signal-item">
            <div className="signal-meta">
              <span className="signal-tag">ENERGY TARIFF</span>
              <span className="signal-date">2026-09-28</span>
              <EvidenceBadge status="disclosed" size="xs" />
            </div>
            <h5 className="signal-headline">State Electricity Regulatory Commission Tariff Order</h5>
            <p className="signal-summary">
              Approved industrial HT power tariff revised by +3.2% for high-demand CNC fabrication units, impacting plant operating overheads by ~₹1.8 Cr annually.
            </p>
            <span className="signal-source">Source: State ERC Tariff Order Notification (Synthetic)</span>
          </article>
        </div>
      </section>
    </div>
  );
}
