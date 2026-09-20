from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

# ==========================================
# 1. Triage Agent Schemas
# ==========================================
class TriageResult(BaseModel):
    severity: str = Field(..., description="Critical, High, Medium, Low")
    priority: str = Field(..., description="Critical, High, Medium, Low")
    affected_component: str = Field(..., description="Subsystem or module affected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reasoning: str = Field(..., description="Explanation for classification")

# ==========================================
# 2. Log Analysis Agent Schemas
# ==========================================
class LogAnalysisResult(BaseModel):
    status: str = Field("Success", description="'Success' or 'Insufficient Evidence'")
    exception_type: Optional[str] = Field(None, description="Extracted exception or error type")
    error_message: Optional[str] = Field(None, description="Primary error message")
    failure_point: Optional[str] = Field(None, description="File and line number of root failure")
    affected_code_path: Optional[str] = Field(None, description="Reconstructed call path")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

# ==========================================
# 3. Root Cause Agent Schemas
# ==========================================
class SupportingEvidenceItem(BaseModel):
    bug_id: str
    source: str
    similarity: float
    evidence: str

class RootCauseResult(BaseModel):
    status: str = Field("Supported", description="'Supported' or 'Insufficient Evidence'")
    root_cause_hypothesis: str = Field(..., description="Probable root cause hypothesis")
    confidence: float = Field(..., ge=0.0, le=1.0)
    supporting_evidence: List[SupportingEvidenceItem] = Field(default_factory=list)
    reasoning: str = Field(..., description="Inductive deduction connecting evidence to symptoms")

# ==========================================
# 4. Duplicate Detection Agent Schemas
# ==========================================
class DuplicateMatchItem(BaseModel):
    bug_id: str
    similarity: float
    title: str
    source: Optional[str] = None
    project: Optional[str] = None
    component: Optional[str] = None
    resolution_summary: Optional[str] = None

class DuplicateDetectionResult(BaseModel):
    status: str = Field("New / Unmatched", description="'Likely Duplicate', 'Related Issue', 'New / Unmatched', or 'Insufficient Evidence'")
    matches: List[DuplicateMatchItem] = Field(default_factory=list)
    reasoning: str = Field(..., description="Explanation of match results and similarity thresholding")

# ==========================================
# 5. Remediation Agent Schemas
# ==========================================
class RemediationRecommendationItem(BaseModel):
    recommendation: str
    confidence: float
    basis: str = Field("Historical Evidence", description="'Historical Evidence', 'General Best Practice', or 'Agent Recommendation'")
    affected_module: Optional[str] = None
    suggested_code: Optional[str] = None
    supporting_bug_ids: List[str] = Field(default_factory=list)
    validation_steps: List[str] = Field(default_factory=list)

class RemediationResult(BaseModel):
    status: str = Field("Supported", description="'Supported' or 'Insufficient Evidence'")
    recommendations: List[RemediationRecommendationItem] = Field(default_factory=list)
    general_guidance: Optional[str] = None

# ==========================================
# Complete Diagnosis Response
# ==========================================
class DiagnosisResponse(BaseModel):
    id: str
    bug_id: str
    status: str
    overall_confidence: float
    triage: TriageResult
    log_analysis: LogAnalysisResult
    root_cause: RootCauseResult
    duplicate_detection: DuplicateDetectionResult
    remediation: RemediationResult
    created_at: datetime
    updated_at: datetime
