import { useState } from "react";
import { Code, Copy, CheckCircle, FileCode, Download } from "lucide-react";
import type { RepairSuggestion } from "../types/workflow";

interface PatchCardProps {
  fix?: RepairSuggestion | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function PatchCard({ fix, isLoading = false, error = null }: PatchCardProps) {
  const [copied, setCopied] = useState(false);

  // 1. Loading State (Skeleton)
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="h-5 w-48 skeleton" />
        </div>
        <div className="h-5 w-40 skeleton mb-3" />
        <div className="h-32 w-full skeleton" />
      </div>
    );
  }

  // 2. Error State
  if (error) {
    return (
      <div className="card border-red-500/30">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="card-title">
            <Code className="w-4 h-4 text-red-400" />
            <h2 className="text-red-400">Patch Generation Error</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <AlertCircleIcon className="w-8 h-8 text-red-500 mb-2 animate-bounce" />
          <p className="text-xs text-red-400 font-semibold">{error}</p>
          <p className="text-[10px] text-slate-500 mt-1">Please inspect code structure or LLM API quotas.</p>
        </div>
      </div>
    );
  }

  // 3. Empty State
  if (!fix || !fix.files || fix.files.length === 0) {
    return (
      <div className="card">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="card-title">
            <Code className="w-4 h-4 text-slate-500" />
            <h2 className="text-slate-400">Generated Patch</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Code className="w-8 h-8 text-slate-700 mb-3 animate-pulse" />
          <p className="text-sm font-semibold text-slate-500">No Patch Available</p>
          <p className="text-xs text-slate-600 mt-1">The repair workflow will output code diff modifications here.</p>
        </div>
      </div>
    );
  }

  // Helper to compile unified patch text
  const getUnifiedPatch = () => {
    return fix.files
      .map(
        (f) =>
          `diff --git a/${f.path} b/${f.path}\n` +
          `index e69de29..4b825dc 100644\n` +
          `--- a/${f.path}\n` +
          `+++ b/${f.path}\n` +
          `@@ -8,7 +8,10 @@\n` +
          f.changes
            .map(
              (c) =>
                c.search
                  .split("\n")
                  .map((l) => `-${l}`)
                  .join("\n") +
                "\n" +
                c.replace
                  .split("\n")
                  .map((l) => `+${l}`)
                  .join("\n")
            )
            .join("\n")
      )
      .join("\n");
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getUnifiedPatch()).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([getUnifiedPatch()], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = "autofix.patch";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header pb-4 mb-5 border-b border-[#1f294d]/40">
          <div className="card-title">
            <FileCode className="w-4 h-4 text-violet-400" />
            <h2>Generated Patch</h2>
          </div>
          <div className="flex items-center gap-2">
            {/* Copy Patch */}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 text-[11px] px-3 py-1.5 rounded-lg bg-[#0c0f20] border border-[#1f294d]/50 text-slate-300 hover:text-white hover:border-[#3b4b8c] transition-all cursor-pointer font-semibold"
            >
              {copied ? (
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5 text-slate-400" />
              )}
              {copied ? "Copied!" : "Copy Patch"}
            </button>

            {/* Download Diff */}
            <button
              onClick={handleDownload}
              className="flex items-center gap-1.5 text-[11px] px-3 py-1.5 rounded-lg bg-[#0c0f20] border border-[#1f294d]/50 text-slate-300 hover:text-white hover:border-[#3b4b8c] transition-all cursor-pointer font-semibold"
            >
              <Download className="w-3.5 h-3.5 text-slate-400" />
              <span>Download</span>
            </button>
          </div>
        </div>

        {/* Confidence pill */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-[10px] uppercase tracking-wider font-bold text-slate-500">
            Confidence Rate:
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            {Math.round(fix.confidence * 100)}% Match
          </span>
        </div>

        {/* Unified GitHub-Style Diffs */}
        <div className="space-y-4">
          {fix.files.map((file, fi) => {
            let oldLineCount = 1;
            let newLineCount = 1;

            return (
              <div
                key={fi}
                className="border border-[#1f294d]/50 rounded-xl overflow-hidden shadow-inner bg-[#090c15]"
              >
                {/* File Header */}
                <div className="bg-[#0c1024] border-b border-[#1f294d]/50 px-4 py-2 flex items-center justify-between">
                  <span className="font-mono text-xs text-slate-300 font-semibold">
                    {file.path}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    diff --git a/{file.path} b/{file.path}
                  </span>
                </div>

                {/* Diff Viewer Grid */}
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse font-mono text-[11px] leading-relaxed text-slate-300">
                    <tbody>
                      {/* Diff block index marker */}
                      <tr className="bg-[#0b0e1a]">
                        <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-slate-600 bg-[#090c15] py-1">..</td>
                        <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-slate-600 bg-[#090c15] py-1">..</td>
                        <td className="px-4 text-violet-400 font-medium py-1">
                          @@ -8,7 +8,10 @@ index e69de29..4b825dc 100644
                        </td>
                      </tr>

                      {file.changes.flatMap((change, ci) => {
                        const searchLines = change.search.split("\n");
                        const replaceLines = change.replace.split("\n");

                        const rows: React.ReactNode[] = [];

                        // Render removals (search block)
                        searchLines.forEach((line) => {
                          const curOld = oldLineCount++;
                          rows.push(
                            <tr key={`rem-${ci}-${curOld}`} className="bg-red-500/5 hover:bg-red-500/10">
                              <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-red-500/60 bg-red-950/20 py-0.5">
                                {curOld}
                              </td>
                              <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-slate-700 bg-[#090c15] py-0.5">
                                {/* Empty */}
                              </td>
                              <td className="px-4 text-red-400 font-medium line-removed py-0.5">
                                {line}
                              </td>
                            </tr>
                          );
                        });

                        // Render additions (replace block)
                        replaceLines.forEach((line) => {
                          const curNew = newLineCount++;
                          rows.push(
                            <tr key={`add-${ci}-${curNew}`} className="bg-emerald-500/5 hover:bg-emerald-500/10">
                              <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-slate-700 bg-[#090c15] py-0.5">
                                {/* Empty */}
                              </td>
                              <td className="w-8 select-none text-center border-r border-[#1f294d]/20 text-emerald-500/60 bg-emerald-950/20 py-0.5">
                                {curNew}
                              </td>
                              <td className="px-4 text-emerald-400 font-medium line-added py-0.5">
                                {line}
                              </td>
                            </tr>
                          );
                        });

                        return rows;
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Simple placeholder icon
function AlertCircleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  );
}