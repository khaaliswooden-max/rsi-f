// API client for the FastAPI backend served by `app.py`.
// `next.config.js` rewrites `/api/*` to `NEXT_PUBLIC_API_URL`, so we can call
// relative `/api/...` paths from the browser without CORS.

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

// ─── Preference / annotation types ─────────────────────────────────────────

export interface DomainInfo {
  id: string;
  name: string;
  icon: string;
  platform: string;
  description?: string;
  categories: string[];
  min_samples: number;
  collected: number;
}

export interface DomainStats {
  collected: number;
  target: number;
  annotators: number;
  preference_distribution?: Record<string, number>;
}

export interface StatsResponse {
  total: number;
  by_domain: Record<string, DomainStats>;
  last_sync: string | null;
}

export interface ResponsePair {
  prompt: string;
  response_a: string;
  response_b: string;
  domain: string;
  category: string;
  difficulty?: string;
}

export interface PreferenceSubmission {
  domain: string;
  category: string;
  prompt: string;
  response_a: string;
  response_b: string;
  preference: "A" | "B" | "TIE";
  annotator_id: string;
  dimension_scores: Record<string, number>;
  notes?: string;
}

// ─── Wofo research types ───────────────────────────────────────────────────

export interface BacktestSummary {
  start_date: string;
  end_date: string;
  n_days: number;
  start_nav: number;
  end_nav: number;
  total_return: number;
  cagr: number;
  sharpe: number;
  max_drawdown: number;
}

export interface BenchmarkStats {
  alpha_annual: number;
  beta: number;
  info_ratio: number;
  r_squared: number;
  up_capture: number;
  down_capture: number;
  total_return_strategy: number;
  total_return_benchmark: number;
  max_drawdown_strategy: number;
  max_drawdown_benchmark: number;
}

export interface FactorDecomposition {
  alpha_annual: number;
  loadings: { mkt_rf?: number; smb?: number; hml?: number; rmw?: number; mom?: number };
  r_squared: number;
  n: number;
  t_stats?: Record<string, number>;
  factor_source?: string;
  factor_proxy?: boolean;
}

export interface FilerEntry {
  slug: string;
  cik: string;
  name: string;
  periods: string[];
  has_data: boolean;
  summary?: BacktestSummary;
  benchmark?: BenchmarkStats;
  factors?: FactorDecomposition;
  rebalances?: number;
}

export interface FilersResponse {
  filers: FilerEntry[];
  n_filers: number;
}

export interface BacktestResponse {
  report_path: string;
  per_filer: Array<{
    label: string;
    summary: BacktestSummary;
    benchmark: BenchmarkStats | null;
    factors: FactorDecomposition;
    rebalances: number;
  }>;
  combined: Array<{
    label: string;
    summary: BacktestSummary;
    benchmark: BenchmarkStats | null;
    factors: FactorDecomposition;
    rebalances: number;
  }>;
  n_strategies: number;
}

export interface Holding {
  name_of_issuer: string;
  title_of_class: string;
  cusip: string;
  value_usd: number;
  shares_or_principal: number;
  sh_or_prn: string;
  put_call: string | null;
}

export interface HoldingsResponse {
  filer: { slug: string; cik: string; name: string };
  period: string;
  available_periods: string[];
  meta: {
    cik: string;
    manager_name: string;
    period_iso: string;
    period_of_report: string;
    table_entry_total: number;
    table_value_total: number;
  };
  top_holdings: Holding[];
  n_total: number;
}

export interface RsiRunSummary {
  id: string;
  started_utc: string | null;
  finished_utc: string | null;
  n_proposals: number;
  verdict_counts: Record<string, number>;
  baseline_summary: Record<string, number> | null;
}

export interface EvalRunSummary {
  id: string;
  suite: string | null;
  label: string | null;
  timestamp_utc: string | null;
  summary: Record<string, number> | null;
}

