from pydantic import BaseModel, Field


class RepoContext(BaseModel):
    files: dict[str, str] = Field(default_factory=dict)


class DependencyGraph(BaseModel):
    nodes: list[str] = Field(default_factory=list)
    edges: list[tuple[str, str]] = Field(default_factory=list)
