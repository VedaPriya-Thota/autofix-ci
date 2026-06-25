from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class WorkflowState(BaseModel):
    repo_url: str | None = None
    ci_log: str | None = None

    structured_logs: dict = {}
    root_cause: dict = {}
    repo_context: dict = {}

    dependency_graph: dict = {}
    fix_suggestion: dict = {}
    validation_result: dict = {}

    final_report: dict = {}