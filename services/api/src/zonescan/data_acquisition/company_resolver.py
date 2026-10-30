"""Deterministic multi-identifier Company Resolver with Ambiguity Handling.

Resolves listed company identities across NSE symbol, BSE code, ISIN, CIN,
legal name, and common name. Detects ambiguous queries (e.g. 'Jio', 'Tata')
and presents exact matching listed entities and subsidiary relations rather
than silently guessing.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .models import CompanyIdentifiers
from .security_master import SecurityMaster, SecurityRecord

logger = logging.getLogger("zonescan.company_resolver")

# Known corporate group / subsidiary disambiguation mapping
# (Used when a user queries a brand/subsidiary name that belongs to a conglomerate)
KNOWN_DISAMBIGUATIONS: Dict[str, List[Dict[str, str]]] = {
    "jio": [
        {
            "symbol": "JIOFIN",
            "name": "Jio Financial Services Limited",
            "bse_code": "543940",
            "isin": "INE758E01017",
            "entity_type": "Direct Listed Equity (Demerged Financial NBFC)",
            "relation": "Independent listed financial services company",
        },
        {
            "symbol": "RELIANCE",
            "name": "Reliance Industries Limited",
            "bse_code": "500325",
            "isin": "INE002A01018",
            "entity_type": "Listed Parent Conglomerate",
            "relation": "Parent company of Jio Platforms Ltd & Reliance Jio Infocomm Ltd (Unlisted Subsidiaries)",
        },
    ],
    "airtel": [
        {
            "symbol": "BHARTIARTL",
            "name": "Bharti Airtel Limited",
            "bse_code": "532454",
            "isin": "INE397D01024",
            "entity_type": "Direct Listed Equity",
            "relation": "Listed telecom operating parent company",
        },
    ],
}


@dataclass(frozen=True, slots=True)
class CandidateMatch:
    """Disambiguation candidate matching a user query."""
    symbol: str
    company_name: str
    bse_code: str
    isin: str
    exchange: str
    security_class: str
    listing_status: str
    relation_note: str = ""


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Result of company entity resolution."""
    status: str                                  # 'resolved', 'ambiguous', 'not_found', 'non_equity'
    query: str
    company: Optional[CompanyIdentifiers] = None
    security: Optional[SecurityRecord] = None
    candidates: Tuple[CandidateMatch, ...] = field(default_factory=tuple)
    message: str = ""

    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved" and self.company is not None


