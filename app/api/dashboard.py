"""
Dashboard API — aggregated statistics for the investigator dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database.database import get_db
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.recovery import RecoveryJob
from app.models.audit import HashRecord, AuditEvent
from app.models.custody import CustodyEvent
from app.models.report import Report
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated dashboard statistics."""

    # Case stats
    total_cases = (await db.execute(select(func.count(Case.id)))).scalar() or 0
    active_cases = (await db.execute(
        select(func.count(Case.id)).where(Case.status == "ACTIVE")
    )).scalar() or 0
    closed_cases = (await db.execute(
        select(func.count(Case.id)).where(Case.status == "CLOSED")
    )).scalar() or 0

    # Evidence stats
    total_evidence = (await db.execute(select(func.count(Evidence.id)))).scalar() or 0

    # Hash/integrity stats
    total_hashes = (await db.execute(select(func.count(HashRecord.id)))).scalar() or 0

    # Recovery stats
    total_jobs = (await db.execute(select(func.count(RecoveryJob.id)))).scalar() or 0
    completed_jobs = (await db.execute(
        select(func.count(RecoveryJob.id)).where(RecoveryJob.status == "COMPLETED")
    )).scalar() or 0

    total_recovered = (await db.execute(
        select(func.sum(RecoveryJob.files_recovered))
    )).scalar() or 0
    total_partial = (await db.execute(
        select(func.sum(RecoveryJob.files_partial))
    )).scalar() or 0
    total_failed = (await db.execute(
        select(func.sum(RecoveryJob.files_failed))
    )).scalar() or 0
    total_found = (await db.execute(
        select(func.sum(RecoveryJob.files_found))
    )).scalar() or 0

    # Custody stats
    total_custody_events = (await db.execute(
        select(func.count(CustodyEvent.id))
    )).scalar() or 0

    # Report stats
    total_reports = (await db.execute(select(func.count(Report.id)))).scalar() or 0

    # Recent activity (last 10 audit events)
    recent_result = await db.execute(
        select(AuditEvent).order_by(AuditEvent.id.desc()).limit(10)
    )
    recent_events = [e.to_dict() for e in recent_result.scalars().all()]

    return {
        "cases": {
            "total": total_cases,
            "active": active_cases,
            "closed": closed_cases,
        },
        "evidence": {
            "total": total_evidence,
            "hashes_computed": total_hashes,
        },
        "recovery": {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "files_found": total_found,
            "files_recovered": total_recovered,
            "files_partial": total_partial,
            "files_failed": total_failed,
        },
        "custody": {
            "total_events": total_custody_events,
        },
        "reports": {
            "total": total_reports,
        },
        "recent_activity": recent_events,
    }