// ─── Fetch helper ──────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json", ...opts?.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => apiFetch<{ status: string; hf_sync_enabled: boolean }>("/health"),
  stats: () => apiFetch<StatsResponse>("/stats"),
  domains: () => apiFetch<DomainInfo[]>("/domains"),
  loadPair: (domain: string, category?: string | null) =>
    apiFetch<ResponsePair>("/load_pair", {
      method: "POST",
      body: JSON.stringify({ domain, category: category || null }),
    }),
  submitPreference: (data: PreferenceSubmission, apiKey?: string) =>
    apiFetch<{ status: string; hash: string }>("/preferences", {
      method: "POST",
      headers: apiKey ? { "X-API-Key": apiKey } : {},
      body: JSON.stringify({ ...data, preference: data.preference }),
    }),

  // Wofo research surface
  wofoFilers: () => apiFetch<FilersResponse>("/wofo/filers"),
  wofoBacktest: () => apiFetch<BacktestResponse>("/wofo/backtest"),
  wofoHoldings: (slug: string, period?: string, top: number = 25) => {
    const qs = new URLSearchParams();
    if (period) qs.set("period", period);
    qs.set("top", String(top));
    return apiFetch<HoldingsResponse>(`/wofo/holdings/${slug}?${qs.toString()}`);
  },
  wofoRsiRuns: (limit: number = 20) => apiFetch<{ runs: RsiRunSummary[] }>(`/wofo/rsi/runs?limit=${limit}`),
  wofoRsiRun: (id: string) => apiFetch<any>(`/wofo/rsi/runs/${id}`),
  wofoEvalRuns: (limit: number = 20) => apiFetch<{ runs: EvalRunSummary[] }>(`/wofo/evals/runs?limit=${limit}`),
  wofoEvalRun: (id: string) => apiFetch<any>(`/wofo/evals/runs/${id}`),
};

// ─── Static fallback used when the backend isn't reachable ─────────────────

export const FALLBACK_DOMAINS: DomainInfo[] = [
  { id: "procurement", name: "Fed/SLED Procurement", icon: "📋", platform: "Aureon", categories: ["rfp_analysis", "proposal_writing", "compliance_check", "vendor_evaluation"], min_samples: 500, collected: 0 },
  { id: "biomedical", name: "Biomedical GB-CI", icon: "🧬", platform: "Symbion", categories: ["biosensor_design", "neural_analysis", "clinical_validation", "regulatory_pathway"], min_samples: 400, collected: 0 },
  { id: "legacy_refactor", name: "Legacy Refactoring", icon: "🔧", platform: "Relian", categories: ["cobol_modernization", "mainframe_migration", "api_extraction", "test_generation"], min_samples: 300, collected: 0 },
  { id: "autonomy", name: "Autonomy OS", icon: "🤖", platform: "Veyra", categories: ["agent_design", "safety_constraints", "tool_use", "multi_agent"], min_samples: 300, collected: 0 },
  { id: "defense_wm", name: "Defense World Models", icon: "🌐", platform: "Orb", categories: ["scene_reconstruction", "isr_analysis", "geospatial", "threat_assessment"], min_samples: 300, collected: 0 },
  { id: "halal", name: "Halal Compliance", icon: "☪️", platform: "Civium", categories: ["certification", "supply_chain", "ingredient_analysis", "audit_prep"], min_samples: 200, collected: 0 },
  { id: "quantum_arch", name: "Quantum Archaeology", icon: "🏛️", platform: "QAWM", categories: ["historical_reconstruction", "artifact_analysis", "provenance", "3d_modeling"], min_samples: 200, collected: 0 },
  { id: "mobile_dc", name: "Mobile Data Center", icon: "📦", platform: "PodX", categories: ["edge_deployment", "ddil_ops", "power_management", "containerization"], min_samples: 200, collected: 0 },
  { id: "hubzone", name: "HUBZone Contracting", icon: "🏢", platform: "Aureon", categories: ["eligibility", "certification_prep", "teaming", "set_aside"], min_samples: 200, collected: 0 },
  { id: "ingestible", name: "Ingestible GB-CI", icon: "💊", platform: "Symbion HW", categories: ["capsule_design", "in_vivo_sensing", "data_telemetry", "regulatory"], min_samples: 200, collected: 0 },
];

// Backward-compat alias used by existing components.
export const DOMAINS = FALLBACK_DOMAINS;

export const DIMENSION_LABELS: Record<string, string> = {
  accuracy: "Accuracy",
  safety: "Safety",
  actionability: "Actionability",
  clarity: "Clarity",
  compliance: "Compliance",
  technical_depth: "Technical Depth",
  ethics: "Ethics",
};
