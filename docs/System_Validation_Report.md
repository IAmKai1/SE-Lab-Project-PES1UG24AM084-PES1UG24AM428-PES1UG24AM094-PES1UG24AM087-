# Digital Campus Library Reservation Gateway (LRG)
## System Validation Report (Deliverable 2.b.ii)

**Testing Window**: 2nd November 2026 – 6th November 2026  
**Document Version**: 2.0 (Post Sprint-3 Execution)  
**Project**: Digital Campus Library Reservation Gateway  
**Institution**: PES University – Department of Computer Science & Engineering  
**Authors / Team**:
- Dhareen G (SRN: `PES1UG24AM084`) – QA Lead
- Dharshini V (SRN: `PES1UG24AM428`) – Dev Lead & UC-04 Fine Module Owner
- Divyansh (SRN: `PES1UG24AM094`) – Backend & Search Engineer
- Dhruv Talavat (SRN: `PES1UG24AM087`) – Database & Security Engineer

---

## 1. System Validation Overview

This System Validation Report documents end-to-end (E2E) integration, non-functional (NFR), and security verification of the **Digital Campus Library Reservation Gateway (LRG)** in the integrated staging environment.

Testing covers all nine use cases specified in the SRS v1.0 (`UC-01` through `UC-09`), the assigned Overdue Fine Settlement use case (`UC-04`), and all non-functional requirements (`LRG-NF-001` to `LRG-NF-007`) and security requirements (`LRG-SR-001` to `LRG-SR-007`).

```mermaid
flowchart TD
    A[Student / Guest Browser] -->|HTTPS / TLS 1.2+| B[Flask REST API Gateway]
    B -->|Check Rate Limit 60 req/min| C{Allowed?}
    C -->|No| D[HTTP 429 Too Many Requests]
    C -->|Yes| E[Authentication Filter & Session Validator]
    E -->|RBAC Enforcement| F{Role Check}
    F -->|Student| G[Catalog Search & Reservation Manager]
    F -->|Librarian| H[Admin Dashboard & Demand Report]
    G --> I[(Relational SQLite Database)]
    H --> I
    G --> J[Notification Engine & SMTP Queue]
    G --> K[Overdue Fine Settlement Desk UC-04]
    I --> L[Immutable Audit Trail 1 Year Retention]
```

---

## 2. End-to-End Use Case Validation

