from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable

from app.graph.exceptions import PermanentFailureError, RetryableError
from app.graph.retry_policy import RetryPolicy
from app.schemas import ExecutionStep

logger = logging.getLogger(__name__)


class RetryExecutor:
    def __init__(self, policy: RetryPolicy) -> None:
        self.policy = policy

    def execute(
        self,
        action: Callable[[], Any],
        step_name: str,
        serialize_output: Callable[[Any], Any],
        append_step: Callable[[ExecutionStep], None],
        post_attempt: Callable[[], None] | None = None,
    ) -> tuple[Any | None, bool]:
        attempt = 1
        while True:
            started_at = datetime.now(timezone.utc)
            step = ExecutionStep(
                name=step_name,
                status="running",
                started_at=started_at.isoformat(),
                finished_at=started_at.isoformat(),
                duration_ms=0.0,
                details=f"attempt {attempt}/{self.policy.max_attempts}",
            )
            should_retry = False
            delay_seconds = 0.0
            try:
                result = action()
                step.status = "success"
                step.output = serialize_output(result)
                return result, True
            except PermanentFailureError as exc:
                step.status = "failed"
                step.error_message = str(exc)
                step.exception_type = exc.__class__.__name__
                logger.error("Node failed permanently: %s", exc)
                return None, False
            except RetryableError as exc:
                step.status = "failed"
                step.error_message = str(exc)
                step.exception_type = exc.__class__.__name__
                should_retry = self._should_retry(exc, attempt)
                if should_retry:
                    delay_seconds = self.policy.delay_seconds(attempt)
                    logger.warning("Retry attempt %s/%s for %s after failure: %s", attempt, self.policy.max_attempts, step_name, exc)
                else:
                    logger.error("Retry exhausted for %s: %s", step_name, exc)
                    return None, False
            except Exception as exc:
                step.status = "failed"
                step.error_message = str(exc)
                step.exception_type = exc.__class__.__name__
                should_retry = self._should_retry(exc, attempt)
                if should_retry:
                    delay_seconds = self.policy.delay_seconds(attempt)
                    logger.warning("Retry attempt %s/%s for %s after failure: %s", attempt, self.policy.max_attempts, step_name, exc)
                else:
                    logger.error("Node failed: %s", exc)
                    return None, False
            finally:
                finished_at = datetime.now(timezone.utc)
                step.finished_at = finished_at.isoformat()
                step.duration_ms = (finished_at - started_at).total_seconds() * 1000
                append_step(step)
                if post_attempt:
                    post_attempt()
            if should_retry:
                if delay_seconds > 0:
                    time.sleep(delay_seconds)
                attempt += 1
                continue
            return None, False

    def _should_retry(self, exception: BaseException, attempt: int) -> bool:
        return self.policy.should_retry(exception, attempt)