class CompanyResolver:
    """Resolves company queries across multiple exchange identifiers with strict ambiguity guards."""

    def __init__(self, security_master: Optional[SecurityMaster] = None) -> None:
        self.security_master = security_master or SecurityMaster()

    def resolve(self, query: str) -> ResolutionResult:
        """Resolve a query into a unique listed company, or return ambiguous candidates.

        Supports:
        - Exact NSE symbol (e.g. 'RELIANCE', 'TCS', 'JIOFIN', 'BHARATFORG')
        - BSE scrip code (e.g. '500325', '532540')
        - ISIN code (e.g. 'INE002A01018')
        - CIN (e.g. 'L17110MH1973PLC019786')
        - Exact legal company name
        - Broad company or brand name with ambiguity detection
        """
        clean = query.strip()
        if not clean:
            return ResolutionResult(
                status="not_found",
                query=query,
                message="Empty query provided.",
            )

        upper = clean.upper()

        # 1. Check exact ISIN (12 chars starting with INE or INF)
        if len(upper) == 12 and (upper.startswith("INE") or upper.startswith("INF")):
            sec = self.security_master.get_by_isin(upper)
            if sec:
                return self._build_resolved(sec, query)

        # 2. Check exact CIN (21 chars containing PLC/PTC/GOI/NPL)
        if len(upper) == 21 and any(tag in upper for tag in ("PLC", "PTC", "GOI", "NPL")):
            sec = self.security_master.get_by_cin(upper)
            if sec:
                return self._build_resolved(sec, query)

        # 3. Check exact numeric BSE Scrip Code (5-6 digits)
        if upper.isdigit() and len(upper) in (5, 6):
            sec = self.security_master.get_by_bse_code(upper)
            if sec:
                return self._build_resolved(sec, query)

        # 4. Check exact NSE Symbol
        sec = self.security_master.get_by_symbol(upper)
        if sec:
            if not sec.is_equity:
                return ResolutionResult(
                    status="non_equity",
                    query=query,
                    security=sec,
                    message=(
                        f"Symbol '{upper}' resolved to {sec.security_class} ({sec.company_name}), "
                        "not an ordinary listed equity company. Security class handled separately."
                    ),
                )
            return self._build_resolved(sec, query)

        # 5. Check known brand / conglomerate ambiguity overrides (e.g., 'Jio')
        lower_query = clean.lower()
        if lower_query in KNOWN_DISAMBIGUATIONS:
            items = KNOWN_DISAMBIGUATIONS[lower_query]
            candidates = tuple(
                CandidateMatch(
                    symbol=item["symbol"],
                    company_name=item["name"],
                    bse_code=item["bse_code"],
                    isin=item["isin"],
                    exchange="NSE/BSE",
                    security_class="EQUITY",
                    listing_status="ACTIVE",
                    relation_note=f"{item['entity_type']}: {item['relation']}",
                )
                for item in items
            )
            return ResolutionResult(
                status="ambiguous",
                query=query,
                candidates=candidates,
                message=(
                    f"Query '{query}' is ambiguous and matches multiple entities across "
                    f"listed parent and demerged/subsidiary units. Please select exact symbol: "
                    + ", ".join(f"{c.symbol} ({c.company_name})" for c in candidates)
                ),
            )

        # 6. Search across security master
        matches = self.security_master.search(clean, limit=10, equity_only=True)
        if not matches:
            return ResolutionResult(
                status="not_found",
                query=query,
                message=f"No listed Indian equity security found matching '{query}'.",
            )

        # If exactly 1 match found, resolve directly
        if len(matches) == 1:
            return self._build_resolved(matches[0], query)

        # If top match is an exact name match (ignoring optional Ltd/Limited suffix), resolve
        def _norm_co_name(n: str) -> str:
            val = n.lower().replace(".", " ").replace(",", " ")
            for sfx in (" limited", " ltd"):
                if val.endswith(sfx):
                    val = val[:-len(sfx)].strip()
            return val.strip()

        exact_matches = [
            m for m in matches
            if _norm_co_name(m.company_name) == _norm_co_name(clean) or m.symbol.lower() == clean.lower()
        ]
        if len(exact_matches) == 1:
            return self._build_resolved(exact_matches[0], query)

        # Multiple matches found -> Ambiguity detected
        candidates = tuple(
            CandidateMatch(
                symbol=m.symbol,
                company_name=m.company_name,
                bse_code=m.bse_code,
                isin=m.isin,
                exchange=m.exchange,
                security_class=m.security_class,
                listing_status=m.listing_status,
                relation_note=f"Sector: {m.sector or 'Diversified'}",
            )
            for m in matches[:5]
        )
        return ResolutionResult(
            status="ambiguous",
            query=query,
            candidates=candidates,
            message=(
                f"Query '{query}' is ambiguous and matches {len(matches)} listed equity companies. "
                "Please specify the exact trading symbol: "
                + ", ".join(f"{c.symbol} ({c.company_name})" for c in candidates)
            ),
        )

    def _build_resolved(self, sec: SecurityRecord, query: str) -> ResolutionResult:
        """Construct a resolved ResolutionResult from a SecurityRecord."""
        identifiers = sec.to_company_identifiers()
        return ResolutionResult(
            status="resolved",
            query=query,
            company=identifiers,
            security=sec,
            message=f"Resolved '{query}' to {sec.company_name} ({sec.symbol}) | ISIN: {sec.isin}",
        )
