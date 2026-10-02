from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.api.auth import get_current_user_optional
from app.services.kb_growth_service import KBGrowthService
from app.schemas.growth import (
    ResolutionSubmission,
    QualityGateCheckResult,
    PromotionResponse,
    GrowthCandidateItem,
    KnowledgeBaseGrowthStats
)

router = APIRouter(prefix="/knowledge-base/growth", tags=["Knowledge Base Growth (M4.2)"])

@router.post("/resolve/{bug_id}")
def mark_bug_resolved(
    bug_id: str,
    payload: ResolutionSubmission,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Marks a defect as resolved with verified fix code and resolution notes."""
    bug = KBGrowthService.resolve_bug(bug_id, payload, db)
    return {
        "status": "success",
        "message": f"Bug {bug_id} marked as resolved.",
        "bug_id": str(bug.id),
        "bug_status": bug.status,
        "resolved_at": bug.resolved_at
    }

@router.get("/validate/{bug_id}", response_model=QualityGateCheckResult)
def validate_quality_gate(
    bug_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Evaluates whether a defect satisfies the Quality Gate criteria
    for inclusion in the Historical Defect Knowledge Base.
    """
    from app.models.bug_report import BugReport
    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bug {bug_id} not found.")
    return KBGrowthService.check_quality_gate(bug, bug.diagnosis)

@router.post("/promote/{bug_id}", response_model=PromotionResponse)
def promote_to_knowledge_base(
    bug_id: str,
    payload: Optional[ResolutionSubmission] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Validates Quality Gate, generates 384-dimensional vector embeddings,
    and indexes the resolved defect into ChromaDB without disrupting historical records.
    """
    return KBGrowthService.promote_to_knowledge_base(bug_id, db, payload)

@router.get("/candidates", response_model=List[GrowthCandidateItem])
def list_growth_candidates(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns all bugs and their eligibility for Knowledge Base indexing."""
    return KBGrowthService.get_candidates(db)

@router.get("/stats", response_model=KnowledgeBaseGrowthStats)
def get_growth_statistics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Returns continuous growth metrics for the Knowledge Base."""
    return KBGrowthService.get_growth_stats(db)
