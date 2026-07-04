from app.graph.supervisor import Supervisor
from app.graph.state import WorkflowState

s = Supervisor()

cases = {
    'needs_log': WorkflowState(ci_log='raw log...'),
    'parsed_only': WorkflowState(ci_log='raw', structured_logs=object()),
    'root_found': WorkflowState(ci_log='raw', structured_logs=object(), root_cause=object()),
    'patched': WorkflowState(ci_log='raw', structured_logs=object(), root_cause=object(), fix_suggestion=object()),
    'validated': WorkflowState(ci_log='raw', structured_logs=object(), root_cause=object(), fix_suggestion=object(), validation_result=object()),
    'completed': WorkflowState(ci_log='raw', structured_logs=object(), root_cause=object(), fix_suggestion=object(), validation_result=object(), final_report=object()),
    'empty': WorkflowState(),
}

for name, state in cases.items():
    node = s.next_node(state)
    print(name, '->', type(node).__name__ if node is not None else None)
