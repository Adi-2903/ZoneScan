"""Universal Indian Issuer and Exchange Scrapy Spiders.

Contains generic spiders for:
1. GenericIssuerSpider: Crawls any verified company website and IR sections.
2. NSECorporateFilingsSpider: Queries official NSE JSON endpoints for any symbol.
3. BSECorporateFilingsSpider: Queries official BSE corporate disclosures for any scrip code.
"""
from __future__ import annotations

import logging
import urllib.parse
from typing import Any, Generator, List, Optional

import scrapy
from scrapy.http import Response

from ..document_filter import DocumentFilter
from ...models import CompanyIdentifiers

logger = logging.getLogger("zonescan.discovery.generic_spider")


class DiscoveredDocument(scrapy.Item):
    """Scrapy item representing a discovered filing document."""
    url = scrapy.Field()
    doc_type = scrapy.Field()       # annual_report, financial_results, xbrl_instance, shareholding_pattern, ...
    fy = scrapy.Field()             # e.g. FY2023-24
    anchor_text = scrapy.Field()
    is_pdf = scrapy.Field()
    is_xml = scrapy.Field()
    is_zip = scrapy.Field()
    source_page = scrapy.Field()
    source_domain = scrapy.Field()
    company_symbol = scrapy.Field()


class GenericIssuerSpider(scrapy.Spider):
    """Universal spider crawling official corporate website and investor relations sections."""

    name = "generic_issuer_spider"

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "COOKIES_ENABLED": True,
        "DEPTH_LIMIT": 3,
        "USER_AGENT": (
            "ZoneScanResearchBot/1.0 (+https://zonescan.app/bot; "
            "academic-research; contact: research@zonescan.app)"
        ),
        "HTTPERROR_ALLOWED_CODES": [403, 404, 429],
    }

    def __init__(
        self,
        symbol: str = "BHARATFORG",
        start_urls: Optional[List[str]] = None,
        allowed_domains: Optional[List[str]] = None,
        target_years: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.symbol = symbol.upper()
        self.start_urls = start_urls or []
        self.allowed_domains = allowed_domains or []
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []
        self.visited_urls: set = set()

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        self.logger.info("Parsing issuer page: %s [status=%d]", response.url, response.status)

        if response.status in (403, 401, 429):
            self.logger.warning("Access restricted (HTTP %d) for %s — skipping", response.status, response.url)
            return

        # 1. Parse all anchor links
        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()
            anchor_text = " ".join(anchor.css("::text").getall()).strip()
            if not href:
                continue

            abs_url = urllib.parse.urljoin(response.url, href)
            parsed = urllib.parse.urlparse(abs_url)

            # Classify link
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
                item["source_domain"] = parsed.netloc
                item["company_symbol"] = self.symbol

                self.discovered.append(dict(item))
                yield item

            elif self.doc_filter.is_followable_link(abs_url, anchor_text):
                # Follow internal IR links within allowed domain
                if abs_url not in self.visited_urls:
                    self.visited_urls.add(abs_url)
                    if any(parsed.netloc.endswith(d) for d in self.allowed_domains):
                        yield response.follow(abs_url, callback=self.parse)


class NSECorporateFilingsSpider(scrapy.Spider):
    """Universal spider querying official NSE India endpoints for any listed company."""

    name = "nse_corporate_filings"
    allowed_domains = ["www.nseindia.com", "nseindia.com", "nsearchives.nseindia.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,      # NSE endpoints allow browser session requests
        "DOWNLOAD_DELAY": 2.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "COOKIES_ENABLED": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "HTTPERROR_ALLOWED_CODES": [403, 404, 429],
    }

    start_urls = ["https://www.nseindia.com/"]

    def __init__(
        self,
        symbol: str = "BHARATFORG",
        target_years: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.symbol = symbol.upper()
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        self.logger.info("Primed NSE session from %s", response.url)

        api_endpoints = [
            f"https://www.nseindia.com/api/annual-reports?index=equities&symbol={self.symbol}",
            f"https://www.nseindia.com/api/corporates-financial-results?index=equities&symbol={self.symbol}",
            f"https://www.nseindia.com/api/corporate-announcements?index=equities&symbol={self.symbol}",
        ]
        for ep in api_endpoints:
            yield scrapy.Request(ep, callback=self._parse_nse_json, dont_filter=True)

    def _parse_nse_json(self, response: Response) -> Generator:  # type: ignore[override]
        if response.status in (403, 401, 429):
            self.logger.warning("NSE endpoint blocked HTTP %d: %s", response.status, response.url)
            return

        try:
            payload = response.json()
        except Exception as exc:
            self.logger.warning("NSE JSON parse failed for %s: %s", response.url, exc)
            return

        entries: List[dict] = []
        if isinstance(payload, list):
            entries = payload
        elif isinstance(payload, dict):
            entries = payload.get("data", []) or []

        for entry in entries:
            # Find PDF or XML link in common NSE response fields
            pdf_url: Optional[str] = None
            for key in ("fileName", "fileUrl", "attachmentName", "attchmntFile", "url", "link"):
                val = entry.get(key, "")
                if val and isinstance(val, str) and (val.lower().endswith(".pdf") or val.lower().endswith(".xml")):
                    pdf_url = val if val.startswith("http") else f"https://www.nseindia.com{val}"
                    break

            if not pdf_url:
                continue

            desc = (
                entry.get("desc")
                or entry.get("subject")
                or entry.get("description")
                or entry.get("companyName", "")
            )
            year_hint = f"{entry.get('fromYr', '')}-{entry.get('toYr', '')}"
            combined_anchor = f"{desc} {year_hint}"

            classification = self.doc_filter.classify(pdf_url, combined_anchor)
            if classification:
                item = DiscoveredDocument()
                item["url"] = classification["url"]
                item["doc_type"] = classification["doc_type"]
                item["fy"] = classification.get("fy") or (f"FY{entry.get('fromYr')}-{str(entry.get('toYr'))[-2:]}" if entry.get("fromYr") else None)
                item["anchor_text"] = classification.get("anchor_text") or desc
                item["is_pdf"] = classification.get("is_pdf", True)
                item["is_xml"] = classification.get("is_xml", False)
                item["is_zip"] = classification.get("is_zip", False)
                item["source_page"] = response.url
                item["source_domain"] = "nseindia.com"
                item["company_symbol"] = self.symbol

                self.discovered.append(dict(item))
                yield item


class BSECorporateFilingsSpider(scrapy.Spider):
    """Universal spider querying official BSE India announcements and XBRL filings for any scrip code."""

    name = "bse_corporate_filings"
    allowed_domains = ["www.bseindia.com", "bseindia.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "LOG_LEVEL": "INFO",
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "HTTPERROR_ALLOWED_CODES": [403, 404, 429],
    }

    def __init__(
        self,
        bse_code: str = "500493",
        symbol: str = "BHARATFORG",
        target_years: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.bse_code = bse_code
        self.symbol = symbol.upper()
        self.doc_filter = DocumentFilter(target_years=target_years)
        self.discovered: List[dict] = []
        self.start_urls = [
            f"https://www.bseindia.com/stock-share-price/x/y/{self.bse_code}/"
        ]

    def parse(self, response: Response) -> Generator:  # type: ignore[override]
        if response.status in (403, 429):
            self.logger.warning("BSE access restricted (HTTP %d) for code %s — skipping", response.status, self.bse_code)
            return

        for anchor in response.css("a[href]"):
            href = anchor.attrib.get("href", "").strip()
            anchor_text = " ".join(anchor.css("::text").getall()).strip()
            if not href:
                continue

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
                item["source_domain"] = "bseindia.com"
                item["company_symbol"] = self.symbol

                self.discovered.append(dict(item))
                yield item
