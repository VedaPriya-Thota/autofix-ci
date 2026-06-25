from pydantic import BaseModel
from typing import Literal


class RootCauseSchema(BaseModel):
    cause: Literal[
        "dependency_failure",
        "build_error",
        "test_failure",
        "runtime_error",
        "unknown"
    ]
    confidence: float
    explanation: str