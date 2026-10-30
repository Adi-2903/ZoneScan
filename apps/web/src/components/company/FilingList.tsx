"use client";

import React, { useState } from "react";
import type { RegulatoryFilingItem } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface FilingListProps {
  filings: RegulatoryFilingItem[];
  onInspectSource: (evidenceId: string) => void;
}

type FilingFilter = "all" | "results" | "contract" | "shareholding" | "expansion";

export function FilingList({ filings, onInspectSource }: FilingListProps) {
  const [filter, setFilter] = useState<FilingFilter>("all");

  const filteredFilings = filings.filter((f) => {
    if (filter === "all") return true;
    return f.type === filter;
  });

  return (
    <div className="filings-container">
      <header className="filings-header">
        <div>
          <h3 className="section-heading">Fictional Filings &amp; Modelled Disclosures</h3>
          <span className="section-subheading">
            Synthetic announcement stream formatted after SEBI (LODR) disclosures for UI testing
          </span>
        </div>

        <div className="segmented-control" role="group" aria-label="Filing type filter">
          <button
            type="button"
            className={`segment-btn ${filter === "all" ? "active" : ""}`}
            onClick={() => setFilter("all")}
          >
            All Filings ({filings.length})
          </button>
          <button
            type="button"
            className={`segment-btn ${filter === "results" ? "active" : ""}`}
            onClick={() => setFilter("results")}
          >
            Financial Results
          </button>
          <button
            type="button"
            className={`segment-btn ${filter === "contract" ? "active" : ""}`}
            onClick={() => setFilter("contract")}
          >
            Commercial Contracts
          </button>
          <button
            type="button"
            className={`segment-btn ${filter === "shareholding" ? "active" : ""}`}
            onClick={() => setFilter("shareholding")}
          >
            Shareholding
          </button>
        </div>
      </header>

      <div className="filings-list">
        {filteredFilings.map((filing) => (
          <article
            key={filing.id}
            className="filing-card"
            tabIndex={0}
            onClick={() => onInspectSource(filing.evidenceId)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onInspectSource(filing.evidenceId);
              }
            }}
          >
            <div className="filing-card-top">
              <div className="filing-meta-group">
                <span className={`filing-type-pill type-${filing.type}`}>
                  {filing.typeLabel}
                </span>
                <span className="filing-date">
                  {filing.date} · {filing.exchange}
                </span>
              </div>
              <EvidenceBadge
                status={filing.status}
                size="xs"
                interactive
                onClick={() => onInspectSource(filing.evidenceId)}
              />
            </div>

            <h4 className="filing-title">{filing.title}</h4>

            <div className="filing-summary-box">
              <span className="summary-label">Plain-Language Summary:</span>
              <p className="summary-content">{filing.plainSummary}</p>
            </div>

            <footer className="filing-card-footer">
              <span className="filing-source-tag">
                Synthetic Demo Model · Fictional Disclosure
              </span>
              <button
                type="button"
                className="btn-view-excerpt"
                onClick={(e) => {
                  e.stopPropagation();
                  onInspectSource(filing.evidenceId);
                }}
              >
                Inspect Modelled Excerpt ↗
              </button>
            </footer>
          </article>
        ))}
      </div>
    </div>
  );
}
