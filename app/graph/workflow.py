from __future__ import annotations

import logging
from typing import Optional

from app.graph.exceptions import NodeExecutionError
from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.graph.supervisor import Supervisor

logger = logging.getLogger(__name__)


class AutoFixWorkflow:
    def __init__(self) -> None:
        self._supervisor = Supervisor()

    def run(self, state: WorkflowState) -> WorkflowState:
        """Orchestrate execution by deferring scheduling to Supervisor."""
        while True:
            node: Optional[BaseNode] = self._supervisor.next_node(state)
            if node is None:
                break
            logger.info("Workflow step: %s", node.__class__.__name__)
            try:
                state = node.execute(state)
            except NodeExecutionError as exc:
                logger.error("Workflow stopped: %s", exc)
                break
        logger.info("Workflow completion: %s", "completed" if state.final_report is not None else "stopped")
        return state