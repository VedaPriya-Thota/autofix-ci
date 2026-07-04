from __future__ import annotations

import os
import shutil
import tempfile
from typing import Any

import git

from app.integrations.safe_patch_engine import SafePatchEngine


class GitAutoFixer:
    def __init__(self) -> None:
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.patch_engine = SafePatchEngine()

    def apply_fix_and_create_pr(self, repo_url: str, fix_data: dict[str, Any]) -> dict[str, Any]:
        repo_name = repo_url.split("github.com/", 1)[1]
        temp_dir = tempfile.mkdtemp()

        try:
            clone_url = f"https://{self.github_token}@github.com/{repo_name}.git"
            repo_local = git.Repo.clone_from(clone_url, temp_dir)

            branch_name = f"autofix/{fix_data.get('reasoning', 'patch')[:20].replace(' ', '_')}"
            repo_local.git.checkout("-b", branch_name)

            patch_result = self.patch_engine.apply_patch(temp_dir, fix_data)
            if not patch_result["modified_files"]:
                return {"status": "no_changes"}

            repo_local.git.add(A=True)
            commit_msg = f"AutoFix CI: {fix_data.get('reasoning', 'AI patch fix')}"
            repo_local.index.commit(commit_msg)
            repo_local.remote().push(branch_name)

            return {
                "status": "pushed",
                "branch": branch_name,
                "modified_files": patch_result["modified_files"],
            }
        except Exception as exc:
            return {"status": "failed", "error": str(exc)}
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)