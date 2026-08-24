"""
Recovery models — recovery jobs and recovered artifacts.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database.database import Base


class RecoveryJob(Base):
    __tablename__ = "recovery_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(30), nullable=False, default="IN_PROGRESS")
    files_found = Column(Integer, default=0)
    files_recovered = Column(Integer, default=0)
    files_partial = Column(Integer, default=0)
    files_failed = Column(Integer, default=0)
    recovery_notes = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "files_found": self.files_found,
            "files_recovered": self.files_recovered,
            "files_partial": self.files_partial,
            "files_failed": self.files_failed,
            "recovery_notes": self.recovery_notes,
        }


class RecoveredArtifact(Base):
    __tablename__ = "recovered_artifacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recovery_job_id = Column(Integer, ForeignKey("recovery_jobs.id"), nullable=False)
    original_name = Column(String(255), nullable=True)
    recovered_path = Column(String(500), nullable=True)
    artifact_type = Column(String(50), nullable=True)
    recovery_status = Column(String(30), nullable=False, default="UNKNOWN")
    hash_value = Column(String(128), nullable=True)
    size = Column(Integer, nullable=True)
    metadata_info = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "recovery_job_id": self.recovery_job_id,
            "original_name": self.original_name,
            "recovered_path": self.recovered_path,
            "artifact_type": self.artifact_type,
            "recovery_status": self.recovery_status,
            "hash_value": self.hash_value,
            "size": self.size,
            "metadata_info": self.metadata_info,
        }
