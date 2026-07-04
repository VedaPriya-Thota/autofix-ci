from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class UnsafePatchPathError(ValueError):
    """Raised when a patch path is outside the repository base directory."""
    pass


class SafePatchEngine:
    def apply_patch(self, repo_path: str, patch_data: Any) -> dict[str, Any]:
        payload = patch_data.model_dump() if hasattr(patch_data, "model_dump") else patch_data
        files = payload.get("files", []) if isinstance(payload, dict) else []
        modified_files: list[str] = []

        try:
            resolved_repo_path = Path(repo_path).resolve()
        except Exception as e:
            raise UnsafePatchPathError(f"Could not resolve repository path {repo_path}: {e}")

        for file_patch in files:
            if isinstance(file_patch, dict):
                patch_path_str = file_patch.get("path", "")
                changes = file_patch.get("changes", [])
            else:
                patch_path_str = getattr(file_patch, "path", "")
                changes = getattr(file_patch, "changes", [])

            # Compute and resolve target path
            target_path = Path(resolved_repo_path) / patch_path_str
            try:
                resolved_target = target_path.resolve()
            except Exception as e:
                raise UnsafePatchPathError(f"Could not resolve path {patch_path_str}: {e}")

            # Verify resolved target path is strictly contained within resolved repository root
            if not resolved_target.is_relative_to(resolved_repo_path) or resolved_target == resolved_repo_path:
                raise UnsafePatchPathError(
                    f"Unsafe patch path detected: {patch_path_str} (resolves to {resolved_target}) "
                    f"is outside repository root {resolved_repo_path}"
                )

            file_path = str(resolved_target)

            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            original_content = content
            for change in changes:
                if isinstance(change, dict):
                    search = change.get("search")
                    replace = change.get("replace")
                else:
                    search = getattr(change, "search", None)
                    replace = getattr(change, "replace", None)
                if search is not None and search in content:
                    content = content.replace(search, replace or "")

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as handle:
                    handle.write(content)
                modified_files.append(os.path.relpath(file_path, repo_path))

        return {"modified_files": modified_files, "status": "applied"}

