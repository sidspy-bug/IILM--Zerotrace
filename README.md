# IILMkimaaki......




# 🔎 ForensicRecover

## Digital Evidence Recovery, Verification, Preservation & Investigation Platform

> **Recover → Verify → Preserve → Track → Analyze → Report**

ForensicRecover is a Python-based digital-forensics platform designed for **authorized government investigation, forensic laboratories, and law-enforcement use cases**.

The main purpose of the platform is to help investigators examine seized computers and storage devices and identify **deleted digital information that may still be technically recoverable**, including information that has been deleted from the Recycle Bin.

The platform combines:

* Digital evidence registration
* Forensic acquisition workflow
* Deleted-data analysis
* Recovery-result management
* Evidence integrity verification
* Chain of custody
* Tamper-evident audit logging
* Investigator dashboard
* Automated forensic reporting

The MVP is designed around **free and open-source technologies** wherever practical.

---

# 📌 Table of Contents

* [1. Project Overview](#1-project-overview)
* [2. Project in Layman Language](#2-project-in-layman-language)
* [3. Real-World Problem](#3-real-world-problem)
* [4. Main Objective](#4-main-objective)
* [5. How Deleted Data Can Remain](#5-how-deleted-data-can-remain)
* [6. Why This Platform Is Needed](#6-why-this-platform-is-needed)
* [7. Important Recovery Reality](#7-important-recovery-reality)
* [8. What the System Does](#8-what-the-system-does)
* [9. Complete End-to-End Workflow](#9-complete-end-to-end-workflow)
* [10. Core Modules](#10-core-modules)
* [11. System Architecture](#11-system-architecture)
* [12. Repository Structure](#12-repository-structure)
* [13. Git Branch Structure](#13-git-branch-structure)
* [14. Branch Responsibilities](#14-branch-responsibilities)
* [15. Technology Stack](#15-technology-stack)
* [16. Database Design](#16-database-design)
* [17. Forensic Recovery Architecture](#17-forensic-recovery-architecture)
* [18. Evidence Integrity](#18-evidence-integrity)
* [19. Chain of Custody](#19-chain-of-custody)
* [20. Dashboard](#20-dashboard)
* [21. Report Generation](#21-report-generation)
* [22. Security](#22-security)
* [23. Zero-Cost MVP](#23-zero-cost-mvp)
* [24. MVP Scope](#24-mvp-scope)
* [25. Development Roadmap](#25-development-roadmap)
* [26. Project Demonstration](#26-project-demonstration)
* [27. Unique Selling Propositions](#27-unique-selling-propositions)
* [28. Future Development](#28-future-development)
* [29. Project Limitations](#29-project-limitations)
* [30. Ethical and Legal Considerations](#30-ethical-and-legal-considerations)
* [31. Team Responsibilities](#31-team-responsibilities)
* [32. Development Guidelines](#32-development-guidelines)
* [33. Installation](#33-installation)
* [34. MVP Success Criteria](#34-mvp-success-criteria)
* [35. Viva / Presentation Explanation](#35-viva--presentation-explanation)
* [36. Final Project Definition](#36-final-project-definition)
* [37. Long-Term Vision](#37-long-term-vision)

---

# 1. Project Overview

Digital devices can contain large amounts of potentially useful information:

* Documents
* Images
* Videos
* Emails
* Browser artifacts
* Application data
* Metadata
* Filesystem records
* Deleted files
* Other digital traces

During an investigation, a person may delete important information and then empty the Recycle Bin.

From a normal user's perspective:

```text
File
  ↓
Delete
  ↓
Recycle Bin
  ↓
Empty Recycle Bin
  ↓
File disappears
```

However, depending on the storage technology, filesystem, system activity, and other circumstances, some information or remnants may remain technically recoverable.

ForensicRecover provides a structured workflow for examining such evidence.

## Environment variables & running (development)

Required environment variables:

- `SECRET_KEY` — a strong secret used to sign JWTs. **Must** be set for production.
- `DATABASE_URL` — optional, defaults to `sqlite+aiosqlite:///./forensic.db` (use Postgres in production).
- `ALGORITHM` — optional JWT algorithm (default: `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES` — optional token TTL (default: `480`).
- `DEV_MODE` — optional; set to `1`, `true`, or `yes` to allow a secure runtime-only secret to be generated for local development when `SECRET_KEY` is not set (not for production).

Quick local run (PowerShell):

```powershell
$env:SECRET_KEY = "your-strong-secret-here"
# optional: $env:DEV_MODE = "1"  # only for local dev, not production
python -m uvicorn app.main:app --reload --port 8000
```

Notes:

- The application will refuse to start in non-dev mode if `SECRET_KEY` is not set.
- For production, provide a persistent `SECRET_KEY` and run behind a TLS-terminating proxy (nginx, load balancer).
- Consider using a managed database (Postgres) and a secrets manager for production secrets.

The platform does **not** promise that every deleted file can be recovered.

Its objective is:

> **To maximize the identification and recovery of technically available digital evidence while preserving evidence integrity and maintaining a complete investigation history.**

---

# 2. Project in Layman Language

Imagine a government investigation team receives a laptop as evidence.

The person who used the laptop deleted some important files and emptied the Recycle Bin.

A normal user cannot simply open the Recycle Bin and see those files anymore.

ForensicRecover acts like a **digital investigation assistant**.

It helps the investigator answer:

```text
What device is this?
        ↓
What storage technology is being used?
        ↓
What filesystem is present?
        ↓
Can deleted information still be technically available?
        ↓
What evidence can be recovered?
        ↓
What evidence cannot be recovered?
        ↓
Was the evidence modified?
        ↓
Who handled the evidence?
        ↓
What actions were performed?
        ↓
What was recovered?
        ↓
What should be included in the final report?
```

In very simple Hinglish:

> **"Agar kisi investigation mein laptop ya storage device seize hota hai aur user ne files delete karke Recycle Bin bhi empty kar diya hai, toh hamara system investigator ko check karne mein help karega ki technically kaunsi deleted information abhi available ho sakti hai, usko forensic process ke through analyze/recover karne ke results ko record karega, evidence ki integrity verify karega, poori custody history maintain karega aur final forensic report generate karega."**

---

# 3. Real-World Problem

Suppose an investigation involves a laptop containing:

```text
evidence.jpg
secret.pdf
conversation.txt
video.mp4
```

The user performs:

```text
Delete
  ↓
Recycle Bin
  ↓
Empty Recycle Bin
```

The files are no longer visible through normal operating-system interfaces.

The forensic investigator still needs to determine whether useful evidence remains technically available.

A traditional workflow may involve multiple tools:

```text
Recovery Tool
      +
Hash Tool
      +
Spreadsheet
      +
Manual Evidence Log
      +
Manual Report
```

This can make the overall investigation workflow difficult to organize.

ForensicRecover aims to provide a unified management layer around the forensic process.

---

# 4. Main Objective

The primary objective is:

> **To help an authorized government forensic investigator maximize the amount of technically recoverable digital evidence from a seized device while maintaining evidence integrity, traceability, and a clear forensic record.**

The project follows six major actions:

```text
RECOVER
   ↓
VERIFY
   ↓
PRESERVE
   ↓
TRACK
   ↓
ANALYZE
   ↓
REPORT
```

---

# 5. How Deleted Data Can Remain

A common misunderstanding is:

> "If I empty the Recycle Bin, the data is immediately physically destroyed."

That is not necessarily true in every storage situation.

A simplified concept is:

```text
Original File
     ↓
User Deletes File
     ↓
Recycle Bin
     ↓
Recycle Bin Emptied
     ↓
File No Longer Visible
     ↓
Some Data/Metadata May Remain
     ↓
Forensic Examination
```

Depending on the storage technology and filesystem, forensic examination may find things such as:

* Filesystem metadata
* Deleted file records
* Unallocated storage content
* File fragments
* Application artifacts
* Other related digital traces

The actual recoverability depends heavily on the circumstances.

---

# 6. Why This Platform Is Needed

The project is **not simply another file-recovery application**.

Existing forensic software already provides many powerful recovery and analysis capabilities.

The actual problem ForensicRecover addresses is the **complete investigation workflow**.

A recovery tool might say:

```text
Found 100 files
```

But an investigation department may also need:

```text
Which case?
Which device?
Which evidence ID?
Who collected it?
When was it acquired?
What was the original hash?
Was the evidence modified?
Which files were recovered?
Which files were partial?
Which files failed?
Who performed the analysis?
When was the report generated?
```

ForensicRecover connects these activities.

The main value is therefore:

> **Recovery + Evidence Management + Integrity + Chain of Custody + Reporting**

---

# 7. Important Recovery Reality

ForensicRecover must **never claim 100% recovery**.

The correct project statement is:

> **"The system attempts to identify and recover technically available evidence."**

Recovery may be affected by:

```text
Storage Technology
Filesystem
Data Overwriting
TRIM
Garbage Collection
Wear Leveling
Encryption
Physical Damage
System Activity
Time Since Deletion
```

Therefore, the platform should report a **recovery potential**, not guarantee recovery.

Example:

```text
HIGH
MEDIUM
LOW
UNCERTAIN
```

---

# 8. What the System Does

The platform provides the following workflow:

```text
1. Create Investigation Case
          ↓
2. Register Evidence
          ↓
3. Record Device Information
          ↓
4. Register Forensic Acquisition
          ↓
5. Generate/Store Evidence Hash
          ↓
6. Analyze Device
          ↓
7. Assess Recovery Potential
          ↓
8. Perform/Integrate Recovery
          ↓
9. Classify Recovery Results
          ↓
10. Verify Integrity
          ↓
11. Maintain Chain of Custody
          ↓
12. Investigator Review
          ↓
13. Generate Final Report
```

---

# 9. Complete End-to-End Workflow

```text
                   ┌──────────────────┐
                   │   SEIZED DEVICE  │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │   CREATE CASE   │
                   └────────┬─────────┘
                            │
                            ▼
                  ┌────────────────────┐
                  │ REGISTER EVIDENCE  │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ FORENSIC ACQUISITION│
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │   FORENSIC IMAGE   │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │   DEVICE ANALYSIS  │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ RECOVERY ASSESSMENT│
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ DELETED DATA SEARCH│
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │  RECOVERY ENGINE   │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ RECOVERED ARTIFACTS│
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │  HASH VERIFICATION │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │  CHAIN OF CUSTODY  │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ INVESTIGATOR REVIEW│
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │   FINAL REPORT     │
                  └────────────────────┘
```

---

# 10. Core Modules

## 10.1 Authentication

Purpose:

> **"Kaun software use kar raha hai aur usko kya access milna chahiye?"**

Features:

```text
Login
Logout
Password Hashing
User Roles
Role-Based Access Control
```

Roles:

```text
ADMIN
INVESTIGATOR
FORENSIC_EXAMINER
VIEWER
```

---

## 10.2 Case Management

Purpose:

> **"Investigation ko organize karna."**

Features:

```text
Create Case
View Case
Update Case
Close Case
Assign Investigator
Case Status
```

Example:

```text
CASE-2026-001

Type:
Cyber Investigation

Investigator:
Officer A

Status:
ACTIVE
```

---

## 10.3 Evidence Management

Every device receives a unique evidence ID.

Example:

```text
Evidence ID:
EV-001

Device:
Laptop

Manufacturer:
Dell

Model:
XXXX

Serial Number:
XXXXXX

Storage:
1 TB HDD

Filesystem:
NTFS
```

---

## 10.4 Forensic Acquisition

The platform records the controlled forensic acquisition process.

Concept:

```text
Original Device
      ↓
Forensic Acquisition
      ↓
Forensic Image
      ↓
Working Copy
      ↓
Analysis
```

The original evidence should be preserved according to applicable forensic procedures.

---

## 10.5 Device Analysis

The platform records or identifies:

```text
Storage Type
Filesystem
Capacity
Device Information
Relevant Metadata
```

Example:

```text
Device:
1 TB HDD

Filesystem:
NTFS

Recovery Potential:
HIGH
```

---

## 10.6 Deleted Data Analysis

The recovery workflow may involve:

```text
Forensic Image
      ↓
Filesystem Analysis
      ↓
Deleted Records
      ↓
Metadata
      ↓
Unallocated Storage
      ↓
File Carving
      ↓
Recovered Artifacts
```

The MVP should integrate established forensic capabilities rather than attempt to recreate an entire commercial forensic engine from scratch.

---

## 10.7 Recovery Result Management

Results are classified as:

```text
FULLY_RECOVERED
PARTIALLY_RECOVERED
NOT_RECOVERABLE
CORRUPTED
UNKNOWN
```

Example:

```text
Files Found:        127
Fully Recovered:     89
Partial:             17
Failed:              21
```

---

## 10.8 Integrity Verification

The system calculates cryptographic hashes such as SHA-256.

Example:

```text
Evidence Image
      ↓
SHA-256
      ↓
A81F92D73C...
```

Later:

```text
Stored Hash
     VS
Current Hash
```

If they match:

```text
✓ VERIFIED
```

If they differ:

```text
⚠ INTEGRITY MISMATCH
```

---

## 10.9 Chain of Custody

The system records:

```text
WHO
WHAT
WHEN
WHY
EVIDENCE ID
```

Example:

```text
10:00
Collected by Officer A

12:00
Received by Forensic Lab

13:30
Assigned to Examiner B

14:00
Acquisition Started

15:30
Recovery Started

18:00
Recovery Completed
```

---

## 10.10 Tamper-Evident Audit Trail

Important events can be linked using hashes.

Concept:

```text
Event 1
   ↓
Hash 1

Event 2 + Hash 1
   ↓
Hash 2

Event 3 + Hash 2
   ↓
Hash 3
```

If an earlier event is modified:

```text
⚠ AUDIT CHAIN INTEGRITY FAILURE
```

This can be implemented without blockchain.

---

## 10.11 Investigator Dashboard

The dashboard provides a simple overview.

Example:

```text
┌───────────────────────────────────────┐
│          FORENSICRECOVER              │
├───────────────────────────────────────┤
│ Cases:              12                │
│ Evidence Items:     48                │
│ Recovery Jobs:      37                │
│ Integrity Alerts:   2                 │
└───────────────────────────────────────┘
```

Case page:

```text
CASE-2026-001

Evidence:
EV-001

Storage:
1 TB HDD

Recovery Potential:
HIGH

Deleted Artifacts:
127

Fully Recovered:
89

Partial:
17

Failed:
21

Integrity:
✓ VERIFIED
```

---

## 10.12 Report Generation

The system generates a structured PDF report.

The report may include:

```text
FORENSIC INVESTIGATION REPORT

Case Information

Evidence Information

Device Information

Acquisition Information

Original Evidence Hash

Recovery Summary

Recovered Artifacts

Partial Recoveries

Non-Recoverable Items

Chain of Custody

Integrity Verification

Investigator Information

Timestamps
```

---

# 11. System Architecture

```text
                  ┌────────────────────┐
                  │     INVESTIGATOR   │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │   WEB DASHBOARD    │
                  └──────────┬─────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │      FASTAPI       │
                  │      BACKEND       │
                  └──────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
      Case Manager     Evidence Manager   Recovery Manager
            │                │                │
            └────────────────┼────────────────┘
                             │
                             ▼
                   Integrity Engine
                             │
                             ▼
                    Custody Manager
                             │
                             ▼
                        SQLite DB
                             │
                             ▼
                     Report Generator
```

---

# 12. Repository Structure

```text
ForensicRecover/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── cases.py
│   │   ├── evidence.py
│   │   ├── recovery.py
│   │   ├── integrity.py
│   │   ├── custody.py
│   │   └── reports.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── case.py
│   │   ├── evidence.py
│   │   ├── acquisition.py
│   │   ├── recovery.py
│   │   └── custody.py
│   │
│   ├── services/
│   │   ├── hashing.py
│   │   ├── acquisition.py
│   │   ├── device_analysis.py
│   │   ├── recovery.py
│   │   ├── custody.py
│   │   └── reporting.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── migrations/
│   │
│   └── utils/
│       ├── security.py
│       └── validators.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── cases.html
│   ├── evidence.html
│   ├── recovery.html
│   └── reports.html
│
├── forensic/
│   ├── images/
│   ├── recovered/
│   └── test-data/
│
├── reports/
│
├── tests/
│   ├── test_auth.py
│   ├── test_cases.py
│   ├── test_evidence.py
│   ├── test_hashing.py
│   ├── test_recovery.py
│   └── test_custody.py
│
└── docs/
    ├── architecture.md
    ├── api.md
    └── forensic-workflow.md
```

---

# 13. Git Branch Structure

Recommended structure:

```text
main
│
└── develop
     │
     ├── feature/authentication
     ├── feature/case-management
     ├── feature/evidence-acquisition
     ├── feature/device-analysis
     ├── feature/data-recovery
     ├── feature/integrity-verification
     ├── feature/chain-of-custody
     └── feature/dashboard-reports
```

---

# 14. Branch Responsibilities

## `main`

Purpose:

> Stable and demo-ready version.

No direct feature development should happen here.

---

## `develop`

Purpose:

> Integration branch.

Completed features are merged here and tested together before promotion to `main`.

---

## `feature/authentication`

Responsible for:

```text
Login
Logout
Password Hashing
Roles
Access Control
```

---

## `feature/case-management`

Responsible for:

```text
Create Case
View Case
Update Case
Close Case
Assign Investigator
Case Status
```

---

## `feature/evidence-acquisition`

Responsible for:

```text
Evidence ID
Device Type
Manufacturer
Model
Serial Number
Capacity
Filesystem
Acquisition Information
Evidence Status
```

---

## `feature/device-analysis`

Responsible for:

```text
HDD Detection
SSD Detection
NVMe Detection
Filesystem Information
Capacity
Device Metadata
Recovery Potential
```

Output:

```text
HIGH
MEDIUM
LOW
UNCERTAIN
```

---

## `feature/data-recovery`

Main forensic integration branch.

Responsible for:

```text
Forensic Image
Filesystem Analysis
Deleted Artifact Detection
Metadata Analysis
Unallocated-Space Analysis
File-Carving Integration
Recovery Results
```

The branch should focus on integrating established forensic capabilities rather than unnecessarily rebuilding mature forensic engines.

---

## `feature/integrity-verification`

Responsible for:

```text
SHA-256
Hash Storage
Hash Comparison
Integrity Status
```

---

## `feature/chain-of-custody`

Responsible for:

```text
Collection
Transfer
Receipt
Acquisition
Analysis
Recovery
Review
```

---

## `feature/dashboard-reports`

Responsible for:

```text
Dashboard
Statistics
Recovery Results
Integrity Alerts
Custody Timeline
PDF Reports
```

---

# 15. Technology Stack

## Backend

```text
Python 3.11+
FastAPI
Uvicorn
Pydantic
```

---

## Database

### MVP

```text
SQLite
```

### Future

```text
PostgreSQL
```

---

## Frontend

### MVP

```text
HTML
CSS
JavaScript
Bootstrap
```

### Future

```text
React
```

---

## Security

```text
Password Hashing
Role-Based Access Control
SHA-256
Audit Logging
Input Validation
```

---

## Forensic Layer

Potential open-source integrations include established forensic capabilities such as:

```text
The Sleuth Kit
Autopsy
Other validated forensic utilities
```

The platform should act as an orchestration and evidence-management layer rather than attempting to replace mature forensic engines in the MVP.

---

## Report Generation

```text
ReportLab
```

---

## Visualization

```text
Chart.js
```

---

## Development Tools

```text
Git
GitHub
VS Code
Python Virtual Environment
```

---

# 16. Database Design

Initial tables:

```text
users
cases
evidence
acquisitions
hash_records
recovery_jobs
recovered_artifacts
custody_events
audit_events
reports
```

---

## Users

```text
id
name
username
password_hash
role
created_at
```

---

## Cases

```text
id
case_number
case_type
description
investigator_id
status
created_at
closed_at
```

---

## Evidence

```text
id
evidence_id
case_id
device_type
manufacturer
model
serial_number
capacity
filesystem
source_path
status
created_at
```

---

## Acquisition

```text
id
evidence_id
acquisition_type
source
image_path
hash
started_at
completed_at
status
```

---

## Hash Records

```text
id
evidence_id
algorithm
hash_value
calculated_at
purpose
```

---

## Recovery Jobs

```text
id
evidence_id
started_at
completed_at
status
files_found
files_recovered
files_partial
files_failed
recovery_notes
```

---

## Recovered Artifacts

```text
id
recovery_job_id
original_name
recovered_path
artifact_type
recovery_status
hash
size
metadata
```

---

## Custody Events

```text
id
evidence_id
from_user
to_user
action
timestamp
remarks
event_hash
previous_hash
```

---

# 17. Forensic Recovery Architecture

The recovery system should be layered:

```text
                 FORENSIC IMAGE
                       │
                       ▼
               Filesystem Analysis
                       │
                       ▼
              Deleted File Detection
                       │
                       ▼
                 Metadata Analysis
                       │
                       ▼
              Unallocated-Space Scan
                       │
                       ▼
                  File Carving
                       │
                       ▼
                Artifact Analysis
                       │
                       ▼
              Recovered Artifacts
```

Each artifact should receive a clear status:

```text
FULLY_RECOVERED
PARTIALLY_RECOVERED
NOT_RECOVERABLE
CORRUPTED
UNKNOWN
```

---

# 18. Evidence Integrity

Every important evidence object should have a cryptographic fingerprint.

Example:

```text
Evidence Image
      ↓
SHA-256
      ↓
A81F92D73C...
```

During verification:

```text
Original Stored Hash
        VS
Current Hash
```

Result:

```text
MATCH
  ↓
✓ VERIFIED
```

or:

```text
MISMATCH
  ↓
⚠ INTEGRITY ALERT
```

---

# 19. Chain of Custody

Example:

```text
Officer A
   ↓
Collected Evidence
   ↓
Forensic Lab
   ↓
Examiner B
   ↓
Acquisition
   ↓
Recovery
   ↓
Investigator Review
   ↓
Final Report
```

Every event should record:

```text
User
Timestamp
Action
Evidence ID
Reason/Remarks
```

---

# 20. Dashboard

The MVP dashboard should show:

## Case Summary

```text
Total Cases
Active Cases
Closed Cases
```

## Evidence Summary

```text
Total Evidence
Verified Evidence
Integrity Alerts
```

## Recovery Summary

```text
Total Recovery Jobs
Fully Recovered
Partially Recovered
Not Recoverable
```

## Timeline

```text
Collection
   ↓
Acquisition
   ↓
Analysis
   ↓
Recovery
   ↓
Review
   ↓
Report
```

---

# 21. Report Generation

The final PDF should contain:

```text
CASE INFORMATION
        ↓
EVIDENCE INFORMATION
        ↓
DEVICE INFORMATION
        ↓
ACQUISITION INFORMATION
        ↓
HASH INFORMATION
        ↓
RECOVERY RESULTS
        ↓
RECOVERED ARTIFACTS
        ↓
CHAIN OF CUSTODY
        ↓
INTEGRITY VERIFICATION
        ↓
INVESTIGATOR REVIEW
```

---

# 22. Security

## Authentication

All users must authenticate.

---

## Role-Based Access Control

```text
ADMIN
  ↓
Full System Access

INVESTIGATOR
  ↓
Case + Evidence Access

FORENSIC_EXAMINER
  ↓
Evidence + Recovery Access

VIEWER
  ↓
Read Only
```

---

## Password Security

Passwords must never be stored in plain text.

Use secure password hashing.

---

## Audit Logging

Important actions should be logged:

```text
Login
Case Creation
Evidence Creation
Evidence Transfer
Acquisition Started
Recovery Started
Recovery Completed
Report Generated
```

---

# 23. Zero-Cost MVP

The initial prototype can be developed using free/open-source software.

| Requirement          | Technology                 |
| -------------------- | -------------------------- |
| Programming          | Python                     |
| Backend              | FastAPI                    |
| Database             | SQLite                     |
| Frontend             | HTML/CSS/JavaScript        |
| UI                   | Bootstrap                  |
| Hashing              | Python `hashlib`           |
| Forensic Integration | Open-source forensic tools |
| Reports              | ReportLab                  |
| Charts               | Chart.js                   |
| Version Control      | Git/GitHub                 |
| IDE                  | VS Code                    |

Target software cost:

```text
₹0
```

Specialized forensic hardware, storage, write blockers, and laboratory infrastructure are separate requirements for real-world deployment.

---

# 24. MVP Scope

The first working MVP should include:

```text
✓ Authentication
✓ Role-Based Access
✓ Case Creation
✓ Evidence Registration
✓ Device Information
✓ Forensic Image Registration
✓ SHA-256 Hashing
✓ Hash Verification
✓ Deleted-Data Analysis Workflow
✓ Recovery Result Management
✓ Chain of Custody
✓ Tamper-Evident Audit Log
✓ Investigator Dashboard
✓ PDF Report
```

---

# 25. Development Roadmap

## Phase 1 — Repository Setup

```text
Create GitHub Repository
        ↓
Create main
        ↓
Create develop
        ↓
Create feature branches
        ↓
Create Python Environment
        ↓
Install Dependencies
        ↓
Create Project Structure
```

Deliverable:

```text
Running FastAPI Application
+
SQLite Database
```

---

## Phase 2 — Authentication

Implement:

```text
Login
Logout
Roles
Password Hashing
Access Control
```

Deliverable:

```text
User
 ↓
Login
 ↓
Dashboard
```

---

## Phase 3 — Case Management

Implement:

```text
Create Case
View Case
Update Case
Close Case
Assign Investigator
```

Deliverable:

```text
CASE-2026-001
```

---

## Phase 4 — Evidence Registration

Implement:

```text
Evidence ID
Device Information
Serial Number
Storage Information
Case Association
```

Deliverable:

```text
CASE-2026-001
      ↓
EV-001
      ↓
Laptop
```

---

## Phase 5 — Acquisition Workflow

Implement:

```text
Forensic Image Registration
Acquisition Metadata
Acquisition Status
Image Location
```

Deliverable:

```text
Original Evidence
       ↓
Forensic Image
       ↓
Evidence Record
```

---

## Phase 6 — Integrity Engine

Implement:

```text
SHA-256 Generation
Hash Storage
Hash Verification
Integrity Status
```

Example:

```text
Original:
A81F92...

Current:
F72A31...

🚨 INTEGRITY MISMATCH
```

---

## Phase 7 — Device Analysis

Implement:

```text
Storage Type
Filesystem
Capacity
Recovery Indicators
Recovery Potential
```

Example:

```text
HDD
NTFS
1 TB

Recovery Potential:
HIGH
```

---

## Phase 8 — Recovery Integration

Integrate appropriate forensic tools/capabilities.

Workflow:

```text
Forensic Image
      ↓
Filesystem Analysis
      ↓
Deleted Artifacts
      ↓
Recovery
      ↓
Recovery Results
```

---

## Phase 9 — Chain of Custody

Implement:

```text
Collection
Transfer
Receive
Acquire
Analyze
Recover
Review
Report
```

Store:

```text
User
Timestamp
Action
Evidence ID
```

---

## Phase 10 — Tamper-Evident Audit

Implement:

```text
event_hash
previous_hash
```

Concept:

```text
Event 1 → Hash A

Event 2 + Hash A → Hash B

Event 3 + Hash B → Hash C
```

---

## Phase 11 — Dashboard

Implement:

```text
Case Dashboard
Evidence Dashboard
Recovery Dashboard
Integrity Alerts
Custody Timeline
```

---

## Phase 12 — Report Generator

Generate:

```text
Case
Evidence
Device
Hash
Recovery
Custody
Integrity
Findings
```

as a PDF.

---

## Phase 13 — Full Integration

Final workflow:

```text
LOGIN
  ↓
CREATE CASE
  ↓
REGISTER EVIDENCE
  ↓
REGISTER FORENSIC IMAGE
  ↓
CALCULATE HASH
  ↓
ANALYZE DEVICE
  ↓
ASSESS RECOVERY
  ↓
RECOVER / ANALYZE
  ↓
HASH ARTIFACTS
  ↓
UPDATE CUSTODY
  ↓
INVESTIGATOR REVIEW
  ↓
GENERATE REPORT
```

---

# 26. Project Demonstration

The MVP should be demonstrated using **synthetic or explicitly authorized forensic test evidence**.

## Step 1 — Create Case

```text
CASE-2026-001
```

## Step 2 — Register Evidence

```text
EV-001
Test Laptop
```

## Step 3 — Load Test Forensic Image

Use a legally safe forensic test image.

## Step 4 — Calculate Hash

```text
SHA-256:
A81F92...
```

## Step 5 — Analyze Deleted Artifacts

Example:

```text
Deleted Artifacts:
47
```

## Step 6 — Show Recovery Results

```text
Fully Recovered:
31

Partial:
8

Failed:
8
```

## Step 7 — Verify Integrity

```text
✓ VERIFIED
```

## Step 8 — Demonstrate Tampering Detection

Modify the test evidence copy and run verification.

Expected:

```text
Stored:
A81F92...

Current:
F83B12...

🚨 INTEGRITY MISMATCH
```

## Step 9 — Show Chain of Custody

```text
Collected
    ↓
Received
    ↓
Acquired
    ↓
Analyzed
    ↓
Recovered
    ↓
Reviewed
```

## Step 10 — Generate Report

```text
FORENSIC INVESTIGATION REPORT.pdf
```

---

# 27. Unique Selling Propositions

The project should **not** claim:

> "We are the first deleted-data recovery software."

There are already mature forensic tools.

The stronger USP is:

> **A unified, investigator-friendly workflow that connects forensic evidence management, recovery-result orchestration, integrity verification, chain of custody, tamper-evident auditing, and reporting in one platform.**

---

## USP 1 — Device-Aware Recovery Assessment

The system considers:

```text
Storage Technology
Filesystem
Device Information
Recovery Indicators
```

and provides:

```text
HIGH
MEDIUM
LOW
UNCERTAIN
```

recovery potential.

---

## USP 2 — Maximum Recoverability Workflow

Future versions can use multiple validated forensic techniques:

```text
Technique A
      +
Technique B
      +
Technique C
      ↓
Compare Results
      ↓
Remove Duplicates
      ↓
Maximum Available Evidence
```

---

## USP 3 — Recovery + Integrity

Instead of only saying:

```text
Recovered 100 files
```

the platform also records:

```text
Which evidence?
Which case?
Which acquisition?
What hash?
Who performed recovery?
When?
Was integrity maintained?
```

---

## USP 4 — Investigator-Friendly Interface

Raw forensic information can be complicated.

The platform converts it into understandable information:

```text
Files Found:
127

Recovered:
89

Partial:
17

Failed:
21
```

---

## USP 5 — Tamper-Evident History

The system cryptographically links audit events.

This creates a clear history:

```text
Evidence
   ↓
Action
   ↓
Person
   ↓
Timestamp
   ↓
Next Action
```

---

## USP 6 — Unified Workflow

Instead of:

```text
Recovery Tool
      +
Hash Tool
      +
Spreadsheet
      +
Manual Custody Log
      +
Manual Report
```

the goal is:

```text
                 FORENSICRECOVER
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
     Recovery       Integrity       Custody
        │              │              │
        └──────────────┼──────────────┘
                       ↓
                    Report
```

---

# 28. Future Development

## Version 1

```text
Automatic Device Detection
Automatic Filesystem Detection
Improved Recovery Assessment
Forensic Tool Integration
```

---

## Version 2

```text
Multi-Engine Recovery
Artifact Classification
Timeline Reconstruction
Advanced Metadata Analysis
```

---

## Version 3 — AI-Assisted Investigation

Future AI features could assist with:

```text
Evidence Prioritization
Artifact Classification
Timeline Summarization
Anomaly Detection
Natural-Language Evidence Search
```

Example:

```text
Investigator:

"Show files deleted around the incident time."

System:

Returns potentially relevant recovered artifacts
and associated timeline information.
```

AI should assist the investigator rather than independently make legal conclusions.

---

## Version 4 — Secure Evidence Exchange

Potential features:

```text
Digital Signatures
Encrypted Evidence Transfer
Secure Evidence Exchange
Centralized Forensic Repository
```

Possible future architecture:

```text
Local Forensic Lab
       ↓
Secure Evidence Platform
       ↓
Regional Lab
       ↓
Central Forensic Lab
```

---

# 29. Project Limitations

## 29.1 No 100% Recovery

Some deleted information may be permanently unavailable.

---

## 29.2 Overwritten Data

If storage areas containing deleted information are overwritten, recovery may not be possible.

---

## 29.3 SSD Limitations

SSD behavior can significantly reduce recoverability.

Factors can include:

```text
TRIM
Garbage Collection
Wear Leveling
Controller Behavior
```

---

## 29.4 Encryption

Encrypted information may not be recoverable without authorized access to the necessary keys or credentials.

---

## 29.5 Physical Damage

Damaged storage may require specialized forensic hardware and laboratory procedures.

---

## 29.6 Proprietary Formats

Some applications use proprietary formats that may require specialized analysis.

---

## 29.7 Tool Dependency

The MVP relies on established forensic tools/capabilities for certain technical operations.

---

## 29.8 Legal Limitations

Technical recovery does not automatically mean legal admissibility.

Real-world forensic use depends on:

```text
Applicable Laws
Agency Procedures
Tool Validation
Examiner Qualifications
Evidence Handling Procedures
Jurisdiction
```

---

# 30. Ethical and Legal Considerations

ForensicRecover must only be used for:

```text
Authorized Investigations
Authorized Digital Forensics
Owned Test Devices
Synthetic Evidence
Laboratory Test Images
Explicitly Authorized Evidence
```

The software must not be used to access or recover information from devices without proper authorization.

The project should be tested primarily using synthetic, laboratory, or explicitly authorized evidence.

---

# 31. Team Responsibilities

Recommended team structure:

```text
Member 1
Authentication + Case Management

Member 2
Evidence Acquisition + Device Analysis

Member 3
Recovery Integration

Member 4
Integrity Verification

Member 5
Chain of Custody + Audit

Member 6
Dashboard + Reports
```

For a smaller team, multiple modules can be combined.

---

# 32. Development Guidelines

## Branching Strategy

Do not directly develop on `main`.

Use:

```text
feature/*
      ↓
Pull Request
      ↓
develop
      ↓
Testing
      ↓
main
```

---

## Commit Naming

Use clear commit messages:

```text
feat: add evidence registration

feat: implement SHA-256 verification

feat: add custody events

fix: resolve evidence hash mismatch

docs: update forensic workflow
```

---

## Pull Request Rules

Every Pull Request should:

1. Have a clear description.
2. Be tested locally.
3. Avoid breaking existing functionality.
4. Be reviewed before merging.
5. Update documentation where necessary.

---

# 33. Installation

## Requirements

```text
Python 3.11+
Git
4GB+ RAM recommended
Windows / Linux
```

---

## Clone Repository

```bash
git clone <repository-url>
cd ForensicRecover
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Backend

```bash
uvicorn app.main:app --reload
```

Application:

```text
http://127.0.0.1:8000
```

---

# 34. MVP Success Criteria

The MVP will be considered successful when it can perform this complete demonstration:

```text
Authorized Test Evidence
          ↓
Create Case
          ↓
Register Device
          ↓
Register Forensic Image
          ↓
Calculate SHA-256
          ↓
Analyze Deleted Artifacts
          ↓
Record Recovery Results
          ↓
Verify Evidence Integrity
          ↓
Record Chain of Custody
          ↓
Display Dashboard
          ↓
Generate PDF Report
```

The goal is not to claim that the prototype can recover every deleted file.

The goal is to demonstrate a:

> **Complete, traceable, transparent and technically credible forensic workflow.**

---

# 35. Viva / Presentation Explanation

## "What exactly does your project do?"

> **"Our project is a digital forensic investigation platform. Suppose an investigation team gets a laptop where a person has deleted important files and emptied the Recycle Bin. Our system helps the investigator register the device as evidence, create or register a forensic working copy, analyze available deleted-data artifacts using appropriate forensic capabilities, record what can and cannot be recovered, verify the evidence using cryptographic hashes, maintain the chain of custody, and finally generate a structured forensic report."**

---

## "Can you recover everything?"

> **"No. Recovery is not guaranteed. It depends on the storage technology, filesystem, overwriting, SSD behavior, encryption and other factors. Our objective is to maximize technically recoverable evidence, not to claim 100% recovery."**

---

## "What is your USP?"

> **"Our USP is not simply file recovery. Existing forensic tools already provide recovery capabilities. Our USP is integrating recovery-result management with evidence integrity verification, chain of custody, tamper-evident audit history, investigator-friendly dashboards and automated reporting in one workflow."**

---

## "Why should a government department use it?"

> **"Because an investigation requires more than finding files. Investigators need to know which evidence was examined, what was recovered, who handled it, whether its integrity was maintained, what actions were performed, and how the final findings were produced. Our platform organizes that complete workflow."**

---

# 36. Final Project Definition

## One-Line Definition

> **ForensicRecover is an authorized digital-forensics platform that helps investigators identify and recover technically recoverable deleted evidence while preserving its integrity and documenting its complete investigation history.**

---

## Short Definition

```text
ForensicRecover =
Digital Evidence Management
+
Deleted-Data Analysis
+
Recovery Integration
+
Integrity Verification
+
Chain of Custody
+
Audit Logging
+
Investigator Dashboard
+
Forensic Reporting
```

---

# 37. Long-Term Vision

The long-term vision is to evolve ForensicRecover into a:

> **Device-aware, multi-tool, evidence-integrity-focused and AI-assisted digital forensic investigation platform.**

Future architecture:

```text
                       FORENSICRECOVER
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Acquisition            Recovery              Analysis
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                       Integrity Layer
                              │
                              ▼
                      Chain of Custody
                              │
                              ▼
                     AI-Assisted Analysis
                              │
                              ▼
                         Investigator
                              │
                              ▼
                           Report
```

---

# 🧠 Core Design Philosophy

The project should follow:

```text
DELETE
  ≠
ALWAYS IMMEDIATELY UNRECOVERABLE

BUT

RECOVERY
  ≠
ALWAYS GUARANTEED
```

Therefore:

```text
FIND WHAT IS TECHNICALLY AVAILABLE
             ↓
          RECOVER
             ↓
           VERIFY
             ↓
          PRESERVE
             ↓
           TRACK
             ↓
          ANALYZE
             ↓
           REPORT
```

---

# 🚀 Recommended MVP Strategy

Do **not** attempt to build the world's most advanced recovery engine in the first version.

The strongest MVP is a complete working workflow:

```text
CASE
 ↓
EVIDENCE
 ↓
FORENSIC IMAGE
 ↓
HASH
 ↓
DELETED-ARTIFACT ANALYSIS
 ↓
RECOVERY RESULTS
 ↓
CHAIN OF CUSTODY
 ↓
INTEGRITY VERIFICATION
 ↓
DASHBOARD
 ↓
PDF REPORT
```

Use established forensic capabilities for technically complex recovery operations.

Then build your own value around:

```text
Evidence Management
+
Automation
+
Integrity
+
Custody
+
Auditability
+
Reporting
+
Investigator Experience
```

---

# 🛡️ ForensicRecover

## Recover the Evidence.

## Verify Its Integrity.

## Preserve Its History.

## Support the Investigation.

### **Recover → Verify → Preserve → Track → Analyze → Report**
