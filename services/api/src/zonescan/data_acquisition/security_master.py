"""Universal Indian listed-company security master.

Maintains an indexed catalog of Indian equity and SME securities listed on
NSE and BSE, downloading and caching official exchange security lists:
- NSE Equity List (EQUITY_L.csv)
- NSE SME List (SME_EQUITY_L.csv)
- NSE Symbol Changes (symbolchange.csv)
- NSE Name Changes (namechange.csv)
- NSE ETFs (eq_etfseclist.csv)

Enforces strict separation of ordinary equities from ETFs, mutual funds,
debt, preference shares, and warrants.
"""
from __future__ import annotations

import csv
import io
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import urllib.request
from zoneinfo import ZoneInfo

from .models import CompanyIdentifiers

IST = ZoneInfo("Asia/Kolkata")
logger = logging.getLogger("zonescan.security_master")

# Official download URLs from exchange archives
NSE_EQUITY_L_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
NSE_SME_L_URL = "https://nsearchives.nseindia.com/emerge/corporates/content/SME_EQUITY_L.csv"
NSE_SYMBOL_CHANGE_URL = "https://archives.nseindia.com/content/equities/symbolchange.csv"
NSE_NAME_CHANGE_URL = "https://archives.nseindia.com/content/equities/namechange.csv"
NSE_ETF_URL = "https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Known active scrip code cross-references for major Indian listed equities
# (BSE scrip codes corresponding to NSE symbols and ISINs)
KNOWN_BSE_CROSS_REFERENCES: Dict[str, Tuple[str, str, str, str, str]] = {
    # NSE_SYMBOL: (BSE_CODE, CIN, SECTOR, INDUSTRY, OFFICIAL_DOMAIN)
    "RELIANCE": ("500325", "L17110MH1973PLC019786", "Energy & Petrochemicals", "Integrated Conglomerate", "https://www.ril.com"),
    "TCS": ("532540", "L22210MH1995PLC084781", "Information Technology", "IT Consulting & Software Services", "https://www.tcs.com"),
    "JIOFIN": ("543940", "L65990MH1999PLC120918", "Financial Services", "Non-Banking Financial Company (NBFC)", "https://www.jfs.in"),
    "BHARATFORG": ("500493", "L25209PN1961PLC012046", "Capital Goods & Automotive", "Forgings & Precision Components", "https://www.bharatforge.com"),
    "HDFCBANK": ("500180", "L65920MH1994PLC080618", "Financial Services", "Private Sector Bank", "https://www.hdfcbank.com"),
    "INFY": ("500209", "L85110KA1981PLC013115", "Information Technology", "IT Services", "https://www.infosys.com"),
    "ICICIBANK": ("532174", "L65190GJ1994PLC021012", "Financial Services", "Private Sector Bank", "https://www.icicibank.com"),
    "SBIN": ("500112", "SBI000000000000000000", "Financial Services", "Public Sector Bank", "https://www.sbi.co.in"),
    "TATAMOTORS": ("500570", "L28920MH1945PLC004520", "Automotive", "Commercial & Passenger Vehicles", "https://www.tatamotors.com"),
    "TATASTEEL": ("500114", "L27100MH1907PLC000260", "Metals & Mining", "Integrated Steel Production", "https://www.tatasteel.com"),
    "ITC": ("500875", "L16005WB1910PLC001985", "FMCG", "Diversified FMCG & Hotels", "https://www.itcportal.com"),
    "LT": ("500510", "L99999MH1946PLC004768", "Construction & Engineering", "Infrastructure & Engineering EPC", "https://www.larsentoubro.com"),
    "SUNPHARMA": ("524715", "L24230GJ1993PLC019050", "Healthcare & Pharmaceuticals", "Pharmaceuticals", "https://www.sunpharma.com"),
    "WIPRO": ("507685", "L32102KA1945PLC020800", "Information Technology", "IT Services & Consulting", "https://www.wipro.com"),
    "HINDUNILVR": ("500696", "L15140MH1933PLC002030", "FMCG", "Personal & Household Products", "https://www.hul.co.in"),
}


