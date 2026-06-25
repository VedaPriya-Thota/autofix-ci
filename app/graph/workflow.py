from app.graph.state import WorkflowState

from app.agents.log_agent import LogAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.repair_agent import RepairAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.report_agent import ReportAgent

from app.tools.repo_context_loader import RepoContextLoader
from app.tools.dependency_graph import DependencyGraphBuilder
from app.graph.tracer import WorkflowTracer


class AutoFixWorkflow:

    def __init__(self):

        self.log_agent = LogAgent()
        self.root_agent = RootCauseAgent()
        self.repair_agent = RepairAgent()
        self.validation_agent = ValidationAgent()
        self.report_agent = ReportAgent()

        self.repo_loader = RepoContextLoader()
        self.graph_builder = DependencyGraphBuilder()
        self.tracer = WorkflowTracer()

    def run(self, state: WorkflowState):

        # -----------------------------
        # 0. MCP + Repo Context Layer
        # -----------------------------
        try:
            if state.repo_url:
                state.repo_context = self.repo_loader.load_context(state.repo_url)
                state.dependency_graph = self.graph_builder.build(state.repo_context)
            else:
                state.repo_context = {}
                state.dependency_graph = {}
        except Exception:
            state.repo_context = {}
            state.dependency_graph = {}

        # -----------------------------
        # 1. Log Analysis Agent
        # -----------------------------
        state.structured_logs = self.log_agent.run(state.ci_log)

        # -----------------------------
        # 2. Root Cause Agent (context-aware)
        # -----------------------------
        state.root_cause = self.root_agent.run({
            "logs": state.structured_logs,
            "repo_context": state.repo_context
        })

        # -----------------------------
        # 3. Repair Agent (context-aware)
        # -----------------------------
        state.fix_suggestion = self.repair_agent.run({
            "root_cause": state.root_cause,
            "repo_context": state.repo_context
        })

        # -----------------------------
        # 4. Validation Agent
        # -----------------------------
        state.validation_result = self.validation_agent.run(
            state.fix_suggestion
        )

        # -----------------------------
        # 5. Report Agent
        # -----------------------------
        state.final_report = self.report_agent.run(state)

        # -----------------------------
        # 6. Execution Trace (FINAL STEP)
        # -----------------------------
        state.execution_trace = self.tracer.trace(state)

        # Attach system-level explainability
        state.final_report["execution_trace"] = state.execution_trace
        state.final_report["dependency_graph"] = state.dependency_graph
        state.final_report["repo_context"] = state.repo_context

        return state