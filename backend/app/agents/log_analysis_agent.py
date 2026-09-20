import logging
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.utils.parsers import parse_stack_trace_heuristically
from app.schemas.diagnosis import LogAnalysisResult

logger = logging.getLogger(__name__)

class LogAnalysisAgent(BaseAgent):
    agent_name: str = "Log Analysis Agent"

    async def analyze(
        self,
        stack_trace: Optional[str] = None,
        error_logs: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parses execution logs and stack traces. Handles missing logs with 'Insufficient Evidence'.
        """
        combined_logs = f"{stack_trace or ''}\n{error_logs or ''}".strip()

        # Check for empty logs
        if not combined_logs or len(combined_logs) < 10:
            return {
                "status": "Insufficient Evidence",
                "exception_type": None,
                "error_message": "No stack trace or runtime logs were provided in the submission.",
                "failure_point": None,
                "affected_code_path": None,
                "confidence": 0.0
            }

        # Attempt LLM if configured
        if LLMService.is_external_llm_available():
            system_prompt = (
                "You are an expert Runtime Log and Stack Trace Analysis Agent. Parse the provided log text and extract a JSON object with:\n"
                "- 'status': 'Success' or 'Insufficient Evidence'\n"
                "- 'exception_type': Specific exception or error class name (e.g., NullPointerException, KeyError)\n"
                "- 'error_message': Primary root error message\n"
                "- 'failure_point': Specific source file and line number where the fault was triggered (e.g., AuthService.java:42)\n"
                "- 'affected_code_path': Sequence of method calls or modules from top to bottom (e.g., Controller -> Service -> DAO)\n"
                "- 'confidence': Float between 0.0 and 1.0\n"
                "Do not hallucinate files or lines not present in the log."
            )
            user_prompt = f"Logs / Stack Trace:\n{combined_logs[:2000]}"
            llm_result = await LLMService.generate_json(system_prompt, user_prompt)
            if llm_result and "exception_type" in llm_result:
                try:
                    valid_res = LogAnalysisResult(**llm_result)
                    return valid_res.model_dump()
                except Exception:
                    pass

        # Deterministic Heuristic Regex Parser
        return self.heuristic_analyze(stack_trace, error_logs, description)

    def heuristic_analyze(
        self,
        stack_trace: Optional[str] = None,
        error_logs: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        combined = f"{stack_trace or ''}\n{error_logs or ''}".strip()
        if not combined or len(combined) < 10:
            return {
                "status": "Insufficient Evidence",
                "exception_type": None,
                "error_message": "No stack trace or runtime error logs provided.",
                "failure_point": None,
                "affected_code_path": None,
                "confidence": 0.0
            }

        parsed = parse_stack_trace_heuristically(combined)
        return parsed
