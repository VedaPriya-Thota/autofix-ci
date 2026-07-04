import json
import logging
from typing import Any

from app.config import config
from app.schemas import RepairPlan
from app.tools.patch_generator import PatchGenerator

logger = logging.getLogger(__name__)


class RepairAgent:
    def __init__(self) -> None:
        self.model: Any | None = None
        self._initialize_model()
        self.patch = PatchGenerator()

    def _initialize_model(self) -> None:
        if not config.GEMINI_API_KEY:
            self.model = None
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        except Exception:
            self.model = None

    def run(self, input_data: dict[str, Any]) -> RepairPlan:

        root_cause = input_data.get("root_cause", {})
        repo_context = input_data.get("repo_context", {})

        if hasattr(root_cause, "model_dump"):
            root_cause = root_cause.model_dump()
        if hasattr(repo_context, "model_dump"):
            repo_context = repo_context.model_dump()

        if self.model is None:
            logger.warning("Repair agent unavailable; using fallback")
            return RepairPlan(files=[], reasoning="repair agent unavailable; using fallback", confidence=0.3)

        root_cause_json = json.dumps(root_cause, indent=2)
        repo_context_json = json.dumps(repo_context, indent=2)

        prompt = (
            "You are a senior DevOps engineer in a large-scale production engineering team.\n\n"
            "Your task is to generate a safe, minimal, and effective fix for a CI/CD failure.\n\n"
            "You are given:\n\n"
            "### ROOT CAUSE:\n"
            f"{root_cause_json}\n\n"
            "### REPOSITORY CONTEXT (important files):\n"
            f"{repo_context_json}\n\n"
            "---\n\n"
            "### YOUR TASK:\n"
            "1. Identify the exact file(s) that need modification\n"
            "2. Propose minimal fix (do NOT over-change code)\n"
            "3. Ensure fix is production-safe\n"
            "4. Consider dependency conflicts, CI pipelines, Docker builds, tests\n\n"
            "---\n\n"
            "### OUTPUT FORMAT (STRICT JSON ONLY):\n\n"
            "{\n"
            "  \"files\": [\n"
            "    {\n"
            "      \"path\": \"relative/file/path.py\",\n"
            "      \"changes\": [\n"
            "        {\n"
            "          \"search\": \"old code snippet\",\n"
            "          \"replace\": \"new corrected code\"\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            "  \"reasoning\": \"why this fix works\",\n"
            "  \"confidence\": 0.0\n"
            "}\n\n"
            "Rules:\n"
            "- Return ONLY JSON in the specified format\n"
            "- No markdown\n"
            "- No extra text\n"
            "- Be precise and conservative\n"
        )

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean Gemini formatting artifacts
            text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)

            # Basic validation fallback safety
            if not isinstance(result, dict) or "files" not in result:
                raise ValueError("Invalid output structure")

            # Return canonical schema instance
            return RepairPlan(**result)

        except Exception as e:
            return RepairPlan(files=[], reasoning=f"repair agent failed: {str(e)}", confidence=0.3)