export interface RootCauseResult {
  cause: "dependency_failure" | "build_error" | "test_failure" | "runtime_error" | "unknown";
  confidence: number;
  explanation: string;
}

export interface PatchChange {
  search: string;
  replace: string;
}

export interface PatchFile {
  path: string;
  changes: PatchChange[];
}

export interface RepairSuggestion {
  files: PatchFile[];
  reasoning: string;
  confidence: number;
}

export interface ValidationResult {
  valid: boolean;
  ci_status: string;
  risk: string;
  success_probability: number;
}

export interface ExecutionStep {
  name: string;
  status: string;
  started_at: string;
  finished_at: string;
  duration_ms: number;
  output?: any;
  error_message?: string | null;
  exception_type?: string | null;
  details?: string | null;
}

export interface ExecutionTrace {
  steps: ExecutionStep[];
}

export interface DependencyGraph {
  nodes: string[];
  edges: [string, string][];
}

export interface RepoContext {
  files: Record<string, string>;
}

export interface FinalReport {
  summary: string;
  root_cause: RootCauseResult;
  fix: RepairSuggestion;
  validation: ValidationResult;
  execution_trace?: ExecutionTrace | null;
  dependency_graph?: DependencyGraph | null;
  repo_context?: RepoContext | null;
}
