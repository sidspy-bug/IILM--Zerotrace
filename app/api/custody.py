"""
Chain of Custody API — record and verify custody events.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models.user import User
from app.services.custody import record_custody_event, get_custody_timeline, verify_custody_chain
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/custody", tags=["Chain of Custody"])


class CustodyEventCreate(BaseModel):
    evidence_id: int
    action: str
    from_user: Optional[str] = None
    to_user: Optional[str] = None
    remarks: Optional[str] = None


@router.post("/events")
async def create_custody_event(
    data: CustodyEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER")),
):
    """Record a new custody event."""
    event = await record_custody_event(
        db=db,
        evidence_id=data.evidence_id,
        action=data.action,
        from_user=data.from_user or current_user.name,
        to_user=data.to_user,
        remarks=data.remarks,
    )
    return event.to_dict()


@router.get("/events/{evidence_id}")
async def get_custody_events(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the full custody timeline for an evidence item."""
    timeline = await get_custody_timeline(db, evidence_id)
    return timeline


@router.get("/verify/{evidence_id}")
async def verify_chain(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify the integrity of the custody chain."""
    result = await verify_custody_chain(db, evidence_id)
    return result
