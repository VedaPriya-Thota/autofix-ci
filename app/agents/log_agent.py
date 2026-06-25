import re


class LogAgent:

    def run(self, ci_log: str):

        errors = []

        for line in ci_log.split("\n"):
            if "ERROR" in line or "Exception" in line:
                errors.append(line.strip())

        return {
            "raw_errors": errors,
            "error_count": len(errors),
            "log_type": "ci_failure"
        }