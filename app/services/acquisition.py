"""
Acquisition service — forensic image registration and management.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.acquisition import Acquisition
from app.services.hashing import compute_sha256


async def create_acquisition(
    db: AsyncSession,
    evidence_id: int,
    acquisition_type: str,
    source: str = None,
    image_path: str = None,
) -> Acquisition:
    """Register a new forensic acquisition."""
    acquisition = Acquisition(
        evidence_id=evidence_id,
        acquisition_type=acquisition_type,
        source=source,
        image_path=image_path,
        status="IN_PROGRESS",
    )
    db.add(acquisition)
    await db.commit()
    await db.refresh(acquisition)
    return acquisition


async def complete_acquisition(
    db: AsyncSession,
    acquisition_id: int,
    image_path: str = None,
) -> Acquisition:
    """Mark acquisition as completed and compute hash of the forensic image."""
    result = await db.execute(select(Acquisition).where(Acquisition.id == acquisition_id))
    acquisition = result.scalar_one_or_none()
    if not acquisition:
        return None

    if image_path:
        acquisition.image_path = image_path

    # Compute hash of the forensic image if path exists
    if acquisition.image_path:
        try:
            acquisition.hash_value = compute_sha256(acquisition.image_path)
            acquisition.hash_algorithm = "SHA-256"
        except FileNotFoundError:
            acquisition.hash_value = None

    acquisition.completed_at = datetime.now(timezone.utc)
    acquisition.status = "COMPLETED"
    await db.commit()
    await db.refresh(acquisition)
    return acquisition


async def get_acquisitions_for_evidence(db: AsyncSession, evidence_id: int):
    """Get all acquisitions for an evidence item."""
    result = await db.execute(
        select(Acquisition).where(Acquisition.evidence_id == evidence_id)
    )
    return result.scalars().all()
