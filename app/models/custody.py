"""
Custody model — chain of custody events with tamper-evident hash chain.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database.database import Base


class CustodyEvent(Base):
    __tablename__ = "custody_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    from_user = Column(String(100), nullable=True)
    to_user = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    remarks = Column(Text, nullable=True)
    event_hash = Column(String(128), nullable=False)
    previous_hash = Column(String(128), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "from_user": self.from_user,
            "to_user": self.to_user,
            "action": self.action,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "remarks": self.remarks,
            "event_hash": self.event_hash,
            "previous_hash": self.previous_hash,
        }
