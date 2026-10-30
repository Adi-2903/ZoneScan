"use client";

import React from "react";
import type { CompanyProfile } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface ShareholdingBarProps {
  shareholding: CompanyProfile["shareholding"];
  onInspectSource?: (evidenceId: string) => void;
}

export function ShareholdingBar({ shareholding, onInspectSource }: ShareholdingBarProps) {
  const items = [
    { ...shareholding.promoter, color: "#38bdf8", key: "promoter", label: "Promoter & Group" },
    { ...shareholding.dii, color: "#818cf8", key: "dii", label: "Domestic Inst. (DII)" },
    { ...shareholding.fii, color: "#c084fc", key: "fii", label: "Foreign Inst. (FII)" },
    { ...shareholding.retail, color: "#fb923c", key: "retail", label: "Public & Retail" },
  ];

  return (
    <div className="shareholding-card">
      <header className="shareholding-header">
        <div>
          <h3 className="section-heading">Shareholding Pattern</h3>
          <span className="section-subheading">
            Quarterly distribution as of {shareholding.asOfDate} (Synthetic Demo Model)
          </span>
        </div>
        <div className="header-badge-wrap">
          <EvidenceBadge
            status="disclosed"
            size="xs"
            interactive
            onClick={() => onInspectSource?.(shareholding.evidenceId)}
          />
        </div>
      </header>

      {/* Segmented Visual Bar */}
      <div
        className="shareholding-bar-wrap"
        role="meter"
        aria-label={`Shareholding breakdown: Promoter ${shareholding.promoter.percentage}%, DII ${shareholding.dii.percentage}%, FII ${shareholding.fii.percentage}%, Public ${shareholding.retail.percentage}%`}
        aria-valuenow={100}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        {items.map((item) => (
          <div
            key={item.key}
            className="bar-segment"
            style={{
              width: `${item.percentage}%`,
              backgroundColor: item.color,
            }}
            title={`${item.label}: ${item.percentage.toFixed(2)}%`}
          >
            {item.percentage > 12 && (
              <span className="bar-segment-label">
                {item.percentage.toFixed(1)}%
              </span>
            )}
          </div>
        ))}
      </div>

      {/* Breakdown Cards Grid */}
      <div className="shareholding-grid">
        {items.map((item) => (
          <div key={item.key} className="shareholding-item">
            <div className="item-title-row">
              <span className="category-dot" style={{ backgroundColor: item.color }} aria-hidden="true" />
              <strong className="category-name">{item.label}</strong>
            </div>
            <div className="item-numbers">
              <span className="category-pct">{item.percentage.toFixed(2)}%</span>
              <span
                className={`category-change ${item.changeQoQPct >= 0 ? "positive" : "negative"}`}
                aria-label={`Quarter-over-quarter change: ${item.changeQoQPct >= 0 ? "Up" : "Down"} ${Math.abs(item.changeQoQPct).toFixed(2)} percent`}
              >
                {item.changeQoQPct >= 0 ? "+" : ""}{item.changeQoQPct.toFixed(2)}% QoQ
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Pledge & Institutional Quality Indicator */}
      <footer className="shareholding-footer">
        <div className="pledge-status-pill">
          <span className="status-dot-green" aria-hidden="true" />
          <span>
            Pledged Promoter Stake: <strong>{shareholding.pledgedPct.toFixed(1)}%</strong> (Zero encumbrance)
          </span>
        </div>
        <button
          type="button"
          className="btn-inspect-link"
          onClick={() => onInspectSource?.(shareholding.evidenceId)}
        >
          View SEBI Reg 31 filing ↗
        </button>
      </footer>
    </div>
  );
}
