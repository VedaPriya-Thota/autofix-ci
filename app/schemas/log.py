from pydantic import BaseModel


class StructuredLogs(BaseModel):
    raw_errors: list[str]
    error_count: int
    log_type: str = "ci_failure"
