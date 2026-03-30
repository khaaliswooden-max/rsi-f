"use client";

import { useState, useEffect } from "react";
import { RefreshCw, AlertCircle } from "lucide-react";

interface TopBarProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function TopBar({ title, subtitle, actions }: TopBarProps) {
  const [time, setTime] = useState("");

  useEffect(() => {
    const update = () =>
      setTime(new Date().toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="flex items-center justify-between h-12 px-5 bg-bp-dark2 border-b border-bp-border shrink-0">
      <div className="flex items-center gap-3">
        <div>
          <h1 className="text-sm font-semibold text-bp-text leading-none">{title}</h1>
          {subtitle && <p className="text-2xs text-bp-text-muted mt-0.5">{subtitle}</p>}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {actions}
        <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-bp-dark3 border border-bp-border">
          <span className="w-1.5 h-1.5 rounded-full bg-bp-green animate-pulse-slow shrink-0" />
          <span className="text-2xs font-mono text-bp-text-muted tabular-nums">{time}</span>
        </div>
      </div>
    </header>
  );
}
