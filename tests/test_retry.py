from app.graph.exceptions import PermanentFailureError, RetryableError
from app.graph.retry import RetryExecutor
from app.graph.retry_policy import RetryPolicy
from app.schemas import ExecutionStep


def test_retry_executor_retries_retryable_errors() -> None:
    attempts = 0

    def action() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise RetryableError("temporary")
        return "ok"

    steps: list[ExecutionStep] = []
    executor = RetryExecutor(RetryPolicy(max_attempts=3, initial_delay_seconds=0.0))
    result, succeeded = executor.execute(
        action=action,
        step_name="test",
        serialize_output=lambda value: value,
        append_step=steps.append,
    )

    assert result == "ok"
    assert succeeded is True
    assert attempts == 2
    assert len(steps) == 2


def test_retry_executor_stops_for_permanent_failure() -> None:
    def action() -> str:
        raise PermanentFailureError("permanent")

    steps: list[ExecutionStep] = []
    executor = RetryExecutor(RetryPolicy(max_attempts=3, initial_delay_seconds=0.0))
    result, succeeded = executor.execute(
        action=action,
        step_name="test",
        serialize_output=lambda value: value,
        append_step=steps.append,
    )

    assert result is None
    assert succeeded is False
    assert len(steps) == 1
    assert steps[0].status == "failed"
