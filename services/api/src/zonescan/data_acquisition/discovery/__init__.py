"""Autonomous document discovery sub-package for ZoneScan.

Uses Scrapy as the primary crawling engine to discover annual reports,
financial results, XBRL filings, shareholding patterns, and related-party
disclosures from company Investor Relations pages, NSE India, and BSE India.
"""
from __future__ import annotations

from .document_filter import DocumentFilter, SeedUrl
from .runner import run_discovery

__all__ = ["DocumentFilter", "SeedUrl", "run_discovery"]
