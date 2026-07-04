from __future__ import annotations

import logging
from typing import Optional

from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState

logger = logging.getLogger(__name__)


class Supervisor:
    """Deterministic supervisor that maps workflow state to the next node."""

    def next_node(self, state: WorkflowState) -> Optional[BaseNode]:
        if self._has_failed_step(state):
            logger.warning("Supervisor decision: stop because previous step failed")
            return None

        if state.structured_logs is None and state.ci_log is not None:
            from app.graph.nodes.log_node import LogNode

            logger.info("Supervisor decision: dispatch LogNode")
            return LogNode()

        if state.structured_logs is not None and state.root_cause is None:
            from app.graph.nodes.root_cause_node import RootCauseNode

            logger.info("Supervisor decision: dispatch RootCauseNode")
            return RootCauseNode()

        if state.root_cause is not None and state.fix_suggestion is None:
            from app.graph.nodes.repair_node import RepairNode

            logger.info("Supervisor decision: dispatch RepairNode")
            return RepairNode()

        if state.fix_suggestion is not None and state.validation_result is None:
            from app.graph.nodes.validation_node import ValidationNode

            logger.info("Supervisor decision: dispatch ValidationNode")
            return ValidationNode()

        if state.validation_result is not None and state.final_report is None:
            from app.graph.nodes.report_node import ReportNode

            logger.info("Supervisor decision: dispatch ReportNode")
            return ReportNode()

        logger.info("Supervisor decision: workflow complete")
        return None

    def _has_failed_step(self, state: WorkflowState) -> bool:
        if state.execution_trace is None or not state.execution_trace.steps:
            return False
        return state.execution_trace.steps[-1].status == "failed"
