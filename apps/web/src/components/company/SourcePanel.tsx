"use client";

import React, { useEffect } from "react";
import type { EvidenceDetail } from "@/lib/fixtures/company-intelligence";
import { EvidenceBadge } from "./EvidenceBadge";

interface SourcePanelProps {
  detail: EvidenceDetail | null;
  isOpen: boolean;
  onClose: () => void;
}

export function SourcePanel({ detail, isOpen, onClose }: SourcePanelProps) {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !detail) return null;

  return (
    <div className="source-panel-overlay" role="presentation" onClick={onClose}>
      <div
        className="source-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="source-panel-title"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="source-panel-header">
          <div className="source-panel-header-info">
            <span className="source-eyebrow">LEVEL 3 DISCLOSURE &amp; AUDIT TRAIL</span>
            <h2 id="source-panel-title">{detail.itemName}</h2>
          </div>
          <div className="source-panel-header-actions">
            <EvidenceBadge status={detail.status} size="md" />
            <button
              type="button"
              className="source-panel-close"
              onClick={onClose}
              aria-label="Close disclosure panel"
            >
              ✕
            </button>
          </div>
        </header>

        <div className="source-panel-body">
          <div className="synthetic-notice-box">
            <strong>SYNTHETIC DEMO CITATION</strong>
            <p>
              This audit trail references a synthetic demo fixture. ZoneScan never invents real statutory filings or commercial relationships without licensed verification.
            </p>
          </div>

          <section className="source-section">
            <h3 className="section-title">Evidence Classification</h3>
            <div className="evidence-explanation-card">
              <div className="evidence-status-pill">
                <EvidenceBadge status={detail.status} size="sm" />
              </div>
              <p className="explanation-text">{detail.statusExplanation}</p>
            </div>
          </section>

          {detail.formula && (
            <section className="source-section">
              <h3 className="section-title">Mathematical Derivation Formula</h3>
              <div className="formula-box">
                <code>{detail.formula}</code>
              </div>
              <p className="source-note">
                This metric is Inferred deterministically from disclosed statutory line items. The calculation is transparent and reproducible.
              </p>
            </section>
          )}

          <section className="source-section">
            <h3 className="section-title">Primary Regulatory Source</h3>
            <dl className="source-metadata-grid">
              <div>
                <dt>Document</dt>
                <dd>{detail.sourceDocument ?? "Statutory Master Record"}</dd>
              </div>
              {detail.sourceSection && (
                <div>
                  <dt>Section / Note</dt>
                  <dd>{detail.sourceSection}</dd>
                </div>
              )}
              {detail.sourceDate && (
                <div>
                  <dt>Reporting / Filing Date</dt>
                  <dd>{detail.sourceDate}</dd>
                </div>
              )}
              {detail.filingType && (
                <div>
                  <dt>Filing Classification</dt>
                  <dd>{detail.filingType}</dd>
                </div>
              )}
            </dl>
          </section>

          {detail.verbatimExcerpt && (
            <section className="source-section">
              <h3 className="section-title">Statutory Excerpt</h3>
              <blockquote className="verbatim-quote">
                &ldquo;{detail.verbatimExcerpt}&rdquo;
              </blockquote>
            </section>
          )}

          {detail.verificationSource && (
            <section className="source-section">
              <h3 className="section-title">Independent Verification Cross-Check</h3>
              <p className="verification-text">{detail.verificationSource}</p>
            </section>
          )}

          {detail.missingDataReason && (
            <section className="source-section">
              <h3 className="section-title">Unavailable Data Reason</h3>
              <div className="unavailable-callout">
                <p>{detail.missingDataReason}</p>
              </div>
            </section>
          )}

          <section className="source-section">
            <h3 className="section-title">Plain-Language Context</h3>
            <p className="plain-summary-text">{detail.plainSummary}</p>
          </section>
        </div>

        <footer className="source-panel-footer">
          <span className="source-footer-note">
            ZoneScan Terminal · Level 3 Progressive Disclosure
          </span>
          <button type="button" className="btn-close-panel" onClick={onClose}>
            Done
          </button>
        </footer>
      </div>
    </div>
  );
}
