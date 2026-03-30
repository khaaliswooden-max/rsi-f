"use client";

import { useState, useCallback } from "react";
import {
  ChevronDown,
  RefreshCw,
  Send,
  ThumbsUp,
  ThumbsDown,
  Minus,
  AlertCircle,
  CheckCircle2,
  Loader2,
  User,
  Tag,
  SlidersHorizontal,
} from "lucide-react";
import clsx from "clsx";
import { DOMAINS, DIMENSION_LABELS, type PreferenceSubmission } from "@/src/utils/api";

const DIMENSIONS_BY_DOMAIN: Record<string, string[]> = {
  procurement: ["accuracy", "compliance", "actionability", "clarity"],
  biomedical: ["accuracy", "safety", "technical_depth", "clarity"],
  defense_wm: ["accuracy", "technical_depth", "actionability", "safety"],
  halal: ["accuracy", "compliance", "ethics", "clarity"],
  default: ["accuracy", "safety", "actionability", "clarity"],
};

const SAMPLE_PROMPTS: Record<string, string> = {
  procurement: "You are evaluating a federal procurement assistant. Analyze the following solicitation clause and identify any potential FAR/DFARS compliance issues:\n\n\"The contractor shall deliver all end items within 30 days of award. Late delivery penalties of 2% per day apply. The contractor bears full liability for any subcontractor delays.\"\n\nProvide a detailed compliance analysis with specific FAR references.",
  defense_wm: "Given a set of multi-spectral satellite imagery from a 5km² urban area, describe an approach to build a persistent 3D world model that supports real-time ISR tasking. Include sensor fusion strategy, uncertainty quantification, and update cadence.",
  default: "A user asks: 'What is the best approach for implementing a microservices architecture for a legacy COBOL system migration?' Provide a detailed technical recommendation.",
};

const SAMPLE_RESPONSES = {
  a: "This is **Response A** — a high-quality, detailed answer that addresses all aspects of the query with specific technical depth, regulatory citations, and actionable recommendations. The response is well-structured and demonstrates domain expertise.\n\nKey points covered:\n1. Primary regulatory framework analysis\n2. Risk mitigation strategies\n3. Step-by-step implementation guidance\n4. Common pitfalls and how to avoid them",
  b: "This is **Response B** — an alternative approach that may prioritize different aspects. While covering the core requirements, it takes a different angle on the problem, possibly more concise or focused on a specific subset of concerns.\n\nThe response provides a direct answer with practical guidance, though may lack some depth compared to Response A in certain technical areas.",
};

type Preference = "A" | "B" | "tie" | null;

interface DimensionScores {
  [key: string]: number;
}

