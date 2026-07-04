from pydantic import BaseModel


class PatchChange(BaseModel):
    search: str
    replace: str


class PatchFile(BaseModel):
    path: str
    changes: list[PatchChange]


class RepairSuggestion(BaseModel):
    files: list[PatchFile]
    reasoning: str
    confidence: float
