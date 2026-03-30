import TopBar from "@/components/layout/TopBar";
import { Terminal, Lock, Globe } from "lucide-react";

const ENDPOINTS = [
  {
    method: "GET",
    path: "/api/health",
    description: "Health check and HF sync status",
    auth: false,
    response: `{ "status": "ok", "sync_status": "active", "last_sync": "2024-03-30T12:00:00Z" }`,
  },
  {
    method: "GET",
    path: "/api/stats",
    description: "Annotation counts by domain",
    auth: false,
    response: `{ "total": 1755, "by_domain": { "procurement": { "collected": 500, "target": 500 } } }`,
  },
  {
    method: "GET",
    path: "/api/domains",
    description: "List all domains with metadata",
    auth: false,
    response: `[{ "id": "procurement", "name": "Fed/SLED Procurement", "icon": "📋", ... }]`,
  },
  {
    method: "POST",
    path: "/api/preferences",
    description: "Submit a preference annotation record",
    auth: true,
    body: `{
  "domain": "procurement",
  "category": "rfp_analysis",
  "prompt": "Analyze this RFP...",
  "response_a": "Response A...",
  "response_b": "Response B...",
  "preference": "A",
  "annotator_id": "user_123",
  "dimension_scores": {
    "accuracy": 4,
    "compliance": 5,
    "actionability": 3,
    "clarity": 4
  }
}`,
    response: `{ "success": true, "record_id": "abc123def456" }`,
  },
  {
    method: "POST",
    path: "/api/export",
    description: "Export dataset in DPO-ready or raw JSONL format",
    auth: true,
    body: `{ "format": "dpo", "domain": "procurement" }`,
    response: `[{ "prompt": "...", "chosen": "...", "rejected": "..." }]`,
  },
];

const METHOD_COLORS: Record<string, string> = {
  GET: "text-bp-green bg-bp-green/10 border-bp-green/20",
  POST: "text-bp-blue bg-bp-blue/10 border-bp-blue/20",
  DELETE: "text-bp-red bg-bp-red/10 border-bp-red/20",
};

export default function ApiDocsPage() {
  return (
    <>
      <TopBar title="API Reference" subtitle="REST endpoints for preference collection and export" />
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-5 py-5 space-y-4">

          {/* Auth callout */}
          <div className="flex items-start gap-3 px-4 py-3 rounded border border-bp-orange/30 bg-bp-orange/10">
            <Lock className="w-4 h-4 text-bp-orange mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold text-bp-text">Authentication</p>
              <p className="text-xs text-bp-text-secondary mt-0.5">
                Protected endpoints require an <code className="font-mono text-bp-orange bg-bp-dark3 px-1 py-0.5 rounded">X-API-Key</code> header.
                Contact your workspace admin for credentials.
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

          {/* Endpoints */}
          {ENDPOINTS.map((ep) => (
            <div key={ep.path} className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
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
          ))}

          {/* cURL example */}
          <div className="rounded border border-bp-border bg-bp-dark2 overflow-hidden">
            <div className="flex items-center gap-2 px-4 py-2.5 border-b border-bp-border">
              <Terminal className="w-4 h-4 text-bp-text-muted" />
              <span className="text-2xs font-semibold text-bp-text-muted uppercase tracking-widest">cURL Example</span>
            </div>
            <pre className="text-xs font-mono text-bp-text-secondary bg-bp-dark3 p-4 overflow-x-auto leading-relaxed">
{`curl -X POST https://your-api/api/preferences \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-key" \\
  -d '{
    "domain": "procurement",
    "category": "rfp_analysis",
    "prompt": "Analyze this RFP...",
    "response_a": "...",
    "response_b": "...",
    "preference": "A",
    "annotator_id": "user_123",
    "dimension_scores": {"accuracy": 4, "compliance": 5}
  }'`}
            </pre>
          </div>

        </div>
      </div>
    </>
  );
}
