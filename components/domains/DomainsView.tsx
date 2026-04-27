"use client";

import { useEffect, useState } from "react";
import { ChevronRight, Search, Target, Layers, Loader2, WifiOff } from "lucide-react";
import clsx from "clsx";
import {
  api,
  DIMENSION_LABELS,
  FALLBACK_DOMAINS,
  type DomainInfo,
} from "@/src/utils/api";

const DOMAIN_DETAILS: Record<string, { description: string; scoring: string[]; sample_task: string }> = {
  procurement: {
    description: "Federal and state/local government procurement analysis, covering FAR/DFARS compliance, RFP interpretation, proposal writing, vendor evaluation, and contract management.",
    scoring: ["accuracy", "compliance", "actionability", "clarity"],
    sample_task: "Analyze an RFP for a DISA cloud migration and identify key evaluation criteria.",
  },
  biomedical: {
    description: "Gut-brain axis biosensor development, neural signal processing, clinical validation protocols, and FDA/EU regulatory pathway planning for implantable and wearable medical devices.",
    scoring: ["accuracy", "safety", "technical_depth", "clarity"],
    sample_task: "Design a validation protocol for a novel neural impedance biosensor targeting IBD monitoring.",
  },
  defense_wm: {
    description: "Construction and maintenance of persistent 3D world models from multi-sensor ISR data. Covers scene reconstruction, change detection, geospatial fusion, and threat characterization.",
    scoring: ["accuracy", "technical_depth", "actionability", "safety"],
    sample_task: "Describe a sensor fusion pipeline for building a persistent urban terrain model from SAR and EO/IR inputs.",
  },
  legacy_refactor: {
    description: "Modernization of COBOL, PL/I, and other legacy mainframe systems. Topics include API extraction, data migration, test generation, and incremental refactoring strategies.",
    scoring: ["accuracy", "actionability", "technical_depth", "clarity"],
    sample_task: "Generate a migration roadmap for a 500k-line COBOL payroll system targeting a microservices architecture.",
  },
  autonomy: {
    description: "Agentic AI systems design, multi-agent orchestration, safety constraints, tool-use patterns, and evaluation frameworks for autonomous decision-making pipelines.",
    scoring: ["accuracy", "safety", "technical_depth", "clarity"],
    sample_task: "Design a safety constraint framework for an autonomous procurement agent operating in a government environment.",
  },
  halal: {
    description: "Halal certification processes, supply chain traceability, ingredient analysis, and audit preparation for food, pharmaceuticals, and consumer goods manufacturers.",
    scoring: ["accuracy", "compliance", "ethics", "clarity"],
    sample_task: "Evaluate a food product supply chain for Halal compliance across three tiers of suppliers.",
  },
  quantum_arch: {
    description: "Historical and cultural artifact reconstruction using quantum-classical algorithms, photogrammetry, and multi-spectral analysis for digital preservation and provenance verification.",
    scoring: ["accuracy", "technical_depth", "actionability", "clarity"],
    sample_task: "Propose a 3D reconstruction workflow for a partially-deteriorated ancient manuscript collection.",
  },
  mobile_dc: {
    description: "Edge data center deployment in DDIL (Denied, Disrupted, Intermittent, Limited) environments. Covers containerization, power management, connectivity, and ruggedized hardware.",
    scoring: ["accuracy", "actionability", "technical_depth", "clarity"],
    sample_task: "Design a deployment architecture for a containerized AI inference workload in a forward-deployed mobile data center.",
  },
  hubzone: {
    description: "HUBZone program eligibility determination, certification preparation, teaming arrangements, and set-aside strategy for small businesses pursuing federal contracting.",
    scoring: ["accuracy", "compliance", "actionability", "clarity"],
    sample_task: "Assess HUBZone eligibility for a 25-person IT firm with offices in two census tracts.",
  },
  ingestible: {
    description: "Ingestible biosensor capsule design for in-vivo gut monitoring, including sensor modalities, data telemetry, power harvesting, and biocompatibility/regulatory considerations.",
    scoring: ["accuracy", "safety", "technical_depth", "clarity"],
    sample_task: "Design a data telemetry protocol for a capsule-based pH and microbiome sensor traversing the GI tract.",
  },
};

