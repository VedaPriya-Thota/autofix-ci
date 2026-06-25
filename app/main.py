from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import AutoFixWorkflow
from app.graph.state import WorkflowState
from app.integrations.github_webhook import router as github_router

app = FastAPI()
workflow = AutoFixWorkflow()

app.include_router(github_router)

class InputRequest(BaseModel):
    ci_log: str


@app.post("/analyze")
def analyze(req: InputRequest):

    state = WorkflowState(ci_log=req.ci_log)

    result = workflow.run(state)

    return result.final_report