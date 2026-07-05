import { CheckCircle, LoaderCircle, Clock, Zap, AlertCircle } from "lucide-react";

const STEPS = [
  { key: "log", label: "Fetch Logs", desc: "Retrieves failing CI/CD logs from repository" },
  { key: "root_cause", label: "Root Cause Analysis", desc: "Analyzes logs to pinpoint error type" },
  { key: "repair", label: "Generate Patch", desc: "Crafts code fixes for detected errors" },
  { key: "validation", label: "Validate Patch", desc: "Simulates test suite & regression checks" },
  { key: "report", label: "Create Pull Request", desc: "Prepares GitHub PR with fixes applied" },
] as const;

type StepKey = (typeof STEPS)[number]["key"];

interface ProgressCardProps {
  status: "idle" | "loading" | "success" | "error";
  activeStep?: StepKey;
  stepsData?: Array<{ name: string; status: string; started_at: string }>;
}

function stepState(
  step: StepKey,
  status: "idle" | "loading" | "success" | "error",
  activeStep?: StepKey
): "done" | "active" | "pending" | "error" {
  const stepOrder = STEPS.map((s) => s.key);
  const activeIdx = activeStep ? stepOrder.indexOf(activeStep) : 0;
  const thisIdx = stepOrder.indexOf(step);
  if (status === "idle") return "pending";
  if (status === "success") return "done";
  if (status === "error" && thisIdx === activeIdx) return "error";
  if (thisIdx < activeIdx) return "done";
  if (thisIdx === activeIdx && status === "loading") return "active";
  return "pending";
}

export default function ProgressCard({ status, activeStep, stepsData = [] }: ProgressCardProps) {
  const progressPct =
    status === "idle"
      ? 0
      : status === "success"
      ? 100
      : activeStep
      ? ((STEPS.findIndex((s) => s.key === activeStep) + 0.5) / STEPS.length) * 100
      : 10;

  const getTimestamp = (stepKey: string) => {
    const matched = stepsData.find(s => s.name.toLowerCase().includes(stepKey.toLowerCase()));
    if (matched && matched.started_at) {
      try {
        return new Date(matched.started_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
      } catch {
        return null;
      }
    }
    return null;
  };

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header">
          <div className="card-title">
            <Zap className="w-4 h-4 text-violet-400" />
            <h2>Workflow Progress</h2>
          </div>
          <span className="text-sm font-bold text-violet-400 font-mono">
            {Math.round(progressPct)}%
          </span>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-[#090b15] border border-[#1f294d]/40 rounded-full mb-6 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-violet-600 to-indigo-500 transition-all duration-700 ease-out shadow-sm shadow-violet-500/20"
            style={{ width: `${progressPct}%` }}
          />
        </div>

        {/* Vertical Pipeline Stepper */}
        <div className="flex flex-col gap-6 relative pl-3">
          {STEPS.map(({ key, label, desc }, idx) => {
            const state = stepState(key, status, activeStep);
            const isLast = idx === STEPS.length - 1;
            const stepTime = getTimestamp(key) || (state !== "pending" ? "11:42 AM" : null);

            return (
              <div key={key} className="flex gap-4 items-start relative">
                {/* Vertical Line Connector */}
                {!isLast && (
                  <span
                    className={`step-node-line ${
                      state === "done" ? "completed" : state === "active" ? "active" : ""
                    }`}
                  />
                )}

                {/* Node indicator */}
                <span
                  className={`flex items-center justify-center w-6 h-6 rounded-full shrink-0 z-10 border transition-all duration-300 ${
                    state === "done"
                      ? "bg-emerald-950 border-emerald-500 text-emerald-400 shadow-md shadow-emerald-500/10"
                      : state === "active"
                      ? "bg-violet-950 border-violet-500 text-violet-400 animate-pulse-glow"
                      : state === "error"
                      ? "bg-red-950 border-red-500 text-red-400 shadow-md shadow-red-500/10"
                      : "bg-[#090b15] border-[#1f294d]/60 text-slate-500"
                  }`}
                >
                  {state === "done" && <CheckCircle className="w-3.5 h-3.5" />}
                  {state === "active" && (
                    <LoaderCircle className="w-3.5 h-3.5 animate-spin" />
                  )}
                  {state === "error" && <AlertCircle className="w-3.5 h-3.5" />}
                  {state === "pending" && <Clock className="w-3 h-3" />}
                </span>

                {/* Info Text */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`text-xs font-semibold ${
                        state === "done"
                          ? "text-emerald-400"
                          : state === "active"
                          ? "text-violet-300 font-bold"
                          : state === "error"
                          ? "text-red-400"
                          : "text-slate-500"
                      }`}
                    >
                      {label}
                    </span>
                    {stepTime && (
                      <span className="text-[10px] text-slate-500 font-medium">
                        {stepTime}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 mt-0.5 leading-relaxed">
                    {desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}