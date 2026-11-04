# Digital Campus Library Reservation Gateway (LRG)
## Software Engineering Mini-Project — Collaborative Team Repository

[![CI Quality Gate](https://github.com/IAmKai1/SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-/actions/workflows/ci.yml/badge.svg)](https://github.com/IAmKai1/SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-/actions)
![Tests](https://img.shields.io/badge/tests-61%2F61%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen)
![Branch Coverage](https://img.shields.io/badge/branch%20coverage-83%25-brightgreen)
![WCAG](https://img.shields.io/badge/accessibility-WCAG%202.1%20AA-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)

Comprehensive collaborative repository for the **Software Engineering Lab Project**, Department of Computer Science & Engineering, **PES University**.

---

## 👥 Team Members & Project Roles

| Student Name | SRN | Primary Role | Assigned Use Case / Subsystem |
| :--- | :--- | :--- | :--- |
| **Dharshini V** | **PES1UG24AM428** | Dev Lead & Full-Stack Architect | **UC-04: Pay Overdue Fine & Settlement** |
| **Dhareen G** | **PES1UG24AM084** | QA Lead & Scrum Master | **UC-06 / UC-07: Return Processing & Notifications** |
| **Divyansh** | **PES1UG24AM094** | Backend & Search Engineer | **UC-01 / UC-02: Catalog Search & Discovery** |
| **Dhruv Talavat**| **PES1UG24AM087** | Database & Security Engineer | **UC-03: Hold Placement & Rate Limiting** |

---

## 🚀 All Three Project Deliverables Summary

Strictly maintained in **this single GitHub repository** as required by the course coordinator:

### 1. Deliverable 1: Requirements, UML, Jira & Architecture (Labs 1–4)
- **Lab 1**: Requirements Engineering, Functional/Non-Functional Specifications, and UML Use Case Modeling.
- **Lab 2**: Jira Agile Backlog, Fibonacci Story Points, and Sprint Execution.
- **Lab 3**: UML Component Architecture, Provided/Required Interfaces, and Architectural Decision Records (ADRs).
- **Lab 4**: Software Requirements Specification (`SRS`), Software Architecture & Design (`SAD`), and Software Test Plan (`STP`).
  - [`Lab-04-SRS-SAD-STP/SRS_Library_Reservation_Gateway (1).pdf`](file:///Lab-04-SRS-SAD-STP/SRS_Library_Reservation_Gateway%20(1).pdf)
  - [`Lab-04-SRS-SAD-STP/SAD_Library_Reservation_Gateway (1).pdf`](file:///Lab-04-SRS-SAD-STP/SAD_Library_Reservation_Gateway%20(1).pdf)
  - [`Lab-04-SRS-SAD-STP/Test_Plan_Library_Reservation_Gateway.docx`](file:///Lab-04-SRS-SAD-STP/Test_Plan_Library_Reservation_Gateway.docx) *(Updated to v2.0)*

### 2. Deliverable 2: Software Implementation & Sprints 1, 2, and 3
- Working modular web application built with **Python / Flask** and **SQLite** (relational engine with foreign key enforcement and transactional integrity):
  - **`src/catalog_search.py`**: Search across 100,000 titles by ISBN, title, or author; pagination (10/page); book detail view; hyphen-flexible ISBN normalization (`TC-SRCH-07`).
  - **`src/auth.py`**: Campus OpenID Connect SSO authentication; 30-minute idle session timeout; 5-attempt brute-force lockout for 15 minutes (`LRG-SR-005`).
  - **`src/reservation_manager.py`**: FIFO hold queue placement; 5-hold limit; Available title rejection; 72-hour auto-expiration worker with cascade queue promotion (`TC-HOLD-06`).
  - **`src/fine_manager.py`**: **UC-04: Pay Overdue Fine**; overdue balance calculation; payment processing via Campus Wallet / UPI; digital receipt issuance; automated hold restrictions.
  - **`src/notification.py`**: Hold-ready notices (72h pickup window); 24h expiration reminders; 3-attempt exponential retry on SMTP downtime.
  - **`src/admin.py`**: Librarian administration center; title return processing; hold demand rankings; book addition/editing; strict RBAC.
  - **`src/security.py`**: Sliding-window rate limiter (60 req/min); SQL injection & XSS sanitization; password non-storage enforcement.
  - **`src/templates/` & `src/static/`**: High-contrast, mobile-responsive web UI meeting **WCAG 2.1 AA** standards from 360px viewport width up.

### 3. Deliverable 3: Complete Testing & Generated Reports (`docs/`)
All four formal test reports executed during the testing window (**2nd Nov to 6th Nov 2026**):

| Deliverable Item | Document Link | Description & Key Results |
| :--- | :--- | :--- |
| **1. Updated Test Cases** | [`docs/Updated_Test_Case_Document.md`](file:///docs/Updated_Test_Case_Document.md) | Details test case changes across Sprints 1–3, adding fine settlement, 72h auto-expire cascade, and updated RTM. |
| **2.i. Unit Test Report** | [`docs/Unit_Test_Report.md`](file:///docs/Unit_Test_Report.md) | 61 unit tests executed across all classes; **100% pass rate**; 0 open defects. |
| **2.ii. System Validation Report** | [`docs/System_Validation_Report.md`](file:///docs/System_Validation_Report.md) | End-to-end flows for UC-01 to UC-09 + UC-04; NFR validation ($P_{90} < 0.006\text{ s}$); 100% RTM acceptance (`A`). |
| **2.iii. Code Coverage Report** | [`docs/Code_Coverage_Report.md`](file:///docs/Code_Coverage_Report.md) | **89% overall statement coverage**; **93.8% business-layer coverage** (exceeds 70% threshold in `LRG-NF-006`). |
| **2.iv. Branch Coverage Report** | [`docs/Branch_Coverage_Report.md`](file:///docs/Branch_Coverage_Report.md) | **82.6% branch coverage** across 270 decision points; evaluates all boundary paths and error gates. |
| **Executive Summary** | [`docs/Test_Summary_Report.md`](file:///docs/Test_Summary_Report.md) | High-level executive test summary, defect aging, and formal quality gate sign-off. |
| **Sprint-3 & Jira Report** | [`docs/Sprint_3_Report_and_Jira_Tracking.md`](file:///docs/Sprint_3_Report_and_Jira_Tracking.md) | Agile tracking, epics, Fibonacci story points, 100% burndown chart, and CI/CD integration. |

---

## 🛠️ Quick Start & Local Execution

### 1. Setup Environment & Install Dependencies
```bash
git clone https://github.com/IAmKai1/SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-.git
cd SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-
pip install -r requirements.txt
```

### 2. Execute Automated Test Suite & Generate Reports
```bash
# Run all 61 tests with statement and branch coverage
pytest --cov=src --cov-branch --cov-report=term-missing --cov-report=html:docs/coverage_html --cov-report=xml:docs/coverage.xml

# Or run via automated test script
python scripts/run_all_tests.py
```

### 3. Launch the Web Application
```bash
python -m src.app
```
Navigate your browser to **`http://localhost:5000`** to access:
- **Catalog Search**: `/`
- **Book Details & Hold Placement**: `/book/<isbn>`
- **My Active Holds**: `/my-holds`
- **Overdue Fines & Payment Desk (UC-04)**: `/fines`
- **Head Librarian Administration**: `/admin/dashboard`
- **Campus SSO Login**: `/login`
- **System Health & Availability**: `/health`

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Configured at [`.github/workflows/ci.yml`](file:///.github/workflows/ci.yml):
- **Triggers**: On every `push` and `pull_request` to `main` and teammate branches.
- **Stages**: Environment Provisioning $\to$ Syntax Check $\to$ Unit Tests $\to$ System Validation $\to$ Coverage Threshold Gating ($\ge 70\%$) $\to$ HTML/XML Report Archiving.

---

## 📂 Repository Directory Structure

```text
SE-Lab-Project/
├── .github/
│   └── workflows/
│       └── ci.yml                     <-- Automated CI/CD pipeline
├── docs/
│   ├── Unit_Test_Report.md            <-- Deliverable 2.b.i
│   ├── System_Validation_Report.md    <-- Deliverable 2.b.ii
│   ├── Code_Coverage_Report.md        <-- Deliverable 2.b.iii
│   ├── Branch_Coverage_Report.md      <-- Deliverable 2.b.iv
│   ├── Test_Summary_Report.md         <-- Executive Testing Summary
│   ├── Updated_Test_Case_Document.md  <-- Deliverable 1.a & 1.b
│   ├── Test_Plan_Library_Reservation_Gateway_v2.0.docx
│   ├── Sprint_3_Report_and_Jira_Tracking.md <-- Deliverable 3.a & 3.b
│   ├── coverage_html/                 <-- Interactive HTML code coverage
│   └── coverage.xml                   <-- Machine-readable Cobertura XML
├── src/
│   ├── __init__.py
│   ├── app.py                         <-- Flask REST Gateway & UI router
│   ├── admin.py                       <-- Librarian Admin & RBAC
│   ├── audit.py                       <-- Immutable audit logging (1 yr)
│   ├── auth.py                        <-- Campus SSO & lockout (LRG-F-010)
│   ├── catalog_search.py              <-- Catalog queries & pagination
│   ├── database.py                    <-- SQLite relational schema & seeds
│   ├── fine_manager.py                <-- UC-04: Overdue Fine Settlement
│   ├── notification.py                <-- Hold-ready email & retry queue
│   ├── reservation_manager.py         <-- Hold placement & 72h auto-expire
│   ├── security.py                    <-- Rate limiting (60/min) & XSS filter
│   ├── templates/                     <-- Accessible HTML5 templates
│   └── static/                        <-- WCAG 2.1 AA responsive CSS/JS
├── tests/
│   ├── conftest.py                    <-- Pytest fixtures & in-memory DB
│   ├── test_admin.py                  <-- TC-ADM tests
│   ├── test_app_routes.py             <-- Web views & API route tests
│   ├── test_auth.py                   <-- TC-AUTH tests
│   ├── test_catalog_search.py         <-- TC-SRCH tests
│   ├── test_coverage_boost.py         <-- Helper & edge case tests
│   ├── test_fine_manager.py           <-- TC-FINE tests (UC-04)
│   ├── test_notification.py           <-- TC-NOTF tests
│   ├── test_reservation_manager.py    <-- TC-HOLD tests
│   ├── test_security_audit.py         <-- TC-SEC & TC-AUD tests
│   └── test_system_e2e.py             <-- End-to-end integration flows
├── scripts/
│   ├── seed_data.py                   <-- Generates large scale test sets
│   └── run_all_tests.py               <-- Automated test execution script
├── Lab-01-Requirements-and-UML/       <-- Lab 1 individual contributions
├── Lab-02-Jira-Agile/                 <-- Lab 2 individual contributions
├── Lab-03-Component-Architecture/     <-- Lab 3 individual contributions
├── Lab-04-SRS-SAD-STP/                <-- Lab 4 core specifications
├── pytest.ini
├── requirements.txt
└── README.md
```

---
*© 2026 PES University — Software Engineering Mini-Project Team Collaboration*
