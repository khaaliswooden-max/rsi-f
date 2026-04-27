import TopBar from "@/components/layout/TopBar";
import { Terminal, Lock, Globe, Database, BarChart3 } from "lucide-react";

interface Endpoint {
  method: "GET" | "POST" | "DELETE";
  path: string;
  description: string;
  auth: boolean;
  body?: string;
  response: string;
}

const PREF_ENDPOINTS: Endpoint[] = [
  {
    method: "GET",
    path: "/api/health",
    description: "Health check + HF sync status",
    auth: false,
    response: `{ "status": "ok", "hf_sync_enabled": true, "dataset_repo": "zuup1/zuup-preferences" }`,
  },
  {
    method: "GET",
    path: "/api/stats",
    description: "Per-domain annotation counts and annotator coverage",
    auth: false,
    response: `{
  "total": 1755,
  "by_domain": {
    "procurement": { "collected": 500, "target": 500, "annotators": 4, "preference_distribution": {"A": 230, "B": 220, "TIE": 50} }
  },
  "last_sync": "2026-04-27T18:42:11Z"
}`,
  },
  {
    method: "GET",
    path: "/api/domains",
    description: "Flat list of all domains with categories and live counts",
    auth: false,
    response: `[
  { "id": "procurement", "name": "Fed/SLED Procurement", "icon": "📋",
    "platform": "Aureon", "categories": ["rfp_analysis", ...],
    "min_samples": 500, "collected": 500 }
]`,
  },
  {
    method: "POST",
    path: "/api/load_pair",
    description: "Generate a fresh prompt + two model responses for annotation",
    auth: false,
    body: `{ "domain": "procurement", "category": "rfp_analysis" }`,
    response: `{ "prompt": "...", "response_a": "...", "response_b": "...",
  "domain": "procurement", "category": "rfp_analysis", "difficulty": "medium" }`,
  },
  {
    method: "POST",
    path: "/api/preferences",
    description: "Submit a preference annotation",
    auth: true,
    body: `{
  "domain": "procurement",
  "category": "rfp_analysis",
  "prompt": "Analyze this RFP...",
  "response_a": "...",
  "response_b": "...",
  "preference": "A",
  "annotator_id": "user_123",
  "dimension_scores": { "accuracy": 4, "compliance": 5, "actionability": 3, "clarity": 4 }
}`,
    response: `{ "status": "saved", "hash": "abc123def456" }`,
  },
  {
    method: "POST",
    path: "/api/export",
    description: "Export dataset in DPO-ready or raw JSONL format (premium key)",
    auth: true,
    body: `{ "format": "dpo", "min_confidence": 0.6, "limit": 1000 }`,
    response: `{ "count": 842, "format": "dpo", "data": [{ "prompt": "...", "chosen": "...", "rejected": "..." }] }`,
  },
];

const WOFO_ENDPOINTS: Endpoint[] = [
  {
    method: "GET",
    path: "/api/wofo/filers",
    description: "N=12 institutional manager roster with backtest summary stats",
    auth: false,
    response: `{ "filers": [
  { "slug": "berkshire", "cik": "0001067983", "name": "Berkshire Hathaway (Buffett)",
    "periods": ["2024Q4", "2025Q1", ..., "2025Q4"], "has_data": true,
    "summary": { "sharpe": 0.41, "cagr": 0.063, "max_drawdown": 0.205 },
    "benchmark": { "alpha_annual": -0.05, "beta": 0.86, "info_ratio": -0.67 } }
], "n_filers": 12 }`,
  },
  {
    method: "GET",
    path: "/api/wofo/backtest",
    description: "Multi-filer backtest comparison (per-filer + combined portfolios)",
    auth: false,
    response: `{ "report_path": "wofo/data/13f/processed/MULTI_FILER_N_REPORT.json",
  "per_filer": [...], "combined": [...], "n_strategies": 16 }`,
  },
  {
    method: "GET",
    path: "/api/wofo/holdings/{slug}",
    description: "Latest 13F holdings for a manager (top N by USD value)",
    auth: false,
    response: `{ "filer": {...}, "period": "2025Q4", "available_periods": [...],
  "meta": { "table_value_total": 5516758344, "table_entry_total": 29, ... },
  "top_holdings": [{ "name_of_issuer": "APPLIED DIGITAL CORP", "value_usd": 278033751, ... }],
  "n_total": 29 }`,
  },
  {
    method: "GET",
    path: "/api/wofo/rsi/runs",
    description: "Recent RSI self-improvement loop runs (proposals, verdicts, baseline)",
    auth: false,
    response: `{ "runs": [
  { "id": "20260427T143119+0000_demo", "started_utc": "...", "n_proposals": 3,
    "verdict_counts": { "IMPROVE": 1, "REGRESS": 1, "INCONCLUSIVE": 1 } }
] }`,
  },
  {
    method: "GET",
    path: "/api/wofo/rsi/runs/{id}",
    description: "Full RSI run report including per-proposal diffs and judge rationales",
    auth: false,
    response: `{ "started_utc": "...", "baseline": {...}, "proposals": [...] }`,
  },
  {
    method: "GET",
    path: "/api/wofo/evals/runs",
    description: "Recent eval suite runs (rubric + signal scores)",
    auth: false,
    response: `{ "runs": [
  { "id": "20260427T143119+0000_rsi", "suite": "rsi_default", "label": "rsi",
    "summary": { "rubric_mean_fraction": 0.375, "signal_mean_alpha_annual": 0.045 } }
] }`,
  },
  {
    method: "GET",
    path: "/api/wofo/evals/runs/{id}",
    description: "Full eval run with per-case rubric scores and signal metrics",
    auth: false,
    response: `{ "suite": "rsi_default", "results": [...], "summary": {...} }`,
  },
];

