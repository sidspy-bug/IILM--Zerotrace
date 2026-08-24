"""
Reports API — generate and download forensic PDF reports.
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.database import get_db
from app.models.case import Case
from app.models.evidence import Evidence
from app.models.recovery import RecoveryJob, RecoveredArtifact
from app.models.custody import CustodyEvent
from app.models.audit import HashRecord
from app.models.report import Report
from app.models.user import User
from app.services.reporting import generate_forensic_report
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.post("/generate/{case_id}")
async def generate_report(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR")),
):
    """Generate a forensic investigation PDF report for a case."""
    # Get case
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Get evidence for this case
    ev_result = await db.execute(select(Evidence).where(Evidence.case_id == case_id))
    evidence_list = [e.to_dict() for e in ev_result.scalars().all()]

    # Get recovery jobs for all evidence in this case
    recovery_jobs = []
    for ev in evidence_list:
        jobs_result = await db.execute(
            select(RecoveryJob).where(RecoveryJob.evidence_id == ev["id"])
        )
        for job in jobs_result.scalars().all():
            arts_result = await db.execute(
                select(RecoveredArtifact).where(RecoveredArtifact.recovery_job_id == job.id)
            )
            artifacts = [a.to_dict() for a in arts_result.scalars().all()]
            recovery_jobs.append({
                "job": job.to_dict(),
                "artifacts": artifacts,
            })

    # Get custody events
    custody_events = []
    for ev in evidence_list:
        cust_result = await db.execute(
            select(CustodyEvent)
            .where(CustodyEvent.evidence_id == ev["id"])
            .order_by(CustodyEvent.id)
        )
        custody_events.extend([c.to_dict() for c in cust_result.scalars().all()])

    # Get integrity records
    integrity_records = []
    for ev in evidence_list:
        hash_result = await db.execute(
            select(HashRecord).where(HashRecord.evidence_id == ev["id"])
        )
        integrity_records.extend([h.to_dict() for h in hash_result.scalars().all()])

    # Generate PDF
    filepath = generate_forensic_report(
        case_data=case.to_dict(),
        evidence_list=evidence_list,
        recovery_jobs=recovery_jobs,
        custody_events=custody_events,
        integrity_records=integrity_records,
        investigator_name=current_user.name,
    )

    # Save report record
    report = Report(
        case_id=case_id,
        file_path=filepath,
        generated_by=current_user.id,
        status="GENERATED",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return {
        "id": report.id,
        "case_id": case_id,
        "file_path": filepath,
        "status": "GENERATED",
        "message": "Report generated successfully",
    }


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download a generated PDF report."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    return FileResponse(
        path=report.file_path,
        filename=os.path.basename(report.file_path),
        media_type="application/pdf",
    )


@router.get("")
async def list_reports(
    case_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all generated reports."""
    query = select(Report)
    if case_id:
        query = query.where(Report.case_id == case_id)
    query = query.order_by(Report.generated_at.desc())

    result = await db.execute(query)
    reports = result.scalars().all()
    return [r.to_dict() for r in reports]
