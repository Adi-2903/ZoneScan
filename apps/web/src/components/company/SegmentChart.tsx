"use client";

import React, { useState } from "react";
import type { BusinessSegment } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface SegmentChartProps {
  segments: BusinessSegment[];
  onInspectSource?: (evidenceId: string) => void;
}

const segmentColors = ["#44ce9a", "#38bdf8", "#818cf8", "#fb923c", "#f47e83"];

export function SegmentChart({ segments, onInspectSource }: SegmentChartProps) {
  const [selectedIdx, setSelectedIdx] = useState<number | null>(0);
  const [viewMode, setViewMode] = useState<"visual" | "table">("visual");

  const activeSegment = selectedIdx !== null ? segments[selectedIdx] : null;

  return (
    <div className="segment-card">
      <header className="segment-header">
        <div>
          <h3 className="section-heading">Business Segment Breakdown</h3>
          <span className="section-subheading">
            Modelled segment revenue &amp; margins (Ind AS 108 Synthetic Structure)
          </span>
        </div>
        <div className="header-actions-wrap">
          <div className="segmented-control">
            <button
              type="button"
              className={`segment-btn ${viewMode === "visual" ? "active" : ""}`}
              onClick={() => setViewMode("visual")}
            >
              Visual
            </button>
            <button
              type="button"
              className={`segment-btn ${viewMode === "table" ? "active" : ""}`}
              onClick={() => setViewMode("table")}
            >
              Table View
            </button>
          </div>
          <EvidenceBadge
            status="disclosed"
            size="xs"
            interactive
            onClick={() => onInspectSource?.(segments[0]?.evidenceId)}
          />
        </div>
      </header>

      {viewMode === "visual" ? (
        <div className="segment-visual-wrap">
          {/* Proportional Segment Bar */}
          <div
            className="segment-bar"
            role="group"
            aria-label="Revenue distribution by business segment"
          >
            {segments.map((seg, idx) => {
              const color = segmentColors[idx % segmentColors.length];
              const isSelected = selectedIdx === idx;
              return (
                <button
                  key={seg.name}
                  type="button"
                  className={`segment-slice ${isSelected ? "is-selected" : ""}`}
                  style={{
                    width: `${seg.revenueSharePct}%`,
                    backgroundColor: color,
                  }}
                  onClick={() => setSelectedIdx(idx)}
                  title={`${seg.name}: ${seg.revenueSharePct}% (₹${seg.revenueCr} Cr)`}
                  aria-pressed={isSelected}
                >
                  {seg.revenueSharePct >= 14 && (
                    <span className="slice-label">
                      {seg.revenueSharePct.toFixed(0)}%
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Interactive Segment Buttons Row */}
          <div className="segment-buttons-row">
            {segments.map((seg, idx) => {
              const color = segmentColors[idx % segmentColors.length];
              const isSelected = selectedIdx === idx;
              return (
                <button
                  key={seg.name}
                  type="button"
                  className={`segment-chip ${isSelected ? "is-active" : ""}`}
                  onClick={() => setSelectedIdx(idx)}
                >
                  <span
                    className="chip-color-dot"
                    style={{ backgroundColor: color }}
                    aria-hidden="true"
                  />
                  <span className="chip-name">{seg.name}</span>
                  <span className="chip-share">{seg.revenueSharePct.toFixed(0)}%</span>
                </button>
              );
            })}
          </div>

          {/* Active Segment Detail Spotlight */}
          {activeSegment && (
            <div className="segment-detail-spotlight">
              <div className="spotlight-header">
                <div>
                  <span className="spotlight-eyebrow">SELECTED DIVISION</span>
                  <h4 className="spotlight-title">{activeSegment.name}</h4>
                </div>
                <button
                  type="button"
                  className="btn-inspect-link"
                  onClick={() => onInspectSource?.(activeSegment.evidenceId)}
                >
                  Inspect Note 36 ↗
                </button>
              </div>

              <div className="spotlight-stats">
                <div className="spotlight-stat-box">
                  <span className="stat-label">Segment Revenue</span>
                  <strong className="stat-value">₹{activeSegment.revenueCr.toFixed(1)} Cr</strong>
                  <span className="stat-sub">{activeSegment.revenueSharePct.toFixed(1)}% of total sales</span>
                </div>
                <div className="spotlight-stat-box">
                  <span className="stat-label">Divisional EBITDA Margin</span>
                  <strong className="stat-value highlight-green">
                    {activeSegment.ebitdaMarginPct.toFixed(1)}%
                  </strong>
                  <span className="stat-sub">Operating profitability</span>
                </div>
              </div>

              <p className="spotlight-desc">{activeSegment.description}</p>
            </div>
          )}
        </div>
      ) : (
        /* Accessible Table Alternative */
        <div className="segment-table-wrap">
          <table className="financial-table">
            <thead>
              <tr>
                <th scope="col">Business Segment</th>
                <th scope="col" className="col-num">Revenue (₹ Cr)</th>
                <th scope="col" className="col-num">Share %</th>
                <th scope="col" className="col-num">EBITDA Margin</th>
                <th scope="col">Status</th>
              </tr>
            </thead>
            <tbody>
              {segments.map((seg, idx) => (
                <tr key={seg.name}>
                  <th scope="row">
                    <span className="flex items-center gap-2">
                      <span
                        className="inline-block w-2.5 h-2.5 rounded-full"
                        style={{ backgroundColor: segmentColors[idx % segmentColors.length] }}
                        aria-hidden="true"
                      />
                      <strong>{seg.name}</strong>
                    </span>
                    <small className="block text-muted text-xs mt-1">{seg.description}</small>
                  </th>
                  <td className="cell-num">₹{seg.revenueCr.toFixed(1)}</td>
                  <td className="cell-num">{seg.revenueSharePct.toFixed(1)}%</td>
                  <td className="cell-num font-semibold text-green">{seg.ebitdaMarginPct.toFixed(1)}%</td>
                  <td>
                    <EvidenceBadge
                      status={seg.status}
                      size="xs"
                      interactive
                      onClick={() => onInspectSource?.(seg.evidenceId)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
