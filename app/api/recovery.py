"""
Recovery API — manage recovery jobs and recovered artifacts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models.recovery import RecoveryJob, RecoveredArtifact
from app.models.user import User
from app.services.recovery import create_recovery_job, run_simulated_recovery, get_job_with_artifacts
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/recovery", tags=["Recovery"])


class RecoveryJobCreate(BaseModel):
    evidence_id: int
    scan_path: Optional[str] = None


class ArtifactCreate(BaseModel):
    original_name: str
    recovered_path: Optional[str] = None
    artifact_type: Optional[str] = None
    recovery_status: str = "UNKNOWN"
    hash_value: Optional[str] = None
    size: Optional[int] = None
    metadata_info: Optional[str] = None


@router.post("/jobs")
async def start_recovery_job(
    data: RecoveryJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER")),
):
    """Start a new recovery job for an evidence item."""
    job = await create_recovery_job(db, data.evidence_id)

    # Run simulated recovery
    completed_job = await run_simulated_recovery(db, job.id, data.scan_path)
    if not completed_job:
        raise HTTPException(status_code=500, detail="Recovery job failed")

    result = await get_job_with_artifacts(db, completed_job.id)
    return result


@router.get("/jobs")
async def list_recovery_jobs(
    evidence_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all recovery jobs."""
    query = select(RecoveryJob)
    if evidence_id:
        query = query.where(RecoveryJob.evidence_id == evidence_id)
    query = query.order_by(RecoveryJob.started_at.desc())

    result = await db.execute(query)
    jobs = result.scalars().all()
    return [j.to_dict() for j in jobs]


@router.get("/jobs/{job_id}")
async def get_recovery_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific recovery job with its artifacts."""
    result = await get_job_with_artifacts(db, job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recovery job not found")
    return result


@router.post("/jobs/{job_id}/artifacts")
async def add_artifact(
    job_id: int,
    data: ArtifactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "FORENSIC_EXAMINER")),
):
    """Manually add a recovered artifact to a job."""
    # Verify job exists
    result = await db.execute(select(RecoveryJob).where(RecoveryJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Recovery job not found")

    artifact = RecoveredArtifact(
        recovery_job_id=job_id,
        original_name=data.original_name,
        recovered_path=data.recovered_path,
        artifact_type=data.artifact_type,
        recovery_status=data.recovery_status,
        hash_value=data.hash_value,
        size=data.size,
        metadata_info=data.metadata_info,
    )
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    return artifact.to_dict()
