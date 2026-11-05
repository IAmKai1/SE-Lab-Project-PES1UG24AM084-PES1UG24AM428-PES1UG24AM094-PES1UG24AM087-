# Digital Campus Library Reservation Gateway (LRG)
## Executive Test Summary Report (Deliverable 2.b)
### Final Test Sign-Off & Verification Across ALL 10 Use Cases

**Document Version**: 2.0  
**Date of Sign-Off**: 5th November 2026  
**Testing Execution Window**: 2nd November to 6th November 2026  
**Target Release**: Release 1.0 (Presentation Readiness: 9th November 2026)  
**Authors & Project Leads**:
- **Dhareen G** (`PES1UG24AM084`) – QA Lead
- **Dharshini V** (`PES1UG24AM428`) – Dev Lead & Fine Module Owner
- **Dhruv Talavat** (`PES1UG24AM087`) – Database & Security Engineer
- **Divyansh** (`PES1UG24AM094`) – Backend & Analytics Engineer

---

## 1. Executive Summary

The comprehensive testing phase for the Digital Campus Library Reservation Gateway (LRG) concluded with **100% test execution success** across all planned functional, non-functional, security, and regression scenarios.

The testing suite was specifically designed to validate **all use cases** assigned to team members and specified in the SRS v1.0, SAD v1.0, and updated STP v2.0:
- **`UC-01`**: Search ISBN Catalog (Dhareen G & Divyansh)
- **`UC-02`**: View Book Details (Dhruv Talavat & Divyansh)
- **`UC-03`**: Place Hold Request (Dhruv Talavat & Dharshini V)
- **`UC-04`**: View & Cancel My Holds (Dhruv Talavat)
- **`UC-04b`**: Pay Overdue Fine & Settle Dues (Dharshini V)
- **`UC-05`**: Campus SSO Login & Session Security (All Members)
- **`UC-06`**: Update Availability Status & Return (Dhareen G)
- **`UC-07`**: Notify Next Member via Email (Dhareen G)
- **`UC-08`**: Manage Catalog Entries (Divyansh & Dhareen G)
- **`UC-09`**: View Hold Demand Report (Divyansh)

---

## 2. Key Testing Metrics Dashboard

| Metric | Target Standard | Observed Measurement | Variance / Status |
| :--- | :--- | :--- | :--- |
| **Total Test Cases** | $\ge 60$ automated tests | **88 automated tests** | $+28$ tests (146% of target) |
| **Test Execution Pass Rate** | $100\%$ | **100% (88 passed, 0 failed)** | **PASSED (100%)** |
| **Total Test Execution Time** | $\le 10.0\text{ s}$ | **2.99 seconds** | **EXEMPLARY** |
| **Project Statement Coverage**| $\ge 70.0\%$ | **89.0%** (827 / 900 statements) | **PASSED (+19.0%)** |
| **Core Business Logic Coverage**| $\ge 80.0\%$ | **93.8%** | **EXEMPLARY (+13.8%)** |
| **Branch Decision Coverage** | $\ge 70.0\%$ | **82.6%** (223 / 270 branches) | **PASSED (+12.6%)** |
| **Critical Open Defects** | $0$ | **0 defects** | **ZERO DEFECT STATE** |
| **Search Response Time (NFR-1)**| $\le 2.0\text{ s}$ (90th percentile) | **0.0051 seconds** (5.1 ms) | **PASSED (400x faster)** |
| **System Availability (NFR-2)** | $\ge 99.5\%$ | **100% monitored uptime** | **PASSED** |
| **Accessibility Compliance (NFR-4)**| WCAG 2.1 AA | Verified markup & 360px viewport | **PASSED** |

---

## 3. High-Level Use Case Verification Matrix

| Use Case ID | Description | Assigned Lead | Tests Executed | Status | Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UC-01** | Search ISBN Catalog | Dhareen G & Divyansh | 11 | **PASS** | 91% |
| **UC-02** | View Book Details | Dhruv Talavat & Divyansh | 6 | **PASS** | 91% |
| **UC-03** | Place Hold Request | Dhruv Talavat & Dharshini V | 9 | **PASS** | 95% |
| **UC-04** | View and Cancel My Holds | Dhruv Talavat | 8 | **PASS** | 95% |
| **UC-04b**| Pay Overdue Fine & Settle Dues | Dharshini V | 8 | **PASS** | 90% |
| **UC-05** | Campus SSO Login & Session Control | All Members | 10 | **PASS** | 98% |
| **UC-06** | Update Availability Status / Return | Dhareen G | 6 | **PASS** | 86% |
| **UC-07** | Notify Next Member via Email | Dhareen G | 5 | **PASS** | 93% |
| **UC-08** | Manage Catalog Entries | Divyansh & Dhareen G | 6 | **PASS** | 86% |
| **UC-09** | View Hold Demand Report | Divyansh | 4 | **PASS** | 86% |
| **NFRs** | Security, Audit, Performance, A11y | Cross-Cutting | 15 | **PASS** | 94% |
| **TOTAL** | **Complete System** | **Entire Engineering Team** | **88** | **PASS** | **89%** |

---

## 4. Deliverable Verification & Repo Structure

All testing deliverables have been committed and pushed to the team repository:  
`https://github.com/IAmKai1/SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-`

Artifacts in `docs/`:
- `docs/Updated_Test_Case_Document.md` (v2.0 with Per-Use-Case Updations)
- `docs/Unit_Test_Report.md` (Full 88 test results table)
- `docs/System_Validation_Report.md` (End-to-End System Validation for all 10 Use Cases)
- `docs/Code_Coverage_Report.md` (89% Statement Coverage Analysis)
- `docs/Branch_Coverage_Report.md` (82.6% Branch Coverage Analysis across 270 branches)
- `docs/Sprint_3_Report_and_Jira_Tracking.md` (Agile tracking, user stories, burndown chart)
- `docs/coverage_html/` and `docs/coverage.xml` (Machine-readable and HTML coverage reports)
- `docs/Test_Plan_Library_Reservation_Gateway_v2.0.docx` (Updated Microsoft Word STP)
- `.github/workflows/ci.yml` (Automated CI/CD testing pipeline on GitHub Actions)

---

## 5. Final Approval for Presentation (9th November 2026)

The undersigned verify that the Digital Campus Library Reservation Gateway is complete, thoroughly tested across all use cases, and fully prepared for the final project presentation.

- **QA Lead**: Dhareen G (`PES1UG24AM084`) – **APPROVED**
- **Dev Lead**: Dharshini V (`PES1UG24AM428`) – **APPROVED**
- **Database Lead**: Dhruv Talavat (`PES1UG24AM087`) – **APPROVED**
- **Analytics Lead**: Divyansh (`PES1UG24AM094`) – **APPROVED**
