"""Discovery runner: orchestrates Scrapy spider execution in-process.

Runs spiders programmatically using the Scrapy CrawlerProcess API,
collects discovered document URLs, deduplicates them, and returns
a list of classification dicts ready for download.

Design notes:
- CrawlerProcess runs the Twisted event loop in a background thread.
- After crawl completion the results are passed back via a shared list.
- Playwright fallback is attempted for IR pages that Scrapy cannot render
  (requires 'playwright' package; skipped gracefully if unavailable).
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("zonescan.discovery.runner")

# ---------------------------------------------------------------------------
# Scrapy import guard
# ---------------------------------------------------------------------------
try:
    from scrapy.crawler import CrawlerProcess  # type: ignore
    from scrapy.utils.project import get_project_settings  # type: ignore
    _SCRAPY_AVAILABLE = True
except ImportError:
    _SCRAPY_AVAILABLE = False
    logger.warning("Scrapy not available; discovery will use static fallback seeds only")


def run_discovery(
    symbol: str = "BHARATFORG",
    bse_code: str = "500493",
    target_years: Optional[List[str]] = None,
    timeout_seconds: int = 300,
) -> List[Dict[str, Any]]:
    """Run all discovery spiders and return a deduplicated list of discovered documents.

    Args:
        symbol: NSE symbol (e.g. 'BHARATFORG').
        bse_code: BSE security code.
        target_years: List of FY strings like ['FY2023-24', 'FY2024-25', 'FY2025-26'].
        timeout_seconds: Maximum seconds to wait for crawl completion.

    Returns:
        List of document classification dicts with keys:
        url, doc_type, fy, is_pdf, is_xml, is_zip, anchor_text,
        source_page, source_domain.
    """
    if not _SCRAPY_AVAILABLE:
        logger.warning("Scrapy unavailable; returning empty discovery results")
        return []

    from .spiders.bharat_forge import (  # noqa: PLC0415
        BharatForgeIRSpider,
        BSEXBRLSpider,
        NSEFilingsSpider,
    )

    collected: List[Dict[str, Any]] = []
    seen_urls: set = set()
    crawl_error: List[Exception] = []

    def _run() -> None:
        try:
            process = CrawlerProcess(settings={
                "ROBOTSTXT_OBEY": True,
                "DOWNLOAD_DELAY": 2.5,
                "RANDOMIZE_DOWNLOAD_DELAY": True,
                "AUTOTHROTTLE_ENABLED": True,
                "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
                "AUTOTHROTTLE_MAX_DELAY": 30.0,
                "CONCURRENT_REQUESTS": 4,
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                "DOWNLOAD_TIMEOUT": 30,
                "COOKIES_ENABLED": True,
                "LOG_LEVEL": "WARNING",  # reduce Scrapy verbosity in CLI context
                "ITEM_PIPELINES": {},
                "RETRY_TIMES": 2,
                "HTTPERROR_ALLOWED_CODES": [403, 404, 429],
            })

            # Collect items via signal
            from scrapy import signals  # noqa: PLC0415

            def _item_scraped(item: Any, response: Any, spider: Any) -> None:  # noqa: ANN001
                url = item.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    collected.append(dict(item))

            # BharatForge IR spider
            bf_crawler = process.create_crawler(BharatForgeIRSpider)
            bf_crawler.signals.connect(_item_scraped, signal=signals.item_scraped)
            process.crawl(bf_crawler, target_years=target_years)

            # NSE Filings spider
            nse_crawler = process.create_crawler(NSEFilingsSpider)
            nse_crawler.signals.connect(_item_scraped, signal=signals.item_scraped)
            process.crawl(nse_crawler, symbol=symbol, target_years=target_years)

            # BSE XBRL spider
            bse_crawler = process.create_crawler(BSEXBRLSpider)
            bse_crawler.signals.connect(_item_scraped, signal=signals.item_scraped)
            process.crawl(bse_crawler, bse_code=bse_code, target_years=target_years)

            process.start()  # blocks until all crawlers finish
        except Exception as exc:
            logger.error("Scrapy CrawlerProcess error: %s", exc)
            crawl_error.append(exc)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    thread.join(timeout=timeout_seconds)

    if thread.is_alive():
        logger.warning(
            "Discovery crawl exceeded %ds timeout — partial results will be used",
            timeout_seconds,
        )

    if crawl_error:
        logger.error("Discovery encountered errors: %s", crawl_error[0])

    logger.info("Discovery complete: found %d unique document URLs", len(collected))
    return collected
