import re
import logging
from typing import Dict, Any, Optional
from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.schemas.diagnosis import TriageResult

logger = logging.getLogger(__name__)

class TriageAgent(BaseAgent):
    agent_name: str = "Triage Agent"

    async def analyze(
        self,
        title: str,
        description: str,
        stack_trace: Optional[str] = None,
        error_logs: Optional[str] = None,
        component: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes Triage analysis. Tries LLM if configured, otherwise falls back to heuristics.
        """
        # Attempt LLM if available
        if LLMService.is_external_llm_available():
            system_prompt = (
                "You are an expert Software Defect Triage Agent. Analyze the submitted bug report and output a valid JSON object "
                "with the following fields:\n"
                "- 'severity': Exactly one of ['Critical', 'High', 'Medium', 'Low']\n"
                "- 'priority': Exactly one of ['Critical', 'High', 'Medium', 'Low']\n"
                "- 'affected_component': Likely architectural component (e.g., Authentication, Database, UI, Network, Storage, API, Core)\n"
                "- 'confidence': Float between 0.0 and 1.0\n"
                "- 'reasoning': Clear, concise explanation for your severity, priority, and component classification.\n"
                "If evidence is vague or insufficient, reflect this with lower confidence (< 0.5) and explicitly note the ambiguity in 'reasoning'."
            )
            user_prompt = (
                f"Title: {title}\n"
                f"Description: {description}\n"
                f"User-provided Component: {component or 'Unspecified'}\n"
                f"Environment: {environment or 'Unspecified'}\n"
                f"Stack Trace Snippet: {stack_trace[:500] if stack_trace else 'None'}\n"
                f"Error Logs Snippet: {error_logs[:500] if error_logs else 'None'}"
            )
            llm_result = await LLMService.generate_json(system_prompt, user_prompt)
            if llm_result and all(k in llm_result for k in ["severity", "priority", "affected_component", "confidence", "reasoning"]):
                try:
                    valid_res = TriageResult(**llm_result)
                    return valid_res.model_dump()
                except Exception:
                    pass

        # Deterministic Heuristic Engine
        return self.heuristic_analyze(title, description, stack_trace, error_logs, component, environment)

    def heuristic_analyze(
        self,
        title: str,
        description: str,
        stack_trace: Optional[str] = None,
        error_logs: Optional[str] = None,
        component: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        combined_text = f"{title} {description} {stack_trace or ''} {error_logs or ''}".lower()

        # Insufficient Evidence check
        if (len(combined_text.strip()) < 35 and not stack_trace and not error_logs) or len(combined_text.strip()) < 20:
            return {
                "severity": "Low",
                "priority": "Low",
                "affected_component": component or "Unspecified",
                "confidence": 0.30,
                "reasoning": "Insufficient Evidence: The bug report contains very little descriptive context or technical error logs to evaluate impact reliably."
            }

        # 1. Detect Component
        if component and component.lower() not in ["unspecified", "general", "general / core subsystem"]:
            detected_component = component
        elif any(w in combined_text for w in ["memory", "leak", "vram", "oom", "metaspace", "heap", "garbage"]):
            detected_component = "Memory & Runtime Resources"
        elif any(w in combined_text for w in ["login", "auth", "token", "jwt", "password", "session", "credential", "cors"]):
            detected_component = "Authentication & Authorization"
        elif any(w in combined_text for w in ["database", "sql", "postgres", "mysql", "sqlite", "query", "deadlock", "transaction", "pool", "connection"]):
            detected_component = "Database / Persistence"
        elif any(w in combined_text for w in ["render", "canvas", "css", "button", "ui", "dom", "display", "widget", "frontend", "modal"]):
            detected_component = "UI & Frontend Rendering"
        elif any(w in combined_text for w in ["http", "socket", "timeout", "network", "fetch", "rest", "api", "endpoint"]):
            detected_component = "Networking & API"
        elif any(w in combined_text for w in ["filenotfound", "filesystem", "disk", "s3", "storage", "ioerror", "directory"]):
            detected_component = "Storage & File System"
        else:
            detected_component = "General / Core Subsystem"

        # 2. Detect Severity
        severity = "Medium"
        priority = "Medium"
        confidence = 0.85
        reasoning_points = []

        if any(w in combined_text for w in [
            "crash", "fatal", "out of memory", "oom", "metaspace", "access_violation",
            "segfault", "assertion failure", "system down", "data corruption", "infinite loop"
        ]):
            severity = "Critical"
            priority = "Critical"
            confidence = 0.93
            reasoning_points.append("Crash, fatal error, or catastrophic resource exhaustion detected.")
        elif any(w in combined_text for w in [
            "nullpointerexception", "npe", "blocked", "cannot login", "fails completely",
            "abort", "unhandled exception", "connection refused", "deadlock", "timeout"
        ]):
            severity = "High"
            priority = "High"
            confidence = 0.89
            reasoning_points.append("Critical runtime exception or core functionality blockage observed.")
        elif any(w in combined_text for w in ["slow", "glitch", "format", "alignment", "warning", "typo", "cosmetic"]):
            severity = "Low"
            priority = "Low"
            confidence = 0.82
            reasoning_points.append("Non-fatal visual, cosmetic, or minor performance degradation.")
        else:
            reasoning_points.append("Standard functional defect impacting component behavior.")

        reasoning_points.append(f"Classified under '{detected_component}' based on matching architectural domain terms.")

        return {
            "severity": severity,
            "priority": priority,
            "affected_component": detected_component,
            "confidence": confidence,
            "reasoning": " ".join(reasoning_points)
        }
