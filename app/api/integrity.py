"""
Integrity API — hash computation and evidence integrity verification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.database.database import get_db
from app.models.evidence import Evidence
from app.models.audit import HashRecord
from app.models.user import User
from app.services.hashing import compute_sha256, compute_sha256_string, verify_integrity
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/api/integrity", tags=["Integrity"])


class HashRequest(BaseModel):
    evidence_id: int
    file_path: Optional[str] = None
    purpose: Optional[str] = "Evidence verification"


@router.post("/hash")
async def calculate_hash(
    data: HashRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "INVESTIGATOR", "FORENSIC_EXAMINER")),
):
    """Calculate SHA-256 hash for an evidence item."""
    # Get the evidence
    result = await db.execute(select(Evidence).where(Evidence.id == data.evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Compute hash
    if data.file_path:
        try:
            hash_value = compute_sha256(data.file_path)
        except FileNotFoundError:
            # Use evidence metadata for hash if file not found
            hash_value = compute_sha256_string(
                f"{evidence.evidence_id}|{evidence.device_type}|{evidence.serial_number}|{evidence.created_at}"
            )
    else:
        # Hash the evidence metadata
        hash_value = compute_sha256_string(
            f"{evidence.evidence_id}|{evidence.device_type}|{evidence.serial_number}|{evidence.created_at}"
        )

    # Store hash record
    record = HashRecord(
        evidence_id=data.evidence_id,
        algorithm="SHA-256",
        hash_value=hash_value,
        purpose=data.purpose,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record.to_dict()


@router.post("/verify/{evidence_id}")
async def verify_evidence_integrity(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify evidence integrity by comparing current hash against stored hash."""
    # Get evidence
    result = await db.execute(select(Evidence).where(Evidence.id == evidence_id))
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Get the latest hash record
    result = await db.execute(
        select(HashRecord)
        .where(HashRecord.evidence_id == evidence_id)
        .order_by(HashRecord.id.desc())
        .limit(1)
    )
    hash_record = result.scalar_one_or_none()

    if not hash_record:
        return {
            "status": "NO_HASH",
            "message": "No hash records found for this evidence. Calculate a hash first.",
            "match": None,
        }

    # Recompute and compare
    current_hash = compute_sha256_string(
        f"{evidence.evidence_id}|{evidence.device_type}|{evidence.serial_number}|{evidence.created_at}"
    )

    match = current_hash == hash_record.hash_value

    return {
        "status": "VERIFIED" if match else "INTEGRITY_MISMATCH",
        "message": "✓ Evidence integrity verified" if match else "⚠ INTEGRITY ALERT — hash mismatch detected",
        "stored_hash": hash_record.hash_value,
        "current_hash": current_hash,
        "algorithm": hash_record.algorithm,
        "match": match,
        "evidence_id": evidence.evidence_id,
    }


@router.get("/records/{evidence_id}")
async def get_hash_records(
    evidence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all hash records for an evidence item."""
    result = await db.execute(
        select(HashRecord)
        .where(HashRecord.evidence_id == evidence_id)
        .order_by(HashRecord.calculated_at.desc())
    )
    records = result.scalars().all()
    return [r.to_dict() for r in records]
