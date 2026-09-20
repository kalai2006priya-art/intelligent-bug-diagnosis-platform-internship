from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class BugCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, description="Brief summary of the defect")
    description: str = Field(..., min_length=10, description="Detailed explanation of the issue and steps to reproduce")
    stack_trace: Optional[str] = Field(None, description="Optional raw stack trace")
    error_logs: Optional[str] = Field(None, description="Optional runtime error logs")
    component: Optional[str] = Field(None, max_length=100, description="Optional component name")
    environment: Optional[str] = Field(None, max_length=255, description="Optional execution environment")

class BugResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    stack_trace: Optional[str] = None
    error_logs: Optional[str] = None
    component: Optional[str] = None
    environment: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    has_diagnosis: bool = False

    class Config:
        from_attributes = True

class BugUploadResponse(BaseModel):
    title: str
    description: str
    stack_trace: Optional[str] = None
    error_logs: Optional[str] = None
    filename: str
    file_size_bytes: int
    detected_format: str