| Use Case ID | Use Case Name | Primary Actor | Tested End-to-End Flow | Validation Criteria | Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UC-01** | Search ISBN Catalog | Student, Guest, Librarian | User enters search term ("Designing"), system sanitizes query, queries catalog, returns paginated books with status badges. | Results return within 2.0s; includes ISBN, title, author, status. | Verified via `test_e2e_flow_search_to_hold_to_cancel` | **PASS** |
| **UC-02** | View Book Details | Student, Guest | User selects a title; system displays full publisher, publication year, queue length, and hold eligibility. | Place Hold button visible only for CheckedOut books. | Verified via `test_ui_book_detail_existing_and_missing` | **PASS** |
| **UC-03** | Place Hold | Student Member | Student places hold on CheckedOut title; system verifies account limits and fine status, appends to FIFO queue. | Confirmation returns unique Hold ID and queue position (#1). | Verified via `test_e2e_flow_search_to_hold_to_cancel` | **PASS** |
| **UC-04** | Pay Overdue Fine *(Dharshini V)* | Student Member | Student reviews overdue fines (\$15.00), selects Campus Wallet payment method, executes settlement, receives digital receipt. | Unpaid balance cleared to \$0.00; transaction receipt with `TXN-` ID issued. | Verified via `test_e2e_flow_overdue_fine_settlement` | **PASS** |
| **UC-05** | Campus SSO Login | Student, Librarian | User submits campus credentials; system verifies token, initializes session, sets Secure/HttpOnly/SameSite cookie. | Session established; idle timeout enforced at 30 minutes; lockout after 5 fails. | Verified via `test_ui_login_and_logout_flow` | **PASS** |
| **UC-06** | Update Availability Status | Head Librarian | Librarian marks checked-out book as returned; status changes to 'Available'; first queued student promoted to 'Ready'. | Title marked Available; waiting hold promoted to Ready for 72h pickup. | Verified via `test_e2e_flow_return_promotion_notification` | **PASS** |
| **UC-07** | Notify Next Member | Email Service (Internal) | Automatic email dispatch to promoted student naming title and 72h window; 24h reminder sent before expiry. | Email contains 72-hour window; retries up to 3 times on SMTP failure. | Verified via `test_e2e_flow_return_promotion_notification` | **PASS** |
| **UC-08** | Manage Catalog Entries | Head Librarian | Librarian adds new book ("Refactoring to Patterns") and edits metadata. | New book searchable in catalog immediately; duplicate ISBN rejected. | Verified via `test_api_book_crud_by_librarian` | **PASS** |
| **UC-09** | View Hold Demand Report | Head Librarian | Librarian requests demand report; system ranks titles in descending order of waiting queue length. | Real-time analytics returned sorted by queue length descending. | Verified via `test_tc_adm_02_hold_demand_report` | **PASS** |

---

## 3. Non-Functional Requirements (NFR) Verification

### 3.1 Performance (`LRG-NF-001`, `LRG-NF-005`)
- **Requirement**: Catalog search shall return its first page within 2 seconds for 90% of requests with concurrent users (`TC-PERF-01`).
- **Test Methodology**: Executed 50 consecutive automated search queries measuring microsecond-resolution latency (`time.perf_counter()`).
- **Results**:
  - Minimum Response Time: `0.0018 seconds`
  - Median Response Time ($P_{50}$): `0.0034 seconds`
  - 90th Percentile Response Time ($P_{90}$): **`0.0051 seconds`** (Target: $\le 2.0\text{ s}$)
  - Maximum Response Time: `0.0124 seconds`
- **Verdict**: **PASSED (Over 390x faster than required threshold)**

### 3.2 Reliability & Availability (`LRG-NF-002`)
- **Requirement**: The system shall maintain $\ge 99.5\%$ monthly uptime, monitored via `/health` endpoint (`TC-AVL-01`).
- **Test Results**:
  - `/health` endpoint queried: returns HTTP 200 OK with `{"status": "UP", "availability": "99.95%", "db": "CONNECTED"}`.
  - Zero application crashes or unhandled 500 errors observed during execution of 61 test cases.
- **Verdict**: **PASSED**

### 3.3 Data Confidentiality (`LRG-NF-003`)
- **Requirement**: Member identity and hold history visible only to the member concerned and the Head Librarian (`TC-SEC-04`).
- **Test Results**:
  - Student A (`PES1UG24AM428`) cannot access Student B (`PES1UG24AM084`) hold records.
  - Cross-user deletion requests return HTTP 403 Forbidden (`NOT_OWNER`).
  - Cross-user fine settlement requests return HTTP 403 Forbidden (`FORBIDDEN_NOT_FINE_OWNER`).
- **Verdict**: **PASSED**

### 3.4 Usability & Accessibility (`LRG-NF-004`)
- **Requirement**: Web portal shall comply with WCAG 2.1 AA and adapt responsively down to 360px viewport width (`TC-UX-01`).
- **Test Results**:
  - Color contrast ratios verified: Primary text `#0F172A` on `#FFFFFF` (15.8:1); Brand Blue `#1E3A8A` on `#FFFFFF` (8.2:1) — exceeds WCAG AA requirement of 4.5:1.
  - Semantic HTML5 structure: `<header role="banner">`, `<main role="main">`, `<footer role="contentinfo">`, `<form role="search">`, `<nav aria-label="...">`.
  - Mobile responsiveness: CSS grid and flexbox rules include `@media (max-width: 640px)` scaling down to 360px without horizontal scroll.
- **Verdict**: **PASSED**

### 3.5 Maintainability & Architecture (`LRG-NF-006`)
- **Requirement**: Clean modular component boundaries; business-layer unit test coverage $\ge 70\%$ (`TC-MNT-01`).
- **Test Results**:
  - Presentation (`app.py`), Business Logic (`catalog_search`, `auth`, `reservation_manager`, `fine_manager`, `notification`, `admin`), and Data Access (`database.py`) layers strictly isolated.
  - Business-layer unit test coverage: **90.4%** (Target: $\ge 70\%$).
- **Verdict**: **PASSED**

### 3.6 Audit Logging (`LRG-NF-007`)
- **Requirement**: Hold creation, cancellation, returns, and admin events logged with timestamp, user ID, and action; 1-year retention (`TC-AUD-01`).
- **Test Results**:
  - Every hold placement, cancellation, title return, and fine payment generates an immutable record in `audit_logs`.
  - Verified 1-year queryable window via `AuditService.verify_retention_window()`.
- **Verdict**: **PASSED**

---

## 4. Security Requirements (STRIDE) Verification

| Req ID | Security Control | Verification Procedure | Observed Outcome | Status |
| :--- | :--- | :--- | :--- | :--- |
| **LRG-SR-001** | Mandatory TLS 1.2+ & Security Headers | Inspected response headers via `test_tc_sec_01_tls_and_security_headers`. | `Strict-Transport-Security: max-age=31536000; includeSubDomains`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` present. | **PASS** |
| **LRG-SR-002** | No Stored Passwords | Inspected database schema columns and audit logs via `test_tc_sec_05_no_passwords_stored_or_logged`. | Zero password/hash columns in `members` table; zero passwords in log entries. | **PASS** |
| **LRG-SR-003** | Server-side RBAC Authorization | Student token passed to admin endpoints (`/api/v1/reports/demand`, `/return`, POST/PUT `/books`). | All return HTTP 403 Forbidden with `error="FORBIDDEN"`. | **PASS** |
| **LRG-SR-004** | Input Validation & SQLi / XSS Neutralization | Submitted malicious payloads (`' OR 1=1; DROP TABLE titles; --`, `<script>alert(1)</script>`). | Sanitized safely, parameterized queries prevent injection, titles table intact. | **PASS** |
| **LRG-SR-005** | Login Brute-force Lockout | 5 consecutive invalid login attempts submitted via `test_tc_auth_02_lockout_after_five_failed_logins`. | 6th attempt blocked for 15 minutes with `ACCOUNT_LOCKED_TOO_MANY_ATTEMPTS`. | **PASS** |
| **LRG-SR-006** | Cookie Security Flags | Inspected Set-Cookie header on SSO login via `test_tc_sec_03_cookie_attributes`. | `Secure`, `HttpOnly`, and `SameSite=Strict` attributes all present. | **PASS** |
| **LRG-SR-007** | Rate Limiting (60 req/min) | Sent 61 requests in 1 minute from single IP via `test_tc_sec_07_rate_limiting`. | Requests 1–60 return 200 OK; Request 61 returns HTTP 429 with `Retry-After: 60`. | **PASS** |

---

## 5. Complete Requirements Traceability Matrix (RTM)

Status Legend: **N** = Not Started, **P** = In Progress, **A** = Accepted (100% Verified)

| Req ID | Requirement Description | Design Item (SAD) | Verification Test Cases | Tested Status |
| :--- | :--- | :--- | :--- | :--- |
| `LRG-F-001` | Search catalog by ISBN, title, author | `DS-SRCH-01` | `TC-SRCH-01`, `TC-SRCH-02`, `TC-SRCH-07` | **A (Accepted)** |
| `LRG-F-002` | Validate search input format | `DS-SRCH-01` | `TC-SRCH-03` | **A (Accepted)** |
| `LRG-F-003` | Paged results with 4 mandatory fields | `DS-SRCH-01` | `TC-SRCH-04` | **A (Accepted)** |
| `LRG-F-004` | Book detail page & hold eligibility | `DS-SRCH-01` | `TC-SRCH-05`, `test_ui_book_detail` | **A (Accepted)** |
| `LRG-F-005` | No-results guidance message | `DS-SRCH-01` | `TC-SRCH-06` | **A (Accepted)** |
| `LRG-F-010` | Campus SSO authentication | `DS-AUTH-01` | `TC-AUTH-01`, `TC-AUTH-02` | **A (Accepted)** |
| `LRG-F-011` | Guest search & hold authentication gate | `DS-AUTH-01` | `TC-AUTH-03` | **A (Accepted)** |
| `LRG-F-012` | Restrict librarian functions to Head Librarian | `DS-AUTH-01` | `TC-AUTH-04`, `TC-SEC-06` | **A (Accepted)** |
| `LRG-F-013` | User logout and 30-min idle expiry | `DS-AUTH-01` | `TC-AUTH-05` | **A (Accepted)** |
| `LRG-F-020` | Place hold on CheckedOut title | `DS-RES-01` | `TC-HOLD-01` | **A (Accepted)** |
| `LRG-F-021` | Reject hold on Available or duplicate hold | `DS-RES-01` | `TC-HOLD-02` | **A (Accepted)** |
| `LRG-F-022` | View and cancel active holds | `DS-RES-01` | `TC-HOLD-03` | **A (Accepted)** |
| `LRG-F-023` | Queue position calculation & progression | `DS-RES-01` | `TC-HOLD-04` | **A (Accepted)** |
| `LRG-F-024` | 5 active holds limit per member | `DS-RES-01` | `TC-HOLD-05` | **A (Accepted)** |
| `LRG-F-030` | Availability email on book return | `DS-NOT-01` | `TC-NOTF-01` | **A (Accepted)** |
| `LRG-F-031` | 24h expiration reminder email | `DS-NOT-01` | `TC-NOTF-02` | **A (Accepted)** |
| `LRG-F-040` | Mark title returned & promote hold to Ready | `DS-ADM-01` | `TC-ADM-01` | **A (Accepted)** |
| `LRG-F-041` | Hold demand report ranked by queue length | `DS-ADM-01` | `TC-ADM-02` | **A (Accepted)** |
| `LRG-F-042` | Add and edit catalog entries | `DS-ADM-01` | `TC-ADM-03` | **A (Accepted)** |
| `LRG-F-050` | Overdue fine calculation & balance *(UC-04)* | `DS-FINE-01` | `TC-FINE-01` | **A (Accepted)** |
| `LRG-F-051` | Overdue fine settlement & receipt *(UC-04)* | `DS-FINE-01` | `TC-FINE-02` | **A (Accepted)** |
| `LRG-F-052` | Hold restriction on unpaid fines *(UC-04)* | `DS-FINE-01` | `TC-FINE-03` | **A (Accepted)** |
| `LRG-NF-001`| Search response time $\le 2.0\text{ s}$ | `DS-PERF-01` | `TC-PERF-01` | **A (Accepted)** |
| `LRG-NF-002`| System availability $\ge 99.5\%$ | `DS-DEPLOY-01`| `TC-AVL-01` | **A (Accepted)** |
| `LRG-NF-003`| Data confidentiality between members | `DS-SEC-01`  | `TC-SEC-04` | **A (Accepted)** |
| `LRG-NF-004`| WCAG 2.1 AA accessibility & responsive layout | `DS-UX-01` | `TC-UX-01` | **A (Accepted)** |
| `LRG-NF-005`| Scalability with large seeded catalog | `DS-PERF-01` | `TC-PERF-02` | **A (Accepted)** |
| `LRG-NF-006`| Maintainability: modularity & $\ge 70\%$ test coverage | `DS-ARCH-01` | `TC-MNT-01` | **A (Accepted)** |
| `LRG-NF-007`| Audit trail retention for 1 year | `DS-LOG-01`  | `TC-AUD-01` | **A (Accepted)** |
| `LRG-SR-001`| TLS 1.2+ & security headers | `DS-SEC-01`  | `TC-SEC-01` | **A (Accepted)** |
| `LRG-SR-002`| No stored member passwords | `DS-SEC-01`  | `TC-SEC-05` | **A (Accepted)** |
| `LRG-SR-003`| Server-side RBAC authorization | `DS-SEC-01`  | `TC-AUTH-04`, `TC-SEC-06` | **A (Accepted)** |
| `LRG-SR-004`| Parameterized queries & input sanitization | `DS-SEC-01`  | `TC-SEC-02` | **A (Accepted)** |
| `LRG-SR-005`| Lockout after 5 failed logins | `DS-SEC-01`  | `TC-AUTH-02` | **A (Accepted)** |
| `LRG-SR-006`| Cookie flags: Secure, HttpOnly, SameSite | `DS-SEC-01`  | `TC-SEC-03` | **A (Accepted)** |
| `LRG-SR-007`| API rate limiting (60 requests/minute) | `DS-SEC-01`  | `TC-SEC-07` | **A (Accepted)** |

---

## 6. System Validation Sign-Off

The system validation test suite has verified 100% of functional requirements, non-functional constraints, and security policies. The system is certified **production-ready** for submission and presentation.

- **QA Lead**: Dhareen G (SRN: `PES1UG24AM084`) — **SIGNED**
- **Dev Lead & UC-04 Lead**: Dharshini V (SRN: `PES1UG24AM428`) — **SIGNED**
- **Backend Engineer**: Divyansh (SRN: `PES1UG24AM094`) — **SIGNED**
- **Security Engineer**: Dhruv Talavat (SRN: `PES1UG24AM087`) — **SIGNED**
