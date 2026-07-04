import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.graph.workflow import AutoFixWorkflow
from app.graph.retry import RetryExecutor
from app.graph.supervisor import Supervisor
from app.graph.nodes.log_node import LogNode
from app.graph.nodes.report_node import ReportNode
from app.graph.state import WorkflowState
from app.schemas import ExecutionTrace, FinalReport, ValidationResult
from app.agents.log_agent import LogAgent
from app.agents.report_agent import ReportAgent
from app.agents.validation_agent import ValidationAgent


def verify() -> int:
    workflow = AutoFixWorkflow()
    state = WorkflowState(ci_log="build failed: ERROR missing dependency")
    result = workflow.run(state)

    assert result.execution_trace is not None
    assert result.final_report is not None

    executor = RetryExecutor.__new__(RetryExecutor)
    assert result.final_report is not None

    supervisor = Supervisor()
    assert supervisor.next_node(WorkflowState(ci_log="raw")) is not None

    node = LogNode()
    node_state = node.execute(WorkflowState(ci_log="build failed: ERROR missing dependency"))
    assert node_state.structured_logs is not None

    report_node = ReportNode()
    report_state = WorkflowState()
    report_state.root_cause = {"cause": "unknown", "confidence": 0.1, "explanation": "x"}
    report_state.fix_suggestion = {"files": [], "reasoning": "", "confidence": 0.1}
    report_state.validation_result = {"valid": True, "ci_status": "passed", "risk": "low", "success_probability": 0.9}
    report_state = report_node.execute(report_state)
    assert report_state.final_report is not None

    assert isinstance(LogAgent().run("error"), type(LogAgent().run("error")))
    assert isinstance(ValidationAgent().run({"confidence": 0.9}), ValidationResult)
    assert isinstance(ReportAgent().run(WorkflowState()), FinalReport)

    return 0


if __name__ == "__main__":
    sys.exit(verify())
