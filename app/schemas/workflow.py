from dataclasses import dataclass
from typing import Optional

from .execution import ExecutionTrace
from .log import StructuredLogs
from .repair import RepairSuggestion
from .report import FinalReport
from .repository import DependencyGraph, RepoContext
from .root_cause import RootCauseResult
from .validation import ValidationResult


@dataclass
class WorkflowState:
    repo_url: Optional[str] = None
    ci_log: Optional[str] = None

    structured_logs: Optional[StructuredLogs] = None
    root_cause: Optional[RootCauseResult] = None
    repo_context: Optional[RepoContext] = None

    dependency_graph: Optional[DependencyGraph] = None
    fix_suggestion: Optional[RepairSuggestion] = None
    validation_result: Optional[ValidationResult] = None
    final_report: Optional[FinalReport] = None
    execution_trace: Optional[ExecutionTrace] = None
