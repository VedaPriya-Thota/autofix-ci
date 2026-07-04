import logging
from typing import Any

from app.schemas import FinalReport, RepairPlan, RootCauseResult, ValidationResult

logger = logging.getLogger(__name__)


class ReportAgent:
    def run(self, state: Any) -> FinalReport:
        rc = state.root_cause
        if hasattr(rc, "model_dump"):
            root_cause_val = RootCauseResult(**rc.model_dump())
        elif isinstance(rc, dict):
            try:
                root_cause_val = RootCauseResult(**rc)
            except Exception:
                root_cause_val = RootCauseResult(cause="unknown", confidence=0.0, explanation="invalid root cause")
        else:
            root_cause_val = RootCauseResult(cause="unknown", confidence=0.0, explanation="missing root cause")

        fix = state.fix_suggestion
        if hasattr(fix, "model_dump"):
            fix_val = fix.model_dump()
        elif isinstance(fix, dict):
            try:
                fix_val = RepairPlan(**fix).model_dump()
            except Exception:
                fix_val = RepairPlan(files=[], reasoning="", confidence=0.0).model_dump()
        else:
            fix_val = RepairPlan(files=[], reasoning="", confidence=0.0).model_dump()

        validation = state.validation_result
        if hasattr(validation, "model_dump"):
            validation_val = validation.model_dump()
        elif isinstance(validation, dict):
            try:
                validation_val = ValidationResult(**validation).model_dump()
            except Exception:
                validation_val = ValidationResult(valid=False, ci_status="failed", risk="high", success_probability=0.0).model_dump()
        else:
            validation_val = ValidationResult(valid=False, ci_status="failed", risk="high", success_probability=0.0).model_dump()

        logger.info("Generated final report for CI failure")
        return FinalReport(
            summary="CI failure analyzed successfully",
            root_cause=root_cause_val.model_dump() if hasattr(root_cause_val, "model_dump") else root_cause_val,
            fix=fix_val,
            validation=validation_val,
        )