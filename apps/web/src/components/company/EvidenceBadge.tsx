import React from "react";
import type { EvidenceStatus } from "@/lib/fixtures/company-intelligence";

interface EvidenceBadgeProps {
  status: EvidenceStatus;
  size?: "xs" | "sm" | "md";
  interactive?: boolean;
  onClick?: (event: React.MouseEvent) => void;
  title?: string;
  className?: string;
  /**
   * When true (default in demo fixtures), displays explicit demo-only classifications
   * to prevent confusing synthetic models with genuine statutory records.
   */
  isSynthetic?: boolean;
}

interface StatusItemConfig {
  label: string;
  glyph: string;
  description: string;
  classes: string;
}

const realStatusConfig: Record<EvidenceStatus, StatusItemConfig> = {
  disclosed: {
    label: "Disclosed",
    glyph: "✓",
    description: "Official statutory regulatory filing or audited financial statement",
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

const syntheticDemoStatusConfig: Record<EvidenceStatus, StatusItemConfig> = {
  disclosed: {
    label: "Demo Disclosed",
    glyph: "DEMO ✓",
    description: "Synthetic demo figure formatted after statutory filing structures. NOT an official corporate record.",
    classes: "badge-disclosed is-demo-badge",
  },
  verified: {
    label: "Demo Verified",
    glyph: "DEMO ✓✓",
    description: "Synthetic benchmark cross-check within prototype models. NOT a licensed regulatory verification.",
    classes: "badge-verified is-demo-badge",
  },
  inferred: {
    label: "Demo Inferred",
    glyph: "DEMO fx",
    description: "Derived by arithmetic formula from synthetic baseline inputs.",
    classes: "badge-inferred is-demo-badge",
  },
  unconfirmed: {
    label: "Demo Unconfirmed",
    glyph: "DEMO ?",
    description: "Fictional unconfirmed report for UI/UX interaction testing.",
    classes: "badge-unconfirmed is-demo-badge",
  },
  unavailable: {
    label: "Unavailable",
    glyph: "—",
    description: "Information not disclosed or unavailable in fixture; never substituted with zero",
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
  isSynthetic = true,
}: EvidenceBadgeProps) {
  const configMap = isSynthetic ? syntheticDemoStatusConfig : realStatusConfig;
  const config = configMap[status] ?? configMap.unavailable;
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
        title={`${tooltipText} (Click to inspect source citation)`}
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
