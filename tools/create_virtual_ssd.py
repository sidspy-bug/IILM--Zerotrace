"""
ForensicRecover — Virtual SSD Creator
======================================
Creates a virtual disk image (.img) populated with realistic
"evidence" files that are written then deleted — simulating a
seized storage device for forensic recovery testing.

The recovery engine can then scan this image to find deleted data.

Usage:
    python tools/create_virtual_ssd.py
"""

import os
import struct
import hashlib
from datetime import datetime

# ──────────────────────────────────────────────
# Output paths
# ──────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR  = os.path.join(BASE_DIR, "forensic", "images")
RECOV_DIR  = os.path.join(BASE_DIR, "forensic", "recovered")
TEST_DIR   = os.path.join(BASE_DIR, "forensic", "test-data")
IMAGE_PATH = os.path.join(IMAGE_DIR, "virtual_ssd.img")
MANIFEST   = os.path.join(IMAGE_DIR, "virtual_ssd_manifest.txt")

# ──────────────────────────────────────────────
# Virtual SSD size  (50 MB is enough for a demo)
# ──────────────────────────────────────────────
SSD_SIZE_MB = 50
SSD_SIZE    = SSD_SIZE_MB * 1024 * 1024


# ──────────────────────────────────────────────
# Realistic "evidence" file content generators
# ──────────────────────────────────────────────

def make_txt(lines):
    return "\n".join(lines).encode("utf-8")

def make_csv(headers, rows):
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(c) for c in row))
    return "\n".join(lines).encode("utf-8")

def make_html(title, body):
    return f"""<!DOCTYPE html>
<html><head><title>{title}</title></head>
<body>{body}</body></html>""".encode("utf-8")

def make_eml(frm, to, subject, body):
    return f"""From: {frm}
To: {to}
Subject: {subject}
Date: Sun, 24 Aug 2026 10:00:00 +0530
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

{body}
""".encode("utf-8")

def make_log(entries):
    lines = []
    for ts, level, msg in entries:
        lines.append(f"[{ts}] [{level}] {msg}")
    return "\n".join(lines).encode("utf-8")

def make_fake_jpg(label="EVIDENCE_IMAGE"):
    """Minimal JPEG with real SOI/EOI markers."""
    soi  = b'\xff\xd8\xff\xe0'
    app0 = b'\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    comment = label.encode("utf-8")
    com_seg = b'\xff\xfe' + struct.pack('>H', len(comment) + 2) + comment
    fake_data = bytes([(i * 37 + 99) % 256 for i in range(2048)])
    eoi  = b'\xff\xd9'
    return soi + app0 + com_seg + fake_data + eoi

def make_fake_pdf(title="FORENSIC DOCUMENT"):
    """Minimal valid PDF structure."""
    body = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td ({title}) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000206 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
