import { Radio, Zap } from "lucide-react";

interface HeaderProps {
  status?: "idle" | "loading" | "success" | "error";
  latency?: number | null;
  repo?: string | null;
  confidence?: number | null;
}

const statusConfig = {
  idle: { label: "Idle", color: "text-[#a78bfa] border-[#7c3aed]/20 bg-[#7c3aed]/10", dot: "bg-[#7c3aed]" },
  loading: { label: "Running", color: "text-amber-400 border-amber-400/20 bg-amber-400/10", dot: "bg-amber-400 animate-pulse" },
  success: { label: "Completed", color: "text-emerald-400 border-emerald-400/20 bg-emerald-400/10", dot: "bg-emerald-400" },
  error: { label: "Failed", color: "text-red-400 border-red-400/20 bg-red-400/10", dot: "bg-red-400" },
};

export default function Header({
  status = "idle",
  latency = 34,
  repo = "AutoFix-CI/core",
  confidence = null,
}: HeaderProps) {
  const cfg = statusConfig[status];

  return (
    <header className="flex flex-col md:flex-row md:items-center justify-between pb-8 border-b border-transparent gap-6">
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-[40px] leading-tight font-extrabold text-white tracking-tight">AutoFix CI</h1>
          {repo && (
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-400 font-mono">
              {repo}
            </span>
          )}
        </div>
        <p className="mt-2 text-sm text-slate-400 font-medium">
          AI-powered GitHub CI Failure Analysis & Auto-Repair
        </p>
      </div>

      <div className="flex items-center flex-wrap gap-4">
        {/* API Latency */}
        {latency !== null && (
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-[#0f1724] border border-transparent text-xs font-semibold text-slate-300">
            <Radio className="w-4 h-4 text-violet-400" />
            <span className="text-xs">Latency</span>
            <span className="text-violet-300 font-mono">{latency}ms</span>
          </div>
        )}

        {/* AI Confidence */}
        {confidence !== null && (
          <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-900 border border-[#1f294d]/30 text-xs font-semibold text-slate-400">
            <Zap className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
            AI Confidence: <span className="text-amber-300 font-mono">{confidence}%</span>
          </div>
        )}

        {/* Pipeline Status Pill */}
        <div className={`badge-status px-3.5 py-2 rounded-xl text-xs font-semibold border ${cfg.color}`}>
          <span className={`inline-block w-2.5 h-2.5 rounded-full ${cfg.dot} shadow-sm`} />
          <span className="text-[12px]">Pipeline</span>
          <span className="font-bold ml-1">{cfg.label}</span>
        </div>

        {/* Backend Connected Pill */}
        <div className="badge-status px-3.5 py-2 rounded-xl text-xs font-semibold border border-emerald-500/10 bg-emerald-500/6 text-emerald-300">
          <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm animate-pulse" />
          <span className="text-[12px]">Backend</span>
          <span className="font-bold ml-1">Connected</span>
        </div>
      </div>
    </header>
  );
}