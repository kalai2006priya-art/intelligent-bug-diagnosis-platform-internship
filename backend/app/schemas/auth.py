from datetime import datetime
from pydantic import BaseModel, Field

from typing import Optional

class UserCreate(BaseModel):
    name: Optional[str] = "Developer"
    email: str = Field(..., min_length=1, max_length=150, description="Valid email address or username")
    password: str = Field(..., min_length=1, max_length=128)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class TokenData(BaseModel):
    user_id: str | None = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

Token.model_rebuild()
