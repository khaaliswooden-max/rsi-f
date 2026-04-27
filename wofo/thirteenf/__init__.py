"""13F-HR fetch / parse / analyze pipeline.

Pulls Form 13F-HR filings directly from SEC EDGAR by CIK, parses the
informationTable XML into normalized rows, and produces quarter-over-quarter
analysis (entries, exits, adds, trims, concentration).

Default target: Situational Awareness LP (CIK 0002045724).
"""
from .fetch import list_filings, fetch_filing, FilingRef
from .parse import parse_infotable, parse_primary_doc, Holding, FilingMeta
from .analyze import build_panel, qoq_changes, concentration

__all__ = [
    "list_filings",
    "fetch_filing",
    "FilingRef",
    "parse_infotable",
    "parse_primary_doc",
    "Holding",
    "FilingMeta",
    "build_panel",
    "qoq_changes",
    "concentration",
]
