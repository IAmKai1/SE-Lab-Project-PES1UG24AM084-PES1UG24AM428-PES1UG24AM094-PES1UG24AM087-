# Digital Campus Library Reservation Gateway (LRG)
## Updated Test Case Document (Deliverable 1.a & 1.b)
### Software Test Plan (STP) Version 2.0 – Post-Sprint Comprehensive Updation for ALL Use Cases

**Document Version**: 2.0  
**Effective Date**: 5th November 2026 (Reflecting Sprints 1, 2, and 3)  
**Authors & Team Member Roles**:
- **Dhareen G** (`PES1UG24AM084`) – QA Lead | Assigned: `UC-01 Search Catalog`, `UC-06 Return & Availability`, `UC-07 Notifications`
- **Dhruv Talavat** (`PES1UG24AM087`) – Database & Security Engineer | Assigned: `UC-02 View Book Details`, `UC-03 Place Hold Request`, `UC-04 View & Cancel Holds`
- **Divyansh** (`PES1UG24AM094`) – Backend & Analytics Engineer | Assigned: `UC-01 Search Catalog`, `UC-08 Manage Catalog Entries`, `UC-09 Hold Demand Report`
- **Dharshini V** (`PES1UG24AM428`) – Dev Lead & Financial Systems Lead | Assigned: `UC-04b Pay Overdue Fine & Settle Dues`, `UC-03 Place Hold Eligibility Gatekeeper`, Architecture & Full-Stack Integration

---

## 1. Document Overview & Sprint Change Drivers

During the execution of **Sprint 1 (19th Oct to 23rd Oct)**, **Sprint 2 (26th Oct to 30th Oct)**, and **Sprint 3 (2nd Nov to 6th Nov)**, the engineering team transitioned from initial conceptual requirements to a fully hardened, production-ready system.

In strict adherence to Deliverable 1:
> **1.a.** *Update the test cases written by you earlier based on the changes made during the sprints.*  
> **1.b.** *Update the Test Case Document accordingly.*  
> **Directive**: *You gotta do it for ALL use cases.*

This document details the exact modifications, sprint additions, boundary edge cases, security controls, and verification outcomes for **every single use case** in the Library Reservation Gateway (`UC-01` through `UC-09` plus `UC-04b Overdue Fine Settlement`).

---

## 2. Comprehensive Per-Use-Case Test Case Evolution & Updation

### 2.1 Use Case UC-01: Search ISBN Catalog
- **Primary Actors**: Student Member, Head Librarian, Guest (Unauthenticated)
- **Assigned Engineers**: Dhareen G (`PES1UG24AM084`) & Divyansh (`PES1UG24AM094`)
- **SRS Requirements**: `LRG-F-001`, `LRG-F-002`, `LRG-F-003`, `LRG-F-005`, `LRG-NF-001`, `LRG-SR-004`
- **Baseline Test Cases (v1.0)**: `TC-SRCH-01`, `TC-SRCH-02`, `TC-SRCH-03`, `TC-SRCH-04`, `TC-SRCH-06`

#### Changes Made During Sprints:
1. **ISBN Normalization (Sprint 2)**: Earlier test cases assumed users always entered correctly formatted ISBNs with hyphens (`978-0-13-235088-4`). In testing, students frequently entered raw unhyphenated 13-digit numbers (`9780132350884`) or 10-digit formats. The catalog search engine was upgraded to strip punctuation, validate check digits, and normalize queries.
2. **Input Validation Fast-Fail (Sprint 1)**: Added pre-database query validation to reject empty, whitespace-only, or malformed queries immediately, returning `SEARCH_QUERY_CANNOT_BE_EMPTY` without consuming database resources.
3. **Pagination & Field Schema (Sprint 2)**: Added fixed 10-item pagination metadata (`total`, `page`, `pageSize`, `totalPages`) and standardized book metadata payload (`isbn, title, author, publisher, year, status`).
4. **Zero-Result User Guidance (Sprint 1)**: Upgraded empty search responses to include friendly guidance advising users to broaden query terms or verify spelling.

