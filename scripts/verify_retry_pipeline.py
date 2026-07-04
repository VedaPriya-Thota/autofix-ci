from app.graph.exceptions import PermanentFailureError, RetryableError
from app.graph.nodes.base_node import BaseNode
from app.graph.state import WorkflowState
from app.graph.supervisor import Supervisor
from app.graph.retry_policy import RetryPolicy
from app.schemas import ExecutionStep, ExecutionTrace


class TransientNode(BaseNode):
    def __init__(self) -> None:
        self.attempts = 0

    def retry_policy(self):
        return RetryPolicy(max_attempts=3, initial_delay_seconds=0.0, exponential_backoff=1.0, retryable_exceptions=(RetryableError,))

    def run_agent(self, state: WorkflowState):
        self.attempts += 1
        if self.attempts < 2:
            raise RetryableError('transient failure')
        return 'ok'

    def update_state(self, state: WorkflowState, result):
        state.repo_context = {'retry': 'success'}


class PermanentNode(BaseNode):
    def retry_policy(self):
        return RetryPolicy(max_attempts=3, initial_delay_seconds=0.0, exponential_backoff=1.0, retryable_exceptions=(RetryableError,))

    def run_agent(self, state: WorkflowState):
        raise PermanentFailureError('permanent failure')

    def update_state(self, state: WorkflowState, result):
        pass


class ImmediateSuccessNode(BaseNode):
    def run_agent(self, state: WorkflowState):
        return 'ok'

    def update_state(self, state: WorkflowState, result):
        state.repo_context = {'status': 'success'}


class ExhaustedNode(BaseNode):
    def __init__(self) -> None:
        self.attempts = 0

    def retry_policy(self):
        return RetryPolicy(max_attempts=2, initial_delay_seconds=0.0, exponential_backoff=1.0, retryable_exceptions=(RetryableError,))

    def run_agent(self, state: WorkflowState):
        self.attempts += 1
        raise RetryableError(f'transient failure {self.attempts}')

    def update_state(self, state: WorkflowState, result):
        pass


def print_trace(state: WorkflowState):
    print('Trace length:', len(state.execution_trace.steps) if state.execution_trace else 0)
    for step in state.execution_trace.steps:
        print(step.model_dump())


def main():
    print('=== success first attempt ===')
    state = WorkflowState()
    node = ImmediateSuccessNode()
    node.execute(state)
    print_trace(state)
    assert len(state.execution_trace.steps) == 1
    assert state.execution_trace.steps[0].status == 'success'

    print('\n=== success after retry ===')
    state = WorkflowState()
    node = TransientNode()
    node.execute(state)
    print_trace(state)
    assert len(state.execution_trace.steps) == 2
    assert state.execution_trace.steps[0].status == 'failed'
    assert state.execution_trace.steps[1].status == 'success'

    print('\n=== permanent failure ===')
    state = WorkflowState()
    node = PermanentNode()
    node.execute(state)
    print_trace(state)
    assert len(state.execution_trace.steps) == 1
    assert state.execution_trace.steps[0].status == 'failed'

    print('\n=== retries exhausted ===')
    state = WorkflowState()
    node = ExhaustedNode()
    node.execute(state)
    print_trace(state)
    assert len(state.execution_trace.steps) == 2
    assert all(step.status == 'failed' for step in state.execution_trace.steps)

    print('\n=== supervisor stop check ===')
    supervisor = Supervisor()
    state = WorkflowState(ci_log='raw log')
    state.execution_trace = ExecutionTrace(steps=[ExecutionStep(name='TestNode', status='failed', started_at='2026-01-01T00:00:00Z', finished_at='2026-01-01T00:00:00Z', duration_ms=0.0)])
    assert supervisor.next_node(state) is None

    state = WorkflowState(ci_log='raw log', structured_logs={'raw_errors': []})
    state.execution_trace = ExecutionTrace(steps=[ExecutionStep(name='TestNode', status='success', started_at='2026-01-01T00:00:00Z', finished_at='2026-01-01T00:00:00Z', duration_ms=0.0)])
    assert supervisor.next_node(state) is not None
    print('Supervisor continues after successful previous execution.')

    print('Retry pipeline verification completed successfully.')


if __name__ == '__main__':
    main()
