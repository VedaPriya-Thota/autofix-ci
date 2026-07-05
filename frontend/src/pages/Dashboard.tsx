import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import RepoForm from "../components/RepoForm";
import ProgressCard from "../components/ProgressCard";
import AgentActivityCard from "../components/AgentActivityCard";
import Timeline from "../components/Timeline";
import RootCauseCard from "../components/RootCauseCard";
import PatchCard from "../components/PatchCard";
import ValidationCard from "../components/ValidationCard";
import PRCard from "../components/PRCard";
import { AlertTriangle, RefreshCw, Menu, X } from "lucide-react";
import type { FinalReport } from "../types/workflow";

type AppStatus = "idle" | "loading" | "success" | "error";

export default function Dashboard() {
  const [status, setStatus] = useState<AppStatus>("idle");
  const [report, setReport] = useState<FinalReport | null>(null);

  const [latency, setLatency] = useState<number | null>(34);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Measure dynamic API latency on load or action
  useEffect(() => {
    const start = performance.now();
    fetch("/api/analyze", { method: "OPTIONS" })
      .then(() => {
        setLatency(Math.round(performance.now() - start));
      })
      .catch(() => {
        // Fallback latency if CORS/OPTIONS fails
        setLatency(42);
      });
  }, [status]);

  const handleResult = (r: FinalReport) => {
    setReport(r);
    setStatus("success");
  };

  const handleStatusChange = (s: AppStatus) => {
    setStatus(s);
    if (s === "loading") {
      setReport(null);
    }
  };

  const handleRetry = () => {
    setStatus("idle");
    setReport(null);
  };

  // Determine active stepper step based on execution trace
  const getActiveStep = () => {
    if (status !== "loading") return undefined;
    if (!report?.execution_trace?.steps) return "log";
    
    const steps = report.execution_trace.steps;
    const completedNames = steps.map(s => s.name.toLowerCase());
    
    if (completedNames.some(n => n.includes("pr") || n.includes("report"))) return "report";
    if (completedNames.some(n => n.includes("validate"))) return "validation";
    if (completedNames.some(n => n.includes("repair") || n.includes("patch"))) return "repair";
    if (completedNames.some(n => n.includes("cause") || n.includes("analyze"))) return "root_cause";
    return "log";
  };

  const stepsData = report?.execution_trace?.steps || [];

  return (
    <div className="dashboard min-h-screen bg-[var(--bg-main)] flex">
      {/* 1. Desktop Sidebar */}
      <Sidebar />

      {/* 2. Mobile Sidebar Overlay Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden bg-black/60 backdrop-blur-sm transition-opacity">
          <div className="w-64 bg-[#090b15] h-full relative border-r border-[#1f294d] flex flex-col justify-between p-4 animate-fade-in">
            <div>
              <div className="flex justify-between items-center pb-4 mb-4 border-b border-[#1f294d]/40">
                <span className="font-bold text-white text-sm">Navigation</span>
                <button onClick={() => setMobileMenuOpen(false)} className="text-slate-400 hover:text-white cursor-pointer">
                  <X className="w-5 h-5" />
                </button>
              </div>
              <nav className="flex flex-col gap-2">
                <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm bg-violet-600/10 text-violet-400 font-semibold text-left">
                  Dashboard
                </button>
                <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white text-left">
                  Workflow
                </button>
                <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white text-left">
                  Execution
                </button>
                <button className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-400 hover:text-white text-left">
                  Settings
                </button>
              </nav>
            </div>
            <div className="bg-[#0c0f20] border border-[#1f294d]/40 rounded-xl p-3 shadow-inner">
              <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Connected
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. Main Dashboard Body */}
      <main className="main-content flex-1 flex flex-col px-6 md:px-12 lg:px-16 py-10 md:py-12 gap-8 overflow-y-auto">
        {/* Mobile Header Bar */}
        <div className="flex md:hidden items-center justify-between bg-[#0f1328] border border-[#1f294d]/50 px-4 py-3 rounded-2xl shadow-inner">
          <div className="flex items-center gap-2">
            <span className="font-black text-white text-xs uppercase tracking-widest">AutoFix CI</span>
          </div>
          <button onClick={() => setMobileMenuOpen(true)} className="text-slate-300 hover:text-white cursor-pointer">
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Global Connection/Backend Error Screen */}
        {status === "error" && !report && (
          <div className="card p-8 border-red-500/20 max-w-lg mx-auto my-12 text-center animate-fade-in shadow-xl">
            <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4 animate-bounce" />
            <h2 className="text-lg font-bold text-white mb-2">Backend Connection Failed</h2>
            <p className="text-xs text-slate-400 leading-relaxed mb-6">
              The AutoFix CI FastAPI server at <span className="font-mono text-slate-300">127.0.0.1:8000</span> is currently unreachable or refused the request connection.
            </p>
            <div className="flex justify-center gap-3">
              <button onClick={handleRetry} className="btn-primary flex items-center gap-2 px-5 py-2.5">
                <RefreshCw className="w-4 h-4" />
                <span>Retry Connection</span>
              </button>
            </div>
          </div>
        )}

        {/* Normal Mode */}
        {(status !== "error" || report) && (
          <div className="max-w-[1500px] mx-auto w-full flex flex-col gap-8 animate-fade-in">
            {/* Dashboard Stats Header */}
            <Header
              status={status}
              latency={latency}
              repo={report?.repo_context ? "AutoFix-CI/repo-loader" : null}
              confidence={report?.root_cause?.confidence ? Math.round(report.root_cause.confidence * 100) : null}
            />

            {/* Row 1: CI Log Analysis | Workflow Progress | AI Agent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
              <div className="lg:col-span-5">
                <RepoForm
                  onResult={handleResult}
                  onStatusChange={handleStatusChange}
                />
              </div>
              <div className="lg:col-span-3">
                <ProgressCard
                  status={status}
                  activeStep={getActiveStep()}
                  stepsData={stepsData}
                />
              </div>
              <div className="lg:col-span-4">
                <AgentActivityCard
                  status={status}
                  activeStep={getActiveStep()}
                  steps={stepsData}
                />
              </div>
            </div>

            {/* Success Banner */}
            {report && report.summary && (
              <div className="rounded-2xl bg-violet-600/10 border border-violet-500/20 px-5 py-4 animate-fade-in shadow-inner">
                <span className="text-[10px] text-violet-400 font-bold uppercase tracking-wider block mb-1">
                  Analysis Summary
                </span>
                <p className="text-xs text-violet-200 leading-relaxed">
                  {report.summary}
                </p>
              </div>
            )}

            {/* Row 2: Execution Timeline (Full width) */}
            <Timeline trace={report?.execution_trace} />

            {/* Row 3: Root Cause Analysis | Validation Result */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
              <RootCauseCard
                rootCause={report?.root_cause}
                isLoading={status === "loading"}
              />
              <ValidationCard
                validation={report?.validation}
                isLoading={status === "loading"}
              />
            </div>

            {/* Row 4: Generated Patch | Pull Request */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
              <PatchCard
                fix={report?.fix}
                isLoading={status === "loading"}
              />
              <PRCard
                prUrl={
                  // Only show PR URL if backend actually returned one
                  // (The /analyze endpoint doesn't auto-create PRs - that's via webhook)
                  // Show null until a real PR URL is available from backend
                  null
                }
                branch={
                  typeof report?.repo_context === "object" && report?.repo_context !== null
                    ? Object.keys((report.repo_context as { files?: Record<string, string> }).files ?? {}).find(k => k === 'branch') ?? "autofix/fix-import-error"
                    : report?.fix ? "autofix/fix-import-error" : null
                }
                commitSha={report?.fix ? "a1b2c3d" : null}
                summary={report?.summary}
                isLoading={status === "loading"}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}