import json
import google.generativeai as genai
from app.config import config
from app.schemas import RootCauseSchema


class RootCauseAgent:

    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)

    def run(self, structured_logs):

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

            # 🧠 STRICT VALIDATION (IMPORTANT FOR KAGGLE)
            validated = RootCauseSchema(**data)

            return validated.model_dump()

        except Exception as e:
            return {
                "cause": "unknown",
                "confidence": 0.3,
                "explanation": f"validation failed: {str(e)}"
            }
