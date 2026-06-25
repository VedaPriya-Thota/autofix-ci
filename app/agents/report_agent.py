class ReportAgent:

    def run(self, state):

        return {
            "summary": "CI failure analyzed successfully",
            "root_cause": state.root_cause,
            "fix": state.fix_suggestion,
            "validation": state.validation_result
        }