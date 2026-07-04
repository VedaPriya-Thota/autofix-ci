from pydantic import BaseModel


class ValidationResult(BaseModel):
    valid: bool
    ci_status: str
    risk: str
    success_probability: float
