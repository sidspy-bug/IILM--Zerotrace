"""
Case model — investigation case management.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    case_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    investigator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String(30), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "case_number": self.case_number,
            "case_type": self.case_type,
            "description": self.description,
            "investigator_id": self.investigator_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }
