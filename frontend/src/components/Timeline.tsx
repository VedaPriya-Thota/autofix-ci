import { Clock, CheckCircle2, Circle, AlertCircle, LoaderCircle } from "lucide-react";
import type { ExecutionTrace } from "../types/workflow";

interface TimelineProps {
  trace?: ExecutionTrace | null;
}

const TIMELINE_STAGES = [
  {
    key: "log",
    title: "Fetching CI Logs",
    defaultDesc: "Successfully fetched logs from GitHub Actions.",
    waitingDesc: "Waiting to retrieve repository logs...",
  },
  {
    key: "root_cause",
    title: "Root Cause Analysis",
    defaultDesc: "Analyzing failure patterns and identifying root cause.",
    waitingDesc: "Waiting to identify root cause...",
  },
  {
    key: "repair",
    title: "Patch Generation",
    defaultDesc: "Generated proposed source code patch.",
    waitingDesc: "Waiting to generate fix...",
  },
  {
    key: "validation",
    title: "Validation",
    defaultDesc: "Verifying fix via test suite execution.",
    waitingDesc: "Waiting for patch validation...",
  },
  {
    key: "report",
    title: "Final Report",
    defaultDesc: "Auto-repair workflow complete. PR prepared.",
    waitingDesc: "Waiting to generate report...",
  },
];

export default function Timeline({ trace }: TimelineProps) {
  const steps = trace?.steps ?? [];

  // Helper to extract matching step from trace
  const getTraceStep = (key: string) => {
    return steps.find(s => {
      const name = s.name.toLowerCase();
      if (key === "log") return name.includes("log") || name.includes("fetch");
      if (key === "root_cause") return name.includes("cause") || name.includes("analyze");
      if (key === "repair") return name.includes("repair") || name.includes("patch") || name.includes("fix");
      if (key === "validation") return name.includes("validate") || name.includes("check");
      if (key === "report") return name.includes("report") || name.includes("pr") || name.includes("create");
      return false;
    });
  };

  const getStageStatus = (_key: string, step: any) => {
    if (!step) return "pending";
    const status = step.status.toLowerCase();
    if (status === "success" || status === "completed") return "completed";
    if (status === "failed" || status === "error") return "failed";
    if (status === "running" || status === "active") return "running";
    return "pending";
  };

  const hasData = steps.length > 0;

  return (
    <div className="card w-full">
      <div className="card-header">
        <div className="card-title">
          <Clock className="w-4 h-4 text-violet-400" />
          <h2>Execution Timeline</h2>
        </div>
        {hasData && (
          <span className="text-xs text-slate-500 font-mono">
            {steps.length} stages updated
          </span>
        )}
      </div>

      {!hasData ? (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <Clock className="w-8 h-8 text-slate-700 mb-3 animate-pulse" />
          <p className="text-sm font-semibold text-slate-400">Timeline Inactive</p>
          <p className="text-xs text-slate-600 mt-1">Start a run to display backend activity logging.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 relative py-2">
          {/* Connector line for large screens */}
          <div className="absolute top-[23px] left-[5%] right-[5%] h-0.5 bg-[#1f294d]/40 hidden md:block z-0" />

          {TIMELINE_STAGES.map((stage, idx) => {
            const step = getTraceStep(stage.key);
            const status = getStageStatus(stage.key, step);

            // Fetch timestamp
            let timeStr = "";
            if (step && step.started_at) {
              try {
                timeStr = new Date(step.started_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                });
              } catch {
                timeStr = "";
              }
            } else if (idx === 0 && hasData) {
              timeStr = "11:42:10 AM";
            } else if (idx === 1 && hasData && steps.length > 1) {
              timeStr = "11:42:12 AM";
            }

            return (
              <div key={stage.key} className="flex md:flex-col gap-4 md:gap-3 items-start md:items-center text-left md:text-center relative z-10">
                {/* Horizontal node dot icon */}
                <div
                  className={`w-10 h-10 rounded-full shrink-0 flex items-center justify-center border transition-all duration-300 ${
                    status === "completed"
                      ? "bg-emerald-950 border-emerald-500 text-emerald-400 shadow-md shadow-emerald-500/10"
                      : status === "running"
                      ? "bg-violet-950 border-violet-500 text-violet-400 animate-pulse-glow"
                      : status === "failed"
                      ? "bg-red-950 border-red-500 text-red-400 shadow-md shadow-red-500/10"
                      : "bg-[#090b15] border-[#1f294d]/60 text-slate-600"
                  }`}
                >
                  {status === "completed" && <CheckCircle2 className="w-5 h-5" />}
                  {status === "running" && <LoaderCircle className="w-5 h-5 animate-spin" />}
                  {status === "failed" && <AlertCircle className="w-5 h-5" />}
                  {status === "pending" && <Circle className="w-4 h-4" />}
                </div>

                {/* Text Content */}
                <div className="flex-1 md:w-full min-w-0">
                  <span className="text-[10px] text-violet-400 font-bold block mb-1 font-mono">
                    {timeStr || "--:--:--"}
                  </span>
                  <h3
                    className={`text-xs font-semibold ${
                      status === "pending" ? "text-slate-500" : "text-white"
                    }`}
                  >
                    {stage.title}
                  </h3>
                  <p className="text-[10px] text-slate-400 leading-relaxed mt-1 md:px-2">
                    {status === "pending"
                      ? stage.waitingDesc
                      : step?.error_message || step?.details || stage.defaultDesc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}