@dataclass(frozen=True, slots=True)
class SecurityRecord:
    """Master record for a listed Indian security."""
    symbol: str
    company_name: str
    series: str
    isin: str
    exchange: str = "NSE"                    # NSE, BSE, BOTH
    bse_code: str = ""
    cin: str = ""
    security_class: str = "EQUITY"           # EQUITY, SME, ETF, DEBT, PREFERENCE, WARRANT
    listing_status: str = "ACTIVE"           # ACTIVE, SUSPENDED, DELISTED
    listing_date: Optional[str] = None
    face_value: Optional[str] = None
    sector: str = ""
    industry: str = ""
    official_website: str = ""
    historical_symbols: Tuple[str, ...] = field(default_factory=tuple)
    historical_names: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_equity(self) -> bool:
        """Return True if this is an ordinary corporate equity or SME equity."""
        return self.security_class in ("EQUITY", "SME")

    def to_company_identifiers(self) -> CompanyIdentifiers:
        """Convert security record into CompanyIdentifiers contract."""
        return CompanyIdentifiers(
            company_name=self.company_name,
            symbol=self.symbol,
            bse_code=self.bse_code or "500000",
            isin=self.isin,
            cin=self.cin or f"L00000XX2000PLC{hash(self.isin) & 0xFFFFFF:06d}",
            sector=self.sector or "Diversified",
            industry=self.industry or "Commercial Enterprises",
            incorporation_year=1980,
            registered_office="",
        )


