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
} from "lucide-react";
import clsx from "clsx";

const NAV = [
  { href: "/annotate", label: "Annotate", icon: MessageSquareDiff, description: "Label preference pairs" },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, description: "Collection progress" },
  { href: "/domains", label: "Domains", icon: BookOpen, description: "Platform taxonomy" },
];

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
          <div className="text-xs font-semibold text-bp-text tracking-wide leading-none">ZUUP</div>
          <div className="text-2xs text-bp-text-muted leading-none mt-0.5 tracking-widest uppercase">Preferences</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 px-2 space-y-0.5">
        <p className="px-2 pt-1 pb-2 text-2xs font-semibold text-bp-text-disabled uppercase tracking-widest">
          Workspace
        </p>
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = path.startsWith(href);
          return (
            <Link
              key={href}
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
        })}

        <div className="pt-3">
          <p className="px-2 pt-1 pb-2 text-2xs font-semibold text-bp-text-disabled uppercase tracking-widest">
            Developer
          </p>
          <Link
            href="/api-docs"
            className={clsx(
              "flex items-center gap-3 px-3 py-2 rounded text-sm transition-all duration-100 group",
              path.startsWith("/api-docs")
                ? "bg-bp-blue/15 text-bp-text border border-bp-blue/20"
                : "text-bp-text-secondary hover:bg-bp-dark1 hover:text-bp-text border border-transparent"
            )}
          >
            <Code2
              className={clsx(
                "w-4 h-4 shrink-0 transition-colors",
                path.startsWith("/api-docs") ? "text-bp-blue" : "text-bp-text-muted group-hover:text-bp-text-secondary"
              )}
            />
            API Reference
          </Link>
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
