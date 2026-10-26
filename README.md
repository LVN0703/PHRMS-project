# Personal Health Record Management and Sharing System (PHRMS)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-black.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-Academic%20Capstone-green.svg)]()

> **Technology Capstone Project (MIS 4500 - Fall 2026)**  
> **Student Author:** Abishekan Sri Baskaran (Student ID: 0001044)  
> **Project Supervisor:** Dr. Ama Kulathilake  
> **Institution:** Northwood University / American National College  

---

## 🏥 Overview

The **Personal Health Record Management and Sharing System (PHRMS / HealthVault)** is a web-based clinical prototype designed to centralize and secure personal health records. It bridges the gap between fragmented patient records from diverse healthcare providers through a structured, four-role workflow with patient-controlled privacy, administrative quality verification, and consultation-ready briefing sheets.

---

## ✨ Core Stakeholder Roles & Portals

### 1. 🧑‍⚕️ Patient User Portal
- **Medical Document Submission (FR02):** Upload PDF, PNG, JPG, and DICOM clinical files with structured metadata (Category, Provider, Date, Notes).
- **Submission Status Tracker (FR04):** Real-time tracking of review states (`PENDING`, `APPROVED`, `CORRECTION_REQUIRED`, `REJECTED`).
- **Correction & Resubmission Flow (FR03):** Inline interface to address registrar feedback and resubmit corrected records.
- **Chronological Health Timeline (FR05):** Auto-sorted by event date in reverse chronological order with category filtering pills.
- **Consultation-Ready Summary Builder (FR08):** Compile patient-selected records and reason for visit into a print-ready briefing sheet.
- **Doctor Access Control (FR06):** Granular grant and revocation toggles per specialist with zero-knowledge authorization gating.
- **Transparency Audit Ledger (FR09):** Sovereign log tracking who viewed or actioned the patient's records.

### 2. 📋 Document Review Team (Registrar Triage)
- **Triage Queue (FR03):** Priority queue of pending submissions with queue SLA countdown monitoring.
- **Side-by-Side Inspection Viewport:** Document canvas with zoom, rotate, letterhead verification, and ECG lead traces.
- **3-Point Verification Affirmation:** Mandatory checks for legibility, date concordance, and clinical taxonomy.
- **Atomic State Transitions:** Execute **Approve & Publish**, **Request Correction**, or **Reject** with mandatory audit notes.

### 3. 🩺 Physician Clinical Portal
- **Delegated Patient Directory (FR07):** Displays only patients who have actively granted consent to the logged-in doctor.
- **Strict Authorization Gate (NFR03):** Access to non-authorized dossiers triggers HTTP 403 Forbidden and logs security violations.
- **Critical Allergy Warning Banner (Aid Red):** Mandatory clinical alert for severe allergies (e.g., Penicillin ICD-10 Z88.0).
- **Dual-Tab Workspace:** Toggle between Consultation-Ready Summaries and the Full Chronological Timeline.

### 4. 🛡️ System Administrator Console
- **System Integrity Telemetry:** SLA compliance tracking (99.98%), user role distribution, and active consent counts.
- **Emergency Institutional Policy Lock:** High-security containment toggle.
- **Central Security Audit Ledger (FR09):** Immutable event history capturing actor, affected patient, action, and details.

---

## 🎨 Unified Design System (`phrms-common.css`)

Mapped strictly to the project's **Medical Logo Color Palette**:
- **Surgical Blue (`#007BA7`):** Primary brand accent, patient portal, action buttons, timeline connectors.
- **Trust Teal (`#008080`):** Secondary accent, physician and reviewer header themes, consultation summary banners.
- **Health Green (`#4CAF50`):** Positive status badges, verified document checkmarks, access granted states.
- **Aid Red (`#D62828`):** Critical clinical allergy alerts, revocation buttons, rejected document states.
- **Clean White (`#FFFFFF`):** Primary card, sheet, and modal surfaces.
- **Cool Gray (`#A9B0B3`):** Canvas background (`#F4F7F8`), borders (`#DCE1E5`), and neutral status badges.

Includes dedicated `@media print` rules for the Consultation Summary sheet.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- `pip`

### 1. Clone the Repository
```bash
git clone https://github.com/LVN0703/PHRMS-project.git
cd PHRMS-project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed Database & Run Application
```bash
# Optional manual seed (app auto-seeds if database is empty on first launch)
python seed.py

# Launch Flask local server
python app.py
```
Open your browser to: **`http://127.0.0.1:5000`**

---

## 🔑 Pre-Seeded Academic Demo Personas

The application features a persistent **Demo Switcher Bar** in the top navigation for seamless 1-click role transitions during evaluative presentations.

| Role | Name | Email | Password | Identifier |
| :--- | :--- | :--- | :--- | :--- |
| **Patient** | Amara Perera | `amara.perera@health.lk` | `password123` | NIC: `199182302481` (Allergy: Penicillin) |
| **Patient** | Rohan Silva | `rohan.silva@health.lk` | `password123` | NIC: `198418903310` |
| **Doctor** | Dr. Nalin Bandara | `dr.bandara@hospital.lk` | `password123` | SLMC: `#18420` (Cardiology) |
| **Doctor** | Dr. Kavindi Jayasinghe | `dr.jayasinghe@hospital.lk` | `password123` | SLMC: `#22910` (General Medicine) |
| **Registrar** | Malini Fernando | `malini.fernando@phrms.gov.lk` | `password123` | Staff ID: `REG-88410` |
| **Admin** | K. Wickramasinghe | `admin.sec@phrms.gov.lk` | `password123` | Staff ID: `SEC-01-CISO` |

---

## 🧪 Automated Testing

Execute the test suite verifying all 9 functional requirements:
```bash
python test_phrms.py
```

Test coverage includes:
- Initial database seeding and persona constraints
- RBAC session redirects for unauthenticated users
- 1-click academic demo role switcher
- Patient document upload & status queueing
- Administrative reviewer approval, correction, and rejection workflows
- Doctor authorization check gate (HTTP 200 vs HTTP 403)
- Dynamic doctor access grant and revocation
- Consultation-ready summary compilation and sheet rendering
- Immutable audit log event tracking

---

## 📄 License
Developed for academic capstone presentation and evaluation purposes under **MIS 4500 Technology Capstone Project (Fall 2026)** at Northwood University / American National College.
