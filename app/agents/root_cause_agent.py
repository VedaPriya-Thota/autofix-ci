import json
import logging
from typing import Any

from app.config import config
from app.schemas import RootCauseSchema

logger = logging.getLogger(__name__)


class RootCauseAgent:
    def __init__(self) -> None:
        self.model: Any | None = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        if not config.GEMINI_API_KEY:
            return

        try:
            import google.generativeai as genai

            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        except Exception:
            self.model = None

    def run(self, structured_logs: Any) -> RootCauseSchema:
        if self.model is None:
            logger.warning("Root cause agent unavailable; using fallback")
            return RootCauseSchema(
                cause="unknown",
                confidence=0.3,
                explanation="root cause agent unavailable; using fallback",
            )
        prompt = f"""
You are a senior DevOps engineer.

Analyze CI/CD logs and return STRICT JSON only.

Logs:
{structured_logs}

Return format:
{{
  "cause": "dependency_failure | build_error | test_failure | runtime_error | unknown",
  "confidence": 0.0-1.0,
  "explanation": "short reasoning"
}}

Rules:
- JSON only
- No markdown
- No extra text
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "")

            data = json.loads(text)
            validated = RootCauseSchema(**data)
            return validated

        except Exception as e:
            return RootCauseSchema(
                cause="unknown",
                confidence=0.3,
                explanation=f"validation failed: {str(e)}"
            )
