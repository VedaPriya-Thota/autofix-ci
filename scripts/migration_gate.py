from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

AGENT_FILES = [
    "app/agents/log_agent.py",
    "app/agents/root_cause_agent.py",
    "app/agents/repair_agent.py",
    "app/agents/validation_agent.py",
    "app/agents/report_agent.py",
]

LEGACY_TERMS = ["StructuredLogs", "RepairSuggestion"]
CANONICAL_TERMS = ["ParsedLog", "RepairPlan"]
AGENT_MODULES = [
    "app.agents.log_agent",
    "app.agents.root_cause_agent",
    "app.agents.repair_agent",
    "app.agents.validation_agent",
    "app.agents.report_agent",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    sys.exit(1)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def schema_import_check() -> None:
    try:
        from app.schemas import ParsedLog, RepairPlan  # noqa: F401
    except Exception as exc:
        fail(f"Schema import check failed: {exc}")


def legacy_leak_detection() -> None:
    for relative_path in AGENT_FILES:
        path = ROOT / relative_path
        if not path.exists():
            fail(f"Agent file missing: {relative_path}")
        text = read_text(path)
        for term in LEGACY_TERMS:
            if term in text:
                fail(f"Legacy schema leakage detected in {relative_path}: {term}")


def agent_import_validation() -> None:
    for module_name in AGENT_MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            fail(f"Failed to import agent module {module_name}: {exc}")


def canonical_schema_usage_check() -> None:
    found = {term: False for term in CANONICAL_TERMS}
    for relative_path in AGENT_FILES:
        path = ROOT / relative_path
        text = read_text(path)
        for term in CANONICAL_TERMS:
            if term in text:
                found[term] = True
    for term, present in found.items():
        if not present:
            fail(f"Canonical schema usage check failed: {term} not found in any agent file")


def smoke_test_execution() -> None:
    try:
        from app.agents.log_agent import LogAgent

        agent = LogAgent()
        agent.run("ERROR test")
    except Exception as exc:
        fail(f"Smoke test failed: {exc}")


def main() -> None:
    schema_import_check()
    legacy_leak_detection()
    agent_import_validation()
    canonical_schema_usage_check()
    smoke_test_execution()
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
