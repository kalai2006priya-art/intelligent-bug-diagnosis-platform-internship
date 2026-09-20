from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.user import User
from app.models.bug_report import BugReport
from app.models.diagnosis import AgentDiagnosis
from app.schemas.bug import BugCreate, BugResponse, BugUploadResponse
from app.schemas.diagnosis import DiagnosisResponse
from app.services.bug_service import BugService
from app.agents.orchestrator import AgentOrchestrator
from app.api.auth import get_current_user, get_current_user_optional

router = APIRouter(tags=["Bug Reports"])
orchestrator = AgentOrchestrator()

@router.post("/bugs", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
def create_bug(
    bug_in: BugCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new defect submission for the authenticated developer."""
    bug = BugService.create_bug(db, bug_in, current_user.id)
    return BugResponse(
        id=bug.id,
        user_id=bug.user_id,
        title=bug.title,
        description=bug.description,
        stack_trace=bug.stack_trace,
        error_logs=bug.error_logs,
        component=bug.component,
        environment=bug.environment,
        status=bug.status,
        created_at=bug.created_at,
        updated_at=bug.updated_at,
        has_diagnosis=False
    )

@router.post("/bugs/upload", response_model=BugUploadResponse)
async def upload_bug_log_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Parses an uploaded `.txt` or `.log` file into structured title, description,
    stack trace, and error log sections for bug submission.
    """
    return await BugService.process_file_upload(file)

@router.get("/bugs", response_model=List[BugResponse])
def list_bugs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists bug reports. Defaults to current authenticated user's submissions."""
    uid = current_user.id if user_only else None
    bugs = BugService.list_bugs(db, user_id=uid, skip=skip, limit=limit)
    response_list = []
    for b in bugs:
        response_list.append(BugResponse(
            id=b.id,
            user_id=b.user_id,
            title=b.title,
            description=b.description,
            stack_trace=b.stack_trace,
            error_logs=b.error_logs,
            component=b.component,
            environment=b.environment,
            status=b.status,
            created_at=b.created_at,
            updated_at=b.updated_at,
            has_diagnosis=b.diagnosis is not None
        ))
    return response_list

@router.get("/bugs/stats/summary")
def get_bug_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns telemetry counts for the developer dashboard."""
    total = BugService.count_bugs(db, user_id=current_user.id)
    diagnosed = BugService.count_diagnosed_bugs(db, user_id=current_user.id)
    return {
        "total_bugs": total,
        "diagnosed_bugs": diagnosed,
        "pending_analysis": max(0, total - diagnosed)
    }

@router.get("/bugs/{bug_id}", response_model=BugResponse)
def get_bug(
    bug_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches details for a specific defect report."""
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug report with ID '{bug_id}' not found."
        )
    return BugResponse(
        id=bug.id,
        user_id=bug.user_id,
        title=bug.title,
        description=bug.description,
        stack_trace=bug.stack_trace,
        error_logs=bug.error_logs,
        component=bug.component,
        environment=bug.environment,
        status=bug.status,
        created_at=bug.created_at,
        updated_at=bug.updated_at,
        has_diagnosis=bug.diagnosis is not None
    )

@router.post("/bugs/{bug_id}/analyze", response_model=DiagnosisResponse)
async def analyze_bug(
    bug_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes the 5-Agent Diagnosis Orchestration pipeline on a defect report:
    Triage -> Log Analysis -> Historical RAG -> Root Cause -> Duplicate Detection -> Remediation.
    """
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug report with ID '{bug_id}' not found."
        )

    diagnosis = await orchestrator.run_pipeline(db, bug)
    return DiagnosisResponse(
        id=diagnosis.id,
        bug_id=diagnosis.bug_id,
        status=diagnosis.status,
        overall_confidence=diagnosis.overall_confidence,
        triage=diagnosis.triage_data,
        log_analysis=diagnosis.log_analysis_data,
        root_cause=diagnosis.root_cause_data,
        duplicate_detection=diagnosis.duplicate_detection_data,
        remediation=diagnosis.remediation_data,
        created_at=diagnosis.created_at,
        updated_at=diagnosis.updated_at
    )

@router.get("/bugs/{bug_id}/diagnosis", response_model=DiagnosisResponse)
def get_bug_diagnosis(
    bug_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the complete structured multi-agent diagnosis report for a defect."""
    bug = BugService.get_bug_by_id(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bug report with ID '{bug_id}' not found."
        )

    diagnosis = db.query(AgentDiagnosis).filter(AgentDiagnosis.bug_id == bug_id).first()
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis report has not been generated for this bug yet. Run POST /bugs/{bug_id}/analyze."
        )

    return DiagnosisResponse(
        id=diagnosis.id,
        bug_id=diagnosis.bug_id,
        status=diagnosis.status,
        overall_confidence=diagnosis.overall_confidence,
        triage=diagnosis.triage_data,
        log_analysis=diagnosis.log_analysis_data,
        root_cause=diagnosis.root_cause_data,
        duplicate_detection=diagnosis.duplicate_detection_data,
        remediation=diagnosis.remediation_data,
        created_at=diagnosis.created_at,
        updated_at=diagnosis.updated_at
    )
