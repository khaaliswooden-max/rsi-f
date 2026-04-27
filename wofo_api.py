"""Read-only HTTP surface for wofo research artifacts.

Exposes the on-disk JSON/Markdown reports produced by `wofo.agent.multi_filer_n`,
the RSI self-improvement loop, and the eval suite so the Next.js front-end can
render them without reaching into the wofo Python package at request time.

Wofo itself stays headless and CLI-driven (Phase-1 governance constraint); this
module only serves what wofo has already written to disk.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException


REPO = Path(__file__).resolve().parent
WOFO_DATA = REPO / "wofo" / "data"
F13_DIR = WOFO_DATA / "13f"
PROCESSED_DIR = F13_DIR / "processed"
RSI_RUNS_DIR = WOFO_DATA / "rsi" / "runs"
EVAL_RUNS_DIR = WOFO_DATA / "evals" / "runs"

# N=12 roster mirrored from wofo.agent.multi_filer_n.ROSTER. Hardcoded here so
# this module never has to import the full wofo agent stack at request time.
@dataclass(frozen=True)
class FilerRef:
    slug: str
    cik: str
    name: str

    @property
    def raw_dir(self) -> Path:
        # The "salp" filer historically stored its raw filings at 13f/raw, while
        # every other filer lives at 13f/<slug>/raw.
        if self.slug == "salp":
            return F13_DIR / "raw"
        return F13_DIR / self.slug / "raw"


ROSTER: tuple[FilerRef, ...] = (
    FilerRef("salp",       "0002045724", "Situational Awareness LP"),
    FilerRef("scion",      "0001649339", "Scion Asset Management (Burry)"),
    FilerRef("pabrai",     "0001549575", "Dalal Street LLC (Pabrai)"),
    FilerRef("baupost",    "0001061768", "Baupost Group (Klarman)"),
    FilerRef("pershing",   "0001336528", "Pershing Square (Ackman)"),
    FilerRef("appaloosa",  "0001656456", "Appaloosa LP (Tepper)"),
    FilerRef("thirdpoint", "0001040273", "Third Point (Loeb)"),
    FilerRef("akre",       "0001112520", "Akre Capital (Akre)"),
    FilerRef("harris",     "0000813917", "Harris Associates (Nygren)"),
    FilerRef("oaktree",    "0000949509", "Oaktree Capital (Marks)"),
    FilerRef("berkshire",  "0001067983", "Berkshire Hathaway (Buffett)"),
    FilerRef("duquesne",   "0001536411", "Duquesne FO (Druckenmiller)"),
)
_BY_SLUG = {f.slug: f for f in ROSTER}


def _load_json(path: Path) -> Any:
    with path.open() as f:
        return json.load(f)


def _list_periods(raw_dir: Path) -> list[str]:
    if not raw_dir.exists():
        return []
    return sorted(p.name for p in raw_dir.iterdir() if p.is_dir())


@lru_cache(maxsize=64)
def _load_filing(raw_dir_str: str, period: str) -> dict[str, Any]:
    """Parse a single quarter's 13F filing. Cached per (raw_dir, period)."""
    from wofo.thirteenf import parse_infotable, parse_primary_doc  # lazy

    raw_dir = Path(raw_dir_str)
    qdir = raw_dir / period
    meta = parse_primary_doc(qdir / "primary_doc.xml")
    holdings = parse_infotable(qdir / "infotable.xml")
    return {
        "meta": {
            "cik": meta.cik,
            "manager_name": meta.manager_name,
            "period_iso": meta.period_iso,
            "period_of_report": meta.period_of_report,
            "report_type": meta.report_type,
            "table_entry_total": meta.table_entry_total,
            "table_value_total": meta.table_value_total,
        },
        "holdings": [h.to_dict() for h in holdings],
    }


def _backtest_rows() -> dict[str, dict[str, Any]]:
    """Index MULTI_FILER_N_REPORT.json by strategy label."""
    path = PROCESSED_DIR / "MULTI_FILER_N_REPORT.json"
    if not path.exists():
        return {}
    rows = _load_json(path)
    return {row["label"]: row for row in rows}


