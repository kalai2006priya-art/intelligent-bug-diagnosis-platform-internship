from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ResolutionSubmission(BaseModel):
    resolution_notes: str = Field(..., min_length=10, description="Detailed explanation of the confirmed fix and resolution")
    confirmed_fix_code: Optional[str] = Field(None, description="Actual code snippet, configuration, or patch applied")
    confirmed_root_cause: Optional[str] = Field(None, description="Confirmed root cause mechanism")
    component: Optional[str] = Field(None, description="Confirmed or updated architectural component")

class QualityGateCheckItem(BaseModel):
    criterion: str
    status: str = Field(..., description="'Passed', 'Failed', or 'Warning'")
    details: str

class QualityGateCheckResult(BaseModel):
    bug_id: str
    is_eligible: bool
    quality_score: float = Field(..., ge=0.0, le=1.0)
    criteria: List[QualityGateCheckItem]
    blocking_reasons: List[str] = Field(default_factory=list)

class PromotionResponse(BaseModel):
    success: bool
    message: str
    bug_id: str
    assigned_kb_id: str
    historical_defect_id: str
    indexed_chunks_count: int
    dataset_source: str = "Platform"
    promoted_at: datetime = Field(default_factory=datetime.utcnow)

class GrowthCandidateItem(BaseModel):
    bug_id: str
    title: str
    component: str
    status: str
    severity: Optional[str] = None
    has_diagnosis: bool
    is_eligible_for_kb: bool
    indexed_in_kb: bool
    resolution_notes: Optional[str] = None
    created_at: datetime

class KnowledgeBaseGrowthStats(BaseModel):
    total_knowledge_base_records: int
    platform_contributed_records: int
    mozilla_records: int
    apache_records: int
    eclipse_records: int
    total_vector_chunks: int
    growth_percentage: float
    recent_platform_promotions: List[Dict[str, Any]] = Field(default_factory=list)
