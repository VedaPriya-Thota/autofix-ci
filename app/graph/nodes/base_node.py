from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from app.graph.exceptions import NodeExecutionError, ValidationError
from app.graph.retry import RetryExecutor
from app.graph.retry_policy import RetryPolicy
from app.graph.state import WorkflowState
from app.schemas import ExecutionStep, ExecutionTrace

logger = logging.getLogger(__name__)


class BaseNode(ABC):
    """Thin node execution lifecycle for the orchestrator."""

    def retry_policy(self) -> RetryPolicy:
        return RetryPolicy()

    def execute(self, state: WorkflowState) -> WorkflowState:
        if state.execution_trace is None:
            state.execution_trace = ExecutionTrace()

        started_at = datetime.now(timezone.utc)
        logger.info("Node started: %s", self.__class__.__name__)
        executor = RetryExecutor(self.retry_policy())

        def action() -> Any:
            self.validate_inputs(state)
            result = self.run_agent(state)
            self.update_state(state, result)
            self.post_execute(state)
            return result

        def append_step(step: ExecutionStep) -> None:
            state.execution_trace.steps.append(step)

        result, succeeded = executor.execute(
            action=action,
            step_name=self.__class__.__name__,
            serialize_output=self._serialize_output,
            append_step=append_step,
        )

        if not succeeded:
            last_step = state.execution_trace.steps[-1] if state.execution_trace.steps else None
            reason = last_step.error_message if last_step else "execution failed"
            logger.error("Node completed with failure: %s (%s)", self.__class__.__name__, reason)
            raise NodeExecutionError(f"{self.__class__.__name__} failed: {reason}")

        finished_at = datetime.now(timezone.utc)
        duration_ms = (finished_at - started_at).total_seconds() * 1000
        logger.info("Node completed: %s in %.2f ms", self.__class__.__name__, duration_ms)
        return state

    def validate_inputs(self, state: WorkflowState) -> None:
        """Optional pre-flight validation before the agent call."""
        if state is None:
            raise ValidationError("workflow state is required")

    @abstractmethod
    def run_agent(self, state: WorkflowState) -> Any:
        """Execute the node-specific agent and return its raw result."""

    @abstractmethod
    def update_state(self, state: WorkflowState, result: Any) -> None:
        """Store the node result back onto the workflow state."""

    def post_execute(self, state: WorkflowState) -> None:
        """Optional hook after state mutation."""
        return None

    def _serialize_output(self, result: Any) -> Any:
        if result is None:
            return None
        if hasattr(result, "model_dump"):
            return result.model_dump()
        if isinstance(result, (str, int, float, bool, dict, list)):
            return result
        return repr(result)
