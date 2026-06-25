import requests


class GitHubMCP:

    def __init__(self, token=None):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}" if token else None
        }

    def get_file(self, repo, path, branch="main"):

        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"

        res = requests.get(url, headers=self.headers)

        if res.status_code == 200:
            return res.json()
        return None