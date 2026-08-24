"""
Input validation utilities.
"""

import re
from datetime import datetime


def generate_case_number() -> str:
    """Generate a case number in format CASE-YYYY-NNN."""
    year = datetime.now().year
    # The actual sequential number will be determined by the caller
    return f"CASE-{year}"


def generate_evidence_id(sequence: int) -> str:
    """Generate an evidence ID in format EV-NNN."""
    return f"EV-{sequence:03d}"


def validate_case_number(case_number: str) -> bool:
    """Validate case number format: CASE-YYYY-NNN."""
    pattern = r"^CASE-\d{4}-\d{3,}$"
    return bool(re.match(pattern, case_number))


def validate_evidence_id(evidence_id: str) -> bool:
    """Validate evidence ID format: EV-NNN."""
    pattern = r"^EV-\d{3,}$"
    return bool(re.match(pattern, evidence_id))


def sanitize_string(value: str) -> str:
    """Basic sanitization — strip whitespace and limit length."""
    if value is None:
        return ""
    return value.strip()[:500]


VALID_DEVICE_TYPES = [
    "Laptop", "Desktop", "Server", "Mobile Phone", "Tablet",
    "External HDD", "External SSD", "USB Drive", "SD Card",
    "NAS", "RAID Array", "Other"
]

VALID_FILESYSTEMS = [
    "NTFS", "FAT32", "exFAT", "EXT4", "EXT3", "EXT2",
    "APFS", "HFS+", "XFS", "Btrfs", "ZFS", "Other", "Unknown"
]

VALID_CASE_TYPES = [
    "Cyber Investigation", "Fraud Investigation", "Criminal Investigation",
    "Corporate Investigation", "Incident Response", "Data Breach",
    "Intellectual Property", "Employee Misconduct", "Other"
]

VALID_EVIDENCE_STATUSES = [
    "REGISTERED", "ACQUIRED", "ANALYZING", "RECOVERED", "CLOSED"
]

VALID_CASE_STATUSES = [
    "ACTIVE", "PENDING", "CLOSED", "ARCHIVED"
]

VALID_RECOVERY_STATUSES = [
    "FULLY_RECOVERED", "PARTIALLY_RECOVERED", "NOT_RECOVERABLE", "CORRUPTED", "UNKNOWN"
]

VALID_CUSTODY_ACTIONS = [
    "COLLECTED", "TRANSFERRED", "RECEIVED", "ACQUISITION_STARTED",
    "ACQUISITION_COMPLETED", "ANALYSIS_STARTED", "RECOVERY_STARTED",
    "RECOVERY_COMPLETED", "REVIEWED", "REPORT_GENERATED", "RETURNED"
]
