from app.graph.nodes.log_node import LogNode
from app.graph.nodes.root_cause_node import RootCauseNode
from app.graph.nodes.repair_node import RepairNode
from app.graph.nodes.validation_node import ValidationNode
from app.graph.nodes.report_node import ReportNode
from app.graph.state import WorkflowState

print('Verifying node execution...')

nodes = [
    (LogNode(), WorkflowState(ci_log='raw log')),
    (RootCauseNode(), WorkflowState(structured_logs={'raw_errors': [], 'error_count': 0, 'log_type': 'ci_failure'}, repo_context={})),
    (RepairNode(), WorkflowState(root_cause={'cause': 'genuine issue', 'confidence': 0.4}, repo_context={})),
    (ValidationNode(), WorkflowState(fix_suggestion={'confidence': 0.9})),
    (ReportNode(), WorkflowState(root_cause={'cause': 'genuine issue', 'confidence': 0.4}, fix_suggestion={'files': [], 'reasoning': 'ok', 'confidence': 0.3}, validation_result={'valid': True, 'ci_status': 'passed', 'risk': 'low', 'success_probability': 0.9})),
]

for node, state in nodes:
    print('Node:', type(node).__name__)
    state_before = state
    updated_state = node.execute(state)
    print('  updated state:', updated_state)
    assert updated_state is state_before

print('All nodes executed successfully.')
