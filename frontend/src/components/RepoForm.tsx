import { useState } from "react";
import { Loader2, Zap, AlertCircle, Terminal } from "lucide-react";
import type { FinalReport } from "../types/workflow";
import { runAnalysis } from "../api/api";

const SAMPLE_LOGS = [
  {
    label: "PyTest ImportError",
    log: `============================= test session starts ==============================
collected 12 items

tests/test_app.py FAILED [100%]

FAILED tests/test_app.py::test_import - ImportError: cannot import name 'parse_config' from 'app.config'
1 failed in 0.45s`,
  },
  {
    label: "Node Dependency Missing",
    log: `npm ERR! code E404
npm ERR! 404 Not Found - GET https://registry.npmjs.org/lodash.deepmerge
npm ERR! 404  'lodash.deepmerge@4.2.2' is not in this registry.
npm ERR! A complete log of this run can be found in: /home/runner/.npm/_logs/2024-01-15T10_30_00_000Z-debug-0.log`,
  },
  {
    label: "Docker Build Timeout",
    log: `Step 5/12 : RUN pip install -r requirements.txt
 ---> Running in a1b2c3d4e5f6
error: timed out waiting for npm registry
The command '/bin/sh -c pip install -r requirements.txt' returned a non-zero code: 1
ERROR: Service 'app' failed to build : Build failed`,
  },
];

interface RepoFormProps {
  onResult: (report: FinalReport) => void;
  onStatusChange: (status: "idle" | "loading" | "success" | "error") => void;
}

export default function RepoForm({ onResult, onStatusChange }: RepoFormProps) {
  const [log, setLog] = useState("");
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handlePreset = (idx: number) => {
    setSelectedPreset(idx);
    setLog(SAMPLE_LOGS[idx].log);
    setError(null);
  };

  const handleSubmit = async () => {
    if (!log.trim()) {
      setError("Please paste a CI log or select a sample above.");
      return;
    }
    setLoading(true);
    setError(null);
    onStatusChange("loading");
    try {
      const report = await runAnalysis(log.trim());
      onResult(report);
      onStatusChange("success");
    } catch (err: unknown) {
      let msg = "Request failed. Is the backend running?";
      if (err instanceof Error) {
        if (err.message.includes("ECONNREFUSED") || err.message.includes("Network Error")) {
          msg = "Cannot connect to the FastAPI backend at 127.0.0.1:8000. Please start the backend server and try again.";
        } else if (err.message.includes("timeout")) {
          msg = "Request timed out. The backend may be overloaded or unreachable.";
        } else if (err.message.includes("500")) {
          msg = "The backend returned an internal error (500). Check server logs for details.";
        } else if (err.message.includes("422")) {
          msg = "Invalid request format. Please ensure your CI log is non-empty text.";
        } else {
          msg = err.message;
        }
      }
      setError(msg);
      onStatusChange("error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header">
          <div className="card-title">
            <Terminal className="w-4 h-4 text-violet-400" />
            <h2>CI Log Analysis</h2>
          </div>
        </div>

        <p className="text-xs text-slate-400 font-medium mb-3">
          Paste your CI/CD failure log text or select a sample:
        </p>

        {/* Log Textarea */}
        <div className="relative mb-5">
          <textarea
            className="w-full h-40 bg-[#090b15] border border-[#1f294d]/60 rounded-xl px-4 py-3 text-xs font-mono text-slate-300 placeholder-slate-600 resize-none focus:outline-none focus:border-violet-500/70 transition-all duration-200 shadow-inner"
            placeholder="Paste logs here..."
            value={log}
            onChange={(e) => {
              setLog(e.target.value);
              setSelectedPreset(null);
              setError(null);
            }}
          />
        </div>

        {/* Sample Selector */}
        <div className="mb-6">
          <span className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-2">
            Sample Selector
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_LOGS.map((s, i) => (
              <button
                key={i}
                onClick={() => handlePreset(i)}
                className={`text-xs px-3.5 py-2 rounded-xl border transition-all duration-200 font-medium cursor-pointer ${
                  selectedPreset === i
                    ? "bg-[#7c3aed]/15 border-[#7c3aed] text-violet-300 shadow-sm"
                    : "bg-[#090b15]/60 border-[#1f294d]/40 text-slate-400 hover:border-slate-500 hover:text-slate-200"
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div>
        {/* Error State */}
        {error && (
          <div className="flex items-start gap-2.5 mb-4 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 animate-fade-in">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
            <div className="flex-1">
              <span className="font-semibold block">Failed to run analysis</span>
              <p className="text-[11px] text-red-400/80 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Submit Action */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn-primary w-full py-3"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Analyzing CI Log...</span>
            </>
          ) : (
            <>
              <Zap className="w-4 h-4 text-white" />
              <span>Analyze</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}