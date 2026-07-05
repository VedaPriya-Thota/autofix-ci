import { GitPullRequest, ExternalLink, GitBranch, GitCommitHorizontal, CheckCircle2, Circle } from "lucide-react";

interface PRCardProps {
  prUrl?: string | null;
  branch?: string | null;
  commitSha?: string | null;
  summary?: string | null;
  isLoading?: boolean;
  error?: string | null;
}

export default function PRCard({
  prUrl,
  branch = "autofix/patch-branch",
  commitSha = "a1b2c3d",
  summary = "AutoFix: Fix ImportError by adding missing dependencies",
  isLoading = false,
  error = null,
}: PRCardProps) {
  // 1. Loading State (Skeleton)
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
          <div className="h-5 w-40 skeleton" />
        </div>
        <div className="flex gap-4 items-center">
          <div className="w-12 h-12 rounded-full skeleton shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-5 w-3/4 skeleton" />
            <div className="h-4 w-1/2 skeleton" />
          </div>
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
            <GitPullRequest className="w-4 h-4 text-red-400" />
            <h2 className="text-red-400">Pull Request Error</h2>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center py-6 text-center">
          <Circle className="w-8 h-8 text-red-500 mb-2 animate-bounce" />
          <p className="text-xs text-red-400 font-semibold">{error}</p>
          <p className="text-[10px] text-slate-500 mt-1">Verify GitHub token scopes and webhook secrets.</p>
        </div>
      </div>
    );
  }

  // 3. Empty State (Clean & Unfinished states handled gracefully)
  if (!prUrl) {
    return (
      <div className="card h-full flex flex-col justify-between">
        <div>
          <div className="card-header pb-4 mb-4 border-b border-[#1f294d]/40">
            <div className="card-title">
              <GitPullRequest className="w-4 h-4 text-slate-500" />
              <h2 className="text-slate-400">Pull Request</h2>
            </div>
          </div>
          <div className="flex flex-col items-center justify-center py-10 text-center">
            <GitPullRequest className="w-9 h-9 text-slate-700 mb-3" />
            <p className="text-sm font-semibold text-slate-500">No Pull Request Created</p>
            <p className="text-xs text-slate-600 mt-1">
              A GitHub Pull Request will be opened automatically upon patch validation completion.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Parse PR ID or number from URL for display title (e.g. #42)
  const prMatch = prUrl.match(/\/pull\/(\d+)/);
  const prNumber = prMatch ? `#${prMatch[1]}` : "#42";

  return (
    <div className="card h-full flex flex-col justify-between">
      <div>
        <div className="card-header pb-4 mb-5 border-b border-[#1f294d]/40">
          <div className="card-title">
            <GitPullRequest className="w-4 h-4 text-violet-400" />
            <h2>Pull Request</h2>
          </div>
          <span className="flex items-center gap-1.5 text-[10px] px-2.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold uppercase tracking-wider">
            Created
          </span>
        </div>

        {/* PR Main Block */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5 bg-[#090b15] border border-[#1f294d]/50 rounded-2xl p-5 mb-5 shadow-inner">
          <div className="flex items-start gap-4">
            {/* GitHub Rounded Avatar Circle */}
            <div className="w-11 h-11 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shrink-0 shadow-md">
              <svg
                className="w-6 h-6 text-white"
                viewBox="0 0 16 16"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" />
              </svg>
            </div>

            {/* Title & Metadata */}
            <div className="min-w-0">
              <h3 className="text-sm font-semibold text-white leading-snug group-hover:text-violet-300 transition-colors">
                AutoFix {prNumber}: Fix {summary || "CI pipeline issue"}
              </h3>
              <div className="flex items-center gap-3 flex-wrap mt-2 font-mono text-[10px] text-slate-400">
                <span className="flex items-center gap-1 bg-[#101430] border border-[#1f294d]/40 rounded-lg px-2 py-0.5">
                  <GitBranch className="w-3.5 h-3.5 text-violet-400" />
                  {branch || "autofix/patch"}
                </span>
                <span className="flex items-center gap-1 bg-[#101430] border border-[#1f294d]/40 rounded-lg px-2 py-0.5">
                  <GitCommitHorizontal className="w-3.5 h-3.5 text-slate-500" />
                  {commitSha ? commitSha.slice(0, 7) : "a1b2c3d"}
                </span>
              </div>
            </div>
          </div>

          {/* View on GitHub Button */}
          <a
            href={prUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-[#3b4b8c] hover:border-violet-500 text-xs font-semibold bg-[#111530] text-slate-200 hover:text-white transition-all shadow-md shrink-0 cursor-pointer"
          >
            <span>View on GitHub</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Footer Metrics Row */}
      <div className="grid grid-cols-3 gap-4 border-t border-[#1f294d]/30 pt-4 mt-1">
        <div>
          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Status
          </span>
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-sm animate-pulse" />
            Open
          </span>
        </div>
        <div>
          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Checks
          </span>
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            All Passing
          </span>
        </div>
        <div>
          <span className="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1">
            Created At
          </span>
          <span className="text-[11px] text-slate-400 font-mono font-medium">
            May 27, 2025 11:42 AM
          </span>
        </div>
      </div>
    </div>
  );
}