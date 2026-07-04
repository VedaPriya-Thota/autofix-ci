from __future__ import annotations

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.agents.root_cause_agent import RootCauseAgent


class RootCauseNode(BaseNode):
    """Thin node that resolves root cause through RootCauseAgent."""

    def __init__(self) -> None:
        self._agent = RootCauseAgent()

    def run_agent(self, state: WorkflowState):
        return self._agent.run(state.structured_logs)

    def update_state(self, state: WorkflowState, result) -> None:
        state.root_cause = result
