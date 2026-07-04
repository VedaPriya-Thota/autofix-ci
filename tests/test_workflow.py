from app.graph.state import WorkflowState
from app.graph.workflow import AutoFixWorkflow


def test_workflow_runs_to_completion() -> None:
    workflow = AutoFixWorkflow()
    state = WorkflowState(ci_log="build failed: ERROR missing dependency")
    result = workflow.run(state)

    assert result.execution_trace is not None
    assert result.final_report is not None
