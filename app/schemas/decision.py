from pydantic import BaseModel


class DecisionResult(BaseModel):
    should_apply: bool
    reason: str
    confidence: float
