"""Scrapy spiders for ZoneScan autonomous filing discovery."""
from .generic_issuer import (
    BSECorporateFilingsSpider,
    DiscoveredDocument,
    GenericIssuerSpider,
    NSECorporateFilingsSpider,
)

__all__ = [
    "DiscoveredDocument",
    "GenericIssuerSpider",
    "NSECorporateFilingsSpider",
    "BSECorporateFilingsSpider",
]
