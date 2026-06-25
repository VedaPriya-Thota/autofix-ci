from app.mcp.github_mcp import GitHubMCP


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
            content = self.mcp.get_file(repo, file)

            if content:
                context[file] = content

        return context