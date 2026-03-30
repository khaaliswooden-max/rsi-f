"use client";

import { Database, TrendingUp, Users, Award, ArrowUpRight } from "lucide-react";
import clsx from "clsx";
import { DOMAINS } from "@/src/utils/api";

interface StatCardProps {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ElementType;
  intent?: "blue" | "green" | "orange" | "red";
  trend?: string;
}

function StatCard({ label, value, sub, icon: Icon, intent = "blue", trend }: StatCardProps) {
  const colors = {
    blue: { bg: "bg-bp-blue/10", border: "border-bp-blue/20", text: "text-bp-blue", accent: "text-bp-blue" },
    green: { bg: "bg-bp-green/10", border: "border-bp-green/20", text: "text-bp-green", accent: "text-bp-green" },
    orange: { bg: "bg-bp-orange/10", border: "border-bp-orange/20", text: "text-bp-orange", accent: "text-bp-orange" },
    red: { bg: "bg-bp-red/10", border: "border-bp-red/20", text: "text-bp-red", accent: "text-bp-red" },
  };
  const c = colors[intent];
  return (
    <div className="rounded border border-bp-border bg-bp-dark2 p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-bp-text-muted uppercase tracking-widest font-semibold">{label}</p>
          <p className="mt-2 text-2xl font-bold text-bp-text tabular-nums">{value}</p>
          {sub && <p className="mt-0.5 text-xs text-bp-text-muted">{sub}</p>}
        </div>
        <div className={clsx("p-2 rounded border", c.bg, c.border)}>
          <Icon className={clsx("w-4 h-4", c.text)} />
        </div>
      </div>
      {trend && (
        <div className="mt-3 flex items-center gap-1 text-xs text-bp-green">
          <ArrowUpRight className="w-3.5 h-3.5" />
          {trend}
        </div>
      )}
    </div>
  );
}

function DomainProgressRow({ domain }: { domain: (typeof DOMAINS)[0] }) {
  const pct = domain.min_samples > 0 ? Math.min(100, Math.round((domain.collected / domain.min_samples) * 100)) : 0;
  const isComplete = pct >= 100;
  const isGood = pct >= 60;

  const barColor = isComplete ? "bg-bp-green" : isGood ? "bg-bp-blue" : pct > 0 ? "bg-bp-orange" : "bg-bp-border";
  const statusColor = isComplete ? "text-bp-green" : isGood ? "text-bp-blue" : pct > 0 ? "text-bp-orange" : "text-bp-text-disabled";
  const statusLabel = isComplete ? "COMPLETE" : isGood ? "IN PROGRESS" : pct > 0 ? "STARTED" : "PENDING";

  return (
    <div className="flex items-center gap-4 py-3 border-b border-bp-border last:border-0 hover:bg-bp-dark1/40 px-4 -mx-4 transition-colors">
      {/* Icon + name */}
      <div className="flex items-center gap-2.5 w-56 shrink-0">
        <span className="text-base">{domain.icon}</span>
        <div className="min-w-0">
          <p className="text-sm text-bp-text font-medium truncate">{domain.name}</p>
          <p className="text-2xs text-bp-text-muted">{domain.platform}</p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="flex-1 min-w-0">
        <div className="flex justify-between mb-1.5">
          <span className="text-2xs text-bp-text-muted font-mono tabular-nums">
            {domain.collected.toLocaleString()} / {domain.min_samples.toLocaleString()}
          </span>
          <span className={clsx("text-2xs font-semibold font-mono tabular-nums", statusColor)}>
            {pct}%
          </span>
        </div>
        <div className="h-1.5 rounded-full bg-bp-dark3 overflow-hidden">
          <div
            className={clsx("h-full rounded-full transition-all duration-500", barColor)}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Status badge */}
      <div className="w-28 flex justify-end shrink-0">
        <span
          className={clsx(
            "text-2xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded border",
            isComplete && "text-bp-green bg-bp-green/10 border-bp-green/20",
            isGood && !isComplete && "text-bp-blue bg-bp-blue/10 border-bp-blue/20",
            !isGood && pct > 0 && "text-bp-orange bg-bp-orange/10 border-bp-orange/20",
            pct === 0 && "text-bp-text-disabled bg-bp-dark3 border-bp-border"
          )}
        >
          {statusLabel}
        </span>
      </div>
    </div>
  );
}

