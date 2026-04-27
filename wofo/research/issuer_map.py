"""Best-effort 13F issuer-name -> ticker mapping.

CUSIP -> ticker is a licensed mapping (CGS) and we will not embed one.
What we can do, for free:

1. Pull SEC's `company_tickers.json` (CIK <-> ticker, public).
2. Normalize 13F `nameOfIssuer` strings and fuzzy-match against company
   names from that file.
3. Allow callers to provide an `IssuerOverride` map for cases where the
   heuristic is wrong or the issuer is a non-CIK security (ADR, ETF,
   foreign listing).

This is intentionally conservative: when in doubt, the function returns
`None` for that issuer rather than guessing. The backtester treats
`None` tickers as "skip".
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.request import Request, urlopen

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


@dataclass
class IssuerOverride:
    """Manual issuer-name (or CUSIP) -> ticker overrides.

    Keys are matched case-insensitively. CUSIP keys take precedence over
    issuer-name keys when both could match.
    """

    by_cusip: dict[str, str] = field(default_factory=dict)
    by_issuer: dict[str, str] = field(default_factory=dict)


_TRIM_TOKENS = re.compile(
    r"\b(CORP|CORPORATION|INC|INCORPORATED|LTD|LIMITED|LLC|PLC|HLDGS?|HOLDINGS?|"
    r"GROUP|CO|COMPANY|CL|CLASS|COM|COMMON|NEW|THE|TR|TRUST|REIT|"
    r"SA|S A|N V|NV|AG|PETE|PETROLEUM)\b",
    re.IGNORECASE,
)
_PUNCT = re.compile(r"[^\w\s]")

# Common 13F abbreviations -> canonical token. Applied after stripping
# corporate suffixes, before lower-casing the result.
_ABBREVIATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bFINL\b", re.I), "FINANCIAL"),
    (re.compile(r"\bMGMT\b", re.I), "MANAGEMENT"),
    (re.compile(r"\bINTL\b", re.I), "INTERNATIONAL"),
    (re.compile(r"\bINDL\b", re.I), "INDUSTRIAL"),
    (re.compile(r"\bMATLS\b", re.I), "MATERIALS"),
    (re.compile(r"\bSVCS?\b", re.I), "SERVICES"),
    (re.compile(r"\bBK\b", re.I), "BANK"),
    (re.compile(r"\bAIRLS\b", re.I), "AIRLINES"),
    (re.compile(r"\bCOMMUN(IC)?\b", re.I), "COMMUNICATIONS"),
    (re.compile(r"\bTRANSP(N)?\b", re.I), "TRANSPORTATION"),
    (re.compile(r"\bRES(O?UR(CES?)?)?\b", re.I), "RESOURCES"),
    (re.compile(r"\bMFG\b", re.I), "MANUFACTURING"),
    (re.compile(r"\bTECHS?\b", re.I), "TECHNOLOGIES"),
    (re.compile(r"\bDEL\b", re.I), ""),
    (re.compile(r"\bMA\b", re.I), ""),
]


def _norm(s: str) -> str:
    s = _PUNCT.sub(" ", s)
    s = _TRIM_TOKENS.sub(" ", s)
    for pat, repl in _ABBREVIATIONS:
        s = pat.sub(repl, s)
    return " ".join(s.lower().split())


def _load_sec_tickers(cache_path: Path | None = None) -> dict:
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text())
    ua = os.environ.get("WOFO_SEC_UA")
    if not ua:
        raise RuntimeError(
            "WOFO_SEC_UA env var required to fetch SEC company_tickers.json"
        )
    req = Request(SEC_TICKERS_URL, headers={"User-Agent": ua})
    with urlopen(req, timeout=30) as resp:
        body = resp.read()
    data = json.loads(body)
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(body)
    return data


def resolve_tickers(
    issuers: dict[str, str],  # cusip -> issuer name
    *,
    overrides: IssuerOverride | None = None,
    sec_tickers_cache: Path | None = None,
) -> tuple[dict[str, str | None], dict[str, str]]:
    """Resolve {cusip: issuer_name} -> ({cusip: ticker_or_None}, {cusip: source}).

    `source` is one of: 'override-cusip', 'override-issuer', 'sec-exact',
    'sec-prefix', 'unmapped'.
    """
    overrides = overrides or IssuerOverride()
    over_cusip = {k.upper(): v for k, v in overrides.by_cusip.items()}
    over_issuer = {_norm(k): v for k, v in overrides.by_issuer.items()}

    sec = _load_sec_tickers(sec_tickers_cache) if (issuers and not all(
        c.upper() in over_cusip or _norm(n) in over_issuer for c, n in issuers.items()
    )) else {}

    sec_index: dict[str, str] = {}
    for entry in sec.values() if isinstance(sec, dict) else []:
        title = entry.get("title", "")
        ticker = entry.get("ticker", "")
        if title and ticker:
            sec_index[_norm(title)] = ticker.upper()

    out: dict[str, str | None] = {}
    src: dict[str, str] = {}
    for cusip, name in issuers.items():
        if cusip.upper() in over_cusip:
            v = over_cusip[cusip.upper()]
            out[cusip] = v.upper() if v else None
            src[cusip] = "override-cusip"
            continue
        n = _norm(name)
        if n in over_issuer:
            v = over_issuer[n]
            out[cusip] = v.upper() if v else None
            src[cusip] = "override-issuer"
            continue
        if n in sec_index:
            out[cusip] = sec_index[n]
            src[cusip] = "sec-exact"
            continue
        # Prefix match: issuer name starts with a known company name (or vice
        # versa). Conservative: require >=2 tokens to avoid false positives.
        candidates = [
            (k, t) for k, t in sec_index.items()
            if (k.startswith(n) or n.startswith(k)) and len(k.split()) >= 2 and len(n.split()) >= 2
        ]
        if len(candidates) == 1:
            out[cusip] = candidates[0][1]
            src[cusip] = "sec-prefix"
            continue
        out[cusip] = None
        src[cusip] = "unmapped"
    return out, src
