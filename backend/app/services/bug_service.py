import os
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status
from app.models.bug_report import BugReport
from app.schemas.bug import BugCreate, BugResponse, BugUploadResponse
from app.utils.parsers import parse_uploaded_log_file

ALLOWED_EXTENSIONS = {".txt", ".log"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

class BugService:
    @staticmethod
    def create_bug(db: Session, bug_in: BugCreate, user_id: str) -> BugReport:
        bug = BugReport(
            user_id=user_id,
            title=bug_in.title.strip(),
            description=bug_in.description.strip(),
            stack_trace=bug_in.stack_trace.strip() if bug_in.stack_trace else None,
            error_logs=bug_in.error_logs.strip() if bug_in.error_logs else None,
            component=bug_in.component.strip() if bug_in.component else None,
            environment=bug_in.environment.strip() if bug_in.environment else None,
            status="Submitted"
        )
        db.add(bug)
        db.commit()
        db.refresh(bug)
        return bug

    @staticmethod
    def get_bug_by_id(db: Session, bug_id: str) -> Optional[BugReport]:
        return db.query(BugReport).filter(BugReport.id == bug_id).first()

    @staticmethod
    def list_bugs(db: Session, user_id: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[BugReport]:
        query = db.query(BugReport)
        if user_id:
            query = query.filter(BugReport.user_id == user_id)
        return query.order_by(BugReport.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_bugs(db: Session, user_id: Optional[str] = None) -> int:
        query = db.query(BugReport)
        if user_id:
            query = query.filter(BugReport.user_id == user_id)
        return query.count()

    @staticmethod
    def count_diagnosed_bugs(db: Session, user_id: Optional[str] = None) -> int:
        query = db.query(BugReport).filter(BugReport.status == "Diagnosed")
        if user_id:
            query = query.filter(BugReport.user_id == user_id)
        return query.count()

    @staticmethod
    async def process_file_upload(file: UploadFile) -> BugUploadResponse:
        filename = file.filename or "uploaded_log.txt"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '{ext}'. Only {list(ALLOWED_EXTENSIONS)} files are supported."
            )

        content_bytes = await file.read()
        file_size = len(content_bytes)
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty. Please provide a valid bug or log file."
            )
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
            )

        # Attempt decoding with UTF-8, fall back to latin-1
        try:
            content_str = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content_str = content_bytes.decode("latin-1", errors="replace")

        parsed = parse_uploaded_log_file(content_str, filename)

        return BugUploadResponse(
            title=parsed["title"],
            description=parsed["description"],
            stack_trace=parsed["stack_trace"],
            error_logs=parsed["error_logs"],
            filename=filename,
            file_size_bytes=file_size,
            detected_format=ext[1:].upper()
        )
