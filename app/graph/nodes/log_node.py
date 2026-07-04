from __future__ import annotations

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.agents.log_agent import LogAgent


class LogNode(BaseNode):
    """Thin node that parses the CI log through LogAgent."""

    def __init__(self) -> None:
        self._agent = LogAgent()

    def run_agent(self, state: WorkflowState):
        return self._agent.run(state.ci_log)

    def update_state(self, state: WorkflowState, result) -> None:
        state.structured_logs = result
