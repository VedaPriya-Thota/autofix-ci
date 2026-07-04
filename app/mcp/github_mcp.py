import base64
import requests
import logging

logger = logging.getLogger(__name__)

class GitHubMCPError(Exception):
    def __init__(self, message, status_code=None, repo=None, path=None, github_response=None):
        super().__init__(message)
        self.status_code = status_code
        self.repo = repo
        self.path = path
        self.github_response = github_response

class GitHubMCPNotFoundError(GitHubMCPError):
    pass

class GitHubMCPAuthError(GitHubMCPError):
    pass

class GitHubMCPRateLimitError(GitHubMCPError):
    pass

class GitHubMCPBinaryFileError(GitHubMCPError):
    pass

class GitHubMCPDecodeError(GitHubMCPError):
    pass


class GitHubMCP:

    def __init__(self, token=None):
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def get_file(self, repo, path, branch="main") -> str | None:
        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
        
        # 1. Try raw content endpoint
        headers_raw = dict(self.headers)
        headers_raw["Accept"] = "application/vnd.github.v3.raw"
        
        try:
            res = requests.get(url, headers=headers_raw)
        except Exception as e:
            raise GitHubMCPError(f"Failed to connect to GitHub API: {e}", repo=repo, path=path)

        # Handle rate limiting
        if res.status_code == 429 or (res.status_code == 403 and "rate limit" in res.text.lower()):
            raise GitHubMCPRateLimitError("GitHub API rate limit exceeded", status_code=res.status_code, repo=repo, path=path, github_response=res.text)
        elif res.status_code == 404:
            raise GitHubMCPNotFoundError(f"File {path} not found in {repo}", status_code=res.status_code, repo=repo, path=path, github_response=res.text)
        elif res.status_code in {401, 403}:
            raise GitHubMCPAuthError(f"Unauthorized or Forbidden to read {path} in {repo}", status_code=res.status_code, repo=repo, path=path, github_response=res.text)
        
        # If raw retrieval was successful (200), process the raw bytes
        if res.status_code == 200:
            content_bytes = res.content
            
            if self._is_binary_bytes(content_bytes):
                raise GitHubMCPBinaryFileError(f"File {path} is a binary file and cannot be read as text", status_code=200, repo=repo, path=path)
                
            if not content_bytes:
                return ""
                
            return content_bytes.decode("utf-8", errors="replace")

        # 2. Fallback: If raw retrieval is not 200, try JSON content endpoint
        headers_json = dict(self.headers)
        headers_json["Accept"] = "application/vnd.github.v3+json"
        
        try:
            res = requests.get(url, headers=headers_json)
        except Exception as e:
            raise GitHubMCPError(f"Failed to connect to GitHub API (fallback): {e}", repo=repo, path=path)

        if res.status_code != 200:
            return None

        try:
            data = res.json()
        except Exception as e:
            raise GitHubMCPDecodeError(f"Failed to parse JSON response: {e}", status_code=200, repo=repo, path=path)

        if isinstance(data, list):
            raise GitHubMCPError(f"Path {path} resolves to a directory, not a file", status_code=200, repo=repo, path=path)

        content_encoded = data.get("content")
        if content_encoded is None:
            raise GitHubMCPDecodeError("Missing 'content' field in JSON response", status_code=200, repo=repo, path=path)
            
        encoding = data.get("encoding", "")
        if encoding != "base64":
            raise GitHubMCPDecodeError(f"Unsupported content encoding: {encoding}", status_code=200, repo=repo, path=path)

        try:
            content_bytes = base64.b64decode(content_encoded.replace("\n", "").replace("\r", ""))
        except Exception as e:
            raise GitHubMCPDecodeError(f"Failed to decode base64 content: {e}", status_code=200, repo=repo, path=path)

        if self._is_binary_bytes(content_bytes):
            raise GitHubMCPBinaryFileError(f"File {path} is a binary file", status_code=200, repo=repo, path=path)

        if not content_bytes:
            return ""

        return content_bytes.decode("utf-8", errors="replace")

    def _is_binary_bytes(self, content_bytes: bytes) -> bool:
        if b"\x00" in content_bytes:
            return True
        sample = content_bytes[:1024]
        if not sample:
            return False
        non_printable = sum(1 for b in sample if (b < 32 and b not in (9, 10, 13)) or b == 127)
        return (non_printable / len(sample)) > 0.3