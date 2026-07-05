import { AlertTriangle, ShieldCheck } from "lucide-react";
import type { RootCauseResult } from "../types/workflow";

interface RootCauseCardProps {
  rootCause?: RootCauseResult | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function RootCauseCard({ rootCause, isLoading = false, error = null }: RootCauseCardProps) {
  // 1. Loading State (Skeleton)
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="h-5 w-40 skeleton" />
        </div>
        <div className="flex justify-between items-center mb-5">
          <div className="h-4 w-24 skeleton" />
          <div className="h-6 w-20 skeleton" />
        </div>
        <div className="space-y-3 mb-5">
          <div className="h-4 w-32 skeleton" />
          <div className="h-16 w-full skeleton" />
        </div>
        <div className="space-y-2">
          <div className="h-4 w-28 skeleton" />
          <div className="h-10 w-full skeleton" />
        </div>
      </div>
    );
  }

  // 2. Error State
  if (error) {
    return (
      <div className="card border-red-500/30">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="card-title">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <h2 className="text-red-400">Root Cause Error</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-500 mb-2 animate-bounce" />
          <p className="text-xs text-red-400 font-semibold">{error}</p>
          <p className="text-[10px] text-slate-500 mt-1">Check logs or try re-running the analysis.</p>
        </div>
      </div>
    );
  }

  // 3. Empty State
  if (!rootCause) {
    return (
      <div className="card">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="card-title">
            <AlertTriangle className="w-4 h-4 text-slate-500" />
            <h2 className="text-slate-400">Root Cause Analysis</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <AlertTriangle className="w-8 h-8 text-slate-700 mb-3" />
          <p className="text-sm font-semibold text-slate-500">Analysis Pending</p>
          <p className="text-xs text-slate-600 mt-1">Start a run to determine failure root causes.</p>
        </div>
      </div>
    );
  }

  // 4. Success State (Dynamically populated from backend)
  const pct = Math.round(rootCause.confidence * 100);

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header pb-4 mb-5 border-b border-[#1f294d]/40">
          <div className="card-title">
            <AlertTriangle className="w-4 h-4 text-violet-400" />
            <h2>Root Cause Analysis</h2>
          </div>
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        </div>

        {/* Failure Type Row */}
        <div className="flex justify-between items-center mb-5 pb-3 border-b border-[#1f294d]/20">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Failure Type</span>
          <span className="px-3 py-1 rounded-lg text-xs font-bold bg-red-500/10 border border-red-500/30 text-red-400 uppercase tracking-wide">
            {rootCause.cause.replace(/_/g, " ")}
          </span>
        </div>

        {/* Confidence Score with bar */}
        <div className="mb-5">
          <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Confidence Score
          </span>
          <div className="flex items-center gap-4">
            <span className="text-xl font-black text-red-400 font-mono tracking-tight shrink-0">
              {pct}%
            </span>
            <div className="flex-1 h-2 bg-[#090b15] border border-[#1f294d]/40 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full transition-all duration-700 shadow-inner"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Analysis Detail */}
        <div className="mb-5">
          <span className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Analysis
          </span>
          <p className="text-xs text-slate-300 leading-relaxed bg-[#090b15]/60 border border-[#1f294d]/30 rounded-xl px-4 py-3 shadow-inner">
            {rootCause.explanation}
          </p>
        </div>
      </div>
    </div>
  );
}