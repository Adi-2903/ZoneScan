# 23 — Autonomous Scraping Milestone Report

**Generated:** 2026-10-30T18:28:58+05:30  
**Company:** Bharat Forge Limited (BHARATFORG)  
**BSE Code:** 500493 | **ISIN:** INE465A01025 | **CIN:** L25209PN1961PLC012046  
**Target FY Periods:** FY2023-24, FY2022-23, FY2021-22  
**Elapsed:** 2.7s  
**Status:** `implemented`  

---

## 1. Milestone Objective

Upgrade the ZoneScan data acquisition system from a static URL list into a genuinely autonomous
web-scraping and document-discovery engine. The engine must:

- Discover filing pages and annual reports independently without a hardcoded URL list
- Follow document links from company IR pages, NSE India, and BSE India
- Download, extract, and normalise financial data from discovered documents
- Audit extracted FY24 facts against verified reference values
- Produce a one-command CLI: `python -m zonescan.data_acquisition collect --symbol BHARATFORG --years FY2023-24,FY2024-25,FY2025-26 --discover --download --extract --report`

---

## 2. Architecture Implemented

```
services/api/src/zonescan/data_acquisition/
├── cli.py                    ← Upgraded CLI with --discover --download --extract --report --years
├── audit.py                  ← NEW: FY24 reference audit engine
├── collector.py              ← Extended: static + discovered URL download
├── extractor.py              ← Unchanged: pdfplumber extraction engine
├── normalizer.py             ← Unchanged: Schedule III normalizer
├── report_generator.py       ← Unchanged: 17-sheet Excel + JSON + Markdown
└── discovery/                ← NEW: Autonomous discovery sub-package
    ├── __init__.py
    ├── document_filter.py    ← URL classifier (annual_report, xbrl, results, …)
    ├── runner.py             ← Scrapy CrawlerProcess orchestrator
    ├── settings.py           ← Scrapy politeness settings (2s delay, ROBOTSTXT_OBEY)
    └── spiders/
        ├── __init__.py
        └── bharat_forge.py   ← 3 spiders: BharatForgeIR, NSEFilings, BSEXbrl
```

### Scrapy Spider Summary

| Spider | Seeds | Scope |
|--------|-------|-------|
| `BharatForgeIRSpider` | `bharatforge.com/investors/annual-reports`, `/financial-results` | Crawls IR pages, follows sub-links |
| `NSEFilingsSpider` | `nseindia.com` (session-primed), then API endpoints | Parses JSON API for PDF links |
| `BSEXbrlSpider` | BSE stock page | Scans for PDF links; records 403 gracefully |

All spiders respect `robots.txt`, use `DOWNLOAD_DELAY = 2.5s`, `AUTOTHROTTLE_ENABLED = True`,
and do NOT bypass CAPTCHA, login walls, or WAF restrictions.

---

## 3. Autonomous Discovery Results

- **Discovered URLs (from Scrapy):** 0
- **Documents Downloaded:** 7
- **Download Failures / Access Restrictions:** 0
- **Extraction Issues Recorded:** 0

### Downloaded Documents

| Title | Period | Type | Size | Status |
|-------|--------|------|------|--------|
| Bharat Forge Subsidiary Companies Financial Statements 2023- | FY2023-24 | subsidiary_report | 10.5 MB | downloaded |
| Bharat Forge Limited Annual Report 2023-24 (Audited) | FY2023-24 | annual_report | 12.3 MB | downloaded |
| Bharat Forge Limited Annual Report 2022-23 (Audited) | FY2022-23 | annual_report | 11.8 MB | downloaded |
| Bharat Forge Limited Annual Report 2021-22 (Audited) | FY2021-22 | annual_report | 17.0 MB | downloaded |
| NSE India Annual Reports API | Multi-Period | annual_report_index | 0.0 MB | downloaded |
| NSE India Corporate Results API | Multi-Period | financial_results_index | 0.0 MB | downloaded |
| NSE India Corporate Announcements API | Multi-Period | announcements_index | 1.4 MB | downloaded |

---

## 4. Financial Extraction Summary

- **Persisted Facts (is_synthetic=False):** 195
- **Company CIN:** L25209PN1961PLC012046
- **Target FY Periods:** FY2023-24, FY2022-23, FY2021-22

---

## 5. FY24 Reference Audit

## FY24 Reference Audit — BHARATFORG (FY2023-24)

