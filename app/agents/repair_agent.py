import json
import google.generativeai as genai
from app.tools.patch_generator import PatchGenerator
from app.config import config



class RepairAgent:

    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.patch = PatchGenerator()

    def run(self, input_data):

        root_cause = input_data.get("root_cause", {})
        repo_context = input_data.get("repo_context", {})

        prompt = f"""
You are a senior DevOps engineer in a large-scale production engineering team.

Your task is to generate a safe, minimal, and effective fix for a CI/CD failure.

You are given:

### ROOT CAUSE:
{json.dumps(root_cause, indent=2)}

### REPOSITORY CONTEXT (important files):
{json.dumps(repo_context, indent=2)}

---

### YOUR TASK:
1. Identify the exact file(s) that need modification
2. Propose minimal fix (do NOT over-change code)
3. Ensure fix is production-safe
4. Consider dependency conflicts, CI pipelines, Docker builds, tests

---

### OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "fix_type": "dependency_fix | config_fix | build_fix | test_fix | docker_fix | unknown",
  "affected_files": ["file1", "file2"],
  "action": "clear step-by-step fix instruction",
  "patch_suggestion": self.patch.generate(original_code, fixed_code),
  "confidence": 0.0,
  "reasoning": "why this fix solves the issue"
}}

Rules:
- Output ONLY JSON
- No markdown
- No extra text
- Be precise and conservative
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean Gemini formatting artifacts
            text = text.replace("```json", "").replace("```", "").strip()

            result = json.loads(text)

            # Basic validation fallback safety
            if "fix_type" not in result:
                raise ValueError("Invalid output structure")

            return result

        except Exception as e:
            return {
                "fix_type": "unknown",
                "affected_files": [],
                "action": "manual review required",
                "patch_suggestion": "",
                "confidence": 0.3,
                "reasoning": f"repair agent failed: {str(e)}"
            }