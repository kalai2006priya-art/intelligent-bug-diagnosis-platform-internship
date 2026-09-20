from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.utils.security import verify_password, get_password_hash, create_access_token

class AuthService:
    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        # Check duplicate email
        existing = db.query(User).filter(User.email == user_in.email.lower()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )
        
        db_user = User(
            name=user_in.name.strip(),
            email=user_in.email.lower().strip(),
            password_hash=get_password_hash(user_in.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_token_for_user(user: User) -> Token:
        token_str = create_access_token(data={"sub": user.id, "email": user.email})
        return Token(
            access_token=token_str,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
