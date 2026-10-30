"""Official Company Domain Verification and IR Entry-Point Discovery.

Validates whether candidate domains belong to the target listed company by
inspecting homepage content, legal name tokens, brand marks, and investor relations
navigation links. Extracts discovered IR and report section URLs for the generic crawler.
"""
from __future__ import annotations

import logging
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..models import CompanyIdentifiers

logger = logging.getLogger("zonescan.domain_verifier")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Common navigation keywords signaling Investor Relations sections
IR_LINK_PATTERNS = re.compile(
    r"(investor|annual.?report|financial.?result|shareholder|corporate.?governance|disclosure|reports)",
    re.IGNORECASE,
)

KNOWN_CANDIDATE_DOMAINS: Dict[str, List[str]] = {
    "BHARATFORG": ["bharatforge.com", "kalyanigroup.com"],
    "RELIANCE": ["ril.com", "reliance.com"],
    "JIOFIN": ["jfs.in", "jio.com"],
    "TCS": ["tcs.com", "tataconsultancyservices.com"],
    "HDFCBANK": ["hdfcbank.com"],
    "INFY": ["infosys.com"],
    "ICICIBANK": ["icicibank.com"],
    "SBIN": ["sbi.co.in"],
    "TATAMOTORS": ["tatamotors.com"],
    "TATASTEEL": ["tatasteel.com"],
    "ITC": ["itcportal.com"],
    "LT": ["larsentoubro.com"],
    "SUNPHARMA": ["sunpharma.com"],
    "WIPRO": ["wipro.com"],
    "HINDUNILVR": ["hul.co.in"],
}


@dataclass(frozen=True, slots=True)
class VerifiedDomain:
    """A verified official company domain with discovered IR entry points."""
    domain: str
    base_url: str
    is_verified: bool
    confidence_score: float
    verification_reason: str
    ir_entry_points: Tuple[str, ...] = field(default_factory=tuple)
    report_links: Tuple[str, ...] = field(default_factory=tuple)


class DomainVerifier:
    """Validates candidate websites and extracts live IR navigation links."""

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def get_candidate_domains(self, symbol: str) -> List[str]:
        """Return candidate official domain strings for a given company symbol."""
        sym_upper = symbol.strip().upper()
        if sym_upper in KNOWN_CANDIDATE_DOMAINS:
            return list(KNOWN_CANDIDATE_DOMAINS[sym_upper])
        sym_clean = re.sub(r"[^A-Za-z0-9]", "", sym_upper).lower()
        return [f"{sym_clean}.com", f"{sym_clean}.in"]

    def extract_ir_links_from_html(self, html: str, base_url: str) -> List[str]:
        """Extract investor relations and annual report URLs from HTML source."""
        hrefs = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html, re.IGNORECASE)
        ir_links: List[str] = []
        for href in hrefs:
            href_clean = href.strip()
            if not href_clean or href_clean.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue
            abs_url = urllib.parse.urljoin(base_url, href_clean)
            if IR_LINK_PATTERNS.search(abs_url):
                if abs_url not in ir_links:
                    ir_links.append(abs_url)
        return ir_links

    def verify_and_discover_ir(
        self,
        candidate_url: str,
        company: CompanyIdentifiers,
    ) -> VerifiedDomain:
        """Fetch candidate website homepage, verify company match, and extract IR links."""
        parsed = urllib.parse.urlparse(candidate_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        domain = parsed.netloc.lower()

        try:
            req = urllib.request.Request(
                base_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                content_bytes = res.read(500000)  # read up to 500KB
                html = content_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            logger.debug("Verification request failed for %s: %s", base_url, e)
            return VerifiedDomain(
                domain=domain,
                base_url=base_url,
                is_verified=False,
                confidence_score=0.0,
                verification_reason=f"Network fetch failed: {e}",
            )

        # Check company match
        legal_name = company.company_name.lower()
        symbol = company.symbol.lower()
        company_tokens = [t for t in re.findall(r"\w+", legal_name) if len(t) > 3 and t not in ("limited", "industries")]

        token_hits = sum(1 for t in company_tokens if t in html.lower())
        token_ratio = token_hits / max(len(company_tokens), 1)

        symbol_hit = symbol in html.lower()

        # Extract links from HTML
        hrefs = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html, re.IGNORECASE)
        ir_links: List[str] = []
        report_links: List[str] = []

        for href in hrefs:
            href_clean = href.strip()
            if not href_clean or href_clean.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            abs_url = urllib.parse.urljoin(base_url, href_clean)
            parsed_href = urllib.parse.urlparse(abs_url)

            # Keep only links within the same root domain
            if not parsed_href.netloc.endswith(domain.replace("www.", "")):
                continue

            if IR_LINK_PATTERNS.search(abs_url):
                if any(x in abs_url.lower() for x in ("annual-report", "annualreport", "reports/annual")):
                    if abs_url not in report_links:
                        report_links.append(abs_url)
                elif abs_url not in ir_links:
                    ir_links.append(abs_url)

        # Confidence calculation
        score = 0.0
        if token_ratio >= 0.5:
            score += 0.4
        if symbol_hit:
            score += 0.2
        if len(ir_links) > 0 or len(report_links) > 0:
            score += 0.4

        is_verified = score >= 0.5

        reason = (
            f"Verified via name token match ({token_hits}/{len(company_tokens)}) "
            f"and {len(ir_links)} IR / {len(report_links)} report links found"
            if is_verified
            else "Insufficient company tokens or IR navigation elements"
        )

        return VerifiedDomain(
            domain=domain,
            base_url=base_url,
            is_verified=is_verified,
            confidence_score=min(score, 1.0),
            verification_reason=reason,
            ir_entry_points=tuple(ir_links[:10]),
            report_links=tuple(report_links[:10]),
        )
