from pydantic import BaseModel

from .root_cause import RootCauseResult
from .repair import RepairSuggestion
from .validation import ValidationResult
from .execution import ExecutionTrace
from .repository import DependencyGraph, RepoContext


class FinalReport(BaseModel):
    summary: str
    root_cause: RootCauseResult
    fix: RepairSuggestion
    validation: ValidationResult
    execution_trace: ExecutionTrace | None = None
    dependency_graph: DependencyGraph | None = None
    repo_context: RepoContext | None = None