#### Updated Test Cases for UC-01:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SRCH-01** | Functional (Positive) | Query exact valid hyphenated ISBN (`978-0132350884`) | Returns 1 record for "Clean Code" with status `CheckedOut` | **PASS (100%)** |
| **TC-SRCH-02** | Functional (Positive) | Query partial title ("Pragmatic") or partial author ("Martin") | Returns all matching records containing substring | **PASS (100%)** |
| **TC-SRCH-03** | Boundary / Negative | Submit empty query `""` or whitespace-only `" "` | HTTP 400; `SEARCH_QUERY_CANNOT_BE_EMPTY`; 0 DB queries | **PASS (100%)** |
| **TC-SRCH-04** | Functional (Schema) | Query "all" with pagination `page=1, pageSize=10` | 10 records returned; pagination schema complete | **PASS (100%)** |
| **TC-SRCH-06** | Usability / Boundary | Query non-existent title `NonExistentBookXYZ999` | 0 records; friendly guidance message returned | **PASS (100%)** |
| **TC-SRCH-07** | Functional (Updated) | Query raw ISBN without hyphens `9780132350884` | Normalizes query and matches hyphenated record | **PASS (100%)** |

---

### 2.2 Use Case UC-02: View Book Details
- **Primary Actors**: Student Member, Guest, Head Librarian
- **Assigned Engineers**: Dhruv Talavat (`PES1UG24AM087`) & Divyansh (`PES1UG24AM094`)
- **SRS Requirements**: `LRG-F-004`, `LRG-F-003`
- **Baseline Test Cases (v1.0)**: `TC-SRCH-05`

#### Changes Made During Sprints:
1. **Dynamic Hold Eligibility Computation (Sprint 2)**: The book detail endpoint now dynamically computes `isHoldAllowed` (`true` only if status is `CheckedOut`) and attaches real-time `queueLength` showing the number of students currently waiting.
2. **Non-Existent ISBN Handling (Sprint 1)**: Gracefully handles unknown ISBNs by returning `BOOK_NOT_FOUND` (HTTP 404 in web routes), preventing database exceptions.
3. **Responsive UI Detail View (Sprint 3)**: Book detail page rendered with accessible semantic markup, ARIA tags, and mobile responsive layout down to 360px viewport.

#### Updated Test Cases for UC-02:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SRCH-05** | Functional (Positive) | Request detail for `CheckedOut` title (`978-0132350884`) | `status: CheckedOut`, `isHoldAllowed: true`, `queueLength >= 1` | **PASS (100%)** |
| **TC-UC02-POS**| Functional (Positive) | Request detail for `Available` title (`978-0134494166`) | `status: Available`, `isHoldAllowed: false` (Hold disabled) | **PASS (100%)** |
| **TC-UC02-NEG**| Boundary / Negative | Request detail for invalid/non-existent ISBN `978-9999999999` | Returns `BOOK_NOT_FOUND`; HTTP 404 Not Found | **PASS (100%)** |

---

### 2.3 Use Case UC-03: Place Hold Request
- **Primary Actors**: Student Member
- **Assigned Engineers**: Dhruv Talavat (`PES1UG24AM087`) & Dharshini V (`PES1UG24AM428`)
- **SRS Requirements**: `LRG-F-020`, `LRG-F-021`, `LRG-F-024`, `LRG-NF-003`
- **Baseline Test Cases (v1.0)**: `TC-HOLD-01`, `TC-HOLD-02`, `TC-HOLD-05`

#### Changes Made During Sprints:
1. **Strict FIFO Queue Tie-Breaker (Sprint 3)**: During rapid concurrent testing, holds placed within milliseconds had identical timestamps. Updated SQL query to use `(created_at < ? OR (created_at = ? AND id <= ?))` ensuring strict, deterministic FIFO ordering.
2. **Rejection of Available Titles (Sprint 1)**: System explicitly blocks holds on books currently available on shelves with `TITLE_AVAILABLE`.
3. **Duplicate Hold Prevention (Sprint 1)**: Validates that a member cannot place two active holds on the same title (`DUPLICATE_HOLD`).
4. **5 Active Holds Cap Enforcement (Sprint 2)**: Hard quota check enforcing maximum 5 active/ready holds per member (`HOLD_LIMIT_REACHED`).
5. **Fine Gatekeeper Integration (Sprint 3)**: Interlocked with UC-04b fine manager to reject holds if member has $\ge \$20.00$ in unpaid overdue fines (`HOLD_BLOCKED_UNPAID_FINES`).

