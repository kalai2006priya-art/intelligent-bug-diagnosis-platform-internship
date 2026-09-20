import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    error_logs = Column(Text, nullable=True)
    component = Column(String(100), nullable=True)
    environment = Column(String(255), nullable=True)
    status = Column(String(30), default="Submitted", nullable=False)  # Submitted, Analyzing, Diagnosed, Failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bugs")
    diagnosis = relationship("AgentDiagnosis", back_populates="bug", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BugReport {self.id}: {self.title[:30]}>"
