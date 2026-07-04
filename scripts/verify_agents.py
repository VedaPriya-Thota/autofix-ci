from app.agents.repair_agent import RepairAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.report_agent import ReportAgent
from app.schemas import RepairPlan, ValidationResult, FinalReport

class MockState:
    pass

repair = RepairAgent()
fix = repair.run({
    'root_cause': {'cause': 'test', 'confidence': 0.1},
    'repo_context': {}
})
print('repair type:', type(fix).__name__, isinstance(fix, RepairPlan))

validation = ValidationAgent()
validation_result = validation.run(fix)
print('validation type:', type(validation_result).__name__, isinstance(validation_result, ValidationResult))

report = ReportAgent()
state = MockState()
state.root_cause = {'cause': 'test', 'confidence': 0.1}
state.fix_suggestion = fix
state.validation_result = validation_result
final = report.run(state)
print('report type:', type(final).__name__, isinstance(final, FinalReport))
