from app.agents.log_agent import LogAgent
from app.agents.report_agent import ReportAgent
from app.agents.validation_agent import ValidationAgent
from app.graph.state import WorkflowState
from app.schemas import ValidationResult


def test_log_agent_parses_errors() -> None:
    agent = LogAgent()
    result = agent.run("build failed\nERROR dependency missing")
    assert result.error_count == 1


def test_validation_agent_returns_validation_result() -> None:
    agent = ValidationAgent()
    result = agent.run({"confidence": 0.9})
    assert isinstance(result, ValidationResult)


def test_report_agent_builds_final_report() -> None:
    state = WorkflowState()
    state.root_cause = {"cause": "unknown", "confidence": 0.1, "explanation": "x"}
    state.fix_suggestion = {"files": [], "reasoning": "", "confidence": 0.1}
    state.validation_result = {"valid": True, "ci_status": "passed", "risk": "low", "success_probability": 0.9}

    result = ReportAgent().run(state)
    assert result.summary == "CI failure analyzed successfully"
