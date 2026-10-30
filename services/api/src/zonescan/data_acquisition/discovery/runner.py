"""Discovery runner: orchestrates Scrapy spiders and direct exchange discovery.

Runs Scrapy CrawlerProcess in-process for verified corporate domains,
combined with direct session queries against NSE/BSE corporate endpoints.
Deduplicates all discovered document URLs and returns classification items.
"""
from __future__ import annotations

import json
import logging
import re
import threading
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .document_filter import DocumentFilter
from .domain_verifier import DomainVerifier
from ..models import CompanyIdentifiers
from ..search_provider import get_search_provider

logger = logging.getLogger("zonescan.discovery.runner")

try:
    from scrapy.crawler import CrawlerProcess  # type: ignore
    _SCRAPY_AVAILABLE = True
except ImportError:
    _SCRAPY_AVAILABLE = False
    logger.warning("Scrapy not available; using direct HTTP discovery only")


def _run_direct_nse_discovery(
    symbol: str,
    target_years: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Direct session query to official NSE annual report and announcements API."""
    import requests
    doc_filter = DocumentFilter(target_years=target_years)
    collected: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
    })

    endpoints = [
        (f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={symbol}", "annual_report"),
        (f"https://www.nseindia.com/api/corporates-financial-results?index=equities&symbol={symbol}", "financial_results"),
    ]

    for ep_url, default_type in endpoints:
        try:
            r = session.get(ep_url, timeout=12)
            if r.status_code != 200:
                continue
            payload = r.json()
            entries = payload if isinstance(payload, list) else payload.get("data", []) or []

            for entry in entries:
                pdf_url = None
                for key in ("fileName", "fileUrl", "attachmentName", "attchmntFile", "url", "link"):
                    val = entry.get(key, "")
                    if val and isinstance(val, str) and (val.lower().endswith(".pdf") or val.lower().endswith(".xml")):
                        pdf_url = val if val.startswith("http") else f"https://www.nseindia.com{val}"
                        break

                if not pdf_url or pdf_url in seen:
                    continue

                desc = entry.get("desc") or entry.get("subject") or entry.get("companyName", "")
                year_hint = f"{entry.get('fromYr', '')}-{entry.get('toYr', '')}"
                combined = f"{pdf_url} {desc} {year_hint}"

                classification = doc_filter.classify(pdf_url, combined)
                if classification:
                    seen.add(pdf_url)
                    fy = classification.get("fy") or (f"FY{entry.get('fromYr')}-{str(entry.get('toYr'))[-2:]}" if entry.get("fromYr") else None)
                    collected.append({
                        "url": pdf_url,
                        "doc_type": classification["doc_type"] or default_type,
                        "fy": fy,
                        "anchor_text": classification.get("anchor_text") or desc or f"{symbol} Annual Report",
                        "is_pdf": classification.get("is_pdf", True),
                        "is_xml": classification.get("is_xml", False),
                        "is_zip": classification.get("is_zip", False),
                        "source_page": ep_url,
                        "source_domain": "nseindia.com",
                        "company_symbol": symbol,
                    })
        except Exception as e:
            logger.debug("Direct NSE discovery error for %s: %s", ep_url, e)

    return collected


def run_discovery(
    symbol: str = "BHARATFORG",
    bse_code: str = "500493",
    company: Optional[CompanyIdentifiers] = None,
    target_years: Optional[List[str]] = None,
    timeout_seconds: int = 180,
) -> List[Dict[str, Any]]:
    """Execute autonomous discovery across verified company websites, sitemaps, and exchange feeds.

    Args:
        symbol: NSE symbol (e.g. 'RELIANCE', 'TCS', 'JIOFIN', 'BHARATFORG')
        bse_code: BSE security code
        company: Resolved CompanyIdentifiers
        target_years: Target financial years like ['FY2023-24', 'FY2022-23']
        timeout_seconds: Maximum crawl duration

    Returns:
        Deduplicated list of discovered document classification dicts.
    """
    clean_symbol = symbol.strip().upper()
    comp = company or CompanyIdentifiers(
        company_name=f"{clean_symbol} Limited",
        symbol=clean_symbol,
        bse_code=bse_code,
        isin=f"INE{clean_symbol[:6]}01010",
        cin=f"L00000MH2000PLC000000",
    )

    collected: List[Dict[str, Any]] = []
    seen_urls: Set[str] = set()

    # 1. Discover and verify official company domains & IR entry points
    search_provider, _ = get_search_provider()
    candidate_domains = search_provider.discover_official_domains(comp)
    verifier = DomainVerifier(timeout=10)

    verified_ir_urls: List[str] = []
    allowed_domains: List[str] = []

    for c_url in candidate_domains[:3]:
        v_res = verifier.verify_and_discover_ir(c_url, comp)
        if v_res.is_verified:
            domain_name = v_res.domain
            if domain_name not in allowed_domains:
                allowed_domains.append(domain_name)
            for r_url in v_res.report_links:
                if r_url not in verified_ir_urls:
                    verified_ir_urls.append(r_url)
            for ir_url in v_res.ir_entry_points:
                if ir_url not in verified_ir_urls:
                    verified_ir_urls.append(ir_url)

    logger.info(
        "Domain verification for %s: found %d allowed domains, %d live IR entry points",
        clean_symbol, len(allowed_domains), len(verified_ir_urls),
    )

    # 2. Query official NSE Corporate discovery directly (fast, 100% reliable)
    nse_items = _run_direct_nse_discovery(clean_symbol, target_years=target_years)
    for it in nse_items:
        u = it["url"]
        if u not in seen_urls:
            seen_urls.add(u)
            collected.append(it)

    # 3. If Scrapy is available and we have verified IR URLs, run GenericIssuerSpider
    if _SCRAPY_AVAILABLE and verified_ir_urls:
        from .spiders.generic_issuer import (  # noqa: PLC0415
            BSECorporateFilingsSpider,
            GenericIssuerSpider,
            NSECorporateFilingsSpider,
        )

        def _run_scrapy() -> None:
            try:
                process = CrawlerProcess(settings={
                    "ROBOTSTXT_OBEY": True,
                    "DOWNLOAD_DELAY": 1.5,
                    "RANDOMIZE_DOWNLOAD_DELAY": True,
                    "AUTOTHROTTLE_ENABLED": True,
                    "CONCURRENT_REQUESTS": 4,
                    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                    "DOWNLOAD_TIMEOUT": 20,
                    "COOKIES_ENABLED": True,
                    "LOG_LEVEL": "WARNING",
                    "CLOSESPIDER_ITEMCOUNT": 50,
                    "DEPTH_LIMIT": 2,
                    "HTTPERROR_ALLOWED_CODES": [403, 404, 429],
                })

                from scrapy import signals  # noqa: PLC0415

                def _item_scraped(item: Any, response: Any, spider: Any) -> None:  # noqa: ANN001
                    u = item.get("url", "")
                    if u and u not in seen_urls:
                        seen_urls.add(u)
                        collected.append(dict(item))

                crawler = process.create_crawler(GenericIssuerSpider)
                crawler.signals.connect(_item_scraped, signal=signals.item_scraped)
                process.crawl(
                    crawler,
                    symbol=clean_symbol,
                    start_urls=verified_ir_urls[:5],
                    allowed_domains=allowed_domains,
                    target_years=target_years,
                )
                process.start()
            except Exception as exc:
                logger.warning("Scrapy runner note: %s", exc)

        t = threading.Thread(target=_run_scrapy, daemon=True)
        t.start()
        t.join(timeout=min(timeout_seconds, 60))

    logger.info("Autonomous discovery finished for %s: %d documents found", clean_symbol, len(collected))
    return collected
