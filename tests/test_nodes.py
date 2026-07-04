from app.graph.nodes.log_node import LogNode
from app.graph.nodes.report_node import ReportNode
from app.graph.state import WorkflowState


def test_log_node_populates_structured_logs() -> None:
    state = WorkflowState(ci_log="build failed: ERROR missing dependency")
    node = LogNode()
    state = node.execute(state)

    assert state.structured_logs is not None
    assert state.structured_logs.error_count >= 1


def test_report_node_creates_final_report() -> None:
    state = WorkflowState()
    state.root_cause = type("RootCause", (), {"model_dump": lambda self: {"cause": "unknown", "confidence": 0.1, "explanation": "x"}})()
    state.fix_suggestion = type("Fix", (), {"model_dump": lambda self: {"files": [], "reasoning": "", "confidence": 0.1}})()
    state.validation_result = type("Validation", (), {"model_dump": lambda self: {"valid": True, "ci_status": "passed", "risk": "low", "success_probability": 0.9}})()
    node = ReportNode()
    state = node.execute(state)

    assert state.final_report is not None
    assert state.final_report.summary == "CI failure analyzed successfully"
