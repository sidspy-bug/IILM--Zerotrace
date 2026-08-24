"""
Device analysis service — storage type detection and recovery potential assessment.
"""


# Recovery potential matrix based on storage technology + filesystem
RECOVERY_MATRIX = {
    ("HDD", "NTFS"): "HIGH",
    ("HDD", "FAT32"): "HIGH",
    ("HDD", "exFAT"): "HIGH",
    ("HDD", "EXT4"): "HIGH",
    ("HDD", "EXT3"): "HIGH",
    ("HDD", "EXT2"): "HIGH",
    ("HDD", "APFS"): "MEDIUM",
    ("HDD", "HFS+"): "MEDIUM",
    ("HDD", "XFS"): "MEDIUM",
    ("HDD", "Btrfs"): "MEDIUM",
    ("SSD", "NTFS"): "MEDIUM",
    ("SSD", "FAT32"): "MEDIUM",
    ("SSD", "exFAT"): "LOW",
    ("SSD", "EXT4"): "LOW",
    ("SSD", "APFS"): "LOW",
    ("NVMe", "NTFS"): "LOW",
    ("NVMe", "EXT4"): "LOW",
    ("NVMe", "APFS"): "LOW",
    ("USB Drive", "FAT32"): "HIGH",
    ("USB Drive", "NTFS"): "HIGH",
    ("USB Drive", "exFAT"): "HIGH",
    ("SD Card", "FAT32"): "HIGH",
    ("SD Card", "exFAT"): "MEDIUM",
    ("External HDD", "NTFS"): "HIGH",
    ("External HDD", "FAT32"): "HIGH",
    ("External HDD", "exFAT"): "HIGH",
    ("External SSD", "NTFS"): "MEDIUM",
    ("External SSD", "exFAT"): "LOW",
}


def classify_storage_type(device_type: str) -> str:
    """Classify the underlying storage technology from device type."""
    hdd_types = ["Laptop", "Desktop", "Server", "External HDD", "NAS"]
    ssd_types = ["External SSD"]
    flash_types = ["USB Drive", "SD Card", "Mobile Phone", "Tablet"]

    if device_type in hdd_types:
        return "HDD"
    elif device_type in ssd_types:
        return "SSD"
    elif device_type in flash_types:
        return "Flash"
    return "Unknown"


def assess_recovery_potential(device_type: str, filesystem: str) -> dict:
    """
    Assess the recovery potential for a given device + filesystem combination.
    Returns a detailed assessment.
    """
    storage_type = classify_storage_type(device_type)

    # Look up in matrix
    potential = RECOVERY_MATRIX.get((device_type, filesystem))
    if not potential:
        potential = RECOVERY_MATRIX.get((storage_type, filesystem))
    if not potential:
        potential = "UNCERTAIN"

    # Build factors affecting recovery
    factors = []
    warnings = []

    if storage_type == "SSD" or device_type in ["External SSD", "NVMe", "Mobile Phone", "Tablet"]:
        factors.append("SSD/Flash storage detected — TRIM and garbage collection may reduce recoverability")
        warnings.append("SSD devices may have already zeroed deleted data sectors")

    if filesystem in ["APFS", "Btrfs", "ZFS"]:
        factors.append(f"{filesystem} is a copy-on-write filesystem — recovery behavior may differ")

    if filesystem == "Unknown":
        factors.append("Unknown filesystem — recovery potential cannot be accurately assessed")
        potential = "UNCERTAIN"

    if storage_type == "HDD":
        factors.append("Traditional magnetic storage — deleted data may remain until overwritten")

    return {
        "device_type": device_type,
        "filesystem": filesystem,
        "storage_type": storage_type,
        "recovery_potential": potential,
        "factors": factors,
        "warnings": warnings,
    }


def get_device_analysis(device_type: str, manufacturer: str, model: str,
                        capacity: str, filesystem: str) -> dict:
    """Full device analysis including recovery assessment."""
    assessment = assess_recovery_potential(device_type, filesystem)

    return {
        "device_info": {
            "type": device_type,
            "manufacturer": manufacturer,
            "model": model,
            "capacity": capacity,
            "filesystem": filesystem,
        },
        "storage_classification": assessment["storage_type"],
        "recovery_potential": assessment["recovery_potential"],
        "analysis_factors": assessment["factors"],
        "warnings": assessment["warnings"],
    }
