import logging
from typing import Any

from app.schemas import ValidationResult

logger = logging.getLogger(__name__)


class ValidationAgent:
    def run(self, fix: Any) -> ValidationResult:
        if hasattr(fix, "model_dump"):
            data = fix.model_dump()
        else:
            data = fix or {}

        confidence = float(data.get("confidence", 0.5))
        logger.info("Validation confidence %.2f", confidence)

        if confidence > 0.8:
            return ValidationResult(valid=True, ci_status="passed", risk="low", success_probability=0.9)

        if confidence > 0.5:
            return ValidationResult(valid=False, ci_status="flaky", risk="medium", success_probability=0.6)

        return ValidationResult(valid=False, ci_status="failed", risk="high", success_probability=0.3)