export default function DashboardView() {
  const totalCollected = DOMAINS.reduce((s, d) => s + d.collected, 0);
  const totalTarget = DOMAINS.reduce((s, d) => s + d.min_samples, 0);
  const completeDomains = DOMAINS.filter((d) => d.collected >= d.min_samples).length;
  const overallPct = Math.round((totalCollected / totalTarget) * 100);

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="max-w-6xl mx-auto px-5 py-5 space-y-5">

        {/* Stat cards */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard
            label="Total Annotations"
            value={totalCollected.toLocaleString()}
            sub={`${overallPct}% of target`}
            icon={Database}
            intent="blue"
            trend="+50 today"
          />
          <StatCard
            label="Domains Active"
            value={`${completeDomains} / ${DOMAINS.length}`}
            sub="platforms covered"
            icon={TrendingUp}
            intent="green"
          />
          <StatCard
            label="Annotators"
            value="12"
            sub="unique contributors"
            icon={Users}
            intent="orange"
          />
          <StatCard
            label="Target Coverage"
            value={`${overallPct}%`}
            sub={`${totalTarget.toLocaleString()} total goal`}
            icon={Award}
            intent={overallPct >= 80 ? "green" : overallPct >= 40 ? "orange" : "red"}
          />
        </div>

        {/* Domain progress table */}
        <div className="rounded border border-bp-border bg-bp-dark2">
          <div className="flex items-center justify-between px-4 py-3 border-b border-bp-border">
            <div>
              <h2 className="text-sm font-semibold text-bp-text">Collection Progress by Domain</h2>
              <p className="text-xs text-bp-text-muted mt-0.5">
                {DOMAINS.filter((d) => d.collected > 0).length} of {DOMAINS.length} domains have data
              </p>
            </div>
            <div className="flex items-center gap-3 text-2xs text-bp-text-muted">
              {(
                [
                  { color: "bg-bp-green", label: "Complete" },
                  { color: "bg-bp-blue", label: "In progress" },
                  { color: "bg-bp-orange", label: "Started" },
                  { color: "bg-bp-border", label: "Pending" },
                ] as const
              ).map(({ color, label }) => (
                <div key={label} className="flex items-center gap-1.5">
                  <span className={clsx("w-2 h-2 rounded-full", color)} />
                  {label}
                </div>
              ))}
            </div>
          </div>
          <div className="px-4 py-1">
            {DOMAINS.map((d) => (
              <DomainProgressRow key={d.id} domain={d} />
            ))}
          </div>
        </div>

        {/* Overall progress bar */}
        <div className="rounded border border-bp-border bg-bp-dark2 px-4 py-4">
          <div className="flex justify-between mb-2">
            <span className="text-xs font-semibold text-bp-text-secondary uppercase tracking-widest">
              Overall Collection Progress
            </span>
            <span className="text-xs font-bold text-bp-text font-mono tabular-nums">
              {totalCollected.toLocaleString()} / {totalTarget.toLocaleString()} ({overallPct}%)
            </span>
          </div>
          <div className="h-3 rounded-full bg-bp-dark3 border border-bp-border overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-bp-blue to-bp-green transition-all duration-700"
              style={{ width: `${overallPct}%` }}
            />
          </div>
          <div className="flex justify-between mt-2">
            <span className="text-2xs text-bp-text-disabled">0</span>
            <span className="text-2xs text-bp-text-disabled">{totalTarget.toLocaleString()} target</span>
          </div>
        </div>

      </div>
    </div>
  );
}
