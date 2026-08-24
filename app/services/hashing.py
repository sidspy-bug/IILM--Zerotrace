"""
Hashing service — SHA-256 computation and integrity verification.
"""

import hashlib
import os


def compute_sha256(file_path: str) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_string(text: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def verify_integrity(file_path: str, stored_hash: str) -> dict:
    """
    Verify file integrity by comparing current hash against stored hash.
    Returns a dict with verification result.
    """
    if not os.path.exists(file_path):
        return {
            "status": "ERROR",
            "message": "File not found",
            "stored_hash": stored_hash,
            "current_hash": None,
            "match": False,
        }

    current_hash = compute_sha256(file_path)
    match = current_hash == stored_hash

    return {
        "status": "VERIFIED" if match else "INTEGRITY_MISMATCH",
        "message": "Evidence integrity verified" if match else "INTEGRITY ALERT — hash mismatch detected",
        "stored_hash": stored_hash,
        "current_hash": current_hash,
        "match": match,
    }


def compute_chain_hash(event_data: str, previous_hash: str = None) -> str:
    """
    Compute a tamper-evident chain hash.
    Each hash includes the previous hash to form an integrity chain.
    """
    combined = event_data
    if previous_hash:
        combined = f"{previous_hash}|{event_data}"
    return compute_sha256_string(combined)
