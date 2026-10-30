"""Document filter: classifies discovered URLs as target filing documents.

Applies heuristic rules to determine whether a discovered URL or link text
is a financially relevant document worthy of downloading for extraction.
No external I/O; pure classification logic.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SeedUrl:
    """A seed URL for the discovery crawler with metadata."""
    url: str
    domain_hint: str                # e.g. "bharatforge.com", "nseindia.com"
    allowed_domains: List[str] = field(default_factory=list)
    label: str = ""                 # human-readable description


# ---------------------------------------------------------------------------
# Heuristic patterns for classifying document URLs and anchor text
# ---------------------------------------------------------------------------

_ANNUAL_REPORT_RE = re.compile(
    r"annual.?report|ar\s*\d{2}[\-_]\d{2}|annual.?accounts",
    re.IGNORECASE,
)
_FINANCIAL_RESULTS_RE = re.compile(
    r"financial.?results?|quarterly.?results?|q[1-4].?fy\d{2}|"
    r"q[1-4].?results?|financial.?statements?|financial.?performance",
    re.IGNORECASE,
)
_XBRL_RE = re.compile(r"xbrl|taxonomy|instance.?document|\.xml$", re.IGNORECASE)
_SHAREHOLDING_RE = re.compile(
    r"shareholding.?pattern|share.?holding|promoter.?holding",
    re.IGNORECASE,
)
_RPT_RE = re.compile(
    r"related.?part(?:y|ies)|rpt|connected.?transaction",
    re.IGNORECASE,
)
_INVESTOR_RELATIONS_RE = re.compile(
    r"investor.?relations?|investors?|ir\.html|annual\-report",
    re.IGNORECASE,
)
_PDF_SUFFIX_RE = re.compile(r"\.pdf(\?.*)?$", re.IGNORECASE)
_XML_SUFFIX_RE = re.compile(r"\.xml(\?.*)?$", re.IGNORECASE)
_ZIP_SUFFIX_RE = re.compile(r"\.zip(\?.*)?$", re.IGNORECASE)

# FY patterns like FY24, FY2024, 2023-24, 24-25, etc.
_FY_IN_URL_RE = re.compile(
    r"(?:fy)?(?P<yy1>\d{2,4})[\-_](?P<yy2>\d{2,4})",
    re.IGNORECASE,
)

# Noise / exclude patterns
_NOISE_RE = re.compile(
    r"privacy|terms.?of.?use|cookie|login|register|careers|contact|"
    r"press.?release|media|gallery|csr|css|\.js|\.png|\.jpg|\.gif|"
    r"\.svg|\.ico|\.woff|\.woff2|\.ttf",
    re.IGNORECASE,
)


def _normalise_fy(raw_y1: str, raw_y2: str) -> Optional[str]:
    """Normalise raw year fragments from URL to FY string like 'FY2023-24'."""
    try:
        y1 = int(raw_y1)
        y2 = int(raw_y2)
        if y1 < 100:
            y1 += 2000
        if y2 < 100:
            y2 += 2000
        if y2 == y1 + 1:
            return f"FY{y1}-{str(y2)[-2:]}"
        # Handle reversed (e.g. 24-23 in some portals)
        if y1 == y2 + 1:
            return f"FY{y2}-{str(y1)[-2:]}"
    except (ValueError, TypeError):
        pass
    return None


class DocumentFilter:
    """Classifies URLs and anchor text to identify high-value corporate filings."""

    def __init__(self, target_years: Optional[List[str]] = None) -> None:
        """
        Args:
            target_years: e.g. ['FY2023-24', 'FY2024-25', 'FY2025-26'].
                          If None, all detected years pass.
        """
        self.target_years: List[str] = target_years or []

    # ------------------------------------------------------------------
    def _extract_fy(self, text: str) -> Optional[str]:
        m = _FY_IN_URL_RE.search(text)
        if m:
            return _normalise_fy(m.group("yy1"), m.group("yy2"))
        return None

    def _fy_matches_target(self, fy: Optional[str]) -> bool:
        if not self.target_years or fy is None:
            return True  # accept when no year filter or year unknown
        return fy in self.target_years

    def _detect_doc_type(self, url: str, anchor_text: str = "") -> Optional[str]:
        combined = f"{url} {anchor_text}"
        if _ANNUAL_REPORT_RE.search(combined):
            return "annual_report"
        if _XBRL_RE.search(combined):
            return "xbrl_instance"
        # Shareholding checked BEFORE financial_results — Q4FY24 in shareholding URLs
        # must not match the financial_results quarterly-results pattern first.
        if _SHAREHOLDING_RE.search(combined):
            return "shareholding_pattern"
        if _RPT_RE.search(combined):
            return "related_party_transactions"
        if _FINANCIAL_RESULTS_RE.search(combined):
            return "financial_results"
        # Generic PDF on an IR page
        if _PDF_SUFFIX_RE.search(url) or _XML_SUFFIX_RE.search(url):
            return "regulatory_filing"
        return None

    # ------------------------------------------------------------------
    def is_followable_link(self, url: str, anchor_text: str = "") -> bool:
        """Return True if this link should be followed during crawl (not a target doc itself)."""
        if _NOISE_RE.search(url):
            return False
        combined = f"{url} {anchor_text}"
        return bool(
            _INVESTOR_RELATIONS_RE.search(combined)
            or _ANNUAL_REPORT_RE.search(combined)
            or _FINANCIAL_RESULTS_RE.search(combined)
            or _SHAREHOLDING_RE.search(combined)
        )

    def classify(
        self,
        url: str,
        anchor_text: str = "",
    ) -> Optional[dict]:
        """Return a classification dict if the URL is a target document, else None.

        Returns:
            dict with keys: url, doc_type, fy, is_pdf, is_xml, is_zip, anchor_text
            or None if the URL should be discarded.
        """
        if _NOISE_RE.search(url):
            return None

        doc_type = self._detect_doc_type(url, anchor_text)
        if doc_type is None:
            return None

        fy = self._extract_fy(f"{url} {anchor_text}")
        if not self._fy_matches_target(fy):
            return None

        return {
            "url": url,
            "doc_type": doc_type,
            "fy": fy,
            "is_pdf": bool(_PDF_SUFFIX_RE.search(url)),
            "is_xml": bool(_XML_SUFFIX_RE.search(url)),
            "is_zip": bool(_ZIP_SUFFIX_RE.search(url)),
            "anchor_text": anchor_text.strip(),
        }
