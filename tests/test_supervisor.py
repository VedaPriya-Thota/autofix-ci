from app.graph.state import WorkflowState
from app.graph.supervisor import Supervisor


def test_next_node_progresses_through_pipeline() -> None:
    supervisor = Supervisor()

    state = WorkflowState(ci_log="raw log")
    assert supervisor.next_node(state).__class__.__name__ == "LogNode"

    state.structured_logs = object()
    assert supervisor.next_node(state).__class__.__name__ == "RootCauseNode"

    state.root_cause = object()
    assert supervisor.next_node(state).__class__.__name__ == "RepairNode"

    state.fix_suggestion = object()
    assert supervisor.next_node(state).__class__.__name__ == "ValidationNode"

    state.validation_result = object()
    assert supervisor.next_node(state).__class__.__name__ == "ReportNode"

    state.final_report = object()
    assert supervisor.next_node(state) is None


def test_next_node_stops_after_failed_step() -> None:
    supervisor = Supervisor()
    state = WorkflowState(ci_log="raw log")
    state.execution_trace = type("Trace", (), {"steps": [type("Step", (), {"status": "failed"})()]})
    assert supervisor.next_node(state) is None
