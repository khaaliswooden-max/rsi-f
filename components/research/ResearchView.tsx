"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import {
  Loader2,
  WifiOff,
  Users,
  BarChart3,
  GitBranch,
  ChevronRight,
  Layers,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
  CircleDashed,
  AlertTriangle,
} from "lucide-react";
import clsx from "clsx";
import {
  api,
  type FilerEntry,
  type BacktestResponse,
  type HoldingsResponse,
  type RsiRunSummary,
} from "@/src/utils/api";

type Tab = "roster" | "backtest" | "rsi";

const TABS: { id: Tab; label: string; icon: React.ElementType; description: string }[] = [
  { id: "roster", label: "Filer Roster", icon: Users, description: "N=12 institutional managers + holdings" },
  { id: "backtest", label: "Backtest & Factors", icon: BarChart3, description: "Sharpe / α / β and 3-factor decomposition" },
  { id: "rsi", label: "RSI Loop", icon: GitBranch, description: "Self-improvement run history" },
];

// ─── helpers ───────────────────────────────────────────────────────────────

const fmtPct = (v: number | undefined | null, digits = 1) =>
  v == null ? "—" : `${(v * 100).toFixed(digits)}%`;
const fmtNum = (v: number | undefined | null, digits = 2) =>
  v == null ? "—" : v.toFixed(digits);
const fmtUsd = (v: number | undefined | null) => {
  if (v == null) return "—";
  if (v >= 1e9) return `$${(v / 1e9).toFixed(2)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(1)}K`;
  return `$${v.toFixed(0)}`;
};

const intentForReturn = (v?: number | null) => {
  if (v == null) return "text-bp-text-muted";
  if (v > 0.05) return "text-bp-green";
  if (v >= 0) return "text-bp-blue";
  return "text-bp-red";
};

// ─── shared chrome ─────────────────────────────────────────────────────────

function StatusBanner({ loading, offline, message }: { loading: boolean; offline: boolean; message?: string }) {
  if (!loading && !offline && !message) return null;
  return (
    <div
      className={clsx(
        "flex items-center gap-2 px-3 py-2 rounded border text-2xs",
        offline
          ? "bg-bp-orange/10 border-bp-orange/30 text-bp-orange"
          : "bg-bp-dark2 border-bp-border text-bp-text-muted"
      )}
    >
      {offline ? <WifiOff className="w-3.5 h-3.5" /> : <Loader2 className="w-3.5 h-3.5 animate-spin" />}
      {message ||
        (offline
          ? "Backend offline — wofo research artifacts unavailable. Start the FastAPI server (`python app.py`) to load."
          : "Loading wofo research artifacts...")}
    </div>
  );
}

// ─── Roster + holdings drill-down ──────────────────────────────────────────

