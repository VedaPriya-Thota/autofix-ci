from app.mcp.github_mcp import GitHubMCP, GitHubMCPError
import logging

logger = logging.getLogger(__name__)


class RepoContextLoader:

    def __init__(self, github_token=None):
        self.mcp = GitHubMCP(token=github_token)

    def load_context(self, repo):

        important_files = [
            "requirements.txt",
            "package.json",
            "Dockerfile",
            ".github/workflows/main.yml"
        ]

        context = {}

        for file in important_files:
            try:
                content = self.mcp.get_file(repo, file)
                if content is not None:
                    context[file] = content
            except GitHubMCPError as e:
                logger.warning(f"Failed to load file {file} from repository {repo}: {e}")
                continue

        return context