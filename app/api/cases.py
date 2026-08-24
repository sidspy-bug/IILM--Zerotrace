"""
Case Management API — CRUD operations for investigation cases.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from app.database.database import get_db
from app.models.case import Case
from app.models.user import User
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/cases", tags=["Cases"])


class CaseCreate(BaseModel):
    case_type: str
    description: Optional[str] = None
    investigator_id: Optional[int] = None


class CaseUpdate(BaseModel):
    case_type: Optional[str] = None
    description: Optional[str] = None
    investigator_id: Optional[int] = None
    status: Optional[str] = None


@router.post("")
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR")),
):
    """Create a new investigation case."""
    # Generate case number
    year = datetime.now().year
    result = await db.execute(select(func.count(Case.id)))
    count = result.scalar() or 0
    case_number = f"CASE-{year}-{count + 1:03d}"

    case = Case(
        case_number=case_number,
        case_type=case_data.case_type,
        description=case_data.description,
        investigator_id=case_data.investigator_id or current_user.id,
        status="ACTIVE",
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return case.to_dict()


@router.get("")
async def list_cases(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all cases, optionally filtered by status."""
    query = select(Case)
    if status:
        query = query.where(Case.status == status)
    query = query.order_by(Case.created_at.desc())

    result = await db.execute(query)
    cases = result.scalars().all()
    return [c.to_dict() for c in cases]


@router.get("/{case_id}")
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific case by ID."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case.to_dict()


@router.put("/{case_id}")
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR")),
):
    """Update a case."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case_data.case_type is not None:
        case.case_type = case_data.case_type
    if case_data.description is not None:
        case.description = case_data.description
    if case_data.investigator_id is not None:
        case.investigator_id = case_data.investigator_id
    if case_data.status is not None:
        case.status = case_data.status

    await db.commit()
    await db.refresh(case)
    return case.to_dict()


@router.patch("/{case_id}/close")
async def close_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR")),
):
    """Close a case."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = "CLOSED"
    case.closed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(case)
    return case.to_dict()
