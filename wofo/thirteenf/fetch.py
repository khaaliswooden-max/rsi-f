"""Fetch Form 13F-HR filings from SEC EDGAR.

EDGAR requires a descriptive User-Agent identifying the requester. Set
WOFO_SEC_UA in the environment, e.g.

    export WOFO_SEC_UA="Wooden Family Office contact@yourdomain.com"
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

EDGAR_SEARCH = "https://efts.sec.gov/LATEST/search-index"
EDGAR_ARCHIVE = "https://www.sec.gov/Archives/edgar/data"
EDGAR_SUBMISSIONS = "https://data.sec.gov/submissions"

# SEC fair-access guidance: <=10 req/s. We pace conservatively.
_REQUEST_INTERVAL_S = 0.2


def _ua() -> str:
    ua = os.environ.get("WOFO_SEC_UA", "").strip()
    if not ua:
        raise RuntimeError(
            "WOFO_SEC_UA env var is required by SEC EDGAR fair-access policy. "
            "Set it to e.g. 'Wooden Family Office contact@yourdomain.com'."
        )
    return ua


def _get(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": _ua(), "Accept-Encoding": "identity"})
    with urlopen(req, timeout=30) as resp:
        data = resp.read()
    time.sleep(_REQUEST_INTERVAL_S)
    return data


@dataclass(frozen=True)
class FilingRef:
    cik: str          # 10-digit zero-padded
    accession: str    # with dashes, e.g. 0002045724-25-000008
    period_ending: str  # YYYY-MM-DD
    file_date: str    # YYYY-MM-DD
    form: str         # "13F-HR" or "13F-HR/A"

    @property
    def accession_nodash(self) -> str:
        return self.accession.replace("-", "")

    @property
    def archive_dir(self) -> str:
        cik_int = int(self.cik)
        return f"{EDGAR_ARCHIVE}/{cik_int}/{self.accession_nodash}"


def list_filings(cik: str, forms: Iterable[str] = ("13F-HR", "13F-HR/A")) -> list[FilingRef]:
    """Return all 13F filings for a CIK, newest first.

    Uses the canonical `data.sec.gov/submissions/CIK{...}.json` index.
    The EFTS search endpoint is rate-limited and sometimes truncates
    results, so we avoid it here.
    """
    cik10 = cik.zfill(10)
    url = f"{EDGAR_SUBMISSIONS}/CIK{cik10}.json"
    payload = json.loads(_get(url))
    forms_set = set(forms)
    out: list[FilingRef] = []
    recent = payload.get("filings", {}).get("recent", {}) or {}
    forms_arr = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    fdates = recent.get("filingDate", [])
    pdates = recent.get("reportDate", [])
    for i, form in enumerate(forms_arr):
        if form not in forms_set:
            continue
        out.append(
            FilingRef(
                cik=cik10,
                accession=accs[i],
                period_ending=pdates[i],
                file_date=fdates[i],
                form=form,
            )
        )
    # Older filings live in a separate paginated structure under "files".
    for f in payload.get("filings", {}).get("files", []) or []:
        more_url = f"{EDGAR_SUBMISSIONS}/{f['name']}"
        try:
            more = json.loads(_get(more_url))
        except Exception:
            continue
        forms_arr = more.get("form", [])
        accs = more.get("accessionNumber", [])
        fdates = more.get("filingDate", [])
        pdates = more.get("reportDate", [])
        for i, form in enumerate(forms_arr):
            if form not in forms_set:
                continue
            out.append(
                FilingRef(
                    cik=cik10,
                    accession=accs[i],
                    period_ending=pdates[i],
                    file_date=fdates[i],
                    form=form,
                )
            )
    out.sort(key=lambda f: f.period_ending, reverse=True)
    return out


_INFOTABLE_RX = re.compile(r'href="([^"]+\.xml)"', re.IGNORECASE)


def _filing_files(ref: FilingRef) -> list[str]:
    html = _get(ref.archive_dir + "/").decode("utf-8", errors="replace")
    files: list[str] = []
    for m in _INFOTABLE_RX.finditer(html):
        href = m.group(1)
        # Only files inside this filing's archive dir, no Financial Report attachments.
        if ref.accession_nodash in href:
            files.append(href.rsplit("/", 1)[-1])
    return sorted(set(files))


def fetch_filing(ref: FilingRef, dest_root: Path) -> Path:
    """Download primary_doc.xml + infotable XML for one filing.

    Returns the directory where the files were written.
    """
    period = _quarter_label(ref.period_ending)
    out = Path(dest_root) / period
    out.mkdir(parents=True, exist_ok=True)

    files = _filing_files(ref)
    primary = next((f for f in files if f.lower() == "primary_doc.xml"), None)
    if primary is None:
        raise RuntimeError(f"primary_doc.xml not found in {ref.archive_dir}")

    # Information table is the other XML file. EDGAR allows arbitrary names
    # (infotable.xml, SALP13fq1.xml, etc.) so we pick the largest non-primary.
    infotables = [f for f in files if f != primary]
    if not infotables:
        raise RuntimeError(f"no information table XML found in {ref.archive_dir}")

    info_name = max(infotables, key=lambda f: len(f))  # weak heuristic; usually only 1
    (out / "primary_doc.xml").write_bytes(_get(f"{ref.archive_dir}/{primary}"))
    (out / "infotable.xml").write_bytes(_get(f"{ref.archive_dir}/{info_name}"))
    (out / "filing_ref.json").write_text(
        json.dumps(
            {
                "cik": ref.cik,
                "accession": ref.accession,
                "period_ending": ref.period_ending,
                "file_date": ref.file_date,
                "form": ref.form,
                "source_infotable_filename": info_name,
            },
            indent=2,
        )
    )
    return out


def _quarter_label(period_ending: str) -> str:
    y, m, _ = period_ending.split("-")
    q = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}[m]
    return f"{y}{q}"
