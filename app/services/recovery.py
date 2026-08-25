"""
Recovery service — recovery job management and simulated forensic analysis.
For the MVP, this simulates forensic recovery by scanning test directories.
"""

import os
import random
from datetime import datetime, timezone
import subprocess
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.recovery import RecoveryJob, RecoveredArtifact
from app.services.hashing import compute_sha256, compute_sha256_string


# Simulated artifact types for demo
ARTIFACT_TYPES = {
    ".jpg": "Image",
    ".jpeg": "Image",
    ".png": "Image",
    ".gif": "Image",
    ".bmp": "Image",
    ".pdf": "Document",
    ".doc": "Document",
    ".docx": "Document",
    ".xls": "Spreadsheet",
    ".xlsx": "Spreadsheet",
    ".txt": "Text File",
    ".csv": "Data File",
    ".mp4": "Video",
    ".avi": "Video",
    ".mkv": "Video",
    ".mp3": "Audio",
    ".wav": "Audio",
    ".zip": "Archive",
    ".rar": "Archive",
    ".html": "Web Page",
    ".eml": "Email",
    ".pst": "Email Archive",
    ".db": "Database",
    ".sqlite": "Database",
    ".log": "Log File",
}


def detect_artifact_type(filename: str) -> str:
    """Detect artifact type from file extension."""
    _, ext = os.path.splitext(filename.lower())
    return ARTIFACT_TYPES.get(ext, "Unknown")


async def create_recovery_job(db: AsyncSession, evidence_id: int) -> RecoveryJob:
    """Create a new recovery job."""
    job = RecoveryJob(
        evidence_id=evidence_id,
        status="IN_PROGRESS",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def run_simulated_recovery(
    db: AsyncSession,
    job_id: int,
    scan_path: str = None,
) -> RecoveryJob:
    """
    Run a simulated forensic recovery.
    Scans a test directory and classifies files as recovered artifacts.
    """
    result = await db.execute(select(RecoveryJob).where(RecoveryJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        return None

    # Default scan path for test data
    if not scan_path:
        scan_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "forensic", "test-data")

    artifacts = []
    files_found = 0
    files_recovered = 0
    files_partial = 0
    files_failed = 0

    if os.path.exists(scan_path):
        for root, dirs, files in os.walk(scan_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                files_found += 1

                # Determine recovery status (simulated)
                file_size = os.path.getsize(file_path)
                # Simulate realistic recovery outcomes
                rand = random.random()
                if rand < 0.65:
                    recovery_status = "FULLY_RECOVERED"
                    files_recovered += 1
                elif rand < 0.85:
                    recovery_status = "PARTIALLY_RECOVERED"
                    files_partial += 1
                elif rand < 0.95:
                    recovery_status = "NOT_RECOVERABLE"
                    files_failed += 1
                else:
                    recovery_status = "CORRUPTED"
                    files_failed += 1

                # Compute hash of recovered file
                try:
                    file_hash = compute_sha256(file_path)
                except Exception:
                    file_hash = compute_sha256_string(filename)

                artifact = RecoveredArtifact(
                    recovery_job_id=job_id,
                    original_name=filename,
                    recovered_path=file_path,
                    artifact_type=detect_artifact_type(filename),
                    recovery_status=recovery_status,
                    hash_value=file_hash,
                    size=file_size,
                    metadata_info=f"Source: {root}",
                )
                artifacts.append(artifact)
                db.add(artifact)
    else:
        # If no test data exists, generate synthetic results
        synthetic_files = [
            ("evidence.jpg", "Image", 245760),
            ("secret.pdf", "Document", 1048576),
            ("conversation.txt", "Text File", 8192),
            ("video.mp4", "Video", 52428800),
            ("financial_records.xlsx", "Spreadsheet", 524288),
            ("browser_history.db", "Database", 131072),
            ("deleted_email.eml", "Email", 32768),
            ("backup.zip", "Archive", 10485760),
            ("photo_001.png", "Image", 3145728),
            ("photo_002.jpg", "Image", 2097152),
            ("notes.txt", "Text File", 4096),
            ("report_draft.docx", "Document", 262144),
            ("audio_recording.mp3", "Audio", 5242880),
            ("system.log", "Log File", 65536),
            ("contacts.csv", "Data File", 16384),
        ]

        for name, atype, size in synthetic_files:
            files_found += 1
            rand = random.random()
            if rand < 0.65:
                recovery_status = "FULLY_RECOVERED"
                files_recovered += 1
            elif rand < 0.85:
                recovery_status = "PARTIALLY_RECOVERED"
                files_partial += 1
            elif rand < 0.95:
                recovery_status = "NOT_RECOVERABLE"
                files_failed += 1
            else:
                recovery_status = "CORRUPTED"
                files_failed += 1

            artifact = RecoveredArtifact(
                recovery_job_id=job_id,
                original_name=name,
                recovered_path=f"forensic/recovered/{name}",
                artifact_type=atype,
                recovery_status=recovery_status,
                hash_value=compute_sha256_string(f"{name}-{size}"),
                size=size,
                metadata_info=f"Synthetic test artifact",
            )
            db.add(artifact)

    # Update job
    job.files_found = files_found
    job.files_recovered = files_recovered
    job.files_partial = files_partial
    job.files_failed = files_failed
    job.completed_at = datetime.now(timezone.utc)
    job.status = "COMPLETED"
    job.recovery_notes = f"Recovery completed. Scanned: {scan_path or 'synthetic data'}"

    await db.commit()
    await db.refresh(job)
    return job


async def get_job_with_artifacts(db: AsyncSession, job_id: int) -> dict:
    """Get a recovery job with all its artifacts."""
    result = await db.execute(select(RecoveryJob).where(RecoveryJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        return None

    artifacts_result = await db.execute(
        select(RecoveredArtifact).where(RecoveredArtifact.recovery_job_id == job_id)
    )
    artifacts = artifacts_result.scalars().all()

    return {
        "job": job.to_dict(),
        "artifacts": [a.to_dict() for a in artifacts],
    }
