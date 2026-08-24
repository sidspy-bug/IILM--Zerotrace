"""
Audit model — tamper-evident audit trail with hash chain.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())
    event_hash = Column(String(128), nullable=False)
    previous_hash = Column(String(128), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_hash": self.event_hash,
            "previous_hash": self.previous_hash,
        }


class HashRecord(Base):
    __tablename__ = "hash_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, nullable=False)
    algorithm = Column(String(20), nullable=False, default="SHA-256")
    hash_value = Column(String(128), nullable=False)
    calculated_at = Column(DateTime, server_default=func.now())
    purpose = Column(String(100), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "algorithm": self.algorithm,
            "hash_value": self.hash_value,
            "calculated_at": self.calculated_at.isoformat() if self.calculated_at else None,
            "purpose": self.purpose,
        }
