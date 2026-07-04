from __future__ import annotations

from typing import Iterable, Type

from app.graph.exceptions import RetryableError


class RetryPolicy:
    """Generic retry configuration for node execution."""

    def __init__(
        self,
        max_attempts: int = 1,
        initial_delay_seconds: float = 0.0,
        exponential_backoff: float = 1.0,
        retryable_exceptions: Iterable[Type[BaseException]] = (),
    ) -> None:
        self.max_attempts = max(1, max_attempts)
        self.initial_delay_seconds = max(0.0, initial_delay_seconds)
        self.exponential_backoff = max(1.0, exponential_backoff)
        self.retryable_exceptions = tuple(retryable_exceptions or (RetryableError,))

    def should_retry(self, exception: BaseException, attempt: int) -> bool:
        if attempt >= self.max_attempts:
            return False
        return self._is_retryable(exception)

    def delay_seconds(self, attempt: int) -> float:
        if attempt >= self.max_attempts:
            return 0.0
        return self.initial_delay_seconds * (self.exponential_backoff ** (attempt - 1))

    def _is_retryable(self, exception: BaseException) -> bool:
        return isinstance(exception, self.retryable_exceptions)
