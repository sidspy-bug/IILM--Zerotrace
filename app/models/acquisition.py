"""
Acquisition model — forensic image acquisition tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database.database import Base


class Acquisition(Base):
    __tablename__ = "acquisitions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    acquisition_type = Column(String(50), nullable=False, default="FULL_DISK")
    source = Column(String(500), nullable=True)
    image_path = Column(String(500), nullable=True)
    hash_value = Column(String(128), nullable=True)
    hash_algorithm = Column(String(20), nullable=True, default="SHA-256")
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="IN_PROGRESS")

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "acquisition_type": self.acquisition_type,
            "source": self.source,
            "image_path": self.image_path,
            "hash_value": self.hash_value,
            "hash_algorithm": self.hash_algorithm,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
        }
