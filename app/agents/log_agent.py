import logging

from app.schemas import ParsedLog

logger = logging.getLogger(__name__)


class LogAgent:
    def run(self, ci_log: str) -> ParsedLog:
        errors: list[str] = []

        for line in ci_log.split("\n"):
            if "ERROR" in line or "Exception" in line:
                errors.append(line.strip())

        logger.info("Parsed %s errors from CI log", len(errors))
        return ParsedLog(raw_errors=errors, error_count=len(errors), log_type="ci_failure")