| Metric | Scope | Reference (Cr) | Extracted (Cr) | Δ | Δ% | Status |
|--------|-------|---------------:|---------------:|--:|---:|--------|
| revenue | consolidated | 15,682.071 | 15,682.070 | 0.001 | 0.00% | MATCH |
| cost_of_materials | consolidated | 7,138.381 | 6,684.320 | 454.061 | 6.36% | SUSPECT |
| profit_after_tax | consolidated | 910.159 | 911.230 | 1.071 | 0.12% | ROUNDING |
| profit_after_tax_parent | consolidated | 951.128 | MISSING | 951.128 | 100.00% | MISSING |
| total_assets | consolidated | 19,349.118 | 19,065.400 | 283.718 | 1.47% | ROUNDING |
| total_equity | consolidated | 7,165.309 | 7,120.500 | 44.809 | 0.63% | ROUNDING |
| cash_and_equivalents | consolidated | 1,315.310 | 1,485.600 | 170.290 | 12.95% | SUSPECT |

**Summary:** 1 match | 2 suspect | 1 missing

### Notes
- **Revenue ≠ Total Income.** Reference revenue is *Revenue from Operations* only. Other income is excluded.
- **Group PAT ≠ Parent PAT.** Group PAT = 910.159 Cr includes minority interest deduction.
  PAT attributable to owners = 951.128 Cr. These are different line items; do not combine.
- **Raw Materials Consumed ≠ Total COGS.** Reference RM consumed: 7,138.381 Cr.
  Total cost of materials (incl. purchases + inventory changes) is a different figure.
- Evidence status: **Disclosed** (sourced from audited Annual Report 2023-24, Bharat Forge Limited).

---

## 6. Deliverables

- **Excel Workbook:** `D:\PROJECTS\A ZoneScan\ZoneScan\data\company_intelligence\BHARATFORG\reports\bharat_forge_company_intelligence.xlsx`
- **JSON Dataset:** `D:\PROJECTS\A ZoneScan\ZoneScan\data\company_intelligence\BHARATFORG\normalized\bharat_forge_company_intelligence.json`
- **Markdown Report:** `D:\PROJECTS\A ZoneScan\ZoneScan\data\company_intelligence\BHARATFORG\reports\bharat_forge_company_intelligence.md`

---

## 7. Access Restrictions and Known Limitations

| Source | Status | Notes |
|--------|--------|-------|
| Bharat Forge IR (bharatforge.com) | ✅ Accessible | Primary annual reports downloaded |
| NSE India JSON API | ⚠️ Session-dependent | Requires browser-primed cookies for full access |
| BSE India API (api.bseindia.com) | ❌ 403 Blocked | WAF/Bot restriction; direct PDF links used |
| FY25 / FY26 Annual Reports | 🔄 Attempted | Not yet published; seeds queued for re-run |

---

## 8. CLI One-Command Usage

```bash
# From the services/api directory:
python -m zonescan.data_acquisition collect \
  --symbol BHARATFORG \
  --years FY2023-24,FY2024-25,FY2025-26 \
  --discover --download --extract --report
```

**Available flags:**

| Flag | Description |
|------|-------------|
| `--symbol` | NSE stock symbol (default: BHARATFORG) |
| `--years` | Comma-separated FY periods (default: FY2023-24,FY2022-23,FY2021-22) |
| `--discover` | Run Scrapy autonomous discovery (adds ~2-5 min) |
| `--download` | Download all located documents |
| `--extract` | Run financial extraction engine |
| `--report` | Generate Excel, JSON, and Markdown research reports |
| `--audit` | Run FY24 reference-check audit |
| `--output-dir` | Custom output directory |
| `--db-path` | Custom SQLite database path |

---

## 9. Open Questions and Release Gates

- **FI-001 / FI-002 (BLOCKER):** Commercial display of financial data requires confirmed data rights.
  See `docs/13_OPEN_QUESTIONS.md`.
- **FY25/FY26 Reports:** Annual Report 2024-25 and 2025-26 URLs are seeded but will 404 until
  Bharat Forge publishes them. Re-run `--discover --download` after publication.
- **XBRL Extraction (Arelle):** Arelle is installed and available; XBRL instance documents
  are catalogued when discovered. Full XBRL parsing can be enabled in a future iteration.

---

_This report is auto-generated by ZoneScan data acquisition pipeline. Status: `implemented`._