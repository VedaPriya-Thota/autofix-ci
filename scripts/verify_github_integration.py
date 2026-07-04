import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.integrations.git_auto_fixer import GitAutoFixer
from app.integrations.github_pr_creator import GitHubPRCreator
from app.integrations.github_webhook import github_webhook
from app.integrations.safe_patch_engine import SafePatchEngine
from app.schemas import RepairPlan


def verify() -> int:
    fixer = GitAutoFixer()
    assert hasattr(fixer, "apply_fix_and_create_pr")

    pr_creator = GitHubPRCreator()
    assert hasattr(pr_creator, "create_pr")

    patch_engine = SafePatchEngine()
    result = patch_engine.apply_patch(
        str(ROOT),
        RepairPlan(files=[], reasoning="", confidence=0.9),
    )
    assert result["status"] == "applied"

    return 0


if __name__ == "__main__":
    sys.exit(verify())
