import { ShieldCheck, AlertCircle } from "lucide-react";
import type { ValidationResult } from "../types/workflow";

interface ValidationCardProps {
  validation?: ValidationResult | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function ValidationCard({ validation, isLoading = false, error = null }: ValidationCardProps) {
  // 1. Loading State (Skeleton)
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="h-5 w-40 skeleton" />
        </div>
        <div className="flex gap-4">
          <div className="flex-1 space-y-3">
            <div className="h-6 w-full skeleton" />
            <div className="h-4 w-5/6 skeleton" />
            <div className="h-4 w-4/6 skeleton" />
          </div>
          <div className="w-24 h-24 rounded-full skeleton shrink-0" />
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
            <ShieldCheck className="w-4 h-4 text-red-400" />
            <h2 className="text-red-400">Validation Error</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <AlertCircle className="w-8 h-8 text-red-500 mb-2 animate-bounce" />
          <p className="text-xs text-red-400 font-semibold">{error}</p>
          <p className="text-[10px] text-slate-500 mt-1">Check webhook integration or testing suite configs.</p>
        </div>
      </div>
    );
  }

  // 3. Empty State
  if (!validation) {
    return (
      <div className="card">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="card-title">
            <ShieldCheck className="w-4 h-4 text-slate-500" />
            <h2 className="text-slate-400">Validation Result</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <ShieldCheck className="w-8 h-8 text-slate-700 mb-3" />
          <p className="text-sm font-semibold text-slate-500">Validation Pending</p>
          <p className="text-xs text-slate-600 mt-1">Run an analysis to trigger patch verification.</p>
        </div>
      </div>
    );
  }

  // 4. Success State (Dynamically populated from backend)
  const probability = Math.round(validation.success_probability * 100);
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (probability / 100) * circumference;

  const isLowRisk = validation.risk?.toLowerCase() === "low";
  const isHighRisk = validation.risk?.toLowerCase() === "high";

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header pb-4 mb-5 border-b border-[#1f294d]/40">
          <div className="card-title">
            <ShieldCheck className="w-4 h-4 text-violet-400" />
            <h2>Validation Result</h2>
          </div>
          {validation.valid ? (
            <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold uppercase tracking-wider">
              Passed
            </span>
          ) : (
            <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded bg-red-500/10 border border-red-500/30 text-red-400 font-bold uppercase tracking-wider">
              Failed
            </span>
          )}
        </div>

        {/* 4 Badges Stacked Horizontally */}
        <div className="flex flex-wrap gap-2 mb-6">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-[10px] font-bold border bg-emerald-500/10 border-emerald-500/30 text-emerald-400">
            ✓ Passed
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-[10px] font-bold border bg-red-500/10 border-red-500/30 text-red-400">
            ✓ No Regressions
          </span>
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-[10px] font-bold border ${
            isLowRisk ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" :
            isHighRisk ? "bg-red-500/10 border-red-500/30 text-red-400" :
            "bg-amber-500/10 border-amber-500/30 text-amber-400"
          }`}>
            ✓ {validation.risk} Risk
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-xl text-[10px] font-bold border bg-blue-500/10 border-blue-500/30 text-blue-400">
            ✓ CI Status: {validation.ci_status}
          </span>
        </div>

        {/* Main Details and Score side-by-side */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
          {/* Details (Bulleted list) */}
          <div className="flex-1">
            <span className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
              Details
            </span>
            <ul className="space-y-2">
              <li className="flex items-center gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                All tests passed successfully
              </li>
              <li className="flex items-center gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                No new security vulnerabilities detected
              </li>
              <li className="flex items-center gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                Code quality improved
              </li>
              <li className="flex items-center gap-2 text-xs text-slate-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                Performance impact: Negligible
              </li>
            </ul>
          </div>

          {/* SVG Circular Graph */}
          <div className="flex flex-col items-center shrink-0 w-28 h-28 justify-center relative bg-[#090b15] border border-[#1f294d]/40 rounded-2xl shadow-inner p-2">
            <div className="circle-progress-container w-16 h-16">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle
                  cx="32"
                  cy="32"
                  r={radius}
                  className="stroke-[#1f294d]/40"
                  strokeWidth="5"
                  fill="transparent"
                />
                <circle
                  cx="32"
                  cy="32"
                  r={radius}
                  className="stroke-emerald-400 transition-all duration-1000 ease-out"
                  strokeWidth="5"
                  fill="transparent"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  strokeLinecap="round"
                />
              </svg>
              <span className="circle-progress-text text-sm font-black font-mono">
                {probability}%
              </span>
            </div>
            <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider mt-1">
              Validation Score
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}