from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExecutionStep(BaseModel):
    name: str
    status: str
    started_at: str
    finished_at: str
    duration_ms: float
    output: Any | None = None
    error_message: str | None = None
    exception_type: str | None = None
    details: str | None = None


class ExecutionTrace(BaseModel):
    steps: list[ExecutionStep] = Field(default_factory=list)

    def append(self, step: ExecutionStep) -> None:
        self.steps.append(step)


def iso_now() -> str:
    return datetime.utcnow().isoformat() + "Z"
