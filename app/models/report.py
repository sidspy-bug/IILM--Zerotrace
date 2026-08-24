"""
Report model — generated forensic report tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    report_type = Column(String(50), nullable=False, default="FORENSIC_INVESTIGATION")
    file_path = Column(String(500), nullable=True)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime, server_default=func.now())
    status = Column(String(30), nullable=False, default="GENERATED")

    def to_dict(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "report_type": self.report_type,
            "file_path": self.file_path,
            "generated_by": self.generated_by,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "status": self.status,
        }
