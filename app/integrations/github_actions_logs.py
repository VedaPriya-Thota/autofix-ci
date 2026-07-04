import io
import os
import zipfile
import requests
import logging

logger = logging.getLogger(__name__)


class GitHubLogFetchError(Exception):
    def __init__(self, message, status_code=None, repo=None, run_id=None, github_response=None):
        super().__init__(message)
        self.status_code = status_code
        self.repo = repo
        self.run_id = run_id
        self.github_response = github_response


class GitHubLogNotFoundError(GitHubLogFetchError):
    pass


class GitHubLogAuthError(GitHubLogFetchError):
    pass


class GitHubLogInvalidArchiveError(GitHubLogFetchError):
    pass


class GitHubActionsLogFetcher:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Accept": "application/vnd.github+json"
        }

    def get_workflow_logs(self, owner, repo, run_id):
        repo_full = f"{owner}/{repo}"
        url = f"https://api.github.com/repos/{repo_full}/actions/runs/{run_id}/logs"

        try:
            response = requests.get(url, headers=self.headers, allow_redirects=False)
        except Exception as e:
            raise GitHubLogFetchError(
                f"Failed to make API request: {e}",
                repo=repo_full,
                run_id=run_id
            )

        if response.status_code == 404:
            raise GitHubLogNotFoundError(
                f"Workflow run logs not found for run_id {run_id}",
                status_code=404,
                repo=repo_full,
                run_id=run_id,
                github_response=response.text
            )
        elif response.status_code in {401, 403}:
            raise GitHubLogAuthError(
                f"Authentication failed or forbidden for run_id {run_id}: status {response.status_code}",
                status_code=response.status_code,
                repo=repo_full,
                run_id=run_id,
                github_response=response.text
            )
        elif response.status_code != 302:
            raise GitHubLogFetchError(
                f"Unexpected status code from GitHub logs API: {response.status_code}",
                status_code=response.status_code,
                repo=repo_full,
                run_id=run_id,
                github_response=response.text
            )

        redirect_url = response.headers.get("Location")
        if not redirect_url:
            raise GitHubLogFetchError(
                "Redirect URL missing in Location header after 302",
                status_code=302,
                repo=repo_full,
                run_id=run_id,
                github_response=str(response.headers)
            )

        # Download the zip file without self.headers (S3 / Azure blobs reject it)
        try:
            zip_response = requests.get(redirect_url)
        except Exception as e:
            raise GitHubLogFetchError(
                f"Failed to request redirect URL: {e}",
                repo=repo_full,
                run_id=run_id
            )

        if zip_response.status_code != 200:
            if zip_response.status_code == 404:
                raise GitHubLogNotFoundError(
                    f"Logs redirect URL returned 404",
                    status_code=404,
                    repo=repo_full,
                    run_id=run_id,
                    github_response=zip_response.text
                )
            elif zip_response.status_code in {401, 403}:
                raise GitHubLogAuthError(
                    f"Logs redirect URL returned status {zip_response.status_code}",
                    status_code=zip_response.status_code,
                    repo=repo_full,
                    run_id=run_id,
                    github_response=zip_response.text
                )
            else:
                raise GitHubLogFetchError(
                    f"Failed to download logs archive: status {zip_response.status_code}",
                    status_code=zip_response.status_code,
                    repo=repo_full,
                    run_id=run_id,
                    github_response=zip_response.text
                )

        try:
            zip_file = zipfile.ZipFile(io.BytesIO(zip_response.content))
        except zipfile.BadZipFile as e:
            raise GitHubLogInvalidArchiveError(
                f"Downloaded file is not a valid zip archive: {e}",
                status_code=zip_response.status_code,
                repo=repo_full,
                run_id=run_id
            )

        contents = []
        # Preserve original archive order by iterating over infolist() in default archive order
        for info in zip_file.infolist():
            if info.is_dir():
                continue

            name = info.filename

            # Reject suspicious filenames (e.g. traversal attacks, absolute paths)
            if ".." in name or name.startswith("/") or name.startswith("\\"):
                logger.warning("Rejecting suspicious filename in logs archive: %s", name)
                continue

            # Ignore hidden metadata (__MACOSX, etc.)
            parts = name.split("/")
            if any(p.startswith(".") or p.startswith("__") for p in parts):
                continue

            # Only process .txt files
            if not name.endswith(".txt"):
                continue

            try:
                with zip_file.open(name) as f:
                    log_bytes = f.read()
            except Exception as e:
                raise GitHubLogInvalidArchiveError(
                    f"Failed to read file {name} from archive: {e}",
                    status_code=200,
                    repo=repo_full,
                    run_id=run_id
                )

            # Strip trailing null bytes if present
            log_bytes = log_bytes.rstrip(b'\x00')

            # UTF-8 decode with replacement fallback
            log_text = log_bytes.decode("utf-8", errors="replace")

            # Normalize line endings: \r\n to \n
            log_text = log_text.replace("\r\n", "\n")

            # Extract job and step names from path if structured (e.g. job_name/step_name.txt)
            if len(parts) >= 2:
                job_name = parts[-2]
                step_name = parts[-1].replace(".txt", "")
            else:
                job_name = "default"
                step_name = parts[0].replace(".txt", "")

            contents.append(f"=== Job: {job_name} | Step: {step_name} ===\n{log_text}")

        if not contents:
            raise GitHubLogInvalidArchiveError(
                "Downloaded logs archive is empty or contains no valid .txt log files",
                status_code=200,
                repo=repo_full,
                run_id=run_id
            )

        return "\n".join(contents)