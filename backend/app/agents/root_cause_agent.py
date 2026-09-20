import logging
from typing import Dict, Any, List, Optional
from app.agents.base_agent import BaseAgent
from app.services.llm_service import LLMService
from app.schemas.diagnosis import RootCauseResult

logger = logging.getLogger(__name__)

class RootCauseAgent(BaseAgent):
    agent_name: str = "Root Cause Agent"

    async def analyze(
        self,
        bug_description: str,
        triage_output: Dict[str, Any],
        log_analysis_output: Dict[str, Any],
        retrieved_defects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes Stage 1 outputs with RAG-retrieved historical defects.
        Outputs structured root cause analysis strictly separating evidence from reasoning.
        """
        # Attempt LLM if configured
        if LLMService.is_external_llm_available():
            system_prompt = (
                "You are an expert Root Cause Analysis Agent. Synthesize user symptoms with retrieved historical defects.\n"
                "CRITICAL REQUIREMENTS:\n"
                "1. Strictly separate Retrieved Evidence from your Agent Reasoning and Root Cause Hypothesis.\n"
                "2. Never assert an unverified hypothesis as an absolute fact.\n"
                "3. If evidence is weak or similarity is low, set status to 'Insufficient Evidence'.\n"
                "Return a JSON object with:\n"
                "- 'status': 'Supported' or 'Insufficient Evidence'\n"
                "- 'root_cause_hypothesis': The probable root cause explanation\n"
                "- 'confidence': Float between 0.0 and 1.0\n"
                "- 'supporting_evidence': Array of objects with {'bug_id', 'source', 'similarity', 'evidence'}\n"
                "- 'reasoning': Deductive reasoning connecting the evidence to the observed failure point"
            )
            user_prompt = (
                f"Bug Description:\n{bug_description}\n\n"
                f"Triage: {triage_output.get('severity')} severity in {triage_output.get('affected_component')}\n"
                f"Parsed Exception: {log_analysis_output.get('exception_type')}\n"
                f"Failure Point: {log_analysis_output.get('failure_point')}\n"
                f"Code Path: {log_analysis_output.get('affected_code_path')}\n\n"
                f"Historical Defect Evidence:\n" +
                "\n".join([
                    f"- Bug ID: {d.get('metadata', {}).get('bug_id')} ({d.get('metadata', {}).get('source')}, sim {d.get('similarity', 0)}): {d.get('text', '')[:200]}"
                    for d in retrieved_defects[:3]
                ])
            )
            llm_result = await LLMService.generate_json(system_prompt, user_prompt)
            if llm_result and "root_cause_hypothesis" in llm_result:
                try:
                    valid = RootCauseResult(**llm_result)
                    return valid.model_dump()
                except Exception:
                    pass

        return self.heuristic_analyze(bug_description, triage_output, log_analysis_output, retrieved_defects)

    def heuristic_analyze(
        self,
        bug_description: str,
        triage_output: Dict[str, Any],
        log_analysis_output: Dict[str, Any],
        retrieved_defects: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        exception = log_analysis_output.get("exception_type")
        failure_point = log_analysis_output.get("failure_point")
        component = triage_output.get("affected_component", "Core")

        # Extract top supporting evidence items
        supporting_evidence = []
        for d in retrieved_defects[:3]:
            meta = d.get("metadata", {})
            sim = d.get("similarity", 0.0)
            if sim > 0.40:
                supporting_evidence.append({
                    "bug_id": meta.get("bug_id", "HIST-DEFECT"),
                    "source": meta.get("source", "Defect Repository"),
                    "similarity": sim,
                    "evidence": f"Historical precedent [{meta.get('title', '')}]. Resolution: {meta.get('resolution', 'Reported fix')}."
                })

        # Check for Insufficient Evidence
        if not exception and not failure_point and len(bug_description.strip()) < 30:
            return {
                "status": "Insufficient Evidence",
                "root_cause_hypothesis": "Insufficient diagnostic evidence to formulate a reliable root cause hypothesis.",
                "confidence": 0.25,
                "supporting_evidence": [],
                "reasoning": "The defect report lacks actionable runtime logs, exception frames, or detailed symptoms required to isolate the failure mechanism."
            }

        # Build grounded hypothesis based on exception and failure point
        if exception == "NullPointerException":
            hypothesis = (
                f"Probable null reference dereference in {failure_point or 'the execution flow'} "
                f"caused by an uninitialized variable or missing null validation on incoming parameters."
            )
            reasoning = (
                f"The stack trace isolates an unhandled NullPointerException in {failure_point}. "
                f"In analogous historical defects, this occurs when boundary data or dependency objects "
                f"are accessed prior to null checks."
            )
            confidence = 0.88 if failure_point else 0.75

        elif exception in ["KeyError", "IndexOutOfBoundsException"]:
            hypothesis = (
                f"Collection access violation in {failure_point or 'data lookup'}: "
                f"the application attempted to access an entry or index that does not exist in the collection."
            )
            reasoning = (
                f"The exception indicates that a lookup operation failed without a defensive existence check "
                f"or default fallback handling."
            )
            confidence = 0.85

        elif exception in ["TimeoutException", "SocketTimeoutException", "ConnectionPoolTimeoutException"]:
            hypothesis = (
                f"Resource starvation or network latency threshold breach in {failure_point or component}: "
                f"the subsystem timed out waiting for a socket, connection lease, or remote service response."
            )
            reasoning = (
                f"High concurrency, network partitions, or connection pool leaks typically precipitate this failure mode, "
                f"as corroborated by historical timeout defects."
            )
            confidence = 0.86

        elif exception in ["OutOfMemoryError", "NativeCrashException"]:
            hypothesis = (
                f"Memory exhaustion or invalid memory dereference in {failure_point or component}: "
                f"runtime resources were depleted or native memory bounds were violated."
            )
            reasoning = (
                f"Correlates with unbounded heap consumption, unreleased native buffers, or cyclic event listener retention."
            )
            confidence = 0.90

        else:
            hypothesis = (
                f"Probable functional anomaly in {component} affecting {failure_point or 'execution logic'}: "
                f"an unexpected state or malformed input disrupted expected control flow."
            )
            reasoning = (
                f"Inferred from defect summary and correlated historical defect records. "
                f"Further telemetry is recommended to verify exact execution state."
            )
            confidence = 0.70

        return {
            "status": "Supported",
            "root_cause_hypothesis": hypothesis,
            "confidence": confidence,
            "supporting_evidence": supporting_evidence,
            "reasoning": reasoning
        }
