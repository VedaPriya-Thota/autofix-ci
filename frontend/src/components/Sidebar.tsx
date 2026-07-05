import { Home, Zap, GitBranch, FileText, Settings, Server } from "lucide-react";

const navItems = [
  { icon: Home, label: "Dashboard", active: true },
  { icon: Zap, label: "Workflow", active: false },
  { icon: GitBranch, label: "Execution", active: false },
  { icon: FileText, label: "Reports", active: false },
  { icon: Settings, label: "Settings", active: false },
];

export default function Sidebar() {
  return (
    <aside className="lg:w-56 md:w-20 w-0 md:flex hidden flex-col shrink-0 min-h-screen bg-[#090b15] border-r border-transparent transition-all duration-300">
      {/* Logo & Branding */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-transparent h-20">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-violet-500 shadow-md shadow-violet-700/30">
          <Zap className="w-5 h-5 text-white" />
        </div>
        <div className="lg:block hidden animate-fade-in">
          <span className="text-sm font-bold text-white tracking-wide">AutoFix CI</span>
          <p className="text-[10px] text-slate-500 font-medium leading-none mt-0.5">AI Repair System</p>
        </div>
      </div>

      {/* Nav Link List */}
      <nav className="flex flex-col gap-3 px-4 pt-6 flex-1">
        {navItems.map(({ icon: Icon, label, active }) => (
          <button
            key={label}
            className={`flex items-center gap-3 px-4 py-3.5 rounded-xl text-sm transition-all duration-200 w-full text-left group relative ${
              active
                ? "bg-violet-600/10 text-violet-400 font-semibold border border-violet-500/20 shadow-inner"
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent"
            }`}
          >
            {/* Active tab glow bar */}
            {active && (
              <span className="absolute left-0 top-1/4 bottom-1/4 w-1 bg-violet-500 rounded-r-full" />
            )}
            <Icon className={`w-4 h-4 shrink-0 transition-transform duration-200 group-hover:scale-110 ${active ? "text-violet-400" : "text-slate-400 group-hover:text-slate-200"}`} />
            <span className="lg:block hidden transition-opacity duration-200">{label}</span>
          </button>
        ))}
      </nav>

      {/* Backend Status Panel (Match prototype exactly) */}
      <div className="px-4 py-4 border-t border-transparent">
        <div className="lg:block hidden bg-[#0c0f20] border border-transparent rounded-xl p-3.5 mb-3.5 animate-fade-in">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 mb-1">
            <Server className="w-3.5 h-3.5 text-violet-400" />
            Backend Status
          </div>
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400/50" />
            Connected
          </div>
          <p className="text-[10px] text-slate-600 font-medium mt-1">FastAPI on port 8000</p>
        </div>

        {/* Footer info */}
        <div className="lg:text-left text-center">
          <p className="text-[10px] text-slate-600 font-semibold">© 2026 AutoFix CI</p>
          <p className="text-[9px] text-slate-700 font-medium">v1.0.0</p>
        </div>
      </div>
    </aside>
  );
}