import logging
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.schemas.diagnosis import RemediationResult

logger = logging.getLogger(__name__)

class RemediationAgent(BaseAgent):
    agent_name: str = "Remediation Agent"

    async def analyze(
        self,
        triage_output: Dict[str, Any],
        log_analysis_output: Dict[str, Any],
        root_cause_output: Dict[str, Any],
        duplicate_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesizes fix recommendations across Historical Evidence, General Best Practice,
        and Agent Recommendations.
        """
        # Attempt LLM if configured
        if LLMService.is_external_llm_available():
            system_prompt = (
                "You are an expert Software Remediation Agent. Provide actionable, testable code and architectural fixes.\n"
                "CRITICAL RULES:\n"
                "1. Explicitly classify each recommendation's 'basis' as exactly one of:\n"
                "   ['Historical Evidence', 'General Best Practice', 'Agent Recommendation']\n"
                "2. Provide concrete validation steps for every recommendation.\n"
                "3. If diagnostic evidence is weak, return status: 'Insufficient Evidence'.\n"
                "Return JSON matching:\n"
                "- 'status': 'Supported' or 'Insufficient Evidence'\n"
                "- 'recommendations': Array of objects with:\n"
                "  {'recommendation', 'confidence', 'basis', 'affected_module', 'suggested_code', 'supporting_bug_ids', 'validation_steps'}\n"
                "- 'general_guidance': Additional architectural recommendations"
            )
            user_prompt = (
                f"Triage: {triage_output}\n"
                f"Log Analysis: {log_analysis_output}\n"
                f"Root Cause: {root_cause_output}\n"
                f"Duplicate Matches: {duplicate_output.get('matches', [])[:2]}"
            )
            llm_result = await LLMService.generate_json(system_prompt, user_prompt)
            if llm_result and "recommendations" in llm_result:
                try:
                    valid = RemediationResult(**llm_result)
                    return valid.model_dump()
                except Exception:
                    pass

        return self.heuristic_analyze(triage_output, log_analysis_output, root_cause_output, duplicate_output)

    def heuristic_analyze(
        self,
        triage_output: Dict[str, Any],
        log_analysis_output: Dict[str, Any],
        root_cause_output: Dict[str, Any],
        duplicate_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        if root_cause_output.get("status") == "Insufficient Evidence":
            return {
                "status": "Insufficient Evidence",
                "recommendations": [],
                "general_guidance": "Insufficient diagnostic evidence to prescribe specific code modifications. Please provide complete stack traces and configuration parameters."
            }

        exception = log_analysis_output.get("exception_type")
        failure_point = log_analysis_output.get("failure_point")
        component = triage_output.get("affected_component", "Core")

        # Collect historical bug IDs
        hist_bug_ids = [m.get("bug_id") for m in duplicate_output.get("matches", []) if m.get("bug_id")]
        if not hist_bug_ids:
            hist_bug_ids = [e.get("bug_id") for e in root_cause_output.get("supporting_evidence", []) if e.get("bug_id")]

        recommendations = []

        # Recommendation 1: Code Fix based on Exception
        if exception == "NullPointerException":
            recommendations.append({
                "recommendation": f"Add defensive null-check guards before dereferencing parameters in {failure_point or component}.",
                "confidence": 0.90,
                "basis": "Historical Evidence" if hist_bug_ids else "General Best Practice",
                "affected_module": failure_point or "Entrypoint Method",
                "suggested_code": (
                    "// Defensive null validation check\n"
                    "if (inputObject == null) {\n"
                    "    logger.warn(\"Null payload encountered at {}\", failureLocation);\n"
                    "    return Optional.empty(); // or throw IllegalArgumentException\n"
                    "}"
                ),
                "supporting_bug_ids": hist_bug_ids[:2],
                "validation_steps": [
                    "1. Formulate a unit test submitting null arguments to the target method.",
                    "2. Assert that the defensive guard handles the null safely without throwing NullPointerException.",
                    "3. Run automated regression tests on all caller endpoints."
                ]
            })
            recommendations.append({
                "recommendation": "Adopt Optional<T> returns and nullability annotations (@NonNull / @Nullable) across service boundaries.",
                "confidence": 0.84,
                "basis": "General Best Practice",
                "affected_module": component,
                "suggested_code": "@NonNull public Optional<UserSession> findSession(@NonNull String sessionId)",
                "supporting_bug_ids": [],
                "validation_steps": [
                    "1. Enable compiler or linter null-safety checks.",
                    "2. Verify clean compile without unhandled null dereferences."
                ]
            })

        elif exception in ["KeyError", "IndexOutOfBoundsException"]:
            recommendations.append({
                "recommendation": f"Verify dictionary/collection key presence before index access in {failure_point or component}.",
                "confidence": 0.88,
                "basis": "General Best Practice",
                "affected_module": failure_point or component,
                "suggested_code": (
                    "# Python defensive dictionary lookup\n"
                    "value = data.get('required_key', default_fallback)\n"
                    "if value is None:\n"
                    "    raise ValueError(\"Missing mandatory parameter: required_key\")"
                ),
                "supporting_bug_ids": hist_bug_ids[:2],
                "validation_steps": [
                    "1. Add unit test with payload missing the required key.",
                    "2. Ensure fallback or graceful validation error is returned."
                ]
            })

        elif exception in ["TimeoutException", "SocketTimeoutException", "ConnectionPoolTimeoutException"]:
            recommendations.append({
                "recommendation": f"Tune connection pool size, idle timeouts, and enforce resource closing in {component}.",
                "confidence": 0.86,
                "basis": "Historical Evidence" if hist_bug_ids else "General Best Practice",
                "affected_module": "ConnectionManager / Pool Config",
                "suggested_code": (
                    "# Ensure response and connections are closed in try-with-resources / finally\n"
                    "with client.stream('GET', url) as response:\n"
                    "    data = response.read()"
                ),
                "supporting_bug_ids": hist_bug_ids[:2],
                "validation_steps": [
                    "1. Execute load test with concurrent connections up to max pool capacity.",
                    "2. Monitor connection pool metrics to ensure connections are returned immediately after use."
                ]
            })

        else:
            recommendations.append({
                "recommendation": f"Implement structured exception handling and input validation in {failure_point or component}.",
                "confidence": 0.78,
                "basis": "Agent Recommendation",
                "affected_module": failure_point or component,
                "suggested_code": (
                    "try {\n"
                    "    processRequest(payload);\n"
                    "} catch (Exception e) {\n"
                    "    logger.error(\"Processing failed for payload: {}\", payload, e);\n"
                    "    throw new ServiceProcessingException(\"Operation failed\", e);\n"
                    "}"
                ),
                "supporting_bug_ids": hist_bug_ids[:2],
                "validation_steps": [
                    "1. Reproduce error scenario using test harness.",
                    "2. Verify graceful recovery and appropriate error logging."
                ]
            })

        return {
            "status": "Supported",
            "recommendations": recommendations,
            "general_guidance": "Adhere to the principle of fail-fast input validation at subsystem boundaries, and ensure all unit tests verify both valid paths and edge-case error conditions."
        }
