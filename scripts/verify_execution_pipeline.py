from app.graph.nodes.log_node import LogNode
from app.graph.nodes.root_cause_node import RootCauseNode
from app.graph.nodes.repair_node import RepairNode
from app.graph.nodes.validation_node import ValidationNode
from app.graph.nodes.report_node import ReportNode
from app.graph.state import WorkflowState

print('Verifying execution context pipeline...')

nodes = [
    LogNode(),
    RootCauseNode(),
    RepairNode(),
    ValidationNode(),
    ReportNode(),
]

state = WorkflowState(ci_log='raw error log')
for node in nodes:
    print('---')
    print('Node:', type(node).__name__)
    try:
        state = node.execute(state)
        print('State execution_trace length:', len(state.execution_trace.steps) if state.execution_trace else 0)
        last = state.execution_trace.steps[-1]
        print(' Last step:', last.name, last.status, last.duration_ms)
        print('  error_message:', last.error_message)
    except Exception as exc:
        print('Node raised unexpectedly:', exc)
        break

print('Final trace length:', len(state.execution_trace.steps) if state.execution_trace else 0)
print('Trace details:')
for step in state.execution_trace.steps:
    print(step.dict())
