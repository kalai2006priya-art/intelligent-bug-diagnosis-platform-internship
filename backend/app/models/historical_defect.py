import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from app.database.session import Base

class HistoricalDefect(Base):
    __tablename__ = "historical_defects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_source = Column(String(50), nullable=False, index=True)  # Mozilla, Apache, Eclipse
    project = Column(String(100), nullable=False, index=True)
    bug_id = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    error_message = Column(String(255), nullable=True)
    component = Column(String(100), nullable=True, index=True)
    severity = Column(String(50), nullable=True)
    priority = Column(String(50), nullable=True)
    resolution = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    comments = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<HistoricalDefect {self.dataset_source}:{self.bug_id}>"
