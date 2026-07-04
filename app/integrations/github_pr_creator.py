from __future__ import annotations

import os
from typing import Any

from github import Github


class GitHubPRCreator:
    def __init__(self) -> None:
        self.github = Github(os.getenv("GITHUB_TOKEN"))

    def create_pr(self, repo_name: str, branch_name: str, title: str, body: str) -> str:
        repo = self.github.get_repo(repo_name)
        pr = repo.create_pull(title=title, body=body, head=branch_name, base="main")
        return pr.html_url