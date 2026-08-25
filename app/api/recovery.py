"""
Recovery API — manage recovery jobs and recovered artifacts.
"""

import os
import mimetypes

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse as FastAPIFileResponse
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models.recovery import RecoveryJob, RecoveredArtifact
from app.models.user import User
from app.services.recovery import create_recovery_job, run_simulated_recovery, get_job_with_artifacts
from app.utils.security import get_current_user, require_role, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt as jose_jwt

router = APIRouter(prefix="/api/recovery", tags=["Recovery"])

# Base directory for resolving relative recovered_path values
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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


def _resolve_artifact_path(recovered_path: str) -> str:
    """Resolve an artifact's recovered_path to an absolute filesystem path."""
    if not recovered_path:
        return None
    if os.path.isabs(recovered_path):
        return recovered_path
    return os.path.join(BASE_DIR, recovered_path)


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: int,
    request: Request,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Download / view a recovered artifact file.

    Supports auth via:
      - Standard Authorization header (Bearer token)
      - Query parameter `?token=...` (for <img>/<iframe> embeds)
    Validates token and ensures the referenced user exists.
    """
    # Determine token: prefer query param, otherwise check Authorization header
    token_to_use = token
    if not token_to_use:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token_to_use = auth_header.split(" ", 1)[1]

    if not token_to_use:
        raise HTTPException(status_code=401, detail="Token required — pass ?token= query param or Authorization header")

    try:
        payload = jose_jwt.decode(token_to_use, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Verify user exists
    result_user = await db.execute(select(User).where(User.username == username))
    user = result_user.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token user")

    result = await db.execute(
        select(RecoveredArtifact).where(RecoveredArtifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = _resolve_artifact_path(artifact.recovered_path)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")

    media_type, _ = mimetypes.guess_type(file_path)
    return FastAPIFileResponse(
        path=file_path,
        filename=artifact.original_name,
        media_type=media_type or "application/octet-stream",
    )


@router.get("/artifacts/{artifact_id}/preview")
async def preview_artifact(
    artifact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the text content of a recovered artifact for in-browser preview."""
    result = await db.execute(
        select(RecoveredArtifact).where(RecoveredArtifact.id == artifact_id)
    )
    artifact = result.scalar_one_or_none()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    file_path = _resolve_artifact_path(artifact.recovered_path)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Artifact file not found on disk")

    # Determine if this is a previewable text-based file
    TEXT_EXTENSIONS = {".txt", ".csv", ".log", ".eml", ".html", ".json", ".xml", ".md"}
    _, ext = os.path.splitext(artifact.original_name.lower())

    if ext in TEXT_EXTENSIONS:
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(100_000)  # Cap at 100KB for safety
            return {
                "artifact_id": artifact.id,
                "original_name": artifact.original_name,
                "preview_type": "text",
                "content": content,
            }
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to read artifact file")

    # For images, return a pointer to the download URL
    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"}
    if ext in IMAGE_EXTENSIONS:
        return {
            "artifact_id": artifact.id,
            "original_name": artifact.original_name,
            "preview_type": "image",
            "download_url": f"/api/recovery/artifacts/{artifact.id}/download",
        }

    # For PDF
    if ext == ".pdf":
        return {
            "artifact_id": artifact.id,
            "original_name": artifact.original_name,
            "preview_type": "pdf",
            "download_url": f"/api/recovery/artifacts/{artifact.id}/download",
        }

    return {
        "artifact_id": artifact.id,
        "original_name": artifact.original_name,
        "preview_type": "binary",
        "message": "This file type cannot be previewed. Use the download button.",
        "download_url": f"/api/recovery/artifacts/{artifact.id}/download",
    }

