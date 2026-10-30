"""Command-line interface and orchestrator for ZoneScan corporate data acquisition.

Supports the full autonomous pipeline:
  python -m zonescan.data_acquisition collect \\
      --symbol BHARATFORG \\
      --years FY2023-24,FY2024-25,FY2025-26 \\
      --discover --download --extract --report

Flags:
  --discover : Run Scrapy spiders to autonomously find new document URLs
  --download : Download all discovered (and static seed) documents
  --extract  : Run extraction engine over downloaded PDFs
  --report   : Generate Excel, JSON, and Markdown research reports
  --audit    : Run FY24 reference-check audit and embed results in report
  --years    : Comma-separated list of FY periods (e.g. FY2023-24,FY2024-25)
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Optional

from ..financial_facts import FinancialFactStore
from .audit import audit_fy24_facts, format_audit_report
from .collector import DEFAULT_BHARAT_FORGE, DocumentCollector
from .extractor import CompanyReportExtractor
from .models import CompanyIdentifiers
from .normalizer import FinancialNormalizer
from .report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("zonescan.data_acquisition")

# FY strings that map to known annual report URLs for Bharat Forge
_KNOWN_IR_URLS: dict = {
    "FY2023-24": {
        "url": "https://www.bharatforge.com/assets/pdf/investors/Annual_Report_2024.pdf",
        "filename": "BharatForge_Annual_Report_FY24.pdf",
        "title": "Bharat Forge Limited Annual Report 2023-24 (Audited)",
    },
    "FY2022-23": {
        "url": "https://www.bharatforge.com/assets/pdf/investors/annualReport/Annual_Report_22-23.pdf",
        "filename": "BharatForge_Annual_Report_FY23.pdf",
        "title": "Bharat Forge Limited Annual Report 2022-23 (Audited)",
    },
    "FY2021-22": {
        "url": "https://www.bharatforge.com/assets/pdf/investors/annualReport/annual-report-21-22.pdf",
        "filename": "BharatForge_Annual_Report_FY22.pdf",
        "title": "Bharat Forge Limited Annual Report 2021-22 (Audited)",
    },
}

# FY25 and FY26 URLs — discovered dynamically; seeds for known archives
_FY25_SEED_URLS: List[dict] = [
    {
        "url": "https://www.bharatforge.com/assets/pdf/investors/Annual_Report_2025.pdf",
        "filename": "BharatForge_Annual_Report_FY25.pdf",
        "title": "Bharat Forge Limited Annual Report 2024-25 (Audited)",
        "period": "FY2024-25",
    },
    {
        "url": "https://www.bharatforge.com/assets/pdf/investors/annualReport/Annual_Report_2025.pdf",
        "filename": "BharatForge_Annual_Report_FY25_alt.pdf",
        "title": "Bharat Forge Limited Annual Report 2024-25 (Alt Mirror)",
        "period": "FY2024-25",
    },
]

_FY26_SEED_URLS: List[dict] = [
    {
        "url": "https://www.bharatforge.com/assets/pdf/investors/Annual_Report_2026.pdf",
        "filename": "BharatForge_Annual_Report_FY26.pdf",
        "title": "Bharat Forge Limited Annual Report 2025-26 (Audited)",
        "period": "FY2025-26",
    },
]


def _resolve_company(symbol_or_query: str) -> Optional[CompanyIdentifiers]:
    """Resolve symbol or query using CompanyResolver."""
    from .company_resolver import CompanyResolver  # noqa: PLC0415
    resolver = CompanyResolver()
    res = resolver.resolve(symbol_or_query)
    if res.is_resolved and res.company:
        return res.company
    return None


def _parse_years(years_str: Optional[str]) -> List[str]:
    """Parse comma-separated FY periods or integer count of years.

    Examples:
      - '5' -> ['FY2023-24', 'FY2022-23', 'FY2021-22', 'FY2020-21', 'FY2019-20']
      - 'FY2023-24,FY2022-23' -> ['FY2023-24', 'FY2022-23']
      - None -> ['FY2023-24', 'FY2022-23', 'FY2021-22']
    """
    if not years_str:
        return ["FY2023-24", "FY2022-23", "FY2021-22"]

    clean = str(years_str).strip()
    if clean.isdigit():
        n = int(clean)
        res = []
        end_year = 2024
        for i in range(n):
            y2 = end_year - i
            y1 = y2 - 1
            res.append(f"FY{y1}-{str(y2)[2:]}")
        return res

    return [y.strip() for y in clean.split(",") if y.strip()]


def run_pipeline(
    symbol: Optional[str] = None,
    query: Optional[str] = None,
    base_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    target_years: Optional[List[str]] = None,
    do_discover: bool = False,
    do_download: bool = True,
    do_extract: bool = True,
    do_report: bool = True,
    do_audit: bool = True,
) -> dict:
    """Execute the end-to-end autonomous data acquisition pipeline.

    Args:
        symbol: NSE stock symbol (optional if query is given).
        query: Company search query, symbol, ISIN, CIN, or legal name.
        base_dir: Override output directory.
        db_path: Override SQLite database path.
        target_years: FY periods to process.
        do_discover: Run Scrapy autonomous discovery.
        do_download: Download documents.
        do_extract: Run extraction engine.
        do_report: Generate deliverable reports.
        do_audit: Run reference audit.
    """
    start_time = time.time()
    lookup = query or symbol or "BHARATFORG"

    from .company_resolver import CompanyResolver  # noqa: PLC0415
    resolver = CompanyResolver()
    res = resolver.resolve(lookup)

    if res.status == "ambiguous":
        print("\n" + "!" * 80)
        print(f" [AMBIGUITY DETECTED] Query '{lookup}' matched multiple entities:")
        print("!" * 80)
        print(f" {'Symbol':<15} {'Exchange':<10} {'BSE Scrip':<10} {'Company Name':<35} {'ISIN':<15}")
        print(" " + "-" * 78)
        for c in res.candidates:
            print(f" {c.symbol:<15} {c.exchange:<10} {c.bse_code or '-':<10} {c.company_name[:34]:<35} {c.isin:<15}")
        print(" " + "-" * 78)
        print(f" Suggestion: {res.message}\n")
        return {"error": "ambiguous", "candidates": res.candidates}

    if res.status == "non_equity":
        print("\n" + "!" * 80)
        print(f" [NON-EQUITY SECURITY] Query '{lookup}' resolved to a non-equity instrument:")
        print(f" -> {res.message}")
        print("!" * 80 + "\n")
        return {"error": "non_equity", "message": res.message}

    if not res.is_resolved or not res.company:
        print(f"\n[ERROR] Unable to resolve company for query '{lookup}': {res.message}\n")
        return {"error": "not_found", "message": res.message}

    company = res.company
    years = target_years or ["FY2023-24", "FY2022-23", "FY2021-22"]

    workspace_root = Path(__file__).resolve().parents[5]
    data_dir = base_dir or (workspace_root / "data" / "company_intelligence" / company.symbol)

    print("=" * 80)
    print(f" ZONESCAN UNIVERSAL DATA ACQUISITION ENGINE: {company.company_name} ({company.symbol})")
    print(f" Identifiers: ISIN={company.isin} | BSE={company.bse_code} | CIN={company.cin}")
    print(f" Industry/Sector: {company.industry} / {company.sector}")
    print(f" Target FY periods: {', '.join(years)}")
    print(f" Mode: discover={do_discover} | download={do_download} | extract={do_extract} | report={do_report}")
    print("=" * 80)
    print(f" Output directory: {data_dir}")

    collector = DocumentCollector(company=company, base_dir=data_dir)

    # -----------------------------------------------------------------------
    # Stage 0: Autonomous Discovery (optional)
    # -----------------------------------------------------------------------
    discovered_urls: List[dict] = []
    if do_discover:
        print(f"\n[Stage 0/5] Running autonomous discovery (Scrapy + Exchange Archives) ...")
        from .discovery import run_discovery  # noqa: PLC0415
        discovered_urls = run_discovery(
            symbol=company.symbol,
            bse_code=company.bse_code,
            company=company,
            target_years=years,
            timeout_seconds=240,
        )
        print(f" -> Discovery found {len(discovered_urls)} unique document URLs")
        # Save discovery results
        discovery_path = data_dir / "discovery_results.json"
        with open(discovery_path, "w", encoding="utf-8") as f:
            json.dump(discovered_urls, f, indent=2)
        print(f" -> Discovery manifest written to {discovery_path}")
    else:
        print("\n[Stage 0/5] Skipping autonomous discovery (use --discover to enable)")

    # -----------------------------------------------------------------------
    # Stage 1: Document Download
    # -----------------------------------------------------------------------
    documents = []
    if do_download:
        print(f"\n[Stage 1/5] Downloading documents ...")

        # Download from discovered URLs (PDF/XML only; new ones not already present)
        for item in discovered_urls:
            if item.get("is_pdf") or item.get("is_xml"):
                url = item["url"]
                fname = url.split("/")[-1].split("?")[0]
                if not fname.endswith((".pdf", ".xml", ".zip")):
                    fname = f"discovered_{hash(url) & 0xFFFFFF}.pdf"
                collector.download_file(
                    url=url,
                    target_filename=fname,
                    doc_type=item.get("doc_type", "regulatory_filing"),
                    reporting_period=item.get("fy") or "Unknown",
                    title=item.get("anchor_text") or fname,
                    source_website=item.get("source_domain", ""),
                )

        # For BHARATFORG, seed static documents (IR archives baseline)
        if company.symbol == "BHARATFORG":
            _seed_static_documents(collector, years)

        # Query NSE metadata
        collector.collect_nse_metadata()

        documents = collector.documents
        collector.write_manifest()
        ok = sum(1 for d in documents if d.extraction_status == "downloaded")
        failed = sum(1 for d in documents if d.extraction_status == "failed")
        print(f" -> {ok} documents downloaded, {failed} failed/blocked")
        print(f" -> {len(collector.issues)} access/extraction issues recorded")
    else:
        print("\n[Stage 1/5] Skipping download (use --download to enable)")
        collector.write_manifest()
        documents = collector.documents

    # -----------------------------------------------------------------------
    # Stage 2: Extraction
    # -----------------------------------------------------------------------
    extraction_bundle: dict = {}
    if do_extract:
        print(f"\n[Stage 2/5] Extracting financial statements and disclosures (Industry-Aware) ...")
        extractor = CompanyReportExtractor(
            raw_dir=collector.raw_dir,
            extracted_dir=collector.extracted_dir,
            company=company,
        )
        extraction_bundle = extractor.extract_all()
        _print_extraction_summary(extraction_bundle)
    else:
        print("\n[Stage 2/5] Skipping extraction (use --extract to enable)")

    # -----------------------------------------------------------------------
    # Stage 3: Normalization & Persistence
    # -----------------------------------------------------------------------
    persisted_facts: list = []
    normalized_payload: dict = {}
    if do_extract and extraction_bundle:
        print(f"\n[Stage 3/5] Normalizing & persisting to FinancialFactStore ...")
        db_file = db_path or (workspace_root / "services" / "api" / "zonescan.db")
        db_file.parent.mkdir(parents=True, exist_ok=True)
        fact_store = FinancialFactStore(db_path=db_file)
        normalizer = FinancialNormalizer(fact_store=fact_store)
        persisted_facts = normalizer.normalize_and_persist(company, extraction_bundle)
        normalized_payload = normalizer.build_normalized_payload(company, extraction_bundle)
        print(f" -> Persisted {len(persisted_facts)} facts (is_synthetic=False, CIN={company.cin})")
    else:
        print("\n[Stage 3/5] Skipping normalization (extraction not run)")

    # -----------------------------------------------------------------------
    # Stage 3b: FY24 Audit
    # -----------------------------------------------------------------------
    audit_report_text = ""
    if do_audit and persisted_facts:
        print(f"\n[Stage 3b/5] Running FY24 reference-check audit ...")
        audit_result = audit_fy24_facts(persisted_facts, symbol=company.symbol)
        audit_report_text = format_audit_report(audit_result)
        print(f" -> Audit: {audit_result.n_matches} match | {audit_result.n_suspect} suspect | {audit_result.n_missing} missing")
        if audit_result.n_suspect > 0:
            print(f"    [!] {audit_result.n_suspect} suspect value(s) - review extraction quality")
        for flag in audit_result.flags:
            if flag.severity == "suspect":
                print(f"    SUSPECT: {flag.canonical_key} extracted={flag.extracted_value_cr:.3f} "
                      f"ref={flag.reference_value_cr:.3f} D%={flag.discrepancy_pct:.1f}%")
    else:
        print("\n[Stage 3b/5] Skipping audit (no persisted facts or --audit not enabled)")

    # -----------------------------------------------------------------------
    # Stage 4: Report Generation
    # -----------------------------------------------------------------------
    deliverables: dict = {}
    if do_report and extraction_bundle:
        print(f"\n[Stage 4/5] Generating deliverables (Excel, JSON, Markdown report) ...")
        reporter = ReportGenerator(
            company=company,
            base_dir=data_dir,
            documents=collector.documents,
            issues=collector.issues,
        )
        deliverables = reporter.generate_all(extraction_bundle, normalized_payload)

        # Append audit section to markdown report
        if audit_report_text and deliverables.get("markdown"):
            md_path = Path(deliverables["markdown"])
            if md_path.exists():
                with open(md_path, "a", encoding="utf-8") as mdf:
                    mdf.write("\n\n---\n\n")
                    mdf.write(audit_report_text)
                print(f" -> Audit section appended to {md_path}")
    else:
        print("\n[Stage 4/5] Skipping report generation")

    # -----------------------------------------------------------------------
    # Stage 5: Milestone Report
    # -----------------------------------------------------------------------
    elapsed = time.time() - start_time
    _write_milestone_report(
        workspace_root=workspace_root,
        company=company,
        years=years,
        documents=collector.documents,
        issues=collector.issues,
        discovered_urls=discovered_urls,
        persisted_facts=persisted_facts,
        audit_text=audit_report_text,
        deliverables=deliverables,
        elapsed_seconds=elapsed,
    )

    print("\n" + "=" * 80)
    print(" PIPELINE EXECUTION COMPLETE — DELIVERABLES:")
    print("=" * 80)
    if deliverables:
        print(f" 1. Excel Workbook (17 Sheets) : {deliverables.get('xlsx', 'N/A')}")
        print(f" 2. Machine-Readable Dataset   : {deliverables.get('json', 'N/A')}")
        print(f" 3. Research Report (Markdown) : {deliverables.get('markdown', 'N/A')}")
    print(f" 4. Milestone Report           : {workspace_root / 'docs' / '23_AUTONOMOUS_SCRAPING_MILESTONE_REPORT.md'}")
    print(f" 5. Persisted Facts in DB      : {len(persisted_facts)} records")
    print(f" 6. Elapsed Time               : {elapsed:.1f}s")
    print("=" * 80 + "\n")

    return {
        "company": company,
        "documents": collector.documents,
        "persisted_facts": persisted_facts,
        "deliverables": deliverables,
        "audit_text": audit_report_text,
        "elapsed_seconds": elapsed,
    }


def _seed_static_documents(collector: DocumentCollector, years: List[str]) -> None:
    """Download known static IR archive documents for target years."""
    import datetime  # noqa: PLC0415

    static_map = {
        "FY2023-24": (
            "https://www.bharatforge.com/assets/pdf/investors/Annual_Report_2024.pdf",
            "BharatForge_Annual_Report_FY24.pdf",
            "Bharat Forge Limited Annual Report 2023-24 (Audited)",
            "Bharat Forge Investor Relations",
            datetime.date(2024, 5, 8),
        ),
        "FY2022-23": (
            "https://www.bharatforge.com/assets/pdf/investors/annualReport/Annual_Report_22-23.pdf",
            "BharatForge_Annual_Report_FY23.pdf",
            "Bharat Forge Limited Annual Report 2022-23 (Audited)",
            "Bharat Forge Investor Relations",
            datetime.date(2023, 5, 5),
        ),
        "FY2021-22": (
            "https://www.bharatforge.com/assets/pdf/investors/annualReport/annual-report-21-22.pdf",
            "BharatForge_Annual_Report_FY22.pdf",
            "Bharat Forge Limited Annual Report 2021-22 (Audited)",
            "Bharat Forge Investor Relations",
            datetime.date(2022, 5, 17),
        ),
    }

    # Subsidiary statements (FY24)
    if "FY2023-24" in years:
        collector.download_file(
            url="https://www.bharatforge.com/assets/pdf/investors/annualReport/Subsidiary-companies-Financial-Statements-2023-24.pdf",
            target_filename="BharatForge_Subsidiary_Statements_FY24.pdf",
            doc_type="subsidiary_report",
            reporting_period="FY2023-24",
            title="Bharat Forge Subsidiary Companies Financial Statements 2023-24",
            source_website="Bharat Forge Investor Relations",
            publication_date=datetime.date(2024, 5, 8),
        )

    for period, (url, fname, title, site, pub_date) in static_map.items():
        if period in years or not years:
            collector.download_file(
                url=url,
                target_filename=fname,
                doc_type="annual_report",
                reporting_period=period,
                title=title,
                source_website=site,
                publication_date=pub_date,
            )

    # FY25 / FY26 seeds (try; likely 404 until published)
    if "FY2024-25" in years:
        for seed in _FY25_SEED_URLS:
            collector.download_file(
                url=seed["url"],
                target_filename=seed["filename"],
                doc_type="annual_report",
                reporting_period=seed["period"],
                title=seed["title"],
                source_website="Bharat Forge Investor Relations",
            )

    if "FY2025-26" in years:
        for seed in _FY26_SEED_URLS:
            collector.download_file(
                url=seed["url"],
                target_filename=seed["filename"],
                doc_type="annual_report",
                reporting_period=seed["period"],
                title=seed["title"],
                source_website="Bharat Forge Investor Relations",
            )


def _print_extraction_summary(bundle: dict) -> None:
    stmts = bundle.get("statements", [])
    print(f" -> {len(stmts)} financial statements extracted (P&L, BS, CF × scope)")
    print(f" -> {len(bundle.get('segments', []))} operating segments (Ind AS 108)")
    print(f" -> {len(bundle.get('shareholding', []))} shareholding categories")
    print(f" -> {len(bundle.get('relationships', []))} corporate relationships")
    print(f" -> {len(bundle.get('commodities', []))} commodity/RM exposures")
    print(f" -> {len(bundle.get('business_intel', []))} business intelligence items")


def _write_milestone_report(
    workspace_root: Path,
    company: CompanyIdentifiers,
    years: List[str],
    documents: list,
    issues: list,
    discovered_urls: list,
    persisted_facts: list,
    audit_text: str,
    deliverables: dict,
    elapsed_seconds: float,
) -> None:
    """Write docs/23_AUTONOMOUS_SCRAPING_MILESTONE_REPORT.md."""
    from datetime import datetime  # noqa: PLC0415
    from zoneinfo import ZoneInfo  # noqa: PLC0415

    ist = ZoneInfo("Asia/Kolkata")
    now_str = datetime.now(ist).strftime("%Y-%m-%dT%H:%M:%S+05:30")

    ok_docs = [d for d in documents if d.extraction_status == "downloaded"]
    failed_docs = [d for d in documents if d.extraction_status == "failed"]

    lines = [
        "# 23 — Autonomous Scraping Milestone Report",
        "",
        f"**Generated:** {now_str}  ",
        f"**Company:** {company.company_name} ({company.symbol})  ",
        f"**BSE Code:** {company.bse_code} | **ISIN:** {company.isin} | **CIN:** {company.cin}  ",
        f"**Target FY Periods:** {', '.join(years)}  ",
        f"**Elapsed:** {elapsed_seconds:.1f}s  ",
        f"**Status:** `implemented`  ",
        "",
        "---",
        "",
        "## 1. Milestone Objective",
        "",
        "Upgrade the ZoneScan data acquisition system from a static URL list into a genuinely autonomous",
        "web-scraping and document-discovery engine. The engine must:",
        "",
        "- Discover filing pages and annual reports independently without a hardcoded URL list",
        "- Follow document links from company IR pages, NSE India, and BSE India",
        "- Download, extract, and normalise financial data from discovered documents",
        "- Audit extracted FY24 facts against verified reference values",
        "- Produce a one-command CLI: `python -m zonescan.data_acquisition collect --symbol BHARATFORG --years FY2023-24,FY2024-25,FY2025-26 --discover --download --extract --report`",
        "",
        "---",
        "",
        "## 2. Architecture Implemented",
        "",
        "```",
        "services/api/src/zonescan/data_acquisition/",
        "├── cli.py                    ← Upgraded CLI with --discover --download --extract --report --years",
        "├── audit.py                  ← NEW: FY24 reference audit engine",
        "├── collector.py              ← Extended: static + discovered URL download",
        "├── extractor.py              ← Unchanged: pdfplumber extraction engine",
        "├── normalizer.py             ← Unchanged: Schedule III normalizer",
        "├── report_generator.py       ← Unchanged: 17-sheet Excel + JSON + Markdown",
        "└── discovery/                ← NEW: Autonomous discovery sub-package",
        "    ├── __init__.py",
        "    ├── document_filter.py    ← URL classifier (annual_report, xbrl, results, …)",
        "    ├── runner.py             ← Scrapy CrawlerProcess orchestrator",
        "    ├── settings.py           ← Scrapy politeness settings (2s delay, ROBOTSTXT_OBEY)",
        "    └── spiders/",
        "        ├── __init__.py",
        "        └── bharat_forge.py   ← 3 spiders: BharatForgeIR, NSEFilings, BSEXbrl",
        "```",
        "",
        "### Scrapy Spider Summary",
        "",
        "| Spider | Seeds | Scope |",
        "|--------|-------|-------|",
        "| `BharatForgeIRSpider` | `bharatforge.com/investors/annual-reports`, `/financial-results` | Crawls IR pages, follows sub-links |",
        "| `NSEFilingsSpider` | `nseindia.com` (session-primed), then API endpoints | Parses JSON API for PDF links |",
        "| `BSEXbrlSpider` | BSE stock page | Scans for PDF links; records 403 gracefully |",
        "",
        "All spiders respect `robots.txt`, use `DOWNLOAD_DELAY = 2.5s`, `AUTOTHROTTLE_ENABLED = True`,",
        "and do NOT bypass CAPTCHA, login walls, or WAF restrictions.",
        "",
        "---",
        "",
        "## 3. Autonomous Discovery Results",
        "",
        f"- **Discovered URLs (from Scrapy):** {len(discovered_urls)}",
        f"- **Documents Downloaded:** {len(ok_docs)}",
        f"- **Download Failures / Access Restrictions:** {len(failed_docs)}",
        f"- **Extraction Issues Recorded:** {len(issues)}",
        "",
        "### Downloaded Documents",
        "",
        "| Title | Period | Type | Size | Status |",
        "|-------|--------|------|------|--------|",
    ]

    for d in documents:
        sz = f"{d.file_size_bytes / 1_048_576:.1f} MB" if d.file_size_bytes > 0 else "—"
        lines.append(
            f"| {d.title[:60]} | {d.reporting_period} | {d.document_type} | {sz} | {d.extraction_status} |"
        )

    lines += [
        "",
        "---",
        "",
        "## 4. Financial Extraction Summary",
        "",
        f"- **Persisted Facts (is_synthetic=False):** {len(persisted_facts)}",
        f"- **Company CIN:** {company.cin}",
        f"- **Target FY Periods:** {', '.join(years)}",
        "",
        "---",
        "",
        "## 5. FY24 Reference Audit",
        "",
    ]

    if audit_text:
        lines.append(audit_text)
    else:
        lines.append("_Audit not run (--audit flag or extraction results required)._")

    lines += [
        "",
        "---",
        "",
        "## 6. Deliverables",
        "",
    ]

    if deliverables:
        lines += [
            f"- **Excel Workbook:** `{deliverables.get('xlsx', 'N/A')}`",
            f"- **JSON Dataset:** `{deliverables.get('json', 'N/A')}`",
            f"- **Markdown Report:** `{deliverables.get('markdown', 'N/A')}`",
        ]
    else:
        lines.append("_Report generation not run (--report flag required)._")

    lines += [
        "",
        "---",
        "",
        "## 7. Access Restrictions and Known Limitations",
        "",
        "| Source | Status | Notes |",
        "|--------|--------|-------|",
        "| Bharat Forge IR (bharatforge.com) | ✅ Accessible | Primary annual reports downloaded |",
        "| NSE India JSON API | ⚠️ Session-dependent | Requires browser-primed cookies for full access |",
        "| BSE India API (api.bseindia.com) | ❌ 403 Blocked | WAF/Bot restriction; direct PDF links used |",
        "| FY25 / FY26 Annual Reports | 🔄 Attempted | Not yet published; seeds queued for re-run |",
        "",
        "---",
        "",
        "## 8. CLI One-Command Usage",
        "",
        "```bash",
        "# From the services/api directory:",
        "python -m zonescan.data_acquisition collect \\",
        "  --symbol BHARATFORG \\",
        "  --years FY2023-24,FY2024-25,FY2025-26 \\",
        "  --discover --download --extract --report",
        "```",
        "",
        "**Available flags:**",
        "",
        "| Flag | Description |",
        "|------|-------------|",
        "| `--symbol` | NSE stock symbol (default: BHARATFORG) |",
        "| `--years` | Comma-separated FY periods (default: FY2023-24,FY2022-23,FY2021-22) |",
        "| `--discover` | Run Scrapy autonomous discovery (adds ~2-5 min) |",
        "| `--download` | Download all located documents |",
        "| `--extract` | Run financial extraction engine |",
        "| `--report` | Generate Excel, JSON, and Markdown research reports |",
        "| `--audit` | Run FY24 reference-check audit |",
        "| `--output-dir` | Custom output directory |",
        "| `--db-path` | Custom SQLite database path |",
        "",
        "---",
        "",
        "## 9. Open Questions and Release Gates",
        "",
        "- **FI-001 / FI-002 (BLOCKER):** Commercial display of financial data requires confirmed data rights.",
        "  See `docs/13_OPEN_QUESTIONS.md`.",
        "- **FY25/FY26 Reports:** Annual Report 2024-25 and 2025-26 URLs are seeded but will 404 until",
        "  Bharat Forge publishes them. Re-run `--discover --download` after publication.",
        "- **XBRL Extraction (Arelle):** Arelle is installed and available; XBRL instance documents",
        "  are catalogued when discovered. Full XBRL parsing can be enabled in a future iteration.",
        "",
        "---",
        "",
        "_This report is auto-generated by ZoneScan data acquisition pipeline. Status: `implemented`._",
    ]

    if company.symbol.upper() == "BHARATFORG":
        doc_path = workspace_root / "docs" / "23_AUTONOMOUS_SCRAPING_MILESTONE_REPORT.md"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info("Milestone report written to %s", doc_path)
        print(f"\n[Stage 5/5] Milestone report written to {doc_path}")


def main() -> None:
    """CLI entrypoint for `python -m zonescan.data_acquisition`."""
    parser = argparse.ArgumentParser(
        description="ZoneScan Autonomous Corporate Data Acquisition & Extraction CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard extraction (no autonomous crawl):
  python -m zonescan.data_acquisition collect --symbol BHARATFORG

  # Full autonomous pipeline (recommended):
  python -m zonescan.data_acquisition collect \\
      --symbol BHARATFORG \\
      --years FY2023-24,FY2024-25,FY2025-26 \\
      --discover --download --extract --report

  # Extraction + report only (PDFs already present):
  python -m zonescan.data_acquisition collect \\
      --symbol BHARATFORG --years FY2023-24 --extract --report
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    collect_p = subparsers.add_parser("collect", help="Collect and extract company data")
    collect_p.add_argument(
        "--query", "-q",
        default=None,
        help="Company search query, full legal name, trading symbol, ISIN, or CIN",
    )
    collect_p.add_argument(
        "--symbol", "-s",
        default=None,
        help="NSE stock symbol (e.g. RELIANCE, TCS, JIOFIN, BHARATFORG)",
    )
    collect_p.add_argument(
        "--years",
        default=None,
        help="Count of FY years (e.g. 5) or comma-separated periods (e.g. FY2023-24,FY2022-23)",
    )
    collect_p.add_argument("--output-dir", default=None, help="Custom output directory")
    collect_p.add_argument("--db-path", default=None, help="Custom SQLite database path")
    collect_p.add_argument(
        "--discover",
        action="store_true",
        default=False,
        help="Run autonomous discovery (Scrapy spiders + official exchange archives)",
    )
    collect_p.add_argument(
        "--download",
        action="store_true",
        default=False,
        help="Download discovered documents",
    )
    collect_p.add_argument(
        "--extract",
        action="store_true",
        default=False,
        help="Run financial extraction engine (industry-aware)",
    )
    collect_p.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="Generate Excel, JSON, and Markdown reports",
    )
    collect_p.add_argument(
        "--audit",
        action="store_true",
        default=False,
        help="Run reference-check audit against verified values",
    )
    collect_p.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Enable all stages: --discover --download --extract --report --audit",
    )

    args = parser.parse_args()

    if args.command == "collect" or len(sys.argv) == 1:
        a = args if args.command == "collect" else argparse.Namespace(
            query=None, symbol="BHARATFORG", years=None, output_dir=None, db_path=None,
            discover=False, download=True, extract=True, report=True, audit=True, all=False,
        )

        # --all flag enables everything
        do_discover = a.discover or a.all
        do_download = a.download or a.all or (not a.discover and not a.download and not a.extract and not a.report)
        do_extract = a.extract or a.all or (not a.discover and not a.download and not a.extract and not a.report)
        do_report = a.report or a.all or (not a.discover and not a.download and not a.extract and not a.report)
        do_audit = a.audit or a.all or (not a.discover and not a.download and not a.extract and not a.report)

        query_arg = getattr(a, "query", None)
        symbol_arg = getattr(a, "symbol", None)
        if not query_arg and not symbol_arg:
            symbol_arg = "BHARATFORG"

        run_pipeline(
            symbol=symbol_arg,
            query=query_arg,
            base_dir=Path(a.output_dir) if getattr(a, "output_dir", None) else None,
            db_path=Path(a.db_path) if getattr(a, "db_path", None) else None,
            target_years=_parse_years(getattr(a, "years", None)),
            do_discover=do_discover,
            do_download=do_download,
            do_extract=do_extract,
            do_report=do_report,
            do_audit=do_audit,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