export default function DomainsView() {
  const [domains, setDomains] = useState<DomainInfo[]>(FALLBACK_DOMAINS);
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string | null>(FALLBACK_DOMAINS[0].id);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api
      .domains()
      .then((d) => {
        if (cancelled) return;
        if (Array.isArray(d) && d.length > 0) {
          setDomains(d);
          setExpanded(d[0].id);
          setOffline(false);
        }
      })
      .catch(() => !cancelled && setOffline(true))
      .finally(() => !cancelled && setLoading(false));
    return () => { cancelled = true; };
  }, []);

  const filtered = domains.filter(
    (d) =>
      d.name.toLowerCase().includes(search.toLowerCase()) ||
      d.platform.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-4xl mx-auto px-5 py-5 space-y-4">

        {(loading || offline) && (
          <div
            className={clsx(
              "flex items-center gap-2 px-3 py-2 rounded border text-2xs",
              offline
                ? "bg-bp-orange/10 border-bp-orange/30 text-bp-orange"
                : "bg-bp-dark2 border-bp-border text-bp-text-muted"
            )}
          >
            {offline ? <WifiOff className="w-3.5 h-3.5" /> : <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            {offline
              ? "Backend offline — showing static taxonomy. Live collection counts unavailable."
              : "Loading domain taxonomy..."}
          </div>
        )}

        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-bp-text-muted pointer-events-none" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search domains or platforms..."
            className="w-full bg-bp-dark2 border border-bp-border rounded pl-9 pr-4 py-2.5 text-sm text-bp-text placeholder:text-bp-text-disabled focus:border-bp-blue focus:outline-none transition-colors"
          />
        </div>

        <div className="space-y-2">
          {filtered.map((domain) => {
            const detail = DOMAIN_DETAILS[domain.id];
            const isOpen = expanded === domain.id;
            const description = domain.description || detail?.description || "—";
            const scoring = detail?.scoring;
            const sampleTask = detail?.sample_task;
            const pct = domain.min_samples > 0
              ? Math.min(100, Math.round((domain.collected / domain.min_samples) * 100))
              : 0;

            return (
              <div
                key={domain.id}
                className="rounded border border-bp-border bg-bp-dark2 overflow-hidden"
              >
                <button
                  onClick={() => setExpanded(isOpen ? null : domain.id)}
                  className="w-full flex items-center gap-4 px-4 py-3 hover:bg-bp-dark1/50 transition-colors text-left"
                >
                  <span className="text-xl">{domain.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-bp-text">{domain.name}</span>
                      <span className="text-2xs text-bp-text-muted px-1.5 py-0.5 rounded bg-bp-dark3 border border-bp-border font-mono">
                        {domain.platform}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-2xs text-bp-text-muted">
                        {domain.categories.length} categories
                      </span>
                      <span className="text-2xs text-bp-text-disabled">·</span>
                      <span className="text-2xs text-bp-text-muted font-mono">
                        {domain.collected} / {domain.min_samples} samples
                      </span>
                      <span className="text-2xs text-bp-text-disabled">·</span>
                      <div className="flex items-center gap-1.5">
                        <div className="w-16 h-1.5 rounded-full bg-bp-dark3">
                          <div
                            className={clsx(
                              "h-full rounded-full",
                              pct >= 100 ? "bg-bp-green" : pct > 0 ? "bg-bp-blue" : "bg-bp-border"
                            )}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className={clsx("text-2xs font-mono", pct >= 100 ? "text-bp-green" : "text-bp-text-muted")}>
                          {pct}%
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight
                    className={clsx(
                      "w-4 h-4 text-bp-text-muted transition-transform duration-150 shrink-0",
                      isOpen && "rotate-90"
                    )}
                  />
                </button>

                {isOpen && (
                  <div className="border-t border-bp-border px-4 py-4 space-y-4">
                    <p className="text-sm text-bp-text-secondary leading-relaxed">{description}</p>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="flex items-center gap-1.5 mb-2">
                          <Layers className="w-3.5 h-3.5 text-bp-text-muted" />
                          <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">
                            Categories
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {domain.categories.map((c) => (
                            <span
                              key={c}
                              className="text-2xs px-2 py-1 rounded bg-bp-dark3 border border-bp-border text-bp-text-secondary font-mono"
                            >
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>

                      {scoring && (
                        <div>
                          <div className="flex items-center gap-1.5 mb-2">
                            <Target className="w-3.5 h-3.5 text-bp-text-muted" />
                            <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">
                              Scoring Dimensions
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {scoring.map((dim, i) => (
                              <span
                                key={dim}
                                className={clsx(
                                  "text-2xs px-2 py-1 rounded border font-medium",
                                  i < 2
                                    ? "bg-bp-blue/10 border-bp-blue/20 text-bp-blue"
                                    : "bg-bp-dark3 border-bp-border text-bp-text-secondary"
                                )}
                              >
                                {DIMENSION_LABELS[dim] ?? dim}
                                {i < 2 && <span className="ml-1 opacity-60">●</span>}
                              </span>
                            ))}
                          </div>
                          <p className="text-2xs text-bp-text-disabled mt-1.5">● Critical dimensions</p>
                        </div>
                      )}
                    </div>

                    {sampleTask && (
                      <div className="rounded bg-bp-dark3 border border-bp-border px-3 py-2.5">
                        <p className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest mb-1">
                          Example Task
                        </p>
                        <p className="text-xs text-bp-text-secondary leading-relaxed">{sampleTask}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
