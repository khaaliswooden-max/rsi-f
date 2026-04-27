"""Parse 13F-HR XML into normalized rows.

Schema reference:
  https://www.sec.gov/files/edgar/13f-document.xsd
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

NS_INFO = "{http://www.sec.gov/edgar/document/thirteenf/informationtable}"
NS_FILER = "{http://www.sec.gov/edgar/thirteenffiler}"
NS_COMMON = "{http://www.sec.gov/edgar/common}"


@dataclass(frozen=True)
class Holding:
    name_of_issuer: str
    title_of_class: str
    cusip: str
    value_usd: int          # 13F values are in whole USD as of 2023+
    shares_or_principal: int
    sh_or_prn: str          # "SH" or "PRN"
    put_call: str | None    # "Put", "Call", or None
    investment_discretion: str
    other_managers: str
    voting_sole: int
    voting_shared: int
    voting_none: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FilingMeta:
    cik: str
    manager_name: str
    period_of_report: str   # MM-DD-YYYY as written in the filing
    period_iso: str         # YYYY-MM-DD
    report_type: str
    form_13f_file_number: str
    crd_number: str | None
    sec_file_number: str | None
    is_amendment: bool
    other_included_managers_count: int
    table_entry_total: int
    table_value_total: int  # whole USD


def _text(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def _int(node: ET.Element | None) -> int:
    t = _text(node)
    return int(t) if t else 0


def parse_infotable(path: str | Path) -> list[Holding]:
    tree = ET.parse(path)
    root = tree.getroot()
    rows: list[Holding] = []
    for it in root.findall(f"{NS_INFO}infoTable"):
        shrs_node = it.find(f"{NS_INFO}shrsOrPrnAmt")
        voting = it.find(f"{NS_INFO}votingAuthority")
        rows.append(
            Holding(
                name_of_issuer=_text(it.find(f"{NS_INFO}nameOfIssuer")),
                title_of_class=_text(it.find(f"{NS_INFO}titleOfClass")),
                cusip=_text(it.find(f"{NS_INFO}cusip")),
                value_usd=_int(it.find(f"{NS_INFO}value")),
                shares_or_principal=_int(shrs_node.find(f"{NS_INFO}sshPrnamt")) if shrs_node is not None else 0,
                sh_or_prn=_text(shrs_node.find(f"{NS_INFO}sshPrnamtType")) if shrs_node is not None else "",
                put_call=_text(it.find(f"{NS_INFO}putCall")) or None,
                investment_discretion=_text(it.find(f"{NS_INFO}investmentDiscretion")),
                other_managers=_text(it.find(f"{NS_INFO}otherManager")),
                voting_sole=_int(voting.find(f"{NS_INFO}Sole")) if voting is not None else 0,
                voting_shared=_int(voting.find(f"{NS_INFO}Shared")) if voting is not None else 0,
                voting_none=_int(voting.find(f"{NS_INFO}None")) if voting is not None else 0,
            )
        )
    return rows


def parse_primary_doc(path: str | Path) -> FilingMeta:
    tree = ET.parse(path)
    root = tree.getroot()

    header = root.find(f"{NS_FILER}headerData")
    filer_info = header.find(f"{NS_FILER}filerInfo") if header is not None else None
    creds = filer_info.find(f"{NS_FILER}filer/{NS_FILER}credentials") if filer_info is not None else None
    cik = _text(creds.find(f"{NS_FILER}cik")) if creds is not None else ""
    period = _text(filer_info.find(f"{NS_FILER}periodOfReport")) if filer_info is not None else ""

    form = root.find(f"{NS_FILER}formData")
    cover = form.find(f"{NS_FILER}coverPage") if form is not None else None
    summary = form.find(f"{NS_FILER}summaryPage") if form is not None else None

    manager_name = ""
    report_type = ""
    file_no = ""
    crd = None
    sec_file = None
    is_amend = False
    if cover is not None:
        fm = cover.find(f"{NS_FILER}filingManager")
        if fm is not None:
            manager_name = _text(fm.find(f"{NS_FILER}name"))
        report_type = _text(cover.find(f"{NS_FILER}reportType"))
        file_no = _text(cover.find(f"{NS_FILER}form13FFileNumber"))
        crd = _text(cover.find(f"{NS_FILER}crdNumber")) or None
        sec_file = _text(cover.find(f"{NS_FILER}secFileNumber")) or None
        is_amend = _text(cover.find(f"{NS_FILER}isAmendment")).lower() == "true"

    other_mgrs = 0
    table_entry_total = 0
    table_value_total = 0
    if summary is not None:
        other_mgrs = _int(summary.find(f"{NS_FILER}otherIncludedManagersCount"))
        table_entry_total = _int(summary.find(f"{NS_FILER}tableEntryTotal"))
        table_value_total = _int(summary.find(f"{NS_FILER}tableValueTotal"))

    return FilingMeta(
        cik=cik,
        manager_name=manager_name,
        period_of_report=period,
        period_iso=_period_to_iso(period),
        report_type=report_type,
        form_13f_file_number=file_no,
        crd_number=crd,
        sec_file_number=sec_file,
        is_amendment=is_amend,
        other_included_managers_count=other_mgrs,
        table_entry_total=table_entry_total,
        table_value_total=table_value_total,
    )


def _period_to_iso(period: str) -> str:
    """Convert 'MM-DD-YYYY' to 'YYYY-MM-DD'. Returns '' if unparseable."""
    parts = period.split("-")
    if len(parts) != 3:
        return ""
    m, d, y = parts
    return f"{y}-{m}-{d}"
