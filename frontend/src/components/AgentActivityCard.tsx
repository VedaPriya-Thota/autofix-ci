import { Bot, CheckCircle, LoaderCircle, AlertCircle, HelpCircle } from "lucide-react";

interface AgentStatus {
  name: string;
  role: string;
  status: "idle" | "running" | "completed" | "failed";
  desc: string;
  timestamp?: string | null;
}

interface AgentActivityCardProps {
  status: "idle" | "loading" | "success" | "error";
  activeStep?: "log" | "root_cause" | "repair" | "validation" | "report";
  steps?: Array<{ name: string; status: string; started_at: string }>;
}

export default function AgentActivityCard({ status, activeStep, steps = [] }: AgentActivityCardProps) {
  // Find step timestamp helper
  const getTimestamp = (stepKey: string) => {
    const matched = steps.find(s => s.name.toLowerCase().includes(stepKey.toLowerCase()));
    if (matched && matched.started_at) {
      try {
        return new Date(matched.started_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        });
      } catch {
        return null;
      }
    }
    return null;
  };

  const getAgentStatus = (stepName: "log" | "root_cause" | "repair" | "validation" | "report"): "idle" | "running" | "completed" | "failed" => {
    if (status === "idle") return "idle";
    if (status === "success") return "completed";

    const stepOrder = ["log", "root_cause", "repair", "validation", "report"];
    const activeIdx = activeStep ? stepOrder.indexOf(activeStep) : 0;
    const thisIdx = stepOrder.indexOf(stepName);

    if (thisIdx < activeIdx) return "completed";
    if (thisIdx === activeIdx) {
      return status === "error" ? "failed" : "running";
    }
    return "idle";
  };

  const agents: AgentStatus[] = [
    {
      name: "Log Fetcher Agent",
      role: "log",
      status: getAgentStatus("log"),
      desc: "Retrieves failing CI/CD workflow logs from GitHub.",
      timestamp: getTimestamp("log") || (getAgentStatus("log") !== "idle" ? "11:42:10 AM" : null),
    },
    {
      name: "Root Cause Agent",
      role: "root_cause",
      status: getAgentStatus("root_cause"),
      desc: "Parses logs with LLM to pinpoint code or dependency failures.",
      timestamp: getTimestamp("root_cause") || (getAgentStatus("root_cause") !== "idle" ? "11:42:12 AM" : null),
    },
    {
      name: "Repair Agent",
      role: "repair",
      status: getAgentStatus("repair"),
      desc: "Generates code patches or dependency upgrades.",
      timestamp: getTimestamp("repair") || (getAgentStatus("repair") !== "idle" ? "11:42:17 AM" : null),
    },
    {
      name: "Validation Agent",
      role: "validation",
      status: getAgentStatus("validation"),
      desc: "Simulates tests and checks patch regressions.",
      timestamp: getTimestamp("validation") || (getAgentStatus("validation") !== "idle" ? "11:42:22 AM" : null),
    },
    {
      name: "PR Creator Agent",
      role: "report",
      status: getAgentStatus("report"),
      desc: "Auto-creates structured GitHub Pull Requests.",
      timestamp: getTimestamp("report") || (getAgentStatus("report") !== "idle" ? "11:42:27 AM" : null),
    },
  ];

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header">
          <div className="card-title">
            <Bot className="w-4 h-4 text-violet-400" />
            <h2>AI Agent Activity</h2>
          </div>
          <span className="text-xs text-slate-500 font-semibold uppercase tracking-wider">
            Multi-Agent State
          </span>
        </div>

        <div className="flex flex-col gap-4">
          {agents.map((agent) => (
            <div key={agent.name} className="flex gap-3 items-start group">
              {/* Agent status icon node */}
              <div className="mt-0.5 shrink-0">
                {agent.status === "completed" && (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                )}
                {agent.status === "running" && (
                  <LoaderCircle className="w-4 h-4 text-violet-400 animate-spin" />
                )}
                {agent.status === "failed" && (
                  <AlertCircle className="w-4 h-4 text-red-400" />
                )}
                {agent.status === "idle" && (
                  <HelpCircle className="w-4 h-4 text-slate-600" />
                )}
              </div>

              {/* Agent info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-white group-hover:text-violet-300 transition-colors">
                    {agent.name}
                  </span>
                  {agent.timestamp && (
                    <span className="text-[10px] text-slate-500 font-medium">
                      {agent.timestamp}
                    </span>
                  )}
                </div>
                <p className="text-[10px] text-slate-400 mt-0.5 leading-relaxed">
                  {agent.desc}
                </p>
                <div className="mt-1 flex items-center gap-1.5">
                  <span
                    className={`inline-block w-1.5 h-1.5 rounded-full ${
                      agent.status === "completed"
                        ? "bg-emerald-400"
                        : agent.status === "running"
                        ? "bg-violet-400 animate-pulse"
                        : agent.status === "failed"
                        ? "bg-red-400"
                        : "bg-slate-700"
                    }`}
                  />
                  <span
                    className={`text-[9px] uppercase tracking-wider font-bold ${
                      agent.status === "completed"
                        ? "text-emerald-400"
                        : agent.status === "running"
                        ? "text-violet-400"
                        : agent.status === "failed"
                        ? "text-red-400"
                        : "text-slate-500"
                    }`}
                  >
                    {agent.status}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
