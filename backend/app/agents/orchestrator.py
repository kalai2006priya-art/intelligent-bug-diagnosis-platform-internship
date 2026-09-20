import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.bug_report import BugReport
from app.models.diagnosis import AgentDiagnosis
from app.rag.retriever import RAGRetriever
from app.agents.triage_agent import TriageAgent
from app.agents.log_analysis_agent import LogAnalysisAgent
from app.agents.root_cause_agent import RootCauseAgent
from app.agents.duplicate_detection_agent import DuplicateDetectionAgent
from app.agents.remediation_agent import RemediationAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.log_analysis_agent = LogAnalysisAgent()
        self.root_cause_agent = RootCauseAgent()
        self.duplicate_detection_agent = DuplicateDetectionAgent()
        self.remediation_agent = RemediationAgent()

    async def run_pipeline(self, db: Session, bug: BugReport) -> AgentDiagnosis:
        """
        Executes the multi-agent diagnosis pipeline across all 5 agents:
        Stage 1: Triage + Log Analysis
        Stage 2: RAG Retrieval + Root Cause + Duplicate Detection
        Stage 3: Remediation
        Stage 4: Commit to Database
        """
        logger.info(f"Starting orchestration pipeline for Bug ID: {bug.id}")
        bug.status = "Analyzing"
        db.commit()

        # -------------------------------------------------------------
        # STAGE 1: Triage Agent & Log Analysis Agent
        # -------------------------------------------------------------
        try:
            triage_res = await self.triage_agent.analyze(
                title=bug.title,
                description=bug.description,
                stack_trace=bug.stack_trace,
                error_logs=bug.error_logs,
                component=bug.component,
                environment=bug.environment
            )
        except Exception as e:
            logger.error(f"Triage Agent failed: {e}", exc_info=True)
            triage_res = {
                "severity": "Medium",
                "priority": "Medium",
                "affected_component": bug.component or "General",
                "confidence": 0.3,
                "reasoning": f"Analysis partially unavailable due to agent error: {str(e)}"
            }

        try:
            log_analysis_res = await self.log_analysis_agent.analyze(
                stack_trace=bug.stack_trace,
                error_logs=bug.error_logs,
                description=bug.description
            )
        except Exception as e:
            logger.error(f"Log Analysis Agent failed: {e}", exc_info=True)
            log_analysis_res = {
                "status": "Insufficient Evidence",
                "exception_type": None,
                "error_message": f"Log analysis failed: {str(e)}",
                "failure_point": None,
                "affected_code_path": None,
                "confidence": 0.0
            }

        # -------------------------------------------------------------
        # STAGE 2: RAG Retrieval from Historical Knowledge Base
        # -------------------------------------------------------------
        rag_query = f"{bug.title} {log_analysis_res.get('exception_type') or ''} {log_analysis_res.get('failure_point') or ''} {bug.description[:200]}".strip()
        try:
            retrieved_defects = RAGRetriever.retrieve_similar_defects(rag_query, top_k=5)
        except Exception as e:
            logger.error(f"RAG Retrieval failed: {e}", exc_info=True)
            retrieved_defects = []

        # Find any other bugs previously submitted by users on this platform for duplicate search
        submitted_matches = []
        try:
            prior_bugs = db.query(BugReport).filter(BugReport.id != bug.id).order_by(BugReport.created_at.desc()).limit(10).all()
            for pb in prior_bugs:
                # Simple similarity check
                sim = 0.5
                if pb.title.lower() == bug.title.lower():
                    sim = 0.95
                elif any(word in pb.title.lower() for word in bug.title.lower().split() if len(word) > 4):
                    sim = 0.70
                if sim >= 0.65:
                    submitted_matches.append({
                        "bug_id": str(pb.id)[:8],
                        "similarity": sim,
                        "title": pb.title,
                        "component": pb.component or "General",
                        "status": pb.status
                    })
        except Exception as e:
            logger.warning(f"Could not query submitted bugs: {e}")

        # -------------------------------------------------------------
        # STAGE 3: Root Cause Agent & Duplicate Detection Agent
        # -------------------------------------------------------------
        try:
            root_cause_res = await self.root_cause_agent.analyze(
                bug_description=bug.description,
                triage_output=triage_res,
                log_analysis_output=log_analysis_res,
                retrieved_defects=retrieved_defects
            )
        except Exception as e:
            logger.error(f"Root Cause Agent failed: {e}", exc_info=True)
            root_cause_res = {
                "status": "Insufficient Evidence",
                "root_cause_hypothesis": "Analysis unavailable due to agent error.",
                "confidence": 0.0,
                "supporting_evidence": [],
                "reasoning": f"Root Cause Agent error: {str(e)}"
            }

        try:
            duplicate_res = await self.duplicate_detection_agent.analyze(
                bug_title=bug.title,
                bug_description=bug.description,
                retrieved_defects=retrieved_defects,
                submitted_matches=submitted_matches
            )
        except Exception as e:
            logger.error(f"Duplicate Detection Agent failed: {e}", exc_info=True)
            duplicate_res = {
                "status": "Insufficient Evidence",
                "matches": [],
                "reasoning": f"Duplicate Detection Agent error: {str(e)}"
            }

        # -------------------------------------------------------------
        # STAGE 4: Remediation Agent
        # -------------------------------------------------------------
        try:
            remediation_res = await self.remediation_agent.analyze(
                triage_output=triage_res,
                log_analysis_output=log_analysis_res,
                root_cause_output=root_cause_res,
                duplicate_output=duplicate_res
            )
        except Exception as e:
            logger.error(f"Remediation Agent failed: {e}", exc_info=True)
            remediation_res = {
                "status": "Insufficient Evidence",
                "recommendations": [],
                "general_guidance": f"Remediation unavailable: {str(e)}"
            }

        # Calculate overall confidence
        c_triage = triage_res.get("confidence", 0.5)
        c_log = log_analysis_res.get("confidence", 0.5)
        c_rc = root_cause_res.get("confidence", 0.5)
        overall_confidence = round((c_triage + c_log + c_rc) / 3.0, 2)

        # -------------------------------------------------------------
        # STAGE 5: Save Structured Findings in Database
        # -------------------------------------------------------------
        # Check if diagnosis already exists for this bug
        diagnosis = db.query(AgentDiagnosis).filter(AgentDiagnosis.bug_id == bug.id).first()
        if not diagnosis:
            diagnosis = AgentDiagnosis(bug_id=bug.id)
            db.add(diagnosis)

        diagnosis.status = "Completed"
        diagnosis.overall_confidence = overall_confidence
        diagnosis.triage_json = json.dumps(triage_res)
        diagnosis.log_analysis_json = json.dumps(log_analysis_res)
        diagnosis.root_cause_json = json.dumps(root_cause_res)
        diagnosis.duplicate_detection_json = json.dumps(duplicate_res)
        diagnosis.remediation_json = json.dumps(remediation_res)
        diagnosis.updated_at = datetime.utcnow()

        # Update Bug status
        bug.status = "Diagnosed"
        if triage_res.get("affected_component") and not bug.component:
            bug.component = triage_res["affected_component"]

        db.commit()
        db.refresh(diagnosis)
        logger.info(f"Orchestration completed successfully for Bug ID: {bug.id}")
        return diagnosis
