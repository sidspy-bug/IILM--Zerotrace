"""
Evidence model — digital evidence registration and tracking.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.database.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String(50), unique=True, nullable=False, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), nullable=True)
    capacity = Column(String(50), nullable=True)
    filesystem = Column(String(30), nullable=True)
    source_path = Column(String(500), nullable=True)
    status = Column(String(30), nullable=False, default="REGISTERED")
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "evidence_id": self.evidence_id,
            "case_id": self.case_id,
            "device_type": self.device_type,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "serial_number": self.serial_number,
            "capacity": self.capacity,
            "filesystem": self.filesystem,
            "source_path": self.source_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
