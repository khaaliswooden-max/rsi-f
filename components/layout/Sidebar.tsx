"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquareDiff,
  BookOpen,
  Code2,
  Activity,
  Database,
  BarChart3,
} from "lucide-react";
import clsx from "clsx";

const ANNOTATION_NAV = [
  { href: "/annotate", label: "Annotate", icon: MessageSquareDiff, description: "Label preference pairs" },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, description: "Collection progress" },
  { href: "/domains", label: "Domains", icon: BookOpen, description: "Platform taxonomy" },
];

const RESEARCH_NAV = [
  { href: "/research", label: "Research", icon: BarChart3, description: "Wofo filers, backtest, RSI loop" },
];

function NavItem({
  href,
  label,
  icon: Icon,
  active,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={clsx(
        "flex items-center gap-3 px-3 py-2 rounded text-sm transition-all duration-100 group",
        active
          ? "bg-bp-blue/15 text-bp-text border border-bp-blue/20"
          : "text-bp-text-secondary hover:bg-bp-dark1 hover:text-bp-text border border-transparent"
      )}
    >
      <Icon
        className={clsx(
          "w-4 h-4 shrink-0 transition-colors",
          active ? "text-bp-blue" : "text-bp-text-muted group-hover:text-bp-text-secondary"
        )}
      />
      {label}
    </Link>
  );
}

export default function Sidebar() {
  const path = usePathname();

  return (
    <aside className="flex flex-col w-[220px] min-h-screen bg-bp-dark2 border-r border-bp-border shrink-0">
      {/* Wordmark */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-bp-border">
        <div className="flex items-center justify-center w-7 h-7 rounded bg-bp-blue/20 border border-bp-blue/30">
          <Database className="w-4 h-4 text-bp-blue" />
        </div>
        <div>
          <div className="text-xs font-semibold text-bp-text tracking-wide leading-none">RSI-F</div>
          <div className="text-2xs text-bp-text-muted leading-none mt-0.5 tracking-widest uppercase">
            Preferences · Wofo
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 px-2 space-y-0.5">
        <p className="px-2 pt-1 pb-2 text-2xs font-semibold text-bp-text-disabled uppercase tracking-widest">
          Annotation
        </p>
        {ANNOTATION_NAV.map(({ href, label, icon }) => (
          <NavItem key={href} href={href} label={label} icon={icon} active={path.startsWith(href)} />
        ))}

        <div className="pt-3">
          <p className="px-2 pt-1 pb-2 text-2xs font-semibold text-bp-text-disabled uppercase tracking-widest">
            Wooden FO
          </p>
          {RESEARCH_NAV.map(({ href, label, icon }) => (
            <NavItem key={href} href={href} label={label} icon={icon} active={path.startsWith(href)} />
          ))}
        </div>

        <div className="pt-3">
          <p className="px-2 pt-1 pb-2 text-2xs font-semibold text-bp-text-disabled uppercase tracking-widest">
            Developer
          </p>
          <NavItem href="/api-docs" label="API Reference" icon={Code2} active={path.startsWith("/api-docs")} />
        </div>
      </nav>

      {/* Status indicator */}
      <div className="px-3 py-3 border-t border-bp-border">
        <div className="flex items-center gap-2 px-2 py-1.5 rounded bg-bp-dark3 border border-bp-border">
          <Activity className="w-3 h-3 text-bp-green shrink-0" />
          <span className="text-2xs text-bp-text-muted font-mono">HF SYNC ACTIVE</span>
        </div>
      </div>
    </aside>
  );
}
