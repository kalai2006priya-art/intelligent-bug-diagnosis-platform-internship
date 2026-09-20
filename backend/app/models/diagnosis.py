import uuid
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.session import Base

class AgentDiagnosis(Base):
    __tablename__ = "agent_diagnoses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bug_id = Column(String(36), ForeignKey("bug_reports.id", ondelete="CASCADE"), unique=True, nullable=False)
    status = Column(String(30), default="Completed", nullable=False)  # Completed, Partial, Failed
    overall_confidence = Column(Float, default=0.0, nullable=False)

    # Structured JSON text representations for each of the 5 agents
    triage_json = Column(Text, nullable=False)
    log_analysis_json = Column(Text, nullable=False)
    root_cause_json = Column(Text, nullable=False)
    duplicate_detection_json = Column(Text, nullable=False)
    remediation_json = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bug = relationship("BugReport", back_populates="diagnosis")

    @property
    def triage_data(self):
        return json.loads(self.triage_json) if self.triage_json else {}

    @property
    def log_analysis_data(self):
        return json.loads(self.log_analysis_json) if self.log_analysis_json else {}

    @property
    def root_cause_data(self):
        return json.loads(self.root_cause_json) if self.root_cause_json else {}

    @property
    def duplicate_detection_data(self):
        return json.loads(self.duplicate_detection_json) if self.duplicate_detection_json else {}

    @property
    def remediation_data(self):
        return json.loads(self.remediation_json) if self.remediation_json else {}

    def __repr__(self):
        return f"<AgentDiagnosis for Bug {self.bug_id}>"
