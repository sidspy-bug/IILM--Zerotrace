"""
Evidence Management API — register, track, and manage digital evidence.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models.evidence import Evidence
from app.models.user import User
from app.services.device_analysis import get_device_analysis
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])


class EvidenceCreate(BaseModel):
    case_id: int
    device_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    capacity: Optional[str] = None
    filesystem: Optional[str] = None
    source_path: Optional[str] = None


class EvidenceUpdate(BaseModel):
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    capacity: Optional[str] = None
    filesystem: Optional[str] = None
    source_path: Optional[str] = None
    status: Optional[str] = None


@router.post("")
async def create_evidence(
    data: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER")),
):
    """Register a new piece of evidence."""
    # Generate evidence ID
    result = await db.execute(select(func.count(Evidence.id)))
    count = result.scalar() or 0
    evidence_id = f"EV-{count + 1:03d}"

    evidence = Evidence(
        evidence_id=evidence_id,
        case_id=data.case_id,
        device_type=data.device_type,
        manufacturer=data.manufacturer,
        model=data.model,
        serial_number=data.serial_number,
        capacity=data.capacity,
        filesystem=data.filesystem,
        source_path=data.source_path,
        status="REGISTERED",
    )
    db.add(evidence)
    await db.commit()
    await db.refresh(evidence)
    return evidence.to_dict()


@router.get("")
async def list_evidence(
    case_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List evidence items, optionally filtered by case."""
    query = select(Evidence)
    if case_id:
        query = query.where(Evidence.case_id == case_id)
    query = query.order_by(Evidence.created_at.desc())

    result = await db.execute(query)
    items = result.scalars().all()
    return [e.to_dict() for e in items]


@router.get("/{evidence_db_id}")
async def get_evidence(
    evidence_db_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific evidence item."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_db_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence.to_dict()


@router.put("/{evidence_db_id}")
async def update_evidence(
    evidence_db_id: int,
    data: EvidenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER")),
):
    """Update an evidence item."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_db_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    for field in ["device_type", "manufacturer", "model", "serial_number",
                  "capacity", "filesystem", "source_path", "status"]:
        value = getattr(data, field, None)
        if value is not None:
            setattr(evidence, field, value)

    await db.commit()
    await db.refresh(evidence)
    return evidence.to_dict()


@router.get("/{evidence_db_id}/analysis")
async def analyze_evidence(
    evidence_db_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get device analysis and recovery potential assessment."""
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_db_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    analysis = get_device_analysis(
        device_type=evidence.device_type,
        manufacturer=evidence.manufacturer or "Unknown",
        model=evidence.model or "Unknown",
        capacity=evidence.capacity or "Unknown",
        filesystem=evidence.filesystem or "Unknown",
    )
    return analysis
