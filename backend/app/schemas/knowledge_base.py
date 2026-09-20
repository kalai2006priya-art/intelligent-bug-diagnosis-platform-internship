from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class HistoricalDefectResponse(BaseModel):
    id: str
    dataset_source: str
    project: str
    bug_id: str
    title: str
    description: str
    stack_trace: Optional[str] = None
    error_message: Optional[str] = None
    component: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    resolution: Optional[str] = None
    status: Optional[str] = None
    comments: Optional[str] = None
    source_reference: Optional[str] = None
    similarity: Optional[float] = None

    class Config:
        from_attributes = True

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search terms or bug symptoms")
    top_k: int = Field(5, ge=1, le=20)
    source: Optional[str] = Field(None, description="Optional filter: Mozilla, Apache, Eclipse")

class SemanticSearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[HistoricalDefectResponse]