const METHOD_COLORS: Record<string, string> = {
  GET: "text-bp-green bg-bp-green/10 border-bp-green/20",
  POST: "text-bp-blue bg-bp-blue/10 border-bp-blue/20",
  DELETE: "text-bp-red bg-bp-red/10 border-bp-red/20",
};

function EndpointCard({ ep }: { ep: Endpoint }) {
  return (
    <div className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
      <div className="flex items-center gap-3 px-4 py-3 border-b border-bp-border">
        <span className={`text-2xs font-bold font-mono px-2 py-0.5 rounded border ${METHOD_COLORS[ep.method]}`}>
          {ep.method}
        </span>
        <code className="text-sm font-mono text-bp-text">{ep.path}</code>
        {ep.auth && (
          <div className="flex items-center gap-1 ml-2">
            <Lock className="w-3 h-3 text-bp-orange" />
            <span className="text-2xs text-bp-orange">auth required</span>
          </div>
        )}
        <span className="ml-auto text-xs text-bp-text-muted">{ep.description}</span>
      </div>

      <div className="p-4 space-y-3">
        {ep.body && (
          <div>
            <p className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest mb-1.5">Request Body</p>
            <pre className="text-xs font-mono text-bp-text-secondary bg-bp-dark3 border border-bp-border rounded p-3 overflow-x-auto leading-relaxed">
              {ep.body}
            </pre>
          </div>
        )}
        <div>
          <p className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest mb-1.5">Response</p>
          <pre className="text-xs font-mono text-bp-green bg-bp-dark3 border border-bp-border rounded p-3 overflow-x-auto leading-relaxed">
            {ep.response}
          </pre>
        </div>
      </div>
    </div>
  );
}

function SectionHeader({ icon: Icon, title, subtitle }: { icon: React.ElementType; title: string; subtitle: string }) {
  return (
    <div className="flex items-center gap-3 pt-2">
      <div className="p-2 rounded border border-bp-border bg-bp-dark2">
        <Icon className="w-4 h-4 text-bp-blue" />
      </div>
      <div>
        <h2 className="text-sm font-semibold text-bp-text">{title}</h2>
        <p className="text-2xs text-bp-text-muted">{subtitle}</p>
      </div>
    </div>
  );
}

export default function ApiDocsPage() {
  return (
    <>
      <TopBar title="API Reference" subtitle="REST endpoints for preference collection, export, and wofo research" />
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-5 py-5 space-y-4">

          {/* Auth callout */}
          <div className="flex items-start gap-3 px-4 py-3 rounded border border-bp-orange/30 bg-bp-orange/10">
            <Lock className="w-4 h-4 text-bp-orange mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-bp-text">Authentication</p>
              <p className="text-xs text-bp-text-secondary mt-0.5">
                Protected endpoints require an <code className="font-mono text-bp-orange bg-bp-dark3 px-1 py-0.5 rounded">X-API-Key</code> header.
                Wofo research endpoints are read-only and unauthenticated.
              </p>
            </div>
          </div>

          {/* Base URL */}
          <div className="flex items-center gap-3 px-4 py-3 rounded border border-bp-border bg-bp-dark2">
            <Globe className="w-4 h-4 text-bp-text-muted shrink-0" />
            <div className="flex items-center gap-2">
              <span className="text-xs text-bp-text-muted">Base URL</span>
              <code className="text-xs font-mono text-bp-blue bg-bp-dark3 px-2 py-1 rounded border border-bp-border">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:7860"}
              </code>
            </div>
          </div>

          <SectionHeader
            icon={Database}
            title="Preference Collection"
            subtitle="Annotate, store, and export human preference data"
          />
          {PREF_ENDPOINTS.map((ep) => (
            <EndpointCard key={ep.path} ep={ep} />
          ))}

          <SectionHeader
            icon={BarChart3}
            title="Wofo Research"
            subtitle="Read-only access to 13F holdings, backtests, factor decomposition, and RSI runs"
          />
          {WOFO_ENDPOINTS.map((ep) => (
            <EndpointCard key={ep.path} ep={ep} />
          ))}

          {/* cURL example */}
          <div className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2.5 border-b border-bp-border">
              <Terminal className="w-4 h-4 text-bp-text-muted" />
              <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">cURL Example</span>
            </div>
            <pre className="text-xs font-mono text-bp-text-secondary bg-bp-dark3 p-4 overflow-x-auto leading-relaxed">
{`curl -X POST $BASE/api/preferences \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: $KEY" \\
  -d '{
    "domain": "procurement",
    "category": "rfp_analysis",
    "prompt": "Analyze this RFP...",
    "response_a": "...",
    "response_b": "...",
    "preference": "A",
    "annotator_id": "user_123",
    "dimension_scores": {"accuracy": 4, "compliance": 5}
  }'

curl $BASE/api/wofo/holdings/berkshire?period=2025Q4&top=10`}
            </pre>
          </div>

        </div>
      </div>
    </>
  );
}
