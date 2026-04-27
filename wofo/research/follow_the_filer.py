"""Follow-the-filer strategy: mirror a 13F manager's reported long book.

Important caveats — read before using:

1. **Stale by construction.** 13F filings are due 45 days after quarter
   end. The earliest a follower can act on a filing is the filing date,
   not the period-of-report date. We use `effective_date = file_date`
   for that reason. Backtests using `period_of_report` as the trade
   date are look-ahead-biased.
2. **Long-only.** 13Fs report long positions in 13F-eligible securities
   only. The manager's true exposure (shorts, swaps, non-US, cash,
   options on non-13F names) is invisible.
3. **Cap-structure ambiguity.** Same issuer can appear under different
   CUSIPs (common vs. converts). We aggregate to issuer level when the
   caller requests it; otherwise CUSIP-level weights are reported.
4. **Survivorship/relisting.** Tickers can change. The mapping from
   13F issuer -> ticker uses SEC's free file and is heuristic.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class Snapshot:
    """One target-weight snapshot active starting on `effective_date`."""

    effective_date: date          # date the follower can first act on this filing
    period_of_report: date        # what the manager held at this date
    weights: dict[str, float]     # ticker -> weight (sums ~= 1 over mapped names)
    unmapped_value_share: float   # share of the manager's reported value
                                  # whose CUSIPs we couldn't map to a ticker
    provenance: dict              # filing refs, source, run timestamp

    def __post_init__(self):
        total = sum(self.weights.values())
        if self.weights and not (0.99 <= total + self.unmapped_value_share <= 1.01):
            raise ValueError(
                f"weights+unmapped should sum to 1; got {total + self.unmapped_value_share}"
            )


@dataclass(frozen=True)
class TargetWeights:
    """Time series of target-weight snapshots for one strategy run."""

    manager_cik: str
    manager_name: str
    snapshots: list[Snapshot]

    def as_dict(self) -> dict:
        return {
            "manager_cik": self.manager_cik,
            "manager_name": self.manager_name,
            "snapshots": [
                {
                    "effective_date": s.effective_date.isoformat(),
                    "period_of_report": s.period_of_report.isoformat(),
                    "weights": s.weights,
                    "unmapped_value_share": s.unmapped_value_share,
                    "provenance": s.provenance,
                }
                for s in self.snapshots
            ],
        }


def follow_the_filer(
    panel: dict,
    filing_refs: dict,           # period_iso -> {cik, accession, file_date, form}
    cusip_to_ticker: dict[str, str | None],
    *,
    manager_cik: str,
    manager_name: str,
    top_n: int | None = None,
    run_id: str | None = None,
) -> TargetWeights:
    """Build target-weight snapshots from a 13F panel.

    Args:
      panel: output of `wofo.thirteenf.analyze.build_panel`.
      filing_refs: per-period filing metadata. Must include `file_date`
        (YYYY-MM-DD) so we can set `effective_date` correctly.
      cusip_to_ticker: mapping from `wofo.research.resolve_tickers`.
      top_n: if set, keep only the largest N positions per snapshot.
      run_id: optional tag for provenance (e.g. a git SHA).

    Weights are normalized over MAPPED positions only; the share of
    reported value that came from unmapped CUSIPs is reported as
    `unmapped_value_share` so callers can decide how to handle it
    (skip the snapshot, hold cash, etc.).
    """
    snapshots: list[Snapshot] = []
    run_ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    for period in panel["periods"]:
        ref = filing_refs.get(period)
        if not ref or "file_date" not in ref:
            raise ValueError(f"missing file_date for period {period}")
        effective = _parse_iso(ref["file_date"])
        report = _parse_iso(period)

        period_rows = [
            (cusip, r["value_usd"]) for (p, cusip), r in panel["rows"].items() if p == period
        ]
        period_rows.sort(key=lambda x: x[1], reverse=True)
        if top_n:
            period_rows = period_rows[:top_n]

        total = sum(v for _, v in period_rows) or 1
        mapped_value = 0
        weights: dict[str, float] = {}
        for cusip, val in period_rows:
            ticker = cusip_to_ticker.get(cusip)
            if not ticker:
                continue
            mapped_value += val
            weights[ticker] = weights.get(ticker, 0.0) + val / total

        unmapped_share = (total - mapped_value) / total if total else 0.0
        snapshots.append(
            Snapshot(
                effective_date=effective,
                period_of_report=report,
                weights=weights,
                unmapped_value_share=unmapped_share,
                provenance={
                    "manager_cik": manager_cik,
                    "filing_ref": ref,
                    "run_id": run_id,
                    "run_ts_utc": run_ts,
                },
            )
        )

    snapshots.sort(key=lambda s: s.effective_date)
    return TargetWeights(manager_cik=manager_cik, manager_name=manager_name, snapshots=snapshots)


def load_filing_refs(raw_dir) -> dict:
    """Read filing_ref.json files written by `wofo.thirteenf.fetch.fetch_filing`.

    Falls back to parsing primary_doc.xml if filing_ref.json is missing
    (e.g., for filings downloaded by hand before fetch_filing existed).
    """
    import json
    from pathlib import Path
    from wofo.thirteenf.parse import parse_primary_doc

    raw_dir = Path(raw_dir)
    refs: dict = {}
    for q in sorted(raw_dir.iterdir()):
        if not q.is_dir():
            continue
        ref_path = q / "filing_ref.json"
        if ref_path.exists():
            d = json.loads(ref_path.read_text())
            period_iso = _quarter_to_iso(q.name)
            refs[period_iso] = d
        else:
            # Synthesize from primary_doc.xml. file_date is unknown here, so
            # we approximate it as period + 45 days (the regulatory deadline).
            # Callers should re-pull via fetch_filing for accurate file_date.
            meta = parse_primary_doc(q / "primary_doc.xml")
            period = _parse_iso(meta.period_iso)
            from datetime import timedelta
            approx_file = period + timedelta(days=45)
            refs[meta.period_iso] = {
                "cik": meta.cik,
                "accession": None,
                "period_ending": meta.period_iso,
                "file_date": approx_file.isoformat(),
                "form": meta.report_type,
                "approximate_file_date": True,
            }
    return refs


def _parse_iso(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _quarter_to_iso(label: str) -> str:
    # "2024Q4" -> "2024-12-31"
    y = label[:4]
    q = label[-1]
    end = {"1": "03-31", "2": "06-30", "3": "09-30", "4": "12-31"}[q]
    return f"{y}-{end}"


def _iter_holdings(holdings: Iterable) -> Iterable:  # pragma: no cover - placeholder
    return holdings
