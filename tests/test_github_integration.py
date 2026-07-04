import asyncio
import hashlib
import hmac
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from app.config import config
from app.integrations.git_auto_fixer import GitAutoFixer
from app.integrations.github_pr_creator import GitHubPRCreator
from app.integrations.github_webhook import github_webhook
from app.integrations.safe_patch_engine import SafePatchEngine, UnsafePatchPathError
from app.schemas import RepairPlan


class FakeRequest:
    def __init__(self, payload, headers=None, body_bytes=None):
        self._payload = payload
        self.headers = headers or {}
        if body_bytes is not None:
            self._body = body_bytes
        else:
            self._body = json.dumps(payload).encode("utf-8")

    async def json(self):
        return self._payload

    async def body(self):
        return self._body


def compute_signature(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()



class FakeGitRepo:
    def __init__(self):
        self.calls = []
        self.git = self
        self.remote_calls = []
        self.index = SimpleNamespace(commit=self._commit)

    def _commit(self, message):
        self.calls.append(("index.commit", message))

    def checkout(self, *args, **kwargs):
        self.calls.append(("checkout", args, kwargs))

    def add(self, *args, **kwargs):
        self.calls.append(("add", args, kwargs))

    def commit(self, message):
        self.calls.append(("commit", message))
        return message

    def push(self, *args, **kwargs):
        self.calls.append(("push", args, kwargs))

    def remote(self):
        self.remote_calls.append(("remote",))
        return self


class FakeGithubRepo:
    def __init__(self):
        self.created_prs = []

    def create_pull(self, **kwargs):
        self.created_prs.append(kwargs)
        return SimpleNamespace(html_url="https://example.com/pr/1")


def test_github_webhook_routes_failure_to_workflow_and_pr_creation(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "testsecret")
    workflow_state = SimpleNamespace(final_report=SimpleNamespace(fix=RepairPlan(files=[], reasoning="fix", confidence=0.9)))

    payload = {
        "action": "workflow_run",
        "repository": {"full_name": "octo/demo"},
        "workflow_run": {"id": 42, "conclusion": "failure", "html_url": "https://example.com/workflow"},
        "ref": "refs/heads/main",
        "head_sha": "abc123",
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    sig = compute_signature("testsecret", body_bytes)

    with patch("app.integrations.github_webhook.log_fetcher.get_workflow_logs", return_value="error log") as fetch_logs, patch(
        "app.integrations.github_webhook.workflow.run", return_value=workflow_state
    ) as workflow_run, patch(
        "app.integrations.github_webhook.auto_fixer.apply_fix_and_create_pr", return_value={"status": "pushed", "branch": "autofix/test"}
    ) as apply_fix, patch("app.integrations.github_webhook.pr_creator.create_pr", return_value="https://example.com/pr/1") as create_pr:
        response = asyncio.run(
            github_webhook(
                FakeRequest(
                    payload,
                    headers={"X-Hub-Signature-256": sig},
                    body_bytes=body_bytes
                )
            )
        )

    assert response["status"] == "processed"
    assert fetch_logs.called
    assert workflow_run.called
    assert apply_fix.called
    assert create_pr.called


def test_git_auto_fixer_clones_checks_out_patches_commits_and_pushes(monkeypatch, tmp_path):
    repo = FakeGitRepo()
    readme = tmp_path / "README.md"
    readme.write_text("old\n", encoding="utf-8")

    def fake_clone_from(url, path):
        import shutil

        shutil.copytree(tmp_path, path, dirs_exist_ok=True)
        return repo

    monkeypatch.setattr("app.integrations.git_auto_fixer.git.Repo.clone_from", fake_clone_from)

    fixer = GitAutoFixer()
    result = fixer.apply_fix_and_create_pr(
        "https://github.com/octo/demo",
        {"reasoning": "fix issue", "files": [{"path": "README.md", "changes": [{"search": "old", "replace": "new"}]}]},
    )

    assert result["status"] == "pushed"
    assert result["branch"].startswith("autofix/")
    assert any(call[0] == "checkout" for call in repo.calls)
    assert any(call[0] == "add" for call in repo.calls)
    assert any(call[0] == "index.commit" for call in repo.calls)
    assert any(call[0] == "push" for call in repo.calls)


def test_patch_engine_applies_and_validates_patch(tmp_path):
    target = tmp_path / "README.md"
    target.write_text("old\n", encoding="utf-8")

    engine = SafePatchEngine()
    result = engine.apply_patch(
        str(tmp_path),
        RepairPlan(files=[{"path": "README.md", "changes": [{"search": "old", "replace": "new"}]}], reasoning="", confidence=0.9),
    )

    assert result["status"] == "applied"
    assert result["modified_files"] == ["README.md"]
    assert target.read_text(encoding="utf-8") == "new\n"


def test_patch_engine_nested_directory(tmp_path):
    nested_dir = tmp_path / "src" / "utils"
    nested_dir.mkdir(parents=True, exist_ok=True)
    target = nested_dir / "helper.py"
    target.write_text("def run():\n    pass\n", encoding="utf-8")

    engine = SafePatchEngine()
    result = engine.apply_patch(
        str(tmp_path),
        RepairPlan(files=[{"path": "src/utils/helper.py", "changes": [{"search": "pass", "replace": "return 1"}]}], reasoning="", confidence=0.9),
    )

    assert result["status"] == "applied"
    assert "src/utils/helper.py" in result["modified_files"] or "src\\utils\\helper.py" in result["modified_files"]
    assert "return 1" in target.read_text(encoding="utf-8")


def test_patch_engine_rejects_directory_traversal(tmp_path):
    engine = SafePatchEngine()
    with pytest.raises(UnsafePatchPathError):
        engine.apply_patch(
            str(tmp_path),
            RepairPlan(files=[{"path": "../../outside.py", "changes": [{"search": "foo", "replace": "bar"}]}], reasoning="", confidence=0.9),
        )


def test_patch_engine_rejects_absolute_windows_path(tmp_path):
    engine = SafePatchEngine()
    with pytest.raises(UnsafePatchPathError):
        engine.apply_patch(
            str(tmp_path),
            RepairPlan(files=[{"path": "C:\\Windows\\system32\\cmd.exe", "changes": [{"search": "foo", "replace": "bar"}]}], reasoning="", confidence=0.9),
        )


def test_patch_engine_rejects_absolute_posix_path(tmp_path):
    engine = SafePatchEngine()
    with pytest.raises(UnsafePatchPathError):
        engine.apply_patch(
            str(tmp_path),
            RepairPlan(files=[{"path": "/etc/passwd", "changes": [{"search": "foo", "replace": "bar"}]}], reasoning="", confidence=0.9),
        )


def test_patch_engine_rejects_escaping_symlink(tmp_path):
    engine = SafePatchEngine()

    # Create an outside directory and file
    outside_dir = tmp_path.parent / "outside_dir"
    outside_dir.mkdir(exist_ok=True)
    outside_file = outside_dir / "target.py"
    outside_file.write_text("foo", encoding="utf-8")

    # Create symlink inside repository pointing outside
    symlink_path = tmp_path / "symlink_outside"
    
    try:
        symlink_path.symlink_to(outside_dir, target_is_directory=True)
    except (OSError, NotImplementedError):
        # Symlinks might not be supported/permitted (e.g. non-admin Windows)
        pytest.skip("Symlinks are not supported or permitted on this platform")

    # Attempt to patch target.py via symlink
    with pytest.raises(UnsafePatchPathError):
        engine.apply_patch(
            str(tmp_path),
            RepairPlan(files=[{"path": "symlink_outside/target.py", "changes": [{"search": "foo", "replace": "bar"}]}], reasoning="", confidence=0.9),
        )


def test_pull_request_creator_uses_github_api(monkeypatch):
    fake_repo = FakeGithubRepo()

    class FakeGithub:
        def __init__(self, token):
            self.token = token

        def get_repo(self, repo_name):
            return fake_repo

    monkeypatch.setattr("app.integrations.github_pr_creator.Github", FakeGithub)

    creator = GitHubPRCreator()
    url = creator.create_pr(
        repo_name="octo/demo",
        branch_name="autofix/test",
        title="AutoFix CI: Automated Repair",
        body="Summary",
    )

    assert url == "https://example.com/pr/1"
    assert fake_repo.created_prs[0]["head"] == "autofix/test"


def test_webhook_missing_secret(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", None)
    req = FakeRequest({"action": "push"})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 500
    assert "webhook secret is not configured" in exc_info.value.detail


def test_webhook_missing_signature(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    req = FakeRequest({"action": "push"})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 401
    assert "missing" in exc_info.value.detail or "Signature header" in exc_info.value.detail


def test_webhook_invalid_signature(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    req = FakeRequest({"action": "push"}, headers={"X-Hub-Signature-256": "sha256=invalid"})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 401
    assert "Invalid" in exc_info.value.detail or "signature" in exc_info.value.detail


def test_webhook_accepted_valid_signature(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    payload = {"action": "unsupported", "repository": {"full_name": "octo/demo"}}
    body_bytes = json.dumps(payload).encode("utf-8")
    sig = compute_signature("my_secret", body_bytes)
    
    req = FakeRequest(payload, headers={"X-Hub-Signature-256": sig}, body_bytes=body_bytes)
    response = asyncio.run(github_webhook(req))
    assert response["status"] == "ignored"
    assert response["reason"] == "unsupported event"


def test_webhook_rejected_modified_payload(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    payload = {"action": "unsupported", "repository": {"full_name": "octo/demo"}}
    body_bytes = json.dumps(payload).encode("utf-8")
    sig = compute_signature("my_secret", body_bytes)
    
    modified_body_bytes = json.dumps({"action": "modified", "repository": {"full_name": "octo/demo"}}).encode("utf-8")
    req = FakeRequest(payload, headers={"X-Hub-Signature-256": sig}, body_bytes=modified_body_bytes)
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 401


def test_webhook_rejected_incorrect_secret(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    payload = {"action": "unsupported", "repository": {"full_name": "octo/demo"}}
    body_bytes = json.dumps(payload).encode("utf-8")
    sig = compute_signature("wrong_secret", body_bytes)
    
    req = FakeRequest(payload, headers={"X-Hub-Signature-256": sig}, body_bytes=body_bytes)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 401


def test_webhook_malformed_json_valid_signature(monkeypatch):
    monkeypatch.setattr(config, "GITHUB_WEBHOOK_SECRET", "my_secret")
    malformed_body = b"{"
    sig = compute_signature("my_secret", malformed_body)
    
    req = FakeRequest({}, headers={"X-Hub-Signature-256": sig}, body_bytes=malformed_body)
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(github_webhook(req))
    assert exc_info.value.status_code == 400
    assert "Invalid JSON payload" in exc_info.value.detail


from app.integrations.github_actions_logs import (
    GitHubActionsLogFetcher,
    GitHubLogFetchError,
    GitHubLogNotFoundError,
    GitHubLogAuthError,
    GitHubLogInvalidArchiveError,
)

def create_mock_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return buf.getvalue()

import io
import zipfile

def test_log_fetcher_successful_extraction():
    fetcher = GitHubActionsLogFetcher()
    
    zip_bytes = create_mock_zip({
        "job1/1_step1.txt": b"log line 1\n",
        "job1/2_step2.txt": b"log line 2\r\n", 
        "job2/1_step1.txt": b"another job line\x00", 
    })
    
    class MockRedirectResponse:
        status_code = 200
        content = zip_bytes
        text = ""

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}
        text = ""

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            assert kwargs.get("allow_redirects") is False
            return MockAPIResponse()
        elif "s3.example.com" in url:
            assert "headers" not in kwargs or not kwargs["headers"]
            return MockRedirectResponse()
        raise ValueError(f"Unexpected URL: {url}")

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        logs = fetcher.get_workflow_logs("octo", "demo", 42)
        
    assert "=== Job: job1 | Step: 1_step1 ===" in logs
    assert "log line 1\n" in logs
    assert "=== Job: job1 | Step: 2_step2 ===" in logs
    assert "log line 2\n" in logs  
    assert "\r" not in logs
    assert "=== Job: job2 | Step: 1_step1 ===" in logs
    assert "another job line" in logs
    assert "\x00" not in logs


def test_log_fetcher_missing_location_header():
    fetcher = GitHubActionsLogFetcher()
    
    class MockAPIResponse:
        status_code = 302
        headers = {}  
        text = ""

    with patch("app.integrations.github_actions_logs.requests.get", return_value=MockAPIResponse()):
        with pytest.raises(GitHubLogFetchError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert exc_info.value.status_code == 302
    assert "Location" in str(exc_info.value)


def test_log_fetcher_404_error():
    fetcher = GitHubActionsLogFetcher()
    
    class MockAPIResponse:
        status_code = 404
        text = "Not Found"

    with patch("app.integrations.github_actions_logs.requests.get", return_value=MockAPIResponse()):
        with pytest.raises(GitHubLogNotFoundError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert exc_info.value.status_code == 404
    assert exc_info.value.repo == "octo/demo"
    assert exc_info.value.run_id == 42
    assert exc_info.value.github_response == "Not Found"


def test_log_fetcher_403_error():
    fetcher = GitHubActionsLogFetcher()
    
    class MockAPIResponse:
        status_code = 403
        text = "Forbidden"

    with patch("app.integrations.github_actions_logs.requests.get", return_value=MockAPIResponse()):
        with pytest.raises(GitHubLogAuthError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert exc_info.value.status_code == 403
    assert exc_info.value.repo == "octo/demo"


def test_log_fetcher_redirect_non_200():
    fetcher = GitHubActionsLogFetcher()
    
    class MockRedirectResponse:
        status_code = 500
        text = "Internal S3 Error"

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            return MockAPIResponse()
        elif "s3.example.com" in url:
            return MockRedirectResponse()

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubLogFetchError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert exc_info.value.status_code == 500
    assert "download logs archive" in str(exc_info.value)


def test_log_fetcher_corrupted_zip():
    fetcher = GitHubActionsLogFetcher()
    
    class MockRedirectResponse:
        status_code = 200
        content = b"not a zip file"

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            return MockAPIResponse()
        elif "s3.example.com" in url:
            return MockRedirectResponse()

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubLogInvalidArchiveError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert "not a valid zip archive" in str(exc_info.value)


def test_log_fetcher_empty_archive():
    fetcher = GitHubActionsLogFetcher()
    
    zip_bytes = create_mock_zip({})
    
    class MockRedirectResponse:
        status_code = 200
        content = zip_bytes

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            return MockAPIResponse()
        elif "s3.example.com" in url:
            return MockRedirectResponse()

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubLogInvalidArchiveError) as exc_info:
            fetcher.get_workflow_logs("octo", "demo", 42)
            
    assert "empty or contains no valid .txt log files" in str(exc_info.value)


def test_log_fetcher_non_text_files_and_suspicious_paths():
    fetcher = GitHubActionsLogFetcher()
    
    zip_bytes = create_mock_zip({
        "job1/1_step1.txt": b"valid log",
        "job1/2_step2.png": b"binary png content", 
        "../outside.txt": b"malicious",              
        "__MACOSX/meta.txt": b"metadata",            
        ".hidden.txt": b"hidden file",               
    })
    
    class MockRedirectResponse:
        status_code = 200
        content = zip_bytes

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            return MockAPIResponse()
        elif "s3.example.com" in url:
            return MockRedirectResponse()

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        logs = fetcher.get_workflow_logs("octo", "demo", 42)
        
    assert "valid log" in logs
    assert "binary png content" not in logs
    assert "malicious" not in logs
    assert "metadata" not in logs
    assert "hidden file" not in logs


def test_log_fetcher_utf8_fallback():
    fetcher = GitHubActionsLogFetcher()
    
    zip_bytes = create_mock_zip({
        "job1/1_step1.txt": b"valid prefix\xffinvalid bytes",
    })
    
    class MockRedirectResponse:
        status_code = 200
        content = zip_bytes

    class MockAPIResponse:
        status_code = 302
        headers = {"Location": "https://s3.example.com/logs.zip"}

    def mock_get(url, *args, **kwargs):
        if "api.github.com" in url:
            return MockAPIResponse()
        elif "s3.example.com" in url:
            return MockRedirectResponse()

    with patch("app.integrations.github_actions_logs.requests.get", side_effect=mock_get):
        logs = fetcher.get_workflow_logs("octo", "demo", 42)
        
    assert "valid prefix" in logs
    assert "\ufffd" in logs

from app.mcp.github_mcp import (
    GitHubMCP,
    GitHubMCPNotFoundError,
    GitHubMCPAuthError,
    GitHubMCPRateLimitError,
    GitHubMCPDecodeError,
    GitHubMCPBinaryFileError,
)
from app.tools.repo_context_loader import RepoContextLoader
import base64

def test_github_mcp_raw_success():
    mcp = GitHubMCP(token="secret")
    
    class MockRawResponse:
        status_code = 200
        content = b"print('hello world')"
        text = "print('hello world')"
        
    def mock_get(url, headers):
        assert headers["Accept"] == "application/vnd.github.v3.raw"
        assert headers["Authorization"] == "token secret"
        return MockRawResponse()
        
    with patch("app.mcp.github_mcp.requests.get", side_effect=mock_get):
        content = mcp.get_file("octo/demo", "main.py")
        assert content == "print('hello world')"

def test_github_mcp_base64_fallback_success():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 406
        content = b""
        text = ""
        
    class MockJsonResponse:
        status_code = 200
        def json(self):
            return {
                "content": base64.b64encode(b"fallback content").decode("utf-8"),
                "encoding": "base64"
            }
            
    def mock_get(url, headers):
        if "vnd.github.v3.raw" in headers.get("Accept", ""):
            return MockRawResponse()
        return MockJsonResponse()
        
    with patch("app.mcp.github_mcp.requests.get", side_effect=mock_get):
        content = mcp.get_file("octo/demo", "main.py")
        assert content == "fallback content"

def test_github_mcp_invalid_base64():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 406
        text = ""
        
    class MockJsonResponse:
        status_code = 200
        def json(self):
            return {
                "content": "not-valid-base64!@#$",
                "encoding": "base64"
            }
            
    def mock_get(url, headers):
        if "raw" in headers.get("Accept", ""):
            return MockRawResponse()
        return MockJsonResponse()
        
    with patch("app.mcp.github_mcp.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubMCPDecodeError) as exc_info:
            mcp.get_file("octo/demo", "main.py")
        assert "decode base64" in str(exc_info.value)

def test_github_mcp_unsupported_encoding():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 406
        text = ""
        
    class MockJsonResponse:
        status_code = 200
        def json(self):
            return {
                "content": "some text",
                "encoding": "utf-8"
            }
            
    def mock_get(url, headers):
        if "raw" in headers.get("Accept", ""):
            return MockRawResponse()
        return MockJsonResponse()
        
    with patch("app.mcp.github_mcp.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubMCPDecodeError) as exc_info:
            mcp.get_file("octo/demo", "main.py")
        assert "Unsupported content encoding" in str(exc_info.value)

def test_github_mcp_binary_file_rejection_raw():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 200
        content = b"\x00\x01\x02\x03 binary data \x00"
        
    with patch("app.mcp.github_mcp.requests.get", return_value=MockRawResponse()):
        with pytest.raises(GitHubMCPBinaryFileError):
            mcp.get_file("octo/demo", "image.png")

def test_github_mcp_empty_file():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 200
        content = b""
        
    with patch("app.mcp.github_mcp.requests.get", return_value=MockRawResponse()):
        assert mcp.get_file("octo/demo", "empty.txt") == ""

def test_github_mcp_missing_content_field():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 406
        text = ""
        
    class MockJsonResponse:
        status_code = 200
        def json(self):
            return {"name": "main.py", "encoding": "base64"} 
            
    def mock_get(url, headers):
        if "raw" in headers.get("Accept", ""):
            return MockRawResponse()
        return MockJsonResponse()
        
    with patch("app.mcp.github_mcp.requests.get", side_effect=mock_get):
        with pytest.raises(GitHubMCPDecodeError) as exc_info:
            mcp.get_file("octo/demo", "main.py")
        assert "Missing 'content' field" in str(exc_info.value)

def test_github_mcp_404():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 404
        text = "Not Found"
        
    with patch("app.mcp.github_mcp.requests.get", return_value=MockRawResponse()):
        with pytest.raises(GitHubMCPNotFoundError):
            mcp.get_file("octo/demo", "missing.txt")

def test_github_mcp_403():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 403
        text = "Forbidden"
        
    with patch("app.mcp.github_mcp.requests.get", return_value=MockRawResponse()):
        with pytest.raises(GitHubMCPAuthError):
            mcp.get_file("octo/demo", "secret.txt")

def test_github_mcp_rate_limiting():
    mcp = GitHubMCP()
    
    class MockRawResponse:
        status_code = 403
        text = "API rate limit exceeded"
        
    with patch("app.mcp.github_mcp.requests.get", return_value=MockRawResponse()):
        with pytest.raises(GitHubMCPRateLimitError):
            mcp.get_file("octo/demo", "main.py")

def test_repo_context_loader_continues_after_failure():
    loader = RepoContextLoader()
    
    def mock_get_file(repo, file):
        if file == "Dockerfile":
            raise GitHubMCPNotFoundError("Not found")
        elif file == "package.json":
            raise GitHubMCPBinaryFileError("Binary")
        return f"content of {file}"
        
    with patch.object(loader.mcp, "get_file", side_effect=mock_get_file):
        context = loader.load_context("octo/demo")
        
    assert "Dockerfile" not in context
    assert "package.json" not in context
    assert context["requirements.txt"] == "content of requirements.txt"
    assert context[".github/workflows/main.yml"] == "content of .github/workflows/main.yml"
