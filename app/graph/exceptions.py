from __future__ import annotations


class RetryableError(Exception):
    """Marker exception for retryable failures."""


class PermanentFailureError(Exception):
    """Marker exception for non-retryable permanent failures."""


class ValidationError(PermanentFailureError):
    """Raised when workflow input or node input is invalid."""


class WorkflowExecutionError(Exception):
    """Raised when the workflow cannot continue."""


class NodeExecutionError(WorkflowExecutionError, PermanentFailureError):
    """Raised when a node fails permanently."""