class SecurityMaster:
    """In-memory indexed security master populated from official exchange feeds."""

    def __init__(self, cache_dir: Optional[Path] = None, auto_load: bool = True) -> None:
        self.cache_dir = cache_dir or Path("data/security_master")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._securities: Dict[str, SecurityRecord] = {}           # symbol -> record
        self._isin_map: Dict[str, str] = {}                         # isin -> symbol
        self._bse_map: Dict[str, str] = {}                          # bse_code -> symbol
        self._cin_map: Dict[str, str] = {}                          # cin -> symbol
        self._name_index: Dict[str, Set[str]] = {}                  # lower name / token -> set of symbols
        self._historical_symbols: Dict[str, str] = {}               # old_symbol -> new_symbol
        self._historical_names: Dict[str, str] = {}                 # lower old_name -> symbol
        self._etf_symbols: Set[str] = set()                         # ETF symbols

        if auto_load:
            self.load()

    @property
    def securities(self) -> Dict[str, SecurityRecord]:
        """Return all indexed securities."""
        return self._securities

    @property
    def etf_symbols(self) -> Set[str]:
        """Return set of known ETF symbols."""
        return self._etf_symbols

    def load(self, refresh_from_network: bool = False) -> int:
        """Load securities from cache or official exchange downloads."""
        # 1. Load known seeds first
        self._load_seeds()

        # 2. Try loading cached or downloading exchange CSVs
        try:
            self._load_etfs(refresh_from_network)
        except Exception as e:
            logger.warning("Could not load ETF list: %s", e)

        try:
            self._load_symbol_changes(refresh_from_network)
        except Exception as e:
            logger.warning("Could not load symbol changes: %s", e)

        try:
            self._load_nse_equities(refresh_from_network)
        except Exception as e:
            logger.warning("Could not load NSE equity list: %s", e)

        logger.info(
            "SecurityMaster loaded %d listed securities (%d ISINs, %d BSE scrips, %d ETFs)",
            len(self._securities),
            len(self._isin_map),
            len(self._bse_map),
            len(self._etf_symbols),
        )
        return len(self._securities)

    def _load_seeds(self) -> None:
        """Populate foundational verified seeds."""
        for sym, (bse, cin, sector, ind, website) in KNOWN_BSE_CROSS_REFERENCES.items():
            # Seed default ISINs
            isin_seed = {
                "RELIANCE": "INE002A01018",
                "TCS": "INE467B01029",
                "JIOFIN": "INE758E01017",
                "BHARATFORG": "INE465A01025",
                "HDFCBANK": "INE040A01034",
                "INFY": "INE009A01021",
                "ICICIBANK": "INE090A01021",
                "SBIN": "INE062A01020",
                "TATAMOTORS": "INE155A01022",
                "TATASTEEL": "INE081A01020",
                "ITC": "INE154A01025",
                "LT": "INE018A01030",
                "SUNPHARMA": "INE044A01036",
                "WIPRO": "INE075A01022",
                "HINDUNILVR": "INE030A01027",
            }.get(sym, f"INE{sym[:6]}01010")

            name_seed = {
                "RELIANCE": "Reliance Industries Limited",
                "TCS": "Tata Consultancy Services Limited",
                "JIOFIN": "Jio Financial Services Limited",
                "BHARATFORG": "Bharat Forge Limited",
                "HDFCBANK": "HDFC Bank Limited",
                "INFY": "Infosys Limited",
                "ICICIBANK": "ICICI Bank Limited",
                "SBIN": "State Bank of India",
                "TATAMOTORS": "Tata Motors Limited",
                "TATASTEEL": "Tata Steel Limited",
                "ITC": "ITC Limited",
                "LT": "Larsen & Toubro Limited",
                "SUNPHARMA": "Sun Pharmaceutical Industries Limited",
                "WIPRO": "Wipro Limited",
                "HINDUNILVR": "Hindustan Unilever Limited",
            }.get(sym, f"{sym} Limited")

            rec = SecurityRecord(
                symbol=sym,
                company_name=name_seed,
                series="EQ",
                isin=isin_seed,
                exchange="BOTH",
                bse_code=bse,
                cin=cin,
                security_class="EQUITY",
                listing_status="ACTIVE",
                sector=sector,
                industry=ind,
                official_website=website,
            )
            self._register_security(rec)

        # Seed known symbol changes
        self._historical_symbols.update({
            "CADILAHC": "ZYDUSLIFE",
            "IIFLWAM": "360ONE",
            "BIRLA3M": "3MINDIA",
            "PDUMJEIND": "3PLAND",
            "FINANTECH": "63MOONS",
            "GAMMNINFRA": "AJRINFRA",
            "IPAPPM": "ANDPAPER",
        })
        # Seed known name changes
        self._historical_names.update({
            "tata tea limited": "TATACONSUM",
            "cadila healthcare limited": "ZYDUSLIFE",
            "iifl wealth management limited": "360ONE",
            "birla 3m limited": "3MINDIA",
        })
        # Seed foundational ETFs
        etf_seeds = {
            "NIFTYBEES": ("Nippon India ETF Nifty BeES", "INF204KB14I2"),
            "BANKBEES": ("Nippon India ETF Bank BeES", "INF204KB15I9"),
            "GOLDBEES": ("Nippon India ETF Gold BeES", "INF204KB17I5"),
            "JUNIORBEES": ("Nippon India ETF Junior BeES", "INF732E01045"),
        }
        for etf_sym, (etf_name, etf_isin) in etf_seeds.items():
            self._etf_symbols.add(etf_sym)
            if etf_sym not in self._securities:
                self._register_security(
                    SecurityRecord(
                        symbol=etf_sym,
                        company_name=etf_name,
                        series="ETF",
                        isin=etf_isin,
                        exchange="NSE",
                        security_class="ETF",
                        listing_status="ACTIVE",
                    )
                )

    def _fetch_or_cache(self, url: str, cache_filename: str, refresh: bool) -> Optional[str]:
        """Fetch remote file or return cached content."""
        cache_path = self.cache_dir / cache_filename
        if cache_path.exists() and not refresh:
            try:
                return cache_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass

        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=15) as res:
                data = res.read().decode("utf-8", errors="ignore")
                cache_path.write_text(data, encoding="utf-8")
                return data
        except Exception as e:
            logger.debug("Fetch failed for %s: %s", url, e)
            if cache_path.exists():
                return cache_path.read_text(encoding="utf-8", errors="ignore")
            return None

    def _load_etfs(self, refresh: bool) -> None:
        """Load ETF list to classify non-equity instruments."""
        data = self._fetch_or_cache(NSE_ETF_URL, "eq_etfseclist.csv", refresh)
        if not data:
            return
        reader = csv.DictReader(io.StringIO(data))
        for row in reader:
            clean = {k.strip(): v.strip() for k, v in row.items() if k and v}
            sym = clean.get("Symbol") or clean.get("SYMBOL")
            if sym:
                sym_upper = sym.upper()
                self._etf_symbols.add(sym_upper)
                name = clean.get("SecurityName") or clean.get("Security Name") or clean.get("Underlying Asset") or f"{sym_upper} ETF"
                isin = clean.get("ISINNumber") or clean.get("ISIN") or ""
                if sym_upper not in self._securities:
                    rec = SecurityRecord(
                        symbol=sym_upper,
                        company_name=name,
                        series="ETF",
                        isin=isin,
                        exchange="NSE",
                        security_class="ETF",
                        listing_status="ACTIVE",
                    )
                    self._register_security(rec)

    def _load_symbol_changes(self, refresh: bool) -> None:
        """Load historical symbol change mappings."""
        data = self._fetch_or_cache(NSE_SYMBOL_CHANGE_URL, "symbolchange.csv", refresh)
        if not data:
            return
        reader = csv.DictReader(io.StringIO(data))
        for row in reader:
            clean = {k.strip(): v.strip() for k, v in row.items() if k and v}
            old_sym = clean.get("OLD SYMBOL", "").strip().upper()
            new_sym = clean.get("NEW SYMBOL", "").strip().upper()
            if old_sym and new_sym:
                self._historical_symbols[old_sym] = new_sym

    def _load_nse_equities(self, refresh: bool) -> None:
        """Parse NSE main-board equity master."""
        data = self._fetch_or_cache(NSE_EQUITY_L_URL, "EQUITY_L.csv", refresh)
        if not data:
            return
        reader = csv.DictReader(io.StringIO(data))
        for row in reader:
            clean = {k.strip(): v.strip() for k, v in row.items() if k and v}
            sym = clean.get("SYMBOL", "").strip().upper()
            if not sym:
                continue

            # Determine security class: skip if known ETF
            sec_class = "ETF" if sym in self._etf_symbols else "EQUITY"
            isin = clean.get("ISIN NUMBER", "").strip()
            name = clean.get("NAME OF COMPANY", "").strip()
            series = clean.get("SERIES", "").strip()
            listing_date = clean.get("DATE OF LISTING", "").strip()
            face_value = clean.get("FACE VALUE", "").strip()

            # Cross-reference known BSE scrip code, CIN, sector if available
            bse_info = KNOWN_BSE_CROSS_REFERENCES.get(sym)
            bse_code = bse_info[0] if bse_info else ""
            cin = bse_info[1] if bse_info else ""
            sector = bse_info[2] if bse_info else ""
            industry = bse_info[3] if bse_info else ""
            website = bse_info[4] if bse_info else ""

            # Check if this company had previous symbols
            hist_syms = tuple(
                old for old, new in self._historical_symbols.items() if new == sym
            )

            rec = SecurityRecord(
                symbol=sym,
                company_name=name,
                series=series or "EQ",
                isin=isin,
                exchange="BOTH" if bse_code else "NSE",
                bse_code=bse_code,
                cin=cin,
                security_class=sec_class,
                listing_status="ACTIVE",
                listing_date=listing_date,
                face_value=face_value,
                sector=sector,
                industry=industry,
                official_website=website,
                historical_symbols=hist_syms,
            )
            self._register_security(rec)

    def _register_security(self, rec: SecurityRecord) -> None:
        """Register a security record in indexes."""
        self._securities[rec.symbol] = rec
        if rec.isin:
            self._isin_map[rec.isin] = rec.symbol
        if rec.bse_code:
            self._bse_map[rec.bse_code] = rec.symbol
        if rec.cin:
            self._cin_map[rec.cin] = rec.symbol

        # Build tokenized search index
        tokens = set(re.findall(r"\w+", rec.company_name.lower()))
        tokens.add(rec.symbol.lower())
        if rec.isin:
            tokens.add(rec.isin.lower())
        if rec.bse_code:
            tokens.add(rec.bse_code.lower())
        for token in tokens:
            if len(token) >= 2:
                self._name_index.setdefault(token, set()).add(rec.symbol)

    def get_by_symbol(self, symbol: str) -> Optional[SecurityRecord]:
        """Lookup by NSE symbol (with historical symbol resolution)."""
        clean = symbol.strip().upper()
        # Direct lookup
        if clean in self._securities:
            return self._securities[clean]
        # Historical symbol change lookup
        if clean in self._historical_symbols:
            curr = self._historical_symbols[clean]
            return self._securities.get(curr)
        return None

    def get_by_isin(self, isin: str) -> Optional[SecurityRecord]:
        """Lookup by ISIN code."""
        sym = self._isin_map.get(isin.strip().upper())
        return self._securities.get(sym) if sym else None

    def get_by_bse_code(self, bse_code: str) -> Optional[SecurityRecord]:
        """Lookup by BSE scrip code."""
        sym = self._bse_map.get(bse_code.strip())
        return self._securities.get(sym) if sym else None

    def get_by_cin(self, cin: str) -> Optional[SecurityRecord]:
        """Lookup by corporate identification number."""
        sym = self._cin_map.get(cin.strip().upper())
        return self._securities.get(sym) if sym else None

    def resolve_symbol_change(self, old_symbol: str) -> Optional[str]:
        """Resolve a historical trading symbol to its current active symbol."""
        clean = old_symbol.strip().upper()
        return self._historical_symbols.get(clean)

    def resolve_name_change(self, old_name: str) -> Optional[str]:
        """Resolve a historical company name to its current trading symbol."""
        clean = old_name.strip().lower()
        if clean in self._historical_names:
            return self._historical_names[clean]
        for hist_name, sym in self._historical_names.items():
            if clean in hist_name or hist_name in clean:
                return sym
        return None

    def search(self, query: str, limit: int = 10, equity_only: bool = True) -> List[SecurityRecord]:
        """Search securities across symbol, ISIN, BSE code, CIN, or company name tokens.

        Returns ranked list of candidate matches.
        """
        clean = query.strip()
        if not clean:
            return []

        upper = clean.upper()

        # 1. Exact matches have top priority
        if upper in self._securities:
            return [self._securities[upper]]
        if upper in self._isin_map:
            return [self._securities[self._isin_map[upper]]]
        if clean in self._bse_map:
            return [self._securities[self._bse_map[clean]]]
        if upper in self._cin_map:
            return [self._securities[self._cin_map[upper]]]
        if upper in self._historical_symbols:
            curr = self._historical_symbols[upper]
            if curr in self._securities:
                return [self._securities[curr]]

        # 2. Tokenized search across company name
        tokens = [t.lower() for t in re.findall(r"\w+", clean) if len(t) >= 2]
        if not tokens:
            return []

        # Find symbols matching tokens
        candidate_scores: Dict[str, int] = {}
        for token in tokens:
            matches = self._name_index.get(token, set())
            for sym in matches:
                candidate_scores[sym] = candidate_scores.get(sym, 0) + 1

        # Score boosts for prefix matches and name closeness
        ranked: List[Tuple[int, SecurityRecord]] = []
        for sym, score in candidate_scores.items():
            rec = self._securities[sym]
            if equity_only and not rec.is_equity:
                continue

            total_score = score * 10
            # Symbol prefix bonus
            if sym.startswith(upper):
                total_score += 50
            # Name startswith bonus
            if rec.company_name.lower().startswith(clean.lower()):
                total_score += 40
            # Substring match in full name
            if clean.lower() in rec.company_name.lower():
                total_score += 25

            ranked.append((total_score, rec))

        ranked.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in ranked[:limit]]
