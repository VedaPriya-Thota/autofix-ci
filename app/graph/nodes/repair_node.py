from __future__ import annotations

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState


class RepairNode(BaseNode):

    def __init__(self) -> None:
        self._agent = None

    def run_agent(self, state: WorkflowState):
        if self._agent is None:
            from app.agents.repair_agent import RepairAgent

            self._agent = RepairAgent()
        return self._agent.run({
            "root_cause": state.root_cause,
            "repo_context": state.repo_context,
        })

    def update_state(self, state: WorkflowState, result) -> None:
        state.fix_suggestion = result