300
%%EOF"""
    return body.encode("latin-1")

def make_fake_zip(label="backup"):
    """Minimal ZIP with PK magic bytes."""
    filename = f"{label}.txt".encode("utf-8")
    content  = f"This is a fake zip archive: {label}\nForensic test data.\n".encode("utf-8")
    lf_header = (
        b'\x50\x4b\x03\x04'
        + struct.pack('<H', 20)
        + struct.pack('<H', 0)
        + struct.pack('<H', 0)
        + struct.pack('<H', 0)
        + struct.pack('<H', 0)
        + struct.pack('<I', 0)
        + struct.pack('<I', len(content))
        + struct.pack('<I', len(content))
        + struct.pack('<H', len(filename))
        + struct.pack('<H', 0)
        + filename
        + content
    )
    return lf_header


# ──────────────────────────────────────────────
# All evidence files to embed in the virtual SSD
# ──────────────────────────────────────────────
EVIDENCE_FILES = {

    "conversation.txt": make_txt([
        "=== PRIVATE CHAT LOG — 2026-08-20 ===",
        "[10:02] User_A: Did you transfer the funds?",
        "[10:03] User_B: Yes, done. 50 lakh to offshore account.",
        "[10:05] User_A: Delete this chat after.",
        "[10:06] User_B: Already done on my end.",
        "[10:08] User_A: The police wont find anything.",
        "[10:10] User_B: Good. Meeting at the usual place at 9 PM.",
        "=== END OF LOG ===",
    ]),

    "deleted_email.eml": make_eml(
        frm="accused@example.com",
        to="accomplice@darkweb.net",
        subject="RE: Operation Cleanup - DO NOT FORWARD",
        body=(
            "As discussed, all digital evidence has been deleted.\n"
            "The financial trail through the shell companies is covered.\n"
            "Destroy this email after reading.\n\n"
            "Transfer reference: TXN-2026-X9921-OFFSHORE\n"
            "Amount: INR 50,00,000\n"
            "Destination: Account XYZ-99821-CAYMAN\n"
        ),
    ),

    "financial_records.csv": make_csv(
        headers=["Date", "TransactionID", "From", "To", "Amount_INR", "Note"],
        rows=[
            ["2026-08-01", "TXN-001", "MainAccount", "ShellCorp_A", "1000000", "Consulting"],
            ["2026-08-05", "TXN-002", "ShellCorp_A", "OffshoreAcc", "1000000", "Investment"],
            ["2026-08-10", "TXN-003", "MainAccount", "ShellCorp_B", "1500000", "Services"],
            ["2026-08-15", "TXN-004", "ShellCorp_B", "CryptoWallet_X", "1500000", "Transfer"],
            ["2026-08-18", "TXN-005", "MainAccount", "ShellCorp_C", "2500000", "Royalties"],
            ["2026-08-20", "TXN-006", "ShellCorp_C", "OffshoreAcc", "2500000", "Final"],
        ],
    ),

    "bank_statements_aug.csv": make_csv(
        headers=["Date", "Description", "Debit", "Credit", "Balance"],
        rows=[
            ["2026-08-01", "Opening Balance", "", "", "12000000"],
            ["2026-08-01", "NEFT to ShellCorp_A", "1000000", "", "11000000"],
            ["2026-08-05", "RTGS to ShellCorp_B", "1500000", "", "9500000"],
            ["2026-08-10", "Wire Transfer Offshore", "2500000", "", "7000000"],
            ["2026-08-15", "Cash Withdrawal", "500000", "", "6500000"],
            ["2026-08-20", "Final Transfer", "5000000", "", "1500000"],
        ],
    ),

    "evidence_notes.txt": make_txt([
        "CONFIDENTIAL INVESTIGATION NOTES",
        "Subject: Financial Fraud and Money Laundering",
        "Date: 2026-08-20",
        "",
        "Key Findings:",
        "1. Subject transferred INR 50 lakhs through 3 shell companies",
        "2. Offshore account in Cayman Islands identified",
        "3. Crypto wallet used to launder proceeds",
        "4. Multiple devices used — laptop + 2 mobile phones",
        "5. Accomplice identified via email evidence",
        "",
        "Status: UNDER ACTIVE INVESTIGATION",
    ]),

    "meeting_notes.txt": make_txt([
        "Meeting Notes — 2026-08-19 — PRIVATE",
        "Attendees: Accused, Accomplice, Unknown Third Party",
        "Location: Hotel Grand, Room 502",
        "",
        "Discussion Points:",
        "- Evidence destruction timeline agreed",
        "- Code words established for further communication",
        "- Next handover: 2026-09-01",
        "- Amount outstanding: INR 30 lakhs",
        "",
        "NOTE: Destroy this document after reading.",
    ]),

    "system_activity.log": make_log([
        ("2026-08-20 08:00:01", "INFO",  "User login: accused_user"),
        ("2026-08-20 08:15:33", "INFO",  "File access: financial_records.csv"),
        ("2026-08-20 08:22:11", "INFO",  "File access: conversation.txt"),
        ("2026-08-20 08:45:00", "WARN",  "USB device inserted: SanDisk 64GB"),
        ("2026-08-20 08:46:12", "INFO",  "File copy: financial_records.csv -> USB"),
        ("2026-08-20 08:46:44", "INFO",  "File copy: deleted_email.eml -> USB"),
        ("2026-08-20 09:00:00", "WARN",  "Bulk file deletion initiated"),
        ("2026-08-20 09:00:03", "INFO",  "Recycle Bin emptied"),
        ("2026-08-20 09:00:05", "INFO",  "Secure delete attempted on: financial_records.csv"),
        ("2026-08-20 09:00:07", "INFO",  "Secure delete attempted on: conversation.txt"),
        ("2026-08-20 09:01:00", "INFO",  "USB device removed"),
        ("2026-08-20 09:02:11", "INFO",  "Browser history cleared"),
        ("2026-08-20 09:05:00", "INFO",  "User logout: accused_user"),
    ]),

    "browser_history.txt": make_txt([
        "BROWSER HISTORY — Chrome — Recovered",
        "",
        "2026-08-20 08:30:01 | https://offshore-banking.cayman.ky/login",
        "2026-08-20 08:31:44 | https://offshore-banking.cayman.ky/transfer",
        "2026-08-20 08:35:00 | https://cryptowallet-exchange.io/send",
        "2026-08-20 08:38:12 | https://cryptowallet-exchange.io/history",
        "2026-08-20 08:40:55 | google.com/search?q=how+to+delete+files+permanently",
        "2026-08-20 08:41:33 | google.com/search?q=forensic+evidence+destruction",
        "2026-08-20 08:42:10 | eraser-software.com/download",
        "2026-08-20 08:50:00 | protonmail.com (encrypted email session)",
    ]),

    "photo_evidence_001.jpg": make_fake_jpg("CRIME_SCENE_PHOTO_001"),
    "photo_evidence_002.jpg": make_fake_jpg("MEETING_SURVEILLANCE_002"),
    "document_scan.pdf":      make_fake_pdf("CONFIDENTIAL AGREEMENT EXHIBIT A"),
    "backup_files.zip":       make_fake_zip("backup_files"),

    "cached_webpage.html": make_html(
        "Offshore Bank - Transfer Confirmation",
        "<h1>Transfer Confirmation</h1>"
        "<p>Amount: USD 60,000</p>"
        "<p>To: Account XYZ-99821-CAYMAN</p>"
        "<p>Reference: TXN-2026-X9921-OFFSHORE</p>"
        "<p>Status: COMPLETED</p>"
        "<p><small>This page was cached by browser.</small></p>",
    ),
}


# ──────────────────────────────────────────────
# Build the virtual SSD image
# ──────────────────────────────────────────────

def sha256_of(data):
    return hashlib.sha256(data).hexdigest()


def create_virtual_ssd():
    os.makedirs(IMAGE_DIR, exist_ok=True)
    os.makedirs(RECOV_DIR, exist_ok=True)
    os.makedirs(TEST_DIR,  exist_ok=True)

    print("=" * 60)
    print("  ForensicRecover -- Virtual SSD Creator")
    print(f"  Image size : {SSD_SIZE_MB} MB")
    print(f"  Image path : {IMAGE_PATH}")
    print("=" * 60)

    # ── Step 1: Allocate blank image ──────────────
    print("\n[1/4] Allocating blank disk image ...", end=" ", flush=True)
    with open(IMAGE_PATH, "wb") as f:
        chunk = b'\x00' * (1024 * 1024)
        for _ in range(SSD_SIZE_MB):
            f.write(chunk)
    print("Done.")

    # ── Step 2: Write evidence files into image ───
    print(f"\n[2/4] Writing {len(EVIDENCE_FILES)} evidence files into image ...")

    manifest_lines = [
        "ForensicRecover Virtual SSD -- Evidence Manifest",
        f"Created   : {datetime.now().isoformat()}",
        f"Image     : {IMAGE_PATH}",
        f"Image Size: {SSD_SIZE_MB} MB",
        "",
        f"{'#':<4} {'Filename':<42} {'Size':>12}  {'SHA-256 (first 16)'}",
        "-" * 82,
    ]

    offset = 512        # Skip first 512 bytes (fake boot sector)
    written_files = []

    with open(IMAGE_PATH, "r+b") as f:
        # Fake MBR marker
        f.seek(0)
        f.write(b'FORENSIC_SSD_VER1' + b'\x00' * (512 - 17))

        for idx, (filename, content) in enumerate(EVIDENCE_FILES.items(), 1):
            file_hash = sha256_of(content)
            header = f"[FRFILE:{filename}:{len(content)}:{file_hash}]".encode("utf-8")
            footer = f"[ENDFILE:{filename}]".encode("utf-8")
            block  = header + content + footer

            if offset + len(block) > SSD_SIZE:
                print(f"  Warning: Skipping {filename} -- image full.")
                break

            f.seek(offset)
            f.write(block)

            print(f"  Written  [{idx:02d}] {filename:<42} {len(content):>10} bytes  @ offset {offset}")
            manifest_lines.append(
                f"{idx:<4} {filename:<42} {len(content):>12}  {file_hash[:16]}"
            )
            written_files.append({
                "name": filename, "size": len(content),
                "hash": file_hash, "offset": offset,
            })
            offset += len(block) + 64

    # ── Step 3: Simulate deletion ────────────────
    print(f"\n[3/4] Simulating file deletion (overwriting directory entries) ...")

    deleted = []
    with open(IMAGE_PATH, "r+b") as f:
        for info in written_files:
            filename = info["name"]
            header_marker = f"[FRFILE:{filename}:".encode("utf-8")
            f.seek(info["offset"])
            found = f.read(len(header_marker))
            if found == header_marker:
                # Overwrite directory entry with DELETED tag
                f.seek(info["offset"])
                deleted_marker = f"[DELETED:{filename}:".encode("utf-8")
                f.write(deleted_marker[:len(header_marker)])
                deleted.append(filename)
                print(f"  Deleted  [{filename}]  (data still physically present in unallocated space)")

    manifest_lines += [
        "",
        f"Files Deleted (data still on disk): {len(deleted)}",
    ]
    for d in deleted:
        manifest_lines.append(f"  - {d}")
    manifest_lines += [
        "",
        "NOTE: Deletion only removes the directory entry.",
        "      Actual file data remains in unallocated space.",
        "      ForensicRecover engine will find and recover it.",
    ]

    # ── Step 4: Copy real files to test-data/ ────
    print(f"\n[4/4] Copying recoverable files to forensic/test-data/ ...")
    for filename, content in EVIDENCE_FILES.items():
        dest = os.path.join(TEST_DIR, filename)
        with open(dest, "wb") as f:
            f.write(content)
        print(f"  Copied: {filename}")

    # Write manifest
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write("\n".join(manifest_lines))

    img_size_actual = os.path.getsize(IMAGE_PATH)

    print("\n" + "=" * 60)
    print("  Virtual SSD Created Successfully!")
    print(f"  Image file : {IMAGE_PATH}")
    print(f"  Actual size: {img_size_actual / (1024*1024):.1f} MB")
    print(f"  Files embedded : {len(written_files)}")
    print(f"  Files deleted  : {len(deleted)}")
    print(f"  Manifest   : {MANIFEST}")
    print("=" * 60)
    print()
    print("  NEXT STEPS IN ForensicRecover:")
    print("  1. Go to http://127.0.0.1:8000")
    print("  2. Create a new investigation case")
    print("  3. Register evidence with device type: Virtual SSD")
    print("  4. Run a Recovery Job")
    print("  5. All 13 deleted evidence files will be found!")
    print()
    print(f"  Image path: {IMAGE_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    create_virtual_ssd()
