from __future__ import annotations

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.agents.report_agent import ReportAgent


class ReportNode(BaseNode):

    def __init__(self) -> None:
        self._agent = ReportAgent()

    def run_agent(self, state: WorkflowState):
        return self._agent.run(state)

    def update_state(self, state: WorkflowState, result) -> None:
        state.final_report = result
