const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface DomainInfo {
  id: string;
  name: string;
  icon: string;
  platform: string;
  categories: string[];
  min_samples: number;
  collected: number;
}

export interface StatsResponse {
  total: number;
  by_domain: Record<string, { collected: number; target: number; annotators: number }>;
  last_sync: string | null;
}

export interface PreferenceSubmission {
  domain: string;
  category: string;
  prompt: string;
  response_a: string;
  response_b: string;
  preference: "A" | "B" | "tie";
  annotator_id: string;
  dimension_scores: Record<string, number>;
  notes?: string;
}

export interface ResponsePair {
  prompt: string;
  response_a: string;
  response_b: string;
  domain: string;
  category: string;
}

async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json", ...opts?.headers },
    ...opts,
  });
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`);
  return res.json();
}

export const api = {
  health: () => apiFetch<{ status: string; sync_status: string }>("/health"),
  stats: () => apiFetch<StatsResponse>("/stats"),
  domains: () => apiFetch<DomainInfo[]>("/domains"),
  loadPair: (domain: string, category: string) =>
    apiFetch<ResponsePair>("/load_pair", {
      method: "POST",
      body: JSON.stringify({ domain, category }),
    }),
  submitPreference: (data: PreferenceSubmission, apiKey: string) =>
    apiFetch<{ success: boolean; record_id: string }>("/preferences", {
      method: "POST",
      headers: { "X-API-Key": apiKey },
      body: JSON.stringify(data),
    }),
};

// ─── Static fallback data for demo/offline mode ────────────────────────────

export const DOMAINS: DomainInfo[] = [
  { id: "procurement", name: "Fed/SLED Procurement", icon: "📋", platform: "Aureon", categories: ["rfp_analysis", "proposal_writing", "compliance_check", "vendor_evaluation"], min_samples: 500, collected: 500 },
  { id: "biomedical", name: "Biomedical GB-CI", icon: "🧬", platform: "Symbion", categories: ["biosensor_design", "neural_analysis", "clinical_validation", "regulatory_pathway"], min_samples: 400, collected: 120 },
  { id: "legacy_refactor", name: "Legacy Refactoring", icon: "🔧", platform: "Relian", categories: ["cobol_modernization", "mainframe_migration", "api_extraction", "test_generation"], min_samples: 300, collected: 80 },
  { id: "autonomy", name: "Autonomy OS", icon: "🤖", platform: "Veyra", categories: ["agent_design", "safety_constraints", "tool_use", "multi_agent"], min_samples: 300, collected: 60 },
  { id: "defense_wm", name: "Defense World Models", icon: "🌐", platform: "Orb", categories: ["scene_reconstruction", "isr_analysis", "geospatial", "threat_assessment"], min_samples: 300, collected: 1000 },
  { id: "halal", name: "Halal Compliance", icon: "☪️", platform: "Civium", categories: ["certification", "supply_chain", "ingredient_analysis", "audit_prep"], min_samples: 200, collected: 50 },
  { id: "quantum_arch", name: "Quantum Archaeology", icon: "🏛️", platform: "QAWM", categories: ["historical_reconstruction", "artifact_analysis", "provenance", "3d_modeling"], min_samples: 200, collected: 0 },
  { id: "mobile_dc", name: "Mobile Data Center", icon: "📦", platform: "PodX", categories: ["edge_deployment", "ddil_ops", "power_management", "containerization"], min_samples: 200, collected: 15 },
  { id: "hubzone", name: "HUBZone Contracting", icon: "🏢", platform: "Aureon", categories: ["eligibility", "certification_prep", "teaming", "set_aside"], min_samples: 200, collected: 30 },
  { id: "ingestible", name: "Ingestible GB-CI", icon: "💊", platform: "Symbion HW", categories: ["capsule_design", "in_vivo_sensing", "data_telemetry", "regulatory"], min_samples: 200, collected: 0 },
];

export const DIMENSION_LABELS: Record<string, string> = {
  accuracy: "Accuracy",
  safety: "Safety",
  actionability: "Actionability",
  clarity: "Clarity",
  compliance: "Compliance",
  technical_depth: "Technical Depth",
  ethics: "Ethics",
};
