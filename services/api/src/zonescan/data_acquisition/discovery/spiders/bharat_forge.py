"""Bharat Forge Investor Relations crawler spider.

Crawls the Bharat Forge official IR pages to discover annual reports,
quarterly results, XBRL filings, and other corporate disclosures.
Yields DiscoveredDocument items for each qualifying link found.

Respects robots.txt and applies a 2-second download delay.
Does NOT bypass login, CAPTCHA, or WAF restrictions — if a page
returns 403/401, it is skipped and logged.
"""
from __future__ import annotations

import re
import urllib.parse
from typing import Any, Generator, List, Optional

import scrapy
from scrapy.http import Response

from ..document_filter import DocumentFilter

# ---------------------------------------------------------------------------
# Scrapy item — lightweight dict-like container
# ---------------------------------------------------------------------------

class DiscoveredDocument(scrapy.Item):
    """Scrapy item representing a discovered filing document."""
    url = scrapy.Field()
    doc_type = scrapy.Field()       # annual_report, financial_results, xbrl_instance, …
    fy = scrapy.Field()             # e.g. FY2023-24
    anchor_text = scrapy.Field()
    is_pdf = scrapy.Field()
    is_xml = scrapy.Field()
    is_zip = scrapy.Field()
    source_page = scrapy.Field()    # page where this link was found
    source_domain = scrapy.Field()


# ---------------------------------------------------------------------------
# Bharat Forge IR Spider
# ---------------------------------------------------------------------------

class BharatForgeIRSpider(scrapy.Spider):
    """Crawls bharatforge.com investor relations pages."""

    name = "bharatforge_ir"
    allowed_domains = ["bharatforge.com", "www.bharatforge.com"]

    # Official IR entry points
    start_urls = [
        "https://www.bharatforge.com/investors/annual-reports",
        "https://www.bharatforge.com/investors/financial-results",
        "https://www.bharatforge.com/investors/",
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": (
            "ZoneScanResearchBot/1.0 (+https://zonescan.app/bot; "
            "research-only; contact: research@zonescan.app)"
        ),
    }

    def __init__(self, target_years: Optional[List[str]] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        """Parse an IR index page and follow links to documents and sub-pages."""
        self.logger.info("Parsing IR page: %s [status=%d]", response.url, response.status)

        if response.status in (403, 401, 429):
            self.logger.warning(
                "Access blocked (HTTP %d) for %s — skipping, recording as access restriction",
                response.status, response.url,
            )
            return

        # Classify all anchor hrefs
        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()
            anchor_text = " ".join(anchor.css("::text").getall()).strip()
            if not href:
                continue

            # Resolve relative URLs
            abs_url = urllib.parse.urljoin(response.url, href)

            classification = self.doc_filter.classify(abs_url, anchor_text)
            if classification:
                item = DiscoveredDocument()
                item["url"] = classification["url"]
                item["doc_type"] = classification["doc_type"]
                item["fy"] = classification.get("fy")
                item["anchor_text"] = classification.get("anchor_text", "")
                item["is_pdf"] = classification.get("is_pdf", False)
                item["is_xml"] = classification.get("is_xml", False)
                item["is_zip"] = classification.get("is_zip", False)
                item["source_page"] = response.url
                item["source_domain"] = "bharatforge.com"
                self.discovered.append(dict(item))
                yield item

            elif self.doc_filter.is_followable_link(abs_url, anchor_text):
                # Follow IR sub-pages (within allowed domain only)
                parsed = urllib.parse.urlparse(abs_url)
                if any(parsed.netloc.endswith(d) for d in self.allowed_domains):
                    yield response.follow(abs_url, callback=self.parse)


# ---------------------------------------------------------------------------
# NSE India corporate filings REST spider
# ---------------------------------------------------------------------------

class NSEFilingsSpider(scrapy.Spider):
    """Queries NSE India JSON APIs for corporate filing metadata.

    NSE API responses include direct links to PDF documents filed with the
    exchange. This spider collects those links without scraping the NSE
    browser UI (which requires JS rendering).
    """

    name = "nse_filings"
    allowed_domains = ["www.nseindia.com", "nseindia.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "COOKIES_ENABLED": True,      # NSE APIs require session cookies
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }

    # NSE home page — must be visited first to prime cookies
    start_urls = ["https://www.nseindia.com/"]

    def __init__(
        self,
        symbol: str = "BHARATFORG",
        target_years: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.symbol = symbol
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        """Prime cookies from NSE home page, then query APIs."""
        self.logger.info("Primed NSE session from %s", response.url)

        api_endpoints = [
            f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={self.symbol}",
            f"https://www.nseindia.com/api/corporates-financial-results?index=equities&symbol={self.symbol}",
            f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={self.symbol}",
        ]
        for ep in api_endpoints:
            yield scrapy.Request(ep, callback=self._parse_nse_api, dont_filter=True)

    def _parse_nse_api(self, response: Response) -> Generator:  # type: ignore[override]
        if response.status in (403, 401, 429):
            self.logger.warning("NSE API blocked: %s [%d]", response.url, response.status)
            return

        try:
            data = response.json()
        except Exception as exc:
            self.logger.warning("NSE API JSON parse failed: %s — %s", response.url, exc)
            return

        # NSE annual-reports response shape: {"data": [{"fileName": "...", "year": "2023-24", ...}]}
        entries = []
        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict):
            entries = data.get("data", []) or []

        for entry in entries:
            # Locate PDF link in common NSE response shapes
            pdf_url: Optional[str] = None
            for key in ("fileName", "fileUrl", "attachmentName", "url", "link"):
                val = entry.get(key, "")
                if val and isinstance(val, str) and val.lower().endswith(".pdf"):
                    if val.startswith("http"):
                        pdf_url = val
                    else:
                        pdf_url = f"https://www.nseindia.com{val}"
                    break

            if not pdf_url:
                continue

            anchor = entry.get("description", "") or entry.get("subject", "") or entry.get("year", "")
            classification = self.doc_filter.classify(pdf_url, anchor)
            if classification:
                item: dict = {**classification, "source_page": response.url, "source_domain": "nseindia.com"}
                self.discovered.append(item)
                yield item


# ---------------------------------------------------------------------------
# BSE India XBRL / announcements spider
# ---------------------------------------------------------------------------

class BSEXBRLSpider(scrapy.Spider):
    """Attempts to retrieve BSE corporate announcement and XBRL links.

    BSE API often blocks automated requests with 403. When blocked, the
    spider records the issue and continues with available static links.
    """

    name = "bse_xbrl"
    allowed_domains = ["www.bseindia.com", "bseindia.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 3.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "HTTPERROR_ALLOWED_CODES": [403, 429],
    }

    def __init__(
        self,
        bse_code: str = "500493",
        target_years: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bse_code = bse_code
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []
        self.access_issues: List[dict] = []

    start_urls = ["https://www.bseindia.com/stock-share-price/bharat-forge-ltd/bharatforg/500493/"]

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        if response.status in (403, 429):
            self.logger.warning("BSE access blocked (HTTP %d) — recording issue", response.status)
            self.access_issues.append({
                "url": response.url,
                "status": response.status,
                "description": "BSE returned access restriction on automated request",
            })
            return

        # Scan page for PDF links
        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()
            anchor_text = " ".join(anchor.css("::text").getall()).strip()
            if not href:
                continue
            abs_url = urllib.parse.urljoin(response.url, href)
            classification = self.doc_filter.classify(abs_url, anchor_text)
            if classification:
                item: dict = {**classification, "source_page": response.url, "source_domain": "bseindia.com"}
                self.discovered.append(item)
                yield item
