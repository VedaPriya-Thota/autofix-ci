from fastapi import APIRouter, Request
from app.graph.workflow import AutoFixWorkflow
from app.graph.state import WorkflowState

router = APIRouter()
workflow = AutoFixWorkflow()


@router.post("/github/webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    # Extract key CI failure info
    repo = payload.get("repository", {}).get("full_name")
    action = payload.get("action")

    # Only handle CI failures (GitHub Actions)
    if action not in ["completed"]:
        return {"status": "ignored"}

    conclusion = payload.get("workflow_run", {}).get("conclusion")

    if conclusion != "failure":
        return {"status": "no failure detected"}

    logs_url = payload.get("workflow_run", {}).get("logs_url")

    ci_log = f"GitHub Actions failed. Logs: {logs_url}"

    state = WorkflowState(
        repo_url=repo,
        ci_log=ci_log
    )

    result = workflow.run(state)

    return {
        "status": "processed",
        "result": result.final_report
    }