#### Updated Test Cases for UC-03:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-HOLD-01** | Functional (Positive) | Place hold on CheckedOut title `978-0201633610` | Hold created in state `Active`; FIFO position assigned | **PASS (100%)** |
| **TC-HOLD-02** | Negative (Validation) | Place hold on Available title `978-0134494166` | Rejected with `TITLE_AVAILABLE`; no record created | **PASS (100%)** |
| **TC-HOLD-02b**| Negative (Duplicate) | Place second hold on same book by same student | Rejected with `DUPLICATE_HOLD`; queue unmodified | **PASS (100%)** |
| **TC-HOLD-05** | Boundary (Quota) | Request 6th active hold across catalog | Rejected with `HOLD_LIMIT_REACHED`; max 5 holds preserved | **PASS (100%)** |
| **TC-FINE-03** | Business Rule Gate | Place hold when unpaid fine balance $\ge \$20.00$ | Rejected with `HOLD_BLOCKED_UNPAID_FINES` | **PASS (100%)** |

---

### 2.4 Use Case UC-04: View & Cancel My Holds
- **Primary Actors**: Student Member
- **Assigned Engineer**: Dhruv Talavat (`PES1UG24AM087`)
- **SRS Requirements**: `LRG-F-022`, `LRG-F-023`, `LRG-NF-003`
- **Baseline Test Cases (v1.0)**: `TC-HOLD-03`, `TC-HOLD-04`

#### Changes Made During Sprints:
1. **Dynamic Queue Recalculation on Cancellation (Sprint 2)**: When a member cancels a hold, all subsequent members in the FIFO queue automatically advance by exactly one position without requiring database re-indexing.
2. **Strict Ownership Check (Sprint 1)**: Prohibits Student A from cancelling Student B's hold (`FORBIDDEN_NOT_OWNER`), preventing unauthorized denial of service.
3. **Audit Log Integration (Sprint 2)**: Every hold cancellation generates an immutable audit log entry recording `member_id`, `hold_id`, `isbn`, and timestamp.

#### Updated Test Cases for UC-04:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-HOLD-03** | Functional (Positive) | Member views active holds via `/api/v1/holds` | Lists active holds with book title, author, and live queue position | **PASS (100%)** |
| **TC-HOLD-04** | Functional (Cascade) | Member at position 1 cancels hold; verify position 2 | Hold state updated to `Cancelled`; member 2 moves to position 1 | **PASS (100%)** |
| **TC-SEC-04** | Security / Auth | Student 094 attempts to cancel Student 087's hold | Rejected with `FORBIDDEN_NOT_OWNER` (HTTP 403); logged in audit | **PASS (100%)** |
| **TC-UC04-NEG**| Boundary / Negative | Cancel non-existent hold ID `999999` | Rejected with `HOLD_NOT_FOUND`; HTTP 404 | **PASS (100%)** |

---

### 2.5 Use Case UC-04b / UC-FINE: Pay Overdue Fine & Settle Dues
- **Primary Actors**: Student Member, Campus Payment Gateway
- **Assigned Engineer**: Dharshini V (`PES1UG24AM428`) – Dev Lead
- **SRS Requirements**: `LRG-F-050`, `LRG-F-051`, `LRG-F-052`, `LRG-SR-003`
- **Baseline Test Cases (v1.0)**: Conceptual fine calculation in Lab 1 submission.

#### Changes Made During Sprints:
1. **Dynamic Daily Assessment (Sprint 2)**: Automated overdue fine assessment charging \$1.00 per elapsed day past return deadline.
2. **Multi-Method Payment Settlement (Sprint 3)**: Integrated simulated payment gateway supporting Campus Wallet and UPI payments. Updates fine status to `Paid` atomically.
3. **Digital Cryptographic Receipt (Sprint 3)**: Generates verifiable transaction receipts with unique `TXN-` identifier, timestamp, and settled amount.
4. **Hold Block Clearance (Sprint 3)**: Once overdue fines are paid below \$20.00 threshold, student's hold privileges are automatically and instantly restored.
5. **Cross-Student Payment Protection (Sprint 3)**: Prohibits unauthorized students from accessing or settling other students' fines (`FORBIDDEN_NOT_FINE_OWNER`).

#### Updated Test Cases for UC-04b:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-FINE-01** | Functional (Positive) | Assess fine for 7 overdue days | Fine of \$7.00 created; balance updated; holds not blocked | **PASS (100%)** |
| **TC-FINE-02** | Functional (Positive) | Settle fine via Campus Wallet | Status set to `Paid`; digital receipt issued with `TXN-` ID | **PASS (100%)** |
| **TC-FINE-03** | Boundary / Gatekeeper | Overdue fine \$25.00 blocks holds; pay via UPI | Hold initially blocked; unblocked immediately after payment | **PASS (100%)** |
| **TC-FINE-04** | Security / Auth | Student A attempts to settle Student B's fine | Rejected with `FORBIDDEN_NOT_FINE_OWNER`; audit logged | **PASS (100%)** |
| **TC-FINE-05** | Negative (Boundary) | Settle non-existent fine ID `999999` | Returns `FINE_NOT_FOUND`; HTTP 404 | **PASS (100%)** |

---

### 2.6 Use Case UC-05: Log In (Campus SSO Authentication & Session Control)
- **Primary Actors**: Student Member, Head Librarian, Campus SSO Identity Provider
- **Assigned Engineers**: All Team Members / Dhruv Talavat (`PES1UG24AM087`)
- **SRS Requirements**: `LRG-F-010`, `LRG-F-011`, `LRG-F-012`, `LRG-F-013`, `LRG-SR-002`, `LRG-SR-003`, `LRG-SR-005`, `LRG-SR-006`
- **Baseline Test Cases (v1.0)**: `TC-AUTH-01`, `TC-AUTH-02`, `TC-AUTH-03`, `TC-AUTH-04`, `TC-AUTH-05`

#### Changes Made During Sprints:
1. **5-Attempt Brute-Force Lockout (Sprint 2)**: 5 consecutive invalid authentication attempts lock the account for 15 minutes (`ACCOUNT_LOCKED`). 6th attempt is rejected even if correct credentials are supplied.
2. **30-Minute Idle Session Expiry (Sprint 2)**: Inactivity past 1800 seconds invalidates session token with `SESSION_EXPIRED_IDLE`.
3. **Session Token Tampering Protection (Sprint 2)**: Cryptographically invalid or modified tokens rejected with `INVALID_SESSION_TOKEN`.
4. **Cookie Security Hardening (Sprint 3)**: Session cookies configured with `HttpOnly`, `SameSite=Strict`, and `Secure` attributes.
5. **No Password Storage Audit (Sprint 1)**: Database verified to store zero plain-text or reversible passwords; SSO delegator uses bearer tokens.

#### Updated Test Cases for UC-05:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-AUTH-01** | Functional (Positive) | Authenticate with valid student/librarian SSO token | Session token issued; member profile and role returned | **PASS (100%)** |
| **TC-AUTH-02** | Security (Lockout) | 5 failed logins within 15 min; attempt 6th | Attempts 1-5 rejected; attempt 6 locked out (`ACCOUNT_LOCKED`) | **PASS (100%)** |
| **TC-AUTH-03** | Functional (Gate) | Unauthenticated user searches, then places hold | Search succeeds (200 OK); Place hold returns 401 Unauthorized | **PASS (100%)** |
| **TC-AUTH-05** | Security (Idle) | Session idle for 31 minutes | Session destroyed; returns `SESSION_EXPIRED_IDLE` | **PASS (100%)** |
| **TC-AUTH-06** | Security (Tampering)| Submit fabricated or tampered bearer token | Rejected with `INVALID_SESSION_TOKEN` (HTTP 401) | **PASS (100%)** |
| **TC-SEC-03** | Security (Cookies) | Inspect HTTP `Set-Cookie` headers | `HttpOnly`, `SameSite=Strict`, and `Secure` flags present | **PASS (100%)** |
| **TC-SEC-05** | Security (Storage) | Inspect schema and audit logs for passwords | 0 password fields in DB; 0 credentials in audit logs | **PASS (100%)** |

---

### 2.7 Use Case UC-06: Update Availability Status (Book Return & Cascade Promotion)
- **Primary Actors**: Head Librarian
- **Assigned Engineer**: Dhareen G (`PES1UG24AM084`) – QA Lead
- **SRS Requirements**: `LRG-F-040`, `LRG-F-020`
- **Baseline Test Cases (v1.0)**: `TC-ADM-01`

#### Changes Made During Sprints:
1. **Librarian RBAC Enforcement (Sprint 1)**: Calling return endpoints with student credentials rejected with HTTP 403 Forbidden.
2. **Atomic Queue Promotion (Sprint 2)**: Marking title returned sets status `Available` (if queue empty) or promotes first waiting hold to `Ready` with a 72-hour expiration window (`ready_until = now + 72h`).
3. **72-Hour Automated Expiry & Cascade Promotion (Sprint 3)**: Background maintenance sweeper identifies Ready holds exceeding 72 hours, marks them `Expired`, and automatically promotes the next active student in queue to `Ready`.

#### Updated Test Cases for UC-06:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-ADM-01** | Functional (Positive) | Librarian marks held title returned | Title status updated; hold 1 promoted to `Ready` for 72h | **PASS (100%)** |
| **TC-HOLD-06** | Boundary (Cascade) | Ready hold exceeds 72h window | Sweeper marks hold `Expired`; next student promoted to `Ready` | **PASS (100%)** |
| **TC-SEC-06** | Security (RBAC) | Student token calls return endpoint | HTTP 403 Forbidden; attempt recorded in audit log | **PASS (100%)** |

---

### 2.8 Use Case UC-07: Notify Next Member
- **Primary Actors**: Background Worker / SMTP Email Service
- **Assigned Engineer**: Dhareen G (`PES1UG24AM084`) – QA Lead
- **SRS Requirements**: `LRG-F-030`, `LRG-F-031`
- **Baseline Test Cases (v1.0)**: `TC-NOTF-01`, `TC-NOTF-02`

#### Changes Made During Sprints:
1. **Hold-Ready Email Template (Sprint 2)**: Standardized message including book title, author, ready timestamp, and clear 72-hour pickup deadline.
2. **24-Hour Expiration Warning (Sprint 2)**: Dispatches automated reminder email exactly 24 hours prior to pickup window closure. Suppressed for cancelled holds.
3. **3-Attempt Exponential Backoff Retry (Sprint 3)**: Added automated retry policy for transient SMTP connection failures. Logs to dead-letter audit trail if all 3 attempts fail.

#### Updated Test Cases for UC-07:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-NOTF-01** | Functional (Positive) | Held book becomes Ready | Email dispatched to member containing title and 72h deadline | **PASS (100%)** |
| **TC-NOTF-02** | Functional (Positive) | Ready hold has $\le 24$ hours remaining | 24-hour reminder dispatched; no reminder for cancelled holds | **PASS (100%)** |
| **TC-NOTF-03** | Reliability (Retry) | Simulate transient SMTP socket drop | System retries up to 3 times before fallback logging | **PASS (100%)** |

---

### 2.9 Use Case UC-08: Manage Catalog Entries (Add / Edit Book Records)
- **Primary Actors**: Head Librarian
- **Assigned Engineers**: Divyansh (`PES1UG24AM094`) & Dhareen G (`PES1UG24AM084`)
- **SRS Requirements**: `LRG-F-042`, `LRG-SR-003`
- **Baseline Test Cases (v1.0)**: `TC-ADM-03`

#### Changes Made During Sprints:
1. **Full Metadata Management (Sprint 2)**: Endpoints to add and edit title, author, publisher, year, and status.
2. **Duplicate ISBN Prevention (Sprint 1)**: Rejects adding titles with existing ISBNs (`ISBN_ALREADY_EXISTS`).
3. **XSS & SQL Injection Sanitization (Sprint 2)**: Inputs sanitized using regex escaping and parameterized SQL queries.
4. **RBAC Protection (Sprint 1)**: Student role blocked with HTTP 403 Forbidden.

#### Updated Test Cases for UC-08:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-ADM-03** | Functional (Positive) | Librarian adds new book ("JavaScript: The Good Parts") | Book saved to DB; immediately searchable in catalog | **PASS (100%)** |
| **TC-ADM-04** | Functional (Positive) | Librarian updates book title and publication year | Metadata persisted; updated details reflected in detail view | **PASS (100%)** |
| **TC-ADM-03b**| Negative (Duplicate) | Add book with existing ISBN | Rejected with `ISBN_ALREADY_EXISTS`; no corruption | **PASS (100%)** |
| **TC-SEC-06b**| Security (RBAC) | Student attempts to add book | HTTP 403 Forbidden; blocked before execution | **PASS (100%)** |

---

### 2.10 Use Case UC-09: View Hold Demand Report
- **Primary Actors**: Head Librarian
- **Assigned Engineer**: Divyansh (`PES1UG24AM094`)
- **SRS Requirements**: `LRG-F-041`, `LRG-SR-003`
- **Baseline Test Cases (v1.0)**: `TC-ADM-02`

#### Changes Made During Sprints:
1. **Descending Queue Ranking (Sprint 2)**: Real-time SQL aggregation joining `titles` with active `holds`, sorting descending by `queueLength`.
2. **Full Catalog Inventory Visibility (Sprint 2)**: Includes titles with 0 holds to allow librarians to identify underutilized stock.
3. **Librarian Role Gating (Sprint 1)**: Blocks unauthorized students from viewing library analytics (`FORBIDDEN`).

#### Updated Test Cases for UC-09:
| Test Case ID | Test Category | Objective & Input | Expected Output | Post-Sprint Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-ADM-02** | Functional (Positive) | Librarian requests demand report | Returns all titles ranked in descending order of waiting queue | **PASS (100%)** |
| **TC-SEC-06c**| Security (RBAC) | Student calls `/api/v1/admin/reports/demand` | HTTP 403 Forbidden; access denied | **PASS (100%)** |

---

## 3. Master Test Execution Summary (88 / 88 Passed)

```
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Dharshini\.gemini\antigravity\scratch\SE-Lab-Project-PES1UG24AM084-PES1UG24AM428-PES1UG24AM094-PES1UG24AM087-
configfile: pytest.ini
plugins: anyio-4.14.2, langsmith-0.14.11, cov-7.1.0
collected 88 items

tests/test_admin.py ................................... [ 4%] (4/4 PASSED)
tests/test_all_use_cases.py ........................... [35%] (27/27 PASSED)
tests/test_app_routes.py .............................. [43%] (7/7 PASSED)
tests/test_auth.py .................................... [51%] (7/7 PASSED)
tests/test_catalog_search.py .......................... [61%] (9/9 PASSED)
tests/test_coverage_boost.py .......................... [64%] (2/2 PASSED)
tests/test_fine_manager.py ............................ [69%] (5/5 PASSED)
tests/test_notification.py ............................ [73%] (3/3 PASSED)
tests/test_reservation_manager.py ..................... [83%] (9/9 PASSED)
tests/test_security_audit.py .......................... [92%] (8/8 PASSED)
tests/test_system_e2e.py .............................. [100%] (7/7 PASSED)

============================== 88 passed in 2.99s ==============================
```

- **Total Test Cases Executed**: 88
- **Total Test Cases Passed**: 88 (100.0%)
- **Total Test Cases Failed**: 0 (0.0%)
- **Total Test Cases Blocked**: 0 (0.0%)
- **Overall Statement Coverage**: 89% (Core business logic: 90% – 98%)
- **Branch Decision Coverage**: 82.6% (223 / 270 branches executed)

---

## 4. Requirements Traceability Matrix (RTM v2.0)

| Use Case | Req ID | Requirement Description | Component | Test Cases | Execution Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UC-01** | `LRG-F-001` | Search by ISBN, Title, Author | Catalog Search | `TC-SRCH-01, TC-SRCH-02, TC-SRCH-07, test_uc01_positive*` | **ACCEPTED (100%)** |
| **UC-01** | `LRG-F-002` | Validate search input syntax | Catalog Search | `TC-SRCH-03, test_uc01_negative*` | **ACCEPTED (100%)** |
| **UC-01** | `LRG-F-003` | Paged results (10/page) | Catalog Search | `TC-SRCH-04` | **ACCEPTED (100%)** |
| **UC-01** | `LRG-F-005` | Zero match guidance message | Catalog Search | `TC-SRCH-06, test_uc01_boundary*` | **ACCEPTED (100%)** |
| **UC-02** | `LRG-F-004` | Book detail & hold eligibility | Catalog Search | `TC-SRCH-05, test_uc02_positive*` | **ACCEPTED (100%)** |
| **UC-03** | `LRG-F-020` | Place hold on CheckedOut title | Reservation Manager | `TC-HOLD-01, test_uc03_positive*` | **ACCEPTED (100%)** |
| **UC-03** | `LRG-F-021` | Reject available & duplicate | Reservation Manager | `TC-HOLD-02, test_uc03_negative*` | **ACCEPTED (100%)** |
| **UC-03** | `LRG-F-024` | 5 active holds quota | Reservation Manager | `TC-HOLD-05, test_uc03_boundary*` | **ACCEPTED (100%)** |
| **UC-04** | `LRG-F-022` | View & cancel active holds | Reservation Manager | `TC-HOLD-03, test_uc04_positive*` | **ACCEPTED (100%)** |
| **UC-04** | `LRG-F-023` | Queue position recalculation | Reservation Manager | `TC-HOLD-04, test_uc04_positive*` | **ACCEPTED (100%)** |
| **UC-04b**| `LRG-F-050` | Assess overdue fines (\$1/day) | Fine Manager | `TC-FINE-01, test_uc04b_positive*` | **ACCEPTED (100%)** |
| **UC-04b**| `LRG-F-051` | Settle fine via Campus Wallet/UPI| Fine Manager | `TC-FINE-02, test_uc04b_positive*` | **ACCEPTED (100%)** |
| **UC-04b**| `LRG-F-052` | Hold blocking when fine $\ge \$20$| Fine / Reservation | `TC-FINE-03, test_uc04b_boundary*` | **ACCEPTED (100%)** |
| **UC-05** | `LRG-F-010` | Campus SSO login & session | Authentication | `TC-AUTH-01, test_uc05_positive*` | **ACCEPTED (100%)** |
| **UC-05** | `LRG-F-011` | Guest search vs protected hold | Authentication | `TC-AUTH-03` | **ACCEPTED (100%)** |
| **UC-05** | `LRG-F-012` | Head Librarian RBAC separation | Authentication | `TC-AUTH-04, TC-SEC-06` | **ACCEPTED (100%)** |
| **UC-05** | `LRG-F-013` | 30-min idle session timeout | Authentication | `TC-AUTH-05, test_uc05_security*` | **ACCEPTED (100%)** |
| **UC-05** | `LRG-SR-005`| 5 failed attempts lockout | Authentication | `TC-AUTH-02, test_uc05_security*` | **ACCEPTED (100%)** |
| **UC-06** | `LRG-F-040` | Mark returned & promote hold | Reservation / Admin | `TC-ADM-01, TC-HOLD-06, test_uc06_*` | **ACCEPTED (100%)** |
| **UC-07** | `LRG-F-030` | 72h Hold-ready notification | Notification | `TC-NOTF-01, TC-NOTF-03, test_uc07_*` | **ACCEPTED (100%)** |
| **UC-07** | `LRG-F-031` | 24h Expiration reminder | Notification | `TC-NOTF-02, test_uc07_positive*` | **ACCEPTED (100%)** |
| **UC-08** | `LRG-F-042` | Add & edit catalog entries | Admin / Catalog | `TC-ADM-03, test_uc08_positive*` | **ACCEPTED (100%)** |
| **UC-09** | `LRG-F-041` | View hold demand report | Admin / Analytics | `TC-ADM-02, test_uc09_positive*` | **ACCEPTED (100%)** |

---

## 5. Formal Quality & Engineering Sign-Off

The updated test cases reflect all system changes made across Sprints 1, 2, and 3. All 88 automated tests execute deterministically with 100% pass rate.

- **QA Lead**: Dhareen G (`PES1UG24AM084`) – **APPROVED & VERIFIED**
- **Dev Lead**: Dharshini V (`PES1UG24AM428`) – **APPROVED & VERIFIED**
- **Database & Security Lead**: Dhruv Talavat (`PES1UG24AM087`) – **APPROVED & VERIFIED**
- **Backend & Analytics Lead**: Divyansh (`PES1UG24AM094`) – **APPROVED & VERIFIED**
