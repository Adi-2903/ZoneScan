"""Scrapy settings for ZoneScan autonomous discovery spiders.

Conservative politeness settings to respect robots.txt and avoid
triggering WAF/rate-limiting on exchange portals.
"""
from __future__ import annotations

BOT_NAME = "zonescan_discovery"
SPIDER_MODULES = ["zonescan.data_acquisition.discovery.spiders"]
NEWSPIDER_MODULE = "zonescan.data_acquisition.discovery.spiders"

# Politeness
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2.0          # seconds between requests to the same domain
RANDOMIZE_DOWNLOAD_DELAY = True
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Timeouts
DOWNLOAD_TIMEOUT = 30

# User-Agent: identify as a research tool (non-deceptive)
USER_AGENT = (
    "ZoneScanResearchBot/1.0 (+https://zonescan.app/bot; "
    "research-only; contact: research@zonescan.app)"
)

# Don't follow all cookies
COOKIES_ENABLED = False

# Logging
LOG_LEVEL = "INFO"

# Disable unused middlewares
ITEM_PIPELINES: dict = {}

# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# Respect 429 (Too Many Requests) — don't retry
HTTPERROR_ALLOWED_CODES = [403, 404, 429]
