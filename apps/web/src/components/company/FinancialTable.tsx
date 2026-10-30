"use client";

import React, { useState } from "react";
import type { FinancialYearRow } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface FinancialTableProps {
  rows: FinancialYearRow[];
  onInspectSource: (evidenceId: string) => void;
}

type PeriodFilter = "all" | "annual" | "quarterly";

export function FinancialTable({ rows, onInspectSource }: FinancialTableProps) {
  const [filter, setFilter] = useState<PeriodFilter>("all");
  const [statementView, setStatementView] = useState<"consolidated" | "standalone">("consolidated");

  const showAnnual = filter === "all" || filter === "annual";
  const showQuarterly = filter === "all" || filter === "quarterly";

  const formatCell = (val: number | null, unit: string) => {
    if (val === null) return <span className="cell-unavailable">—</span>;
    if (unit === "%") {
      return `${val.toFixed(2)}%`;
    }
    if (unit === "×") {
      return `${val.toFixed(2)}×`;
    }
    if (unit === "₹") {
      return `₹${val.toFixed(2)}`;
    }
    if (val < 0) {
      return `(${Math.abs(val).toFixed(2)})`;
    }
    return val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  return (
    <div className="financial-table-container">
      <div className="table-toolbar">
        <div className="toolbar-left">
          <div className="segmented-control" role="group" aria-label="Statement period filter">
            <button
              type="button"
              className={`segment-btn ${filter === "all" ? "active" : ""}`}
              onClick={() => setFilter("all")}
            >
              All Periods
            </button>
            <button
              type="button"
              className={`segment-btn ${filter === "annual" ? "active" : ""}`}
              onClick={() => setFilter("annual")}
            >
              Annual (FY23–FY25)
            </button>
            <button
              type="button"
              className={`segment-btn ${filter === "quarterly" ? "active" : ""}`}
              onClick={() => setFilter("quarterly")}
            >
              Quarterly (FY26)
            </button>
          </div>

          <div className="segmented-control ml-2" role="group" aria-label="Consolidated or Standalone view">
            <button
              type="button"
              className={`segment-btn ${statementView === "consolidated" ? "active" : ""}`}
              onClick={() => setStatementView("consolidated")}
            >
              Consolidated
            </button>
            <button
              type="button"
              className={`segment-btn ${statementView === "standalone" ? "active" : ""}`}
              onClick={() => setStatementView("standalone")}
              title="Standalone statements represent parent entity only"
            >
              Standalone
            </button>
          </div>
        </div>

        <div className="toolbar-right">
          <span className="code-pill symbol-pill" style={{ marginRight: "8px", fontSize: "0.7rem" }}>
            SYNTHETIC DEMO STATEMENTS
          </span>
          <span className="unit-indicator">Currency: INR (₹ Crore)</span>
        </div>
      </div>

      <div className="financial-table-scroll-wrap" tabIndex={0} role="region" aria-label="Multi-period financial statements table">
        <table className="financial-table">
          <thead>
            <tr>
              <th scope="col" className="col-sticky-label">
                Financial Line Item
              </th>
              <th scope="col" className="col-evidence-header">
                Evidence
              </th>
              {showAnnual && (
                <>
                  <th scope="col" className="col-num">
                    FY23 <span className="col-sub">Demo Model</span>
                  </th>
                  <th scope="col" className="col-num">
                    FY24 <span className="col-sub">Demo Model</span>
                  </th>
                  <th scope="col" className="col-num">
                    FY25 <span className="col-sub">Demo Model</span>
                  </th>
                </>
              )}
              {showQuarterly && (
                <>
                  <th scope="col" className="col-num col-quarter">
                    Q1 FY26 <span className="col-sub">Demo Q1</span>
                  </th>
                  <th scope="col" className="col-num col-quarter">
                    Q2 FY26 <span className="col-sub">Demo Q2</span>
                  </th>
                </>
              )}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => {
              if (row.isHeader) {
                const colSpanCount = 2 + (showAnnual ? 3 : 0) + (showQuarterly ? 2 : 0);
                return (
                  <tr key={`header-${index}`} className="tr-section-header">
                    <td colSpan={colSpanCount}>
                      <strong>{row.label}</strong>
                    </td>
                  </tr>
                );
              }

              return (
                <tr
                  key={`row-${index}`}
                  className={`tr-data-row ${row.indent ? "tr-indent" : ""} ${row.category === "profit" ? "tr-highlight" : ""}`}
                >
                  <th scope="row" className="cell-sticky-label">
                    <button
                      type="button"
                      className="line-item-trigger"
                      onClick={() => onInspectSource(row.evidenceId)}
                      title={`Inspect evidence for ${row.label}`}
                    >
                      <span>{row.label}</span>
                      {row.unit !== "₹ Cr" && <small className="unit-tag">({row.unit})</small>}
                      <span className="inspect-arrow" aria-hidden="true">↗</span>
                    </button>
                  </th>
                  <td className="cell-evidence">
                    <EvidenceBadge
                      status={row.status}
                      size="xs"
                      interactive
                      onClick={() => onInspectSource(row.evidenceId)}
                    />
                  </td>
                  {showAnnual && (
                    <>
                      <td className="cell-num">{formatCell(row.fy23, row.unit)}</td>
                      <td className="cell-num">{formatCell(row.fy24, row.unit)}</td>
                      <td className="cell-num cell-bold">{formatCell(row.fy25, row.unit)}</td>
                    </>
                  )}
                  {showQuarterly && (
                    <>
                      <td className="cell-num cell-quarter">{formatCell(row.q1fy26, row.unit)}</td>
                      <td className="cell-num cell-quarter cell-bold">{formatCell(row.q2fy26, row.unit)}</td>
                    </>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <footer className="table-footer-legend">
        <span className="legend-note">
          ⓘ Figures in ₹ Crore unless indicated. Click any line item to inspect its statutory disclosure and derivation audit trail.
        </span>
      </footer>
    </div>
  );
}
