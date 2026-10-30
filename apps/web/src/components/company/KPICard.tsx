"use client";

import React from "react";
import type { FinancialMetric } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface KPICardProps {
  metric: FinancialMetric;
  onInspectSource?: (evidenceId: string) => void;
}

export function KPICard({ metric, onInspectSource }: KPICardProps) {
  const isAvailable = metric.value !== null && metric.status !== "unavailable";
  const formattedValue = isAvailable
    ? metric.unit === "%" || metric.unit === "×" || metric.unit === "₹"
      ? `${metric.value?.toFixed(2)}${metric.unit === "×" ? "×" : metric.unit === "%" ? "%" : ""}`
      : metric.value?.toLocaleString("en-IN", { minimumFractionDigits: 1, maximumFractionDigits: 2 })
    : "Unavailable";

  const hasYoY = metric.yoyChangePct !== undefined && metric.yoyChangePct !== null;
  const isPositive = hasYoY && (metric.yoyChangePct ?? 0) >= 0;

  return (
    <article
      className="kpi-card"
      tabIndex={0}
      role="button"
      aria-label={`${metric.name}: ${formattedValue} ${metric.unit}. Evidence: ${metric.status}. Click to inspect source.`}
      onClick={() => onInspectSource?.(metric.evidenceId)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onInspectSource?.(metric.evidenceId);
        }
      }}
    >
      <header className="kpi-header">
        <div>
          <h3 className="kpi-title">{metric.name}</h3>
          <span className="kpi-plain-sub">{metric.plainName}</span>
        </div>
        <EvidenceBadge
          status={metric.status}
          size="xs"
          interactive
          onClick={() => onInspectSource?.(metric.evidenceId)}
        />
      </header>

      <div className="kpi-body">
        <div className="kpi-value-row">
          <span className="kpi-value">
            {metric.unit === "₹" && <span className="kpi-currency">₹</span>}
            {formattedValue}
          </span>
          {metric.unit !== "%" && metric.unit !== "×" && metric.unit !== "₹" && (
            <span className="kpi-unit">{metric.unit}</span>
          )}
        </div>

        {hasYoY && (
          <div className="kpi-trend-row">
            <span
              className={`kpi-trend ${isPositive ? "is-up" : "is-down"}`}
              aria-label={`Year over year change: ${isPositive ? "Up" : "Down"} ${Math.abs(metric.yoyChangePct!).toFixed(1)} percent`}
            >
              <span className="trend-arrow" aria-hidden="true">{isPositive ? "↑" : "↓"}</span>
              <span className="trend-pct">{Math.abs(metric.yoyChangePct!).toFixed(1)}%</span>
              <span className="trend-label">YoY</span>
            </span>
            <span className="kpi-period">{metric.period}</span>
          </div>
        )}

        {!hasYoY && (
          <div className="kpi-trend-row">
            <span className="kpi-period">{metric.period}</span>
          </div>
        )}
      </div>

      <footer className="kpi-footer">
        <span className="kpi-source-prompt">Inspect derivation &amp; citation ↗</span>
      </footer>
    </article>
  );
}
