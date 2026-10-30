import React from "react";
import type { EvidenceStatus } from "@/lib/fixtures/company-intelligence";

interface EvidenceBadgeProps {
  status: EvidenceStatus;
  size?: "xs" | "sm" | "md";
  interactive?: boolean;
  onClick?: (event: React.MouseEvent) => void;
  title?: string;
  className?: string;
}

const statusConfig: Record<EvidenceStatus, {
  label: string;
  glyph: string;
  description: string;
  classes: string;
}> = {
  disclosed: {
    label: "Disclosed",
    glyph: "✓",
    description: "Official statutory regulatory filing or audited annual report",
    classes: "badge-disclosed",
  },
  verified: {
    label: "Verified",
    glyph: "✓✓",
    description: "Cross-checked against independent licensed regulatory source",
    classes: "badge-verified",
  },
  inferred: {
    label: "Inferred",
    glyph: "fx",
    description: "Derived by mathematical formula from disclosed statutory figures",
    classes: "badge-inferred",
  },
  unconfirmed: {
    label: "Unconfirmed",
    glyph: "?",
    description: "Reported in news, market commentary, or management estimate; not yet verified in statutory filing",
    classes: "badge-unconfirmed",
  },
  unavailable: {
    label: "Unavailable",
    glyph: "—",
    description: "Information not disclosed or not available; never substituted with zero",
    classes: "badge-unavailable",
  },
};

export function EvidenceBadge({
  status,
  size = "sm",
  interactive = false,
  onClick,
  title,
  className = "",
}: EvidenceBadgeProps) {
  const config = statusConfig[status] ?? statusConfig.unavailable;
  const tooltipText = title ?? `${config.label}: ${config.description}`;

  const baseClasses = `evidence-badge evidence-badge-${size} ${config.classes} ${interactive ? "is-interactive" : ""} ${className}`;

  if (interactive && onClick) {
    return (
      <button
        type="button"
        className={baseClasses}
        onClick={(e) => {
          e.stopPropagation();
          onClick(e);
        }}
        title={`${tooltipText} (Click to inspect evidence source)`}
        aria-label={`${config.label} evidence. ${config.description}. Click to open source disclosure details.`}
      >
        <span className="badge-glyph" aria-hidden="true">{config.glyph}</span>
        <span className="badge-text">{config.label}</span>
      </button>
    );
  }

  return (
    <span
      className={baseClasses}
      title={tooltipText}
      aria-label={`${config.label} evidence: ${config.description}`}
    >
      <span className="badge-glyph" aria-hidden="true">{config.glyph}</span>
      <span className="badge-text">{config.label}</span>
    </span>
  );
}