export default function AnnotationView() {
  const [annotatorId, setAnnotatorId] = useState("");
  const [selectedDomain, setSelectedDomain] = useState(DOMAINS[0].id);
  const [selectedCategory, setSelectedCategory] = useState(DOMAINS[0].categories[0]);
  const [prompt, setPrompt] = useState(SAMPLE_PROMPTS.procurement);
  const [responseA, setResponseA] = useState(SAMPLE_RESPONSES.a);
  const [responseB, setResponseB] = useState(SAMPLE_RESPONSES.b);
  const [preference, setPreference] = useState<Preference>(null);
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<"idle" | "success" | "error">("idle");
  const [submitMsg, setSubmitMsg] = useState("");

  const domain = DOMAINS.find((d) => d.id === selectedDomain)!;
  const dimensions = DIMENSIONS_BY_DOMAIN[selectedDomain] || DIMENSIONS_BY_DOMAIN.default;

  const [scores, setScores] = useState<DimensionScores>(() =>
    Object.fromEntries(dimensions.map((d) => [d, 3]))
  );

  const handleDomainChange = (id: string) => {
    setSelectedDomain(id);
    const d = DOMAINS.find((x) => x.id === id)!;
    setSelectedCategory(d.categories[0]);
    const dims = DIMENSIONS_BY_DOMAIN[id] || DIMENSIONS_BY_DOMAIN.default;
    setScores(Object.fromEntries(dims.map((d) => [d, 3])));
    setPreference(null);
    setPrompt(SAMPLE_PROMPTS[id] || SAMPLE_PROMPTS.default);
  };

  const handleLoadPair = useCallback(async () => {
    setLoading(true);
    setPreference(null);
    setSubmitStatus("idle");
    // In production: const pair = await api.loadPair(selectedDomain, selectedCategory);
    await new Promise((r) => setTimeout(r, 600));
    setPrompt(SAMPLE_PROMPTS[selectedDomain] || SAMPLE_PROMPTS.default);
    setResponseA(SAMPLE_RESPONSES.a);
    setResponseB(SAMPLE_RESPONSES.b);
    setLoading(false);
  }, [selectedDomain, selectedCategory]);

  const handleSubmit = async () => {
    if (!preference || !annotatorId.trim()) return;
    setSubmitting(true);
    setSubmitStatus("idle");
    try {
      // In production: await api.submitPreference({ ... })
      await new Promise((r) => setTimeout(r, 800));
      setSubmitStatus("success");
      setSubmitMsg("Preference recorded successfully.");
      setPreference(null);
      setNotes("");
    } catch {
      setSubmitStatus("error");
      setSubmitMsg("Failed to submit. Check your connection.");
    } finally {
      setSubmitting(false);
    }
  };

  const scoreColor = (v: number) => {
    if (v >= 4) return "text-bp-green";
    if (v >= 3) return "text-bp-blue";
    if (v >= 2) return "text-bp-orange";
    return "text-bp-red";
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Config bar */}
      <div className="shrink-0 flex items-center gap-3 px-5 py-3 bg-bp-dark2 border-b border-bp-border">
        {/* Annotator ID */}
        <div className="flex items-center gap-2 min-w-0">
          <User className="w-3.5 h-3.5 text-bp-text-muted shrink-0" />
          <input
            type="text"
            value={annotatorId}
            onChange={(e) => setAnnotatorId(e.target.value)}
            placeholder="Annotator ID"
            className="w-36 bg-bp-dark3 border border-bp-border rounded px-2.5 py-1.5 text-xs text-bp-text placeholder:text-bp-text-disabled focus:border-bp-blue focus:outline-none transition-colors"
          />
        </div>

        <div className="w-px h-4 bg-bp-border" />

        {/* Domain selector */}
        <div className="flex items-center gap-2">
          <Tag className="w-3.5 h-3.5 text-bp-text-muted shrink-0" />
          <div className="relative">
            <select
              value={selectedDomain}
              onChange={(e) => handleDomainChange(e.target.value)}
              className="appearance-none bg-bp-dark3 border border-bp-border rounded pl-2.5 pr-7 py-1.5 text-xs text-bp-text focus:border-bp-blue focus:outline-none transition-colors cursor-pointer"
            >
              {DOMAINS.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.icon} {d.name}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-bp-text-muted pointer-events-none" />
          </div>
          <div className="relative">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="appearance-none bg-bp-dark3 border border-bp-border rounded pl-2.5 pr-7 py-1.5 text-xs text-bp-text focus:border-bp-blue focus:outline-none transition-colors cursor-pointer"
            >
              {domain.categories.map((c) => (
                <option key={c} value={c}>
                  {c.replace(/_/g, " ")}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-bp-text-muted pointer-events-none" />
          </div>
        </div>

        <div className="flex-1" />

        <button
          onClick={handleLoadPair}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium bg-bp-dark3 border border-bp-border text-bp-text-secondary hover:text-bp-text hover:border-bp-blue/40 transition-all disabled:opacity-50"
        >
          <RefreshCw className={clsx("w-3.5 h-3.5", loading && "animate-spin")} />
          Load New Pair
        </button>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-5 py-5 space-y-4">
          {/* Prompt */}
          <section className="rounded border border-bp-border bg-bp-dark2">
            <div className="flex items-center justify-between px-4 py-2.5 border-b border-bp-border">
              <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">Prompt</span>
              <span className="text-2xs font-mono text-bp-text-disabled px-1.5 py-0.5 rounded bg-bp-dark3 border border-bp-border">
                {domain.icon} {domain.name} / {selectedCategory.replace(/_/g, " ")}
              </span>
            </div>
            <div className="px-4 py-3">
              {loading ? (
                <div className="flex items-center gap-2 text-bp-text-muted text-sm py-2">
                  <Loader2 className="w-4 h-4 animate-spin" /> Loading prompt...
                </div>
              ) : (
                <p className="text-sm text-bp-text leading-relaxed whitespace-pre-wrap font-mono">{prompt}</p>
              )}
            </div>
          </section>

          {/* Response pair */}
          <div className="grid grid-cols-2 gap-4">
            {(["A", "B"] as const).map((label) => {
              const text = label === "A" ? responseA : responseB;
              const selected = preference === label;
              const color = label === "A" ? "bp-blue" : "bp-green";
              return (
                <section
                  key={label}
                  className={clsx(
                    "rounded border transition-all duration-150",
                    selected
                      ? label === "A"
                        ? "border-bp-blue bg-bp-blue/5 shadow-[0_0_0_1px_rgba(76,144,240,0.2)]"
                        : "border-bp-green bg-bp-green/5 shadow-[0_0_0_1px_rgba(50,164,103,0.2)]"
                      : "border-bp-border bg-bp-dark2 hover:border-bp-border"
                  )}
                >
                  <div className="flex items-center justify-between px-4 py-2.5 border-b border-bp-border">
                    <div className="flex items-center gap-2">
                      <span
                        className={clsx(
                          "flex items-center justify-center w-5 h-5 rounded text-2xs font-bold border",
                          label === "A"
                            ? "bg-bp-blue/20 border-bp-blue/40 text-bp-blue"
                            : "bg-bp-green/20 border-bp-green/40 text-bp-green"
                        )}
                      >
                        {label}
                      </span>
                      <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">
                        Response {label}
                      </span>
                    </div>
                    {selected && (
                      <CheckCircle2
                        className={clsx("w-4 h-4", label === "A" ? "text-bp-blue" : "text-bp-green")}
                      />
                    )}
                  </div>
                  <div className="px-4 py-3 min-h-[160px]">
                    {loading ? (
                      <div className="flex items-center gap-2 text-bp-text-muted text-sm py-2">
                        <Loader2 className="w-4 h-4 animate-spin" /> Loading...
                      </div>
                    ) : (
                      <p className="text-sm text-bp-text-secondary leading-relaxed whitespace-pre-wrap">{text}</p>
                    )}
                  </div>
                </section>
              );
            })}
          </div>

          {/* Scoring + preference */}
          <div className="grid grid-cols-[1fr_320px] gap-4">
            {/* Dimension scores */}
            <section className="rounded border border-bp-border bg-bp-dark2">
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-bp-border">
                <SlidersHorizontal className="w-3.5 h-3.5 text-bp-text-muted" />
                <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">Quality Dimensions</span>
              </div>
              <div className="px-4 py-3 grid grid-cols-2 gap-x-8 gap-y-4">
                {dimensions.map((dim) => (
                  <div key={dim}>
                    <div className="flex justify-between items-center mb-1.5">
                      <label className="text-xs text-bp-text-secondary font-medium">
                        {DIMENSION_LABELS[dim] ?? dim}
                      </label>
                      <span className={clsx("text-xs font-bold font-mono", scoreColor(scores[dim]))}>
                        {scores[dim]}/5
                      </span>
                    </div>
                    <input
                      type="range"
                      min={1}
                      max={5}
                      step={1}
                      value={scores[dim] ?? 3}
                      onChange={(e) =>
                        setScores((s) => ({ ...s, [dim]: Number(e.target.value) }))
                      }
                      className="w-full"
                    />
                    <div className="flex justify-between mt-0.5">
                      <span className="text-2xs text-bp-text-disabled">Poor</span>
                      <span className="text-2xs text-bp-text-disabled">Excellent</span>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Preference + submit */}
            <section className="rounded border border-bp-border bg-bp-dark2 flex flex-col">
              <div className="px-4 py-2.5 border-b border-bp-border">
                <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">
                  Preference
                </span>
              </div>
              <div className="flex-1 px-4 py-3 space-y-3">
                {/* Preference buttons */}
                <div className="grid grid-cols-3 gap-2">
                  {(
                    [
                      { val: "A", label: "Prefer A", icon: ThumbsUp, color: "blue" },
                      { val: "tie", label: "Tie", icon: Minus, color: "muted" },
                      { val: "B", label: "Prefer B", icon: ThumbsDown, color: "green" },
                    ] as const
                  ).map(({ val, label, icon: Icon, color }) => {
                    const active = preference === val;
                    return (
                      <button
                        key={val}
                        onClick={() => setPreference(val)}
                        className={clsx(
                          "flex flex-col items-center gap-1.5 py-3 px-2 rounded border text-xs font-medium transition-all duration-100",
                          active && color === "blue" && "border-bp-blue bg-bp-blue/15 text-bp-blue",
                          active && color === "green" && "border-bp-green bg-bp-green/15 text-bp-green",
                          active && color === "muted" && "border-bp-border bg-bp-dark1 text-bp-text",
                          !active &&
                            "border-bp-border text-bp-text-muted hover:border-bp-border hover:text-bp-text hover:bg-bp-dark1"
                        )}
                      >
                        <Icon className="w-4 h-4" />
                        {label}
                      </button>
                    );
                  })}
                </div>

                {/* Notes */}
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional notes..."
                  rows={3}
                  className="w-full bg-bp-dark3 border border-bp-border rounded px-3 py-2 text-xs text-bp-text placeholder:text-bp-text-disabled resize-none focus:border-bp-blue focus:outline-none transition-colors"
                />

                {/* Status */}
                {submitStatus === "success" && (
                  <div className="flex items-center gap-2 px-3 py-2 rounded bg-bp-green/10 border border-bp-green/30 text-xs text-bp-green">
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    {submitMsg}
                  </div>
                )}
                {submitStatus === "error" && (
                  <div className="flex items-center gap-2 px-3 py-2 rounded bg-bp-red/10 border border-bp-red/30 text-xs text-bp-red">
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    {submitMsg}
                  </div>
                )}
                {!annotatorId.trim() && (
                  <p className="text-2xs text-bp-text-disabled">Set an Annotator ID to submit.</p>
                )}
              </div>

              {/* Submit */}
              <div className="px-4 pb-4">
                <button
                  onClick={handleSubmit}
                  disabled={!preference || !annotatorId.trim() || submitting}
                  className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded text-sm font-medium bg-bp-blue text-white hover:bg-bp-blue-dim active:bg-bp-blue-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  {submitting ? "Submitting..." : "Submit Annotation"}
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
