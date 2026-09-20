from datetime import datetime
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", description="Valid email address")
    password: str = Field(..., min_length=6, max_length=128)

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