def register_wofo_routes(app: Any) -> None:
    """Mount wofo read-only endpoints onto a FastAPI app or router."""
    router = APIRouter(prefix="/api/wofo", tags=["wofo"])

    @router.get("/filers")
    def list_filers() -> dict[str, Any]:
        rows = _backtest_rows()
        out: list[dict[str, Any]] = []
        for f in ROSTER:
            periods = _list_periods(f.raw_dir)
            row = rows.get(f.name)
            entry: dict[str, Any] = {
                "slug": f.slug,
                "cik": f.cik,
                "name": f.name,
                "periods": periods,
                "has_data": bool(periods),
            }
            if row:
                entry["summary"] = row.get("summary")
                entry["benchmark"] = row.get("benchmark")
                entry["factors"] = row.get("factors")
                entry["rebalances"] = row.get("rebalances")
            out.append(entry)
        return {"filers": out, "n_filers": len(out)}

    @router.get("/backtest")
    def backtest_summary() -> dict[str, Any]:
        path = PROCESSED_DIR / "MULTI_FILER_N_REPORT.json"
        if not path.exists():
            raise HTTPException(404, "No backtest report on disk. Run `python -m wofo.agent.multi_filer_n`.")
        rows = _load_json(path)
        # Split into per-filer rows and combined-portfolio rows so the UI can
        # render them in two tables.
        filer_names = {f.name for f in ROSTER}
        per_filer = [r for r in rows if r["label"] in filer_names]
        combined = [r for r in rows if r["label"] not in filer_names]
        return {
            "report_path": str(path.relative_to(REPO)),
            "per_filer": per_filer,
            "combined": combined,
            "n_strategies": len(rows),
        }

    @router.get("/holdings/{slug}")
    def holdings(slug: str, period: str | None = None, top: int = 25) -> dict[str, Any]:
        f = _BY_SLUG.get(slug)
        if not f:
            raise HTTPException(404, f"Unknown filer slug: {slug}")
        periods = _list_periods(f.raw_dir)
        if not periods:
            raise HTTPException(404, f"No 13F data on disk for {slug}.")
        chosen = period or periods[-1]
        if chosen not in periods:
            raise HTTPException(404, f"Period {chosen} not available for {slug}. Have: {periods}")
        try:
            data = _load_filing(str(f.raw_dir), chosen)
        except Exception as e:
            raise HTTPException(500, f"Failed to parse 13F: {type(e).__name__}: {e}")
        sorted_h = sorted(data["holdings"], key=lambda h: h.get("value_usd", 0), reverse=True)
        return {
            "filer": {"slug": f.slug, "cik": f.cik, "name": f.name},
            "period": chosen,
            "available_periods": periods,
            "meta": data["meta"],
            "top_holdings": sorted_h[: max(1, top)],
            "n_total": len(sorted_h),
        }

    @router.get("/rsi/runs")
    def rsi_runs(limit: int = 20) -> dict[str, Any]:
        if not RSI_RUNS_DIR.exists():
            return {"runs": []}
        run_dirs = sorted(
            (p for p in RSI_RUNS_DIR.iterdir() if p.is_dir()),
            key=lambda p: p.name,
            reverse=True,
        )[:limit]
        runs: list[dict[str, Any]] = []
        for d in run_dirs:
            rj = d / "report.json"
            if not rj.exists():
                continue
            try:
                r = _load_json(rj)
            except Exception:
                continue
            proposals = r.get("proposals") or []
            counts: dict[str, int] = {}
            for p in proposals:
                v = p.get("verdict") or p.get("disposition") or "UNKNOWN"
                counts[v] = counts.get(v, 0) + 1
            runs.append({
                "id": d.name,
                "started_utc": r.get("started_utc"),
                "finished_utc": r.get("finished_utc"),
                "n_proposals": len(proposals),
                "verdict_counts": counts,
                "baseline_summary": (r.get("baseline") or {}).get("summary"),
            })
        return {"runs": runs}

    @router.get("/rsi/runs/{run_id}")
    def rsi_run(run_id: str) -> dict[str, Any]:
        d = RSI_RUNS_DIR / run_id
        rj = d / "report.json"
        if not rj.exists():
            raise HTTPException(404, f"RSI run not found: {run_id}")
        return _load_json(rj)

    @router.get("/evals/runs")
    def eval_runs(limit: int = 20) -> dict[str, Any]:
        if not EVAL_RUNS_DIR.exists():
            return {"runs": []}
        run_dirs = sorted(
            (p for p in EVAL_RUNS_DIR.iterdir() if p.is_dir()),
            key=lambda p: p.name,
            reverse=True,
        )[:limit]
        runs: list[dict[str, Any]] = []
        for d in run_dirs:
            rj = d / "result.json"
            if not rj.exists():
                continue
            try:
                r = _load_json(rj)
            except Exception:
                continue
            runs.append({
                "id": d.name,
                "suite": r.get("suite"),
                "label": r.get("label"),
                "timestamp_utc": r.get("timestamp_utc"),
                "summary": r.get("summary"),
            })
        return {"runs": runs}

    @router.get("/evals/runs/{run_id}")
    def eval_run(run_id: str) -> dict[str, Any]:
        rj = EVAL_RUNS_DIR / run_id / "result.json"
        if not rj.exists():
            raise HTTPException(404, f"Eval run not found: {run_id}")
        return _load_json(rj)

    app.include_router(router)