function FilerCard({
  f,
  expanded,
  onToggle,
  holdings,
  loadingHoldings,
}: {
  f: FilerEntry;
  expanded: boolean;
  onToggle: () => void;
  holdings: HoldingsResponse | null;
  loadingHoldings: boolean;
}) {
  const sharpe = f.summary?.sharpe;
  const alpha = f.benchmark?.alpha_annual;
  const beta = f.benchmark?.beta;
  const cagr = f.summary?.cagr;
  const dd = f.summary?.max_drawdown;

  return (
    <div className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
      <button
        onClick={onToggle}
        disabled={!f.has_data}
        className={clsx(
          "w-full flex items-center gap-4 px-4 py-3 text-left transition-colors",
          f.has_data ? "hover:bg-bp-dark1/50" : "opacity-60 cursor-not-allowed"
        )}
      >
        <div className="flex items-center justify-center w-7 h-7 rounded bg-bp-blue/10 border border-bp-blue/20 shrink-0">
          <Users className="w-3.5 h-3.5 text-bp-blue" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-bp-text">{f.name}</span>
            <span className="text-2xs text-bp-text-muted px-1.5 py-0.5 rounded bg-bp-dark3 border border-bp-border font-mono">
              CIK {f.cik}
            </span>
            {!f.has_data && (
              <span className="text-2xs text-bp-orange px-1.5 py-0.5 rounded bg-bp-orange/10 border border-bp-orange/20">
                no filings on disk
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 mt-1 text-2xs text-bp-text-muted font-mono tabular-nums">
            <span>Periods: {f.periods.length}</span>
            <span className="text-bp-text-disabled">·</span>
            <span>Sharpe: <span className={clsx(sharpe != null && sharpe >= 1 ? "text-bp-green" : "text-bp-text")}>{fmtNum(sharpe)}</span></span>
            <span className="text-bp-text-disabled">·</span>
            <span>CAGR: <span className={intentForReturn(cagr)}>{fmtPct(cagr, 1)}</span></span>
            <span className="text-bp-text-disabled">·</span>
            <span>α: <span className={intentForReturn(alpha)}>{fmtPct(alpha, 1)}</span></span>
            <span className="text-bp-text-disabled">·</span>
            <span>β: <span className="text-bp-text">{fmtNum(beta)}</span></span>
            <span className="text-bp-text-disabled">·</span>
            <span>MaxDD: <span className="text-bp-orange">{fmtPct(dd, 1)}</span></span>
          </div>
        </div>
        <ChevronRight
          className={clsx(
            "w-4 h-4 text-bp-text-muted transition-transform duration-150 shrink-0",
            expanded && "rotate-90"
          )}
        />
      </button>

      {expanded && (
        <div className="border-t border-bp-border px-4 py-4 space-y-3">
          {loadingHoldings && (
            <div className="flex items-center gap-2 text-bp-text-muted text-xs">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Parsing 13F filing...
            </div>
          )}
          {!loadingHoldings && !holdings && (
            <div className="text-2xs text-bp-text-muted">No holdings data available.</div>
          )}
          {!loadingHoldings && holdings && (
            <>
              <div className="flex items-center gap-3 flex-wrap text-2xs text-bp-text-muted">
                <span className="font-mono">Period <span className="text-bp-text">{holdings.period}</span></span>
                <span className="text-bp-text-disabled">·</span>
                <span>Total AUM <span className="text-bp-text font-mono">{fmtUsd(holdings.meta.table_value_total)}</span></span>
                <span className="text-bp-text-disabled">·</span>
                <span>Positions <span className="text-bp-text font-mono">{holdings.n_total}</span></span>
                <span className="text-bp-text-disabled">·</span>
                <span>Available: <span className="font-mono text-bp-text-secondary">{holdings.available_periods.join(", ")}</span></span>
              </div>
              <div className="rounded border border-bp-border overflow-hidden">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="bg-bp-dark3 text-bp-text-muted text-2xs uppercase tracking-widest">
                      <th className="text-left px-3 py-2 font-semibold">Issuer</th>
                      <th className="text-left px-3 py-2 font-semibold">Class</th>
                      <th className="text-right px-3 py-2 font-semibold">Value</th>
                      <th className="text-right px-3 py-2 font-semibold">Shares</th>
                      <th className="text-right px-3 py-2 font-semibold">% AUM</th>
                    </tr>
                  </thead>
                  <tbody>
                    {holdings.top_holdings.map((h) => {
                      const pct = holdings.meta.table_value_total
                        ? h.value_usd / holdings.meta.table_value_total
                        : 0;
                      return (
                        <tr key={`${h.cusip}-${h.title_of_class}`} className="border-t border-bp-border hover:bg-bp-dark1/40">
                          <td className="px-3 py-1.5 text-bp-text">{h.name_of_issuer}</td>
                          <td className="px-3 py-1.5 text-bp-text-muted font-mono">{h.title_of_class}</td>
                          <td className="px-3 py-1.5 text-right text-bp-text font-mono tabular-nums">{fmtUsd(h.value_usd)}</td>
                          <td className="px-3 py-1.5 text-right text-bp-text-secondary font-mono tabular-nums">
                            {h.shares_or_principal.toLocaleString()}
                          </td>
                          <td className="px-3 py-1.5 text-right font-mono tabular-nums">
                            <span className={clsx(pct >= 0.1 ? "text-bp-blue" : "text-bp-text-muted")}>
                              {(pct * 100).toFixed(1)}%
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

function RosterTab() {
  const [filers, setFilers] = useState<FilerEntry[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [holdings, setHoldings] = useState<Record<string, HoldingsResponse>>({});
  const [holdingsLoading, setHoldingsLoading] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.wofoFilers()
      .then((r) => !cancelled && setFilers(r.filers))
      .catch(() => !cancelled && setOffline(true))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  const onToggle = useCallback(async (slug: string) => {
    if (expanded === slug) {
      setExpanded(null);
      return;
    }
    setExpanded(slug);
    if (holdings[slug]) return;
    setHoldingsLoading(slug);
    try {
      const h = await api.wofoHoldings(slug, undefined, 25);
      setHoldings((prev) => ({ ...prev, [slug]: h }));
    } catch {
      // Leave undefined; the card will render an empty state.
    } finally {
      setHoldingsLoading(null);
    }
  }, [expanded, holdings]);

  return (
    <div className="space-y-3">
      <StatusBanner loading={loading} offline={offline} />
      {filers?.map((f) => (
        <FilerCard
          key={f.slug}
          f={f}
          expanded={expanded === f.slug}
          onToggle={() => onToggle(f.slug)}
          holdings={holdings[f.slug] ?? null}
          loadingHoldings={holdingsLoading === f.slug}
        />
      ))}
    </div>
  );
}

// ─── Backtest + factor decomposition ───────────────────────────────────────

function BacktestTab() {
  const [report, setReport] = useState<BacktestResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api.wofoBacktest()
      .then((r) => !cancelled && setReport(r))
      .catch((e: any) => {
        if (cancelled) return;
        const msg = String(e?.message || e);
        if (msg.includes("404")) setError("No backtest report on disk yet. Run `python -m wofo.agent.multi_filer_n` to generate one.");
        else setOffline(true);
      })
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  const allRows = useMemo(
    () => (report ? [...report.per_filer, ...report.combined] : []),
    [report]
  );

  return (
    <div className="space-y-4">
      <StatusBanner loading={loading} offline={offline} message={error || undefined} />
      {report && (
        <>
          <div className="flex items-center gap-3 text-2xs text-bp-text-muted">
            <Layers className="w-3.5 h-3.5" />
            {report.n_strategies} strategies · source <code className="font-mono text-bp-text-secondary">{report.report_path}</code>
          </div>

          <section className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
            <div className="px-4 py-2.5 border-b border-bp-border">
              <h3 className="text-sm font-semibold text-bp-text">Risk and return vs SPY</h3>
              <p className="text-2xs text-bp-text-muted mt-0.5">Single-factor (SPY-only) regression — α attributes everything not explained by market beta to skill.</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-bp-dark3 text-bp-text-muted text-2xs uppercase tracking-widest">
                    <th className="text-left px-3 py-2 font-semibold">Strategy</th>
                    <th className="text-right px-3 py-2 font-semibold">Total ret</th>
                    <th className="text-right px-3 py-2 font-semibold">CAGR</th>
                    <th className="text-right px-3 py-2 font-semibold">Sharpe</th>
                    <th className="text-right px-3 py-2 font-semibold">MaxDD</th>
                    <th className="text-right px-3 py-2 font-semibold">α (annual)</th>
                    <th className="text-right px-3 py-2 font-semibold">β</th>
                    <th className="text-right px-3 py-2 font-semibold">InfoRatio</th>
                    <th className="text-right px-3 py-2 font-semibold">Rebal.</th>
                  </tr>
                </thead>
                <tbody>
                  {allRows.map((r, i) => {
                    const isCombined = i >= report.per_filer.length;
                    return (
                      <tr
                        key={r.label}
                        className={clsx(
                          "border-t border-bp-border hover:bg-bp-dark1/40",
                          isCombined && "bg-bp-blue/5"
                        )}
                      >
                        <td className="px-3 py-1.5 text-bp-text font-medium">
                          {isCombined && <span className="text-2xs text-bp-blue mr-2 uppercase tracking-wider">Combo</span>}
                          {r.label}
                        </td>
                        <td className={clsx("px-3 py-1.5 text-right font-mono tabular-nums", intentForReturn(r.summary.total_return))}>
                          {fmtPct(r.summary.total_return, 1)}
                        </td>
                        <td className={clsx("px-3 py-1.5 text-right font-mono tabular-nums", intentForReturn(r.summary.cagr))}>
                          {fmtPct(r.summary.cagr, 1)}
                        </td>
                        <td className="px-3 py-1.5 text-right font-mono tabular-nums">
                          <span className={clsx(r.summary.sharpe >= 1 ? "text-bp-green" : r.summary.sharpe >= 0 ? "text-bp-text" : "text-bp-red")}>
                            {fmtNum(r.summary.sharpe)}
                          </span>
                        </td>
                        <td className="px-3 py-1.5 text-right text-bp-orange font-mono tabular-nums">{fmtPct(r.summary.max_drawdown, 1)}</td>
                        <td className={clsx("px-3 py-1.5 text-right font-mono tabular-nums", intentForReturn(r.benchmark?.alpha_annual))}>
                          {fmtPct(r.benchmark?.alpha_annual, 1)}
                        </td>
                        <td className="px-3 py-1.5 text-right text-bp-text font-mono tabular-nums">{fmtNum(r.benchmark?.beta)}</td>
                        <td className={clsx("px-3 py-1.5 text-right font-mono tabular-nums", intentForReturn(r.benchmark?.info_ratio, ))}>
                          {fmtNum(r.benchmark?.info_ratio)}
                        </td>
                        <td className="px-3 py-1.5 text-right text-bp-text-muted font-mono tabular-nums">{r.rebalances}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          <section className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
            <div className="px-4 py-2.5 border-b border-bp-border">
              <h3 className="text-sm font-semibold text-bp-text">3-factor decomposition (ETF-proxy)</h3>
              <p className="text-2xs text-bp-text-muted mt-0.5">
                Loadings on Mkt-RF (SPY−rf), SMB (IWM−SPY), HML (IWD−IWF). 3-factor α is more conservative than SPY-only α since SMB / HML absorb size and value tilts.
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-bp-dark3 text-bp-text-muted text-2xs uppercase tracking-widest">
                    <th className="text-left px-3 py-2 font-semibold">Strategy</th>
                    <th className="text-right px-3 py-2 font-semibold">α (annual)</th>
                    <th className="text-right px-3 py-2 font-semibold">β_mkt</th>
                    <th className="text-right px-3 py-2 font-semibold">β_smb</th>
                    <th className="text-right px-3 py-2 font-semibold">β_hml</th>
                    <th className="text-right px-3 py-2 font-semibold">R²</th>
                    <th className="text-right px-3 py-2 font-semibold">n</th>
                  </tr>
                </thead>
                <tbody>
                  {allRows.map((r, i) => {
                    const f = r.factors;
                    const L = f?.loadings || {};
                    const isCombined = i >= report.per_filer.length;
                    return (
                      <tr
                        key={r.label}
                        className={clsx("border-t border-bp-border hover:bg-bp-dark1/40", isCombined && "bg-bp-blue/5")}
                      >
                        <td className="px-3 py-1.5 text-bp-text font-medium">{r.label}</td>
                        <td className={clsx("px-3 py-1.5 text-right font-mono tabular-nums", intentForReturn(f?.alpha_annual))}>
                          {fmtPct(f?.alpha_annual, 1)}
                        </td>
                        <td className="px-3 py-1.5 text-right text-bp-text font-mono tabular-nums">{fmtNum(L.mkt_rf)}</td>
                        <td className="px-3 py-1.5 text-right text-bp-text-secondary font-mono tabular-nums">{fmtNum(L.smb)}</td>
                        <td className="px-3 py-1.5 text-right text-bp-text-secondary font-mono tabular-nums">{fmtNum(L.hml)}</td>
                        <td className="px-3 py-1.5 text-right text-bp-text-muted font-mono tabular-nums">{fmtNum(f?.r_squared)}</td>
                        <td className="px-3 py-1.5 text-right text-bp-text-disabled font-mono tabular-nums">{f?.n ?? "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

// ─── RSI loop history ──────────────────────────────────────────────────────

const VERDICT_META: Record<string, { color: string; bg: string; border: string; icon: React.ElementType }> = {
  IMPROVE:      { color: "text-bp-green",  bg: "bg-bp-green/10",  border: "border-bp-green/20",  icon: CheckCircle2 },
  REGRESS:      { color: "text-bp-red",    bg: "bg-bp-red/10",    border: "border-bp-red/20",    icon: XCircle },
  INCONCLUSIVE: { color: "text-bp-text-muted", bg: "bg-bp-dark3", border: "border-bp-border", icon: CircleDashed },
  ERROR:        { color: "text-bp-orange", bg: "bg-bp-orange/10", border: "border-bp-orange/20", icon: AlertTriangle },
};

function VerdictBadge({ verdict, count }: { verdict: string; count: number }) {
  const m = VERDICT_META[verdict] || VERDICT_META.INCONCLUSIVE;
  const Icon = m.icon;
  return (
    <span className={clsx("inline-flex items-center gap-1 text-2xs font-mono px-1.5 py-0.5 rounded border", m.color, m.bg, m.border)}>
      <Icon className="w-3 h-3" />
      {verdict} {count}
    </span>
  );
}

function RsiTab() {
  const [runs, setRuns] = useState<RsiRunSummary[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);
  const [openId, setOpenId] = useState<string | null>(null);
  const [details, setDetails] = useState<Record<string, any>>({});

  useEffect(() => {
    let cancelled = false;
    api.wofoRsiRuns(20)
      .then((r) => !cancelled && setRuns(r.runs))
      .catch(() => !cancelled && setOffline(true))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  const onToggle = async (id: string) => {
    if (openId === id) { setOpenId(null); return; }
    setOpenId(id);
    if (details[id]) return;
    try {
      const r = await api.wofoRsiRun(id);
      setDetails((p) => ({ ...p, [id]: r }));
    } catch {
      /* swallow */
    }
  };

  return (
    <div className="space-y-3">
      <StatusBanner loading={loading} offline={offline} />
      {runs && runs.length === 0 && !loading && !offline && (
        <div className="rounded border border-bp-border bg-bp-dark2 px-4 py-6 text-sm text-bp-text-muted">
          No RSI runs on disk. Generate one with
          <code className="font-mono text-bp-text bg-bp-dark3 border border-bp-border rounded px-1.5 py-0.5 ml-1">
            python -m wofo.rsi.cli demo
          </code>.
        </div>
      )}
      {runs?.map((run) => {
        const open = openId === run.id;
        const detail = details[run.id];
        const proposals: any[] = (detail?.proposals as any[]) || [];
        return (
          <div key={run.id} className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
            <button
              onClick={() => onToggle(run.id)}
              className="w-full flex items-center gap-4 px-4 py-3 text-left hover:bg-bp-dark1/50 transition-colors"
            >
              <div className="flex items-center justify-center w-7 h-7 rounded bg-bp-blue/10 border border-bp-blue/20 shrink-0">
                <GitBranch className="w-3.5 h-3.5 text-bp-blue" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-mono text-bp-text">{run.id}</span>
                  <span className="text-2xs text-bp-text-muted">·</span>
                  <span className="text-2xs text-bp-text-muted">{run.n_proposals} proposals</span>
                </div>
                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                  {Object.entries(run.verdict_counts).map(([v, c]) => (
                    <VerdictBadge key={v} verdict={v} count={c} />
                  ))}
                  {run.baseline_summary?.rubric_mean_fraction != null && (
                    <span className="text-2xs text-bp-text-muted font-mono">
                      baseline rubric {fmtNum(run.baseline_summary.rubric_mean_fraction, 3)}
                    </span>
                  )}
                </div>
              </div>
              <ChevronRight
                className={clsx(
                  "w-4 h-4 text-bp-text-muted transition-transform duration-150 shrink-0",
                  open && "rotate-90"
                )}
              />
            </button>
            {open && (
              <div className="border-t border-bp-border px-4 py-4 space-y-2">
                {!detail && (
                  <div className="flex items-center gap-2 text-bp-text-muted text-xs">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Loading proposals...
                  </div>
                )}
                {detail && proposals.length === 0 && (
                  <div className="text-2xs text-bp-text-muted">No proposals recorded for this run.</div>
                )}
                {proposals.map((p, idx) => {
                  const v = (p.verdict || p.disposition || "INCONCLUSIVE") as string;
                  const m = VERDICT_META[v] || VERDICT_META.INCONCLUSIVE;
                  const Icon = m.icon;
                  const delta: number | undefined = p.delta?.rubric_mean_fraction ?? p.delta_rubric_mean_fraction;
                  return (
                    <div
                      key={idx}
                      className={clsx("rounded border px-3 py-2.5", m.bg, m.border)}
                    >
                      <div className="flex items-center gap-2 flex-wrap">
                        <Icon className={clsx("w-3.5 h-3.5", m.color)} />
                        <span className={clsx("text-2xs font-mono font-semibold tracking-wider", m.color)}>{v}</span>
                        <span className="text-xs text-bp-text font-medium">{p.name || p.id || `proposal_${idx}`}</span>
                        {p.target && (
                          <code className="text-2xs font-mono text-bp-text-muted bg-bp-dark3 border border-bp-border rounded px-1.5 py-0.5">
                            {p.target}
                          </code>
                        )}
                        {p.proposer && (
                          <span className="text-2xs text-bp-text-disabled">via {p.proposer}</span>
                        )}
                        {delta != null && (
                          <span className={clsx("text-2xs font-mono ml-auto flex items-center gap-1",
                            delta > 0 ? "text-bp-green" : delta < 0 ? "text-bp-red" : "text-bp-text-muted")}>
                            {delta > 0 ? <TrendingUp className="w-3 h-3" /> : delta < 0 ? <TrendingDown className="w-3 h-3" /> : null}
                            Δ {delta >= 0 ? "+" : ""}{delta.toFixed(4)}
                          </span>
                        )}
                      </div>
                      {p.rationale && (
                        <p className="text-xs text-bp-text-secondary mt-1.5 leading-relaxed">{p.rationale}</p>
                      )}
                      {p.judge_rationale && (
                        <p className="text-2xs text-bp-text-muted mt-1 italic">judge: {p.judge_rationale}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ─── Outer shell ───────────────────────────────────────────────────────────

export default function ResearchView() {
  const [tab, setTab] = useState<Tab>("roster");

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="shrink-0 flex items-center gap-1 px-5 py-2 bg-bp-dark2 border-b border-bp-border">
        {TABS.map(({ id, label, icon: Icon, description }) => {
          const active = tab === id;
          return (
            <button
              key={id}
              onClick={() => setTab(id)}
              title={description}
              className={clsx(
                "flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium border transition-all duration-100",
                active
                  ? "bg-bp-blue/15 border-bp-blue/30 text-bp-text"
                  : "border-transparent text-bp-text-muted hover:text-bp-text hover:bg-bp-dark1"
              )}
            >
              <Icon className={clsx("w-3.5 h-3.5", active ? "text-bp-blue" : "text-bp-text-muted")} />
              {label}
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-5 py-5">
          {tab === "roster" && <RosterTab />}
          {tab === "backtest" && <BacktestTab />}
          {tab === "rsi" && <RsiTab />}
        </div>
      </div>
    </div>
  );
}
