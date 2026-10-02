import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.bug_report import BugReport
from app.models.diagnosis import AgentDiagnosis
from app.models.historical_defect import HistoricalDefect
from app.rag.chunker import chunk_historical_bug
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore
from app.schemas.growth import (
    ResolutionSubmission,
    QualityGateCheckItem,
    QualityGateCheckResult,
    PromotionResponse,
    GrowthCandidateItem,
    KnowledgeBaseGrowthStats
)

logger = logging.getLogger(__name__)

class KBGrowthService:

    @classmethod
    def check_quality_gate(cls, bug: BugReport, diagnosis: Optional[AgentDiagnosis] = None) -> QualityGateCheckResult:
        criteria: List[QualityGateCheckItem] = []
        blocking_reasons: List[str] = []

        # 1. Title & Description Completeness
        has_title = bool(bug.title and len(bug.title.strip()) >= 5)
        has_desc = bool(bug.description and len(bug.description.strip()) >= 15)
        if has_title and has_desc:
            criteria.append(QualityGateCheckItem(
                criterion="Defect Description Completeness",
                status="Passed",
                details=f"Title ({len(bug.title)} chars) and Description ({len(bug.description)} chars) meet length thresholds."
            ))
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Defect Description Completeness",
                status="Failed",
                details="Title must be >= 5 chars and Description must be >= 15 chars."
            ))
            blocking_reasons.append("Insufficient defect description detail.")

        # 2. Architectural Component
        diag_comp = None
        if diagnosis and diagnosis.triage_json:
            try:
                t_data = json.loads(diagnosis.triage_json) if isinstance(diagnosis.triage_json, str) else diagnosis.triage_json
                diag_comp = t_data.get("affected_component")
            except Exception:
                pass

        comp = bug.component or diag_comp
        if comp and comp.lower() != "general":
            criteria.append(QualityGateCheckItem(
                criterion="Architectural Component Identification",
                status="Passed",
                details=f"Target component specified: '{comp}'."
            ))
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Architectural Component Identification",
                status="Warning",
                details="Component is generic. Consider assigning a specific subsystem."
            ))

        # 3. Error Diagnostics & Stack Frame
        has_logs = bool((bug.stack_trace and len(bug.stack_trace.strip()) > 15) or (bug.error_logs and len(bug.error_logs.strip()) > 10))
        if has_logs:
            criteria.append(QualityGateCheckItem(
                criterion="Error Logs & Trace Context",
                status="Passed",
                details="Runtime stack trace or operational error logs are attached."
            ))
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Error Logs & Trace Context",
                status="Failed",
                details="Missing stack traces or error logs needed for vector indexing."
            ))
            blocking_reasons.append("No stack trace or error log provided.")

        # 4. Root Cause Documentation
        has_rc = False
        rc_text = ""
        if diagnosis and diagnosis.root_cause_json:
            try:
                r_data = json.loads(diagnosis.root_cause_json) if isinstance(diagnosis.root_cause_json, str) else diagnosis.root_cause_json
                rc_text = r_data.get("root_cause_hypothesis", "")
                if rc_text and len(rc_text.strip()) > 10:
                    has_rc = True
            except Exception:
                pass

        if has_rc or (bug.resolution_notes and "cause" in bug.resolution_notes.lower()):
            criteria.append(QualityGateCheckItem(
                criterion="Root Cause Grounding",
                status="Passed",
                details="Root cause hypothesis or causal explanation is documented."
            ))
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Root Cause Grounding",
                status="Warning",
                details="Root cause is not explicitly isolated. Will use resolution notes."
            ))

        # 5. Confirmed Resolution & Fix Details
        has_res = bool(bug.resolution_notes and len(bug.resolution_notes.strip()) >= 10)
        if has_res:
            criteria.append(QualityGateCheckItem(
                criterion="Confirmed Resolution & Actionable Fix",
                status="Passed",
                details=f"Resolution notes provided ({len(bug.resolution_notes)} chars)."
            ))
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Confirmed Resolution & Actionable Fix",
                status="Failed",
                details="Must provide verified resolution notes (minimum 10 characters)."
            ))
            blocking_reasons.append("Confirmed resolution notes are required.")

        # 6. Duplication Check
        if bug.indexed_in_kb:
            criteria.append(QualityGateCheckItem(
                criterion="Indexing Idempotency",
                status="Failed",
                details="This defect is already indexed in the Knowledge Base."
            ))
            blocking_reasons.append("Defect is already indexed in Knowledge Base.")
        else:
            criteria.append(QualityGateCheckItem(
                criterion="Indexing Idempotency",
                status="Passed",
                details="Defect has not been indexed yet."
            ))

        passed_count = sum(1 for c in criteria if c.status == "Passed")
        score = round(passed_count / len(criteria), 2)
        is_eligible = len(blocking_reasons) == 0 and score >= 0.65

        return QualityGateCheckResult(
            bug_id=str(bug.id),
            is_eligible=is_eligible,
            quality_score=score,
            criteria=criteria,
            blocking_reasons=blocking_reasons
        )

    @classmethod
    def resolve_bug(cls, bug_id: str, payload: ResolutionSubmission, db: Session) -> BugReport:
        bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
        if not bug:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bug report {bug_id} not found.")

        bug.status = "Resolved"
        bug.resolution_notes = payload.resolution_notes
        if payload.confirmed_fix_code:
            bug.confirmed_fix_code = payload.confirmed_fix_code
        if payload.component:
            bug.component = payload.component
        bug.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(bug)
        return bug

    @classmethod
    def promote_to_knowledge_base(
        cls,
        bug_id: str,
        db: Session,
        payload: Optional[ResolutionSubmission] = None
    ) -> PromotionResponse:
        bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
        if not bug:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bug report {bug_id} not found.")

        # If resolution payload provided, save resolution first
        if payload:
            bug = cls.resolve_bug(bug_id, payload, db)

        # Check Quality Gate
        gate = cls.check_quality_gate(bug, bug.diagnosis)
        if not gate.is_eligible:
            reasons = "; ".join(gate.blocking_reasons)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Defect failed Quality Gate validation: {reasons}"
            )

        # Extract diagnostics metadata
        severity = "Medium"
        priority = "Medium"
        exception_type = "UnclassifiedException"
        if bug.diagnosis:
            if bug.diagnosis.triage_json:
                try:
                    t_data = json.loads(bug.diagnosis.triage_json) if isinstance(bug.diagnosis.triage_json, str) else bug.diagnosis.triage_json
                    severity = t_data.get("severity", severity)
                    priority = t_data.get("priority", priority)
                except Exception:
                    pass
            if bug.diagnosis.log_analysis_json:
                try:
                    l_data = json.loads(bug.diagnosis.log_analysis_json) if isinstance(bug.diagnosis.log_analysis_json, str) else bug.diagnosis.log_analysis_json
                    exception_type = l_data.get("exception_type", exception_type)
                except Exception:
                    pass

        assigned_kb_id = f"PLATFORM-{bug.id[:8].upper()}"

        # 1. Create or update HistoricalDefect record
        hist_defect = HistoricalDefect(
            dataset_source="Platform",
            project="Platform-Internal",
            bug_id=assigned_kb_id,
            title=bug.title,
            description=bug.description,
            stack_trace=bug.stack_trace or "",
            error_message=exception_type,
            component=bug.component or "General",
            severity=severity,
            priority=priority,
            resolution=bug.resolution_notes or "Resolved via platform verified fix.",
            status="Resolved",
            comments=bug.confirmed_fix_code or "",
            source_reference=f"Platform Bug ID {bug.id}",
            created_at=datetime.utcnow()
        )
        db.add(hist_defect)
        db.commit()
        db.refresh(hist_defect)

        # 2. Generate Chunks for RAG Vector Store
        record_dict = {
            "bug_id": assigned_kb_id,
            "dataset_source": "Platform",
            "project": "Platform-Internal",
            "component": bug.component or "General",
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace or "",
            "resolution": bug.resolution_notes or "",
            "comments": bug.confirmed_fix_code or ""
        }
        chunks = chunk_historical_bug(record_dict)

        # 3. Generate Vector Embeddings & Upsert to ChromaDB
        if chunks:
            chunk_ids = [c["chunk_id"] for c in chunks]
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            embeddings = EmbeddingService.get_embeddings(texts)

            # Non-disruptive upsert to ChromaDB
            VectorStore.add_chunks(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            logger.info(f"Indexed {len(chunks)} chunks for {assigned_kb_id} into ChromaDB.")

        # 4. Update Bug Status
        bug.status = "Resolved"
        bug.indexed_in_kb = True
        db.commit()

        return PromotionResponse(
            success=True,
            message="Defect successfully validated, embedded, and indexed into the Knowledge Base.",
            bug_id=str(bug.id),
            assigned_kb_id=assigned_kb_id,
            historical_defect_id=str(hist_defect.id),
            indexed_chunks_count=len(chunks),
            dataset_source="Platform"
        )

    @classmethod
    def get_candidates(cls, db: Session) -> List[GrowthCandidateItem]:
        bugs = db.query(BugReport).order_by(BugReport.created_at.desc()).all()
        candidates: List[GrowthCandidateItem] = []

        for b in bugs:
            gate = cls.check_quality_gate(b, b.diagnosis)
            candidates.append(GrowthCandidateItem(
                bug_id=str(b.id),
                title=b.title,
                component=b.component or "General",
                status=b.status,
                has_diagnosis=b.diagnosis is not None,
                is_eligible_for_kb=gate.is_eligible,
                indexed_in_kb=b.indexed_in_kb or False,
                resolution_notes=b.resolution_notes,
                created_at=b.created_at
            ))

        return candidates

    @classmethod
    def get_growth_stats(cls, db: Session) -> KnowledgeBaseGrowthStats:
        total_records = db.query(HistoricalDefect).count()
        platform_records = db.query(HistoricalDefect).filter(HistoricalDefect.dataset_source == "Platform").count()
        mozilla_records = db.query(HistoricalDefect).filter(HistoricalDefect.dataset_source == "Mozilla").count()
        apache_records = db.query(HistoricalDefect).filter(HistoricalDefect.dataset_source == "Apache").count()
        eclipse_records = db.query(HistoricalDefect).filter(HistoricalDefect.dataset_source == "Eclipse").count()

        total_chunks = VectorStore.count()
        growth_pct = round((platform_records / max(1, total_records - platform_records)) * 100, 1)

        recent_promotions = []
        recent_hd = db.query(HistoricalDefect).filter(
            HistoricalDefect.dataset_source == "Platform"
        ).order_by(HistoricalDefect.created_at.desc()).limit(5).all()

        for rhd in recent_hd:
            recent_promotions.append({
                "id": str(rhd.id),
                "bug_id": rhd.bug_id,
                "title": rhd.title,
                "component": rhd.component,
                "created_at": rhd.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return KnowledgeBaseGrowthStats(
            total_knowledge_base_records=total_records,
            platform_contributed_records=platform_records,
            mozilla_records=mozilla_records,
            apache_records=apache_records,
            eclipse_records=eclipse_records,
            total_vector_chunks=total_chunks,
            growth_percentage=growth_pct,
            recent_platform_promotions=recent_promotions
        )
