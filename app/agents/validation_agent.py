class ValidationAgent:

    def run(self, fix):

        confidence = fix.get("confidence", 0.5)

        # simulate CI behavior
        if confidence > 0.8:
            return {
                "valid": True,
                "ci_status": "passed",
                "risk": "low",
                "success_probability": 0.9
            }

        if confidence > 0.5:
            return {
                "valid": False,
                "ci_status": "flaky",
                "risk": "medium",
                "success_probability": 0.6
            }

        return {
            "valid": False,
            "ci_status": "failed",
            "risk": "high",
            "success_probability": 0.3
        }