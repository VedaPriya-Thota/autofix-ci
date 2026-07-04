from __future__ import annotations

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.agents.validation_agent import ValidationAgent


class ValidationNode(BaseNode):

    def __init__(self) -> None:
        self._agent = ValidationAgent()

    def run_agent(self, state: WorkflowState):
        return self._agent.run(state.fix_suggestion)

    def update_state(self, state: WorkflowState, result) -> None:
        state.validation_result = result
