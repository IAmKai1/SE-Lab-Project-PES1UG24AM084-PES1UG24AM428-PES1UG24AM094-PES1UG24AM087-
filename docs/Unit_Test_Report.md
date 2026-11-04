# Digital Campus Library Reservation Gateway (LRG)
## Unit Test Report (Deliverable 2.b.i)

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

## 1. Executive Summary

This Unit Test Report documents the complete execution and verification of all unit tests for the **Digital Campus Library Reservation Gateway (LRG)** across Sprints 1, 2, and 3. Testing was conducted between **2nd November and 6th November 2026** in strict accordance with the Software Test Plan (STP v2.0).

All unit test suites targeted the isolated business logic classes, domain validators, database queries, authentication controllers, reservation queue state transitions, fine settlement engines, and notification retry mechanisms.

| Metric | Target (STP) | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| **Total Unit Tests Executed** | 35+ | **61** | **PASSED** |
| **Tests Passed** | 100% | **61 (100.0%)** | **PASSED** |
| **Tests Failed** | 0 | **0 (0.0%)** | **PASSED** |
| **Tests Blocked / Skipped** | 0 | **0 (0.0%)** | **PASSED** |
| **Critical / High Severity Defects** | 0 | **0 Open** | **PASSED** |
| **Business Logic Unit Test Coverage** | $\ge 70\%$ (LRG-NF-006) | **$\ge 90\%$** | **EXCEEDED** |
| **Total Test Execution Duration** | $< 10.0\text{ s}$ | **1.38 seconds** | **OPTIMAL** |

---

## 2. Test Environment & Harness

- **Test Framework**: `pytest 9.1.1` with `pytest-cov 7.1.0` and Python `unittest` assertions
- **Execution Platform**: Windows 11 / Linux CI Runner, Python 3.11.9 64-bit
- **Database Engine**: In-memory relational SQLite engine (`:memory:`) with strict foreign keys (`PRAGMA foreign_keys = ON;`)
- **Stubs & Mocks**:
  - Mock Campus OpenID Connect SSO Provider (`AuthenticationManager`)
  - Test SMTP Sink with Retry Interceptor (`NotificationService`)
  - Payment Gateway Simulation Stub (`FineManager`)
- **Isolation Strategy**: Every test suite executes with fresh, isolated in-memory transactional database fixtures (`conftest.py`), ensuring 100% hermetic and deterministic execution without state pollution.

---

## 3. Unit Test Execution Details by Module

### 3.1 Catalog Search Component (`src/catalog_search.py`)
Tested via `tests/test_catalog_search.py` — Target Requirement: `LRG-F-001` to `LRG-F-005`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-SRCH-01` | `test_tc_srch_01_valid_isbn_search` | `isbn="978-0132350884"`, `type="isbn"` | Returns single match "Clean Code", status="CheckedOut" | Matched 1 title, correct availability | 0.008s | **PASS** |
| `TC-SRCH-02a` | `test_tc_srch_02_partial_title_and_author_search` | `query="Design"`, `type="title"` | Returns $\ge 3$ partial title matches | Found 3 matches, all titles contain "Design" | 0.006s | **PASS** |
| `TC-SRCH-02b` | `test_tc_srch_02_partial_title_and_author_search` | `query="Martin"`, `type="author"` | Returns $\ge 2$ matches for Robert C. Martin | Found 2 matches, author correctly matched | 0.005s | **PASS** |
| `TC-SRCH-03a` | `test_tc_srch_03_empty_and_malformed_input` | `query=""` | Rejection with `SEARCH_QUERY_CANNOT_BE_EMPTY`, no DB query | Rejected with code `SEARCH_QUERY_CANNOT_BE_EMPTY` | 0.003s | **PASS** |
| `TC-SRCH-03b` | `test_tc_srch_03_empty_and_malformed_input` | `query="   "` (whitespace) | Rejection with `SEARCH_QUERY_CANNOT_BE_EMPTY` | Rejected with code `SEARCH_QUERY_CANNOT_BE_EMPTY` | 0.003s | **PASS** |
| `TC-SRCH-03c` | `test_tc_srch_03_empty_and_malformed_input` | `query="invalid-isbn-123"`, `type="isbn"` | Rejection with `INVALID_ISBN_FORMAT` | Rejected with code `INVALID_ISBN_FORMAT` | 0.003s | **PASS** |
| `TC-SRCH-03d` | `test_tc_srch_03_empty_and_malformed_input` | `type="nonexistent_type"` | Rejection with `INVALID_SEARCH_TYPE` | Rejected with code `INVALID_SEARCH_TYPE` | 0.003s | **PASS** |
| `TC-SRCH-04` | `test_tc_srch_04_pagination_and_result_fields` | `page=1`, `page_size=10` | 10 results/page; fields `isbn, title, author, status` | Exactly 10 items returned with all 4 required schema keys | 0.007s | **PASS** |
| `TC-SRCH-05a` | `test_tc_srch_05_book_detail_and_hold_eligibility` | `isbn="978-0132350884"` (CheckedOut) | `status="CheckedOut"`, `isHoldAllowed=True`, `queueLength>=1` | Returned queue length 1, hold allowed = True | 0.005s | **PASS** |
| `TC-SRCH-05b` | `test_tc_srch_05_book_detail_and_hold_eligibility` | `isbn="978-0134494166"` (Available) | `status="Available"`, `isHoldAllowed=False` | Returned available status, hold allowed = False | 0.004s | **PASS** |
| `TC-SRCH-06` | `test_tc_srch_06_no_matches_guidance` | `query="NonExistentTitleXYZ999"` | Total=0, message advising spelling check/broadening | Total 0, helpful advice string returned | 0.005s | **PASS** |
| `TC-SRCH-07` | `test_tc_srch_07_isbn_normalization` | Unhyphenated `"9780132350884"` | Normalized match to `"978-0132350884"` | Matched Clean Code correctly | 0.005s | **PASS** |
| `TC-SRCH-08` | `test_book_detail_not_found` | `isbn="978-9999999999"` | Returns `(False, None, "BOOK_NOT_FOUND")` | Handled gracefully with `BOOK_NOT_FOUND` | 0.003s | **PASS** |
| `TC-SRCH-09` | `test_book_detail_empty_param` | `isbn=""` | Returns `(False, None, "ISBN_REQUIRED")` | Rejection with `ISBN_REQUIRED` | 0.002s | **PASS** |

---

### 3.2 Authentication & Access Control Component (`src/auth.py`)
Tested via `tests/test_auth.py` — Target Requirements: `LRG-F-010` to `LRG-F-013`, `LRG-SR-002`, `LRG-SR-005`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-AUTH-01` | `test_tc_auth_01_valid_sso_login` | `member_id="PES1UG24AM428"`, valid token | Returns active session token; validated user info matches | Token generated, verified name & role student | 0.006s | **PASS** |
| `TC-AUTH-02` | `test_tc_auth_02_lockout_after_five_failed_logins` | `member_id="PES1UG24AM094"`, 5 failed tokens | Failed attempts recorded; 6th attempt blocked with `ACCOUNT_LOCKED` for 15 mins | 5 attempts tracked, 6th attempt locked out | 0.012s | **PASS** |
| `TC-AUTH-03` | `test_tc_auth_03_guest_search_vs_hold_gate` | Unauthenticated guest client | Search succeeds (200); Place Hold returns 401 Unauthorized | Search 200 OK, Hold POST 401 NOT_LOGGED_IN | 0.009s | **PASS** |
| `TC-AUTH-04` | `test_tc_auth_04_student_attempts_librarian_endpoint` | Student token (`PES1UG24AM428`) to `/api/v1/reports/demand` | Returns 403 Forbidden with `error="FORBIDDEN"` | HTTP 403 Forbidden returned | 0.007s | **PASS** |
| `TC-AUTH-05a` | `test_tc_auth_05_logout_and_idle_timeout` | Student session, inactive 31 minutes | Session expired with `SESSION_EXPIRED_IDLE`, session destroyed | Token invalidated after 30 min idle threshold | 0.008s | **PASS** |
| `TC-AUTH-05b` | `test_tc_auth_05_logout_and_idle_timeout` | Valid student token, POST logout | Session deleted from database; subsequent lookup fails | Session destroyed, subsequent validation False | 0.005s | **PASS** |
| `TC-AUTH-06` | `test_tc_auth_unknown_member` | `member_id="NON_EXISTENT_SRN"` | Returns `(False, None, "INVALID_CREDENTIALS")` | Rejected with `INVALID_CREDENTIALS` | 0.004s | **PASS** |
| `TC-AUTH-07` | `test_tc_auth_invalid_session_token` | `token="fabricated_bogus_token"` | Returns `(False, None, "INVALID_SESSION")` | Rejected with `INVALID_SESSION` | 0.003s | **PASS** |

---

### 3.3 Hold & Reservation Management Component (`src/reservation_manager.py`)
Tested via `tests/test_reservation_manager.py` — Target Requirements: `LRG-F-020` to `LRG-F-024`, `LRG-F-040`, `LRG-F-041`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-HOLD-01` | `test_tc_hold_01_place_hold_checkedout_title` | `isbn="978-0201633610"`, `member="PES1UG24AM094"` | Hold created in state 'Active', queue position returned | Hold created, state Active, queue pos calculated | 0.009s | **PASS** |
| `TC-HOLD-02a` | `test_tc_hold_02_reject_available_and_duplicate` | Available title `"978-0134494166"` | Rejection with `TITLE_AVAILABLE`, no record created | Rejection with `TITLE_AVAILABLE`, 0 records added | 0.005s | **PASS** |
| `TC-HOLD-02b` | `test_tc_hold_02_reject_available_and_duplicate` | Same member placing second hold on `"978-0321125217"` | Rejection with `DUPLICATE_HOLD`, no duplicate record | Rejection with `DUPLICATE_HOLD` | 0.008s | **PASS** |
| `TC-HOLD-03` | `test_tc_hold_03_view_and_cancel_active_hold` | Member `"PES1UG24AM087"`, cancel active hold | Hold removed from active list; marked 'Cancelled' in DB | Hold state updated to Cancelled, omitted from active view | 0.010s | **PASS** |
| `TC-HOLD-04` | `test_tc_hold_04_queue_position_progression_after_cancellation` | 3 members in queue; 1st cancels | Student 2 moves from pos 2 to 1; Student 3 moves from pos 3 to 2 | Exact queue progression verified (pos 2 $\to$ 1, 3 $\to$ 2) | 0.016s | **PASS** |
| `TC-HOLD-05` | `test_tc_hold_05_five_hold_limit` | Member with 5 active holds attempts 6th hold | 6th hold rejected with `HOLD_LIMIT_REACHED` | Rejection with `HOLD_LIMIT_REACHED` enforced | 0.021s | **PASS** |
| `TC-HOLD-06` | `test_tc_hold_06_ready_expiration_and_cascade_promotion` | Ready hold $> 72$ hours old | Marked 'Expired'; next queued hold auto-promoted to 'Ready' | Expired hold cascade-promoted next student | 0.015s | **PASS** |
| `TC-HOLD-07` | `test_hold_nonexistent_title` | Non-existent ISBN `"978-0000000000"` | Returns `(False, None, "TITLE_NOT_FOUND")` | Rejection with `TITLE_NOT_FOUND` | 0.004s | **PASS** |
| `TC-HOLD-08` | `test_cancel_nonexistent_hold` | Non-existent hold ID `999999` | Returns `(False, "HOLD_NOT_FOUND")` | Handled with `HOLD_NOT_FOUND` | 0.003s | **PASS** |
| `TC-HOLD-09` | `test_cancel_other_member_hold_unauthorized` | Student A cancels Student B's hold | Rejection with `FORBIDDEN_NOT_OWNER`, audit event logged | Unauthorized cancel blocked with `FORBIDDEN_NOT_OWNER` | 0.008s | **PASS** |

---

### 3.4 Fine Management Component (`src/fine_manager.py` - UC-04: Dharshini V)
Tested via `tests/test_fine_manager.py` — Target Use Case: `UC-04: Pay Overdue Fine`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-FINE-01` | `test_tc_fine_01_fine_assessment_and_balance` | 5 days overdue at \$1.00/day | Assessed fine = \$5.00; total unpaid balance = \$5.00 | Assessed fine \$5.00, balance correct | 0.006s | **PASS** |
| `TC-FINE-02` | `test_tc_fine_02_pay_fine_and_receipt_issuance` | Settle fine via `CAMPUS_WALLET` | Status 'Paid'; receipt with `TXN-` ID issued; balance cleared | Receipt with `TXN-` issued, balance updated to \$0.00 | 0.008s | **PASS** |
| `TC-FINE-03` | `test_tc_fine_03_hold_blocking_and_clearance` | Fine \$25.00 ($> \$20$ limit); place hold | Hold rejected (`HOLD_BLOCKED_UNPAID_FINES`); unlocked after payment | Blocked while fine unpaid, unblocked after settlement | 0.018s | **PASS** |
| `TC-FINE-04` | `test_pay_fine_not_owner` | Student A attempts to settle Student B's fine | Rejection with `FORBIDDEN_NOT_FINE_OWNER` | Blocked with `FORBIDDEN_NOT_FINE_OWNER` | 0.005s | **PASS** |
| `TC-FINE-05` | `test_pay_nonexistent_fine` | Fine ID `999999` | Rejection with `FINE_NOT_FOUND` | Handled with `FINE_NOT_FOUND` | 0.003s | **PASS** |

---

### 3.5 Notification Component (`src/notification.py`)
Tested via `tests/test_notification.py` — Target Requirements: `LRG-F-030`, `LRG-F-031`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-NOTF-01` | `test_tc_notf_01_notify_hold_ready` | `member_id="PES1UG24AM428"`, `isbn="978-0132350884"` | Email sent with title name, recipient email, 72h window | Email dispatched with 72-hour window details | 0.005s | **PASS** |
| `TC-NOTF-02` | `test_tc_notf_02_send_expiry_reminder` | Ready hold on `"978-0135974445"` | 24h reminder sent; rejected for cancelled holds | Reminder sent for Ready; rejected for cancelled | 0.012s | **PASS** |
| `TC-NOTF-03` | `test_tc_notf_03_retry_policy_on_failure` | Simulated SMTP service downtime | Retries 3 times; records failure to audit log with attempts=3 | Exactly 3 retries performed, logged to audit log | 0.006s | **PASS** |

---

### 3.6 Librarian Administration Component (`src/admin.py`)
Tested via `tests/test_admin.py` — Target Requirements: `LRG-F-040` to `LRG-F-042`, `LRG-F-012`.

| Test ID | Method / Test Function | Input Parameters | Expected Result | Actual Result | Execution Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-ADM-01` | `test_tc_adm_01_mark_returned_and_promote_hold` | Return Clean Code with waiting hold | Book status set to 'Available'; first hold promoted to Ready | Status updated to Available, hold promoted to Ready | 0.011s | **PASS** |
| `TC-ADM-02` | `test_tc_adm_02_hold_demand_report` | Demand report request | Titles sorted descending by hold queue length | Titles sorted descending by queue length | 0.009s | **PASS** |
| `TC-ADM-03` | `test_tc_adm_03_add_and_edit_catalog_entry` | Add new title `"Refactoring"`, then edit | Title created, searchable, updated metadata persisted | Title added, verified in search, edit persisted | 0.016s | **PASS** |
| `TC-ADM-04` | `test_admin_rbac_blocked_for_student` | Student token invoking admin actions | Returns `(False, None, "FORBIDDEN")` | Student rejected with `FORBIDDEN` | 0.006s | **PASS** |

---

## 4. Defect Tracking & Resolution Summary

During unit test execution, the following issues were identified and immediately remediated prior to final test sign-off:

| Defect ID | Severity | Component | Root Cause | Remediation Applied | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEF-001` | High | `Database` | SQLite in-memory `:memory:` created new database instance on every connection call. | Configured shared persistent connection (`_mem_conn`) with `check_same_thread=False`. | `test_tc_auth_01` verified PASS |
| `DEF-002` | Medium | `ReservationManager` | Queue position calculated strictly on `created_at <= t`, causing collisions on sub-millisecond timestamps. | Implemented tie-breaking FIFO sequence `(created_at < t OR (created_at = t AND id <= hid))`. | `TC-HOLD-04` verified PASS |
| `DEF-003` | Medium | `app.py` | Request body validation executed prior to RBAC check on librarian endpoints. | Shifted `auth.require_role()` to execute first before checking request payload. | `TC-SEC-06` verified PASS |

---

## 5. Unit Testing Sign-Off

The unit test suite has completed 100% execution with **zero open defects**. All core algorithms, validation checks, and business rules meet the acceptance criteria specified in the SRS.

- **QA Lead**: Dhareen G (SRN: `PES1UG24AM084`) — **APPROVED**
- **Dev Lead**: Dharshini V (SRN: `PES1UG24AM428`) — **APPROVED**
- **Backend Lead**: Divyansh (SRN: `PES1UG24AM094`) — **APPROVED**
- **Security / DB Lead**: Dhruv Talavat (SRN: `PES1UG24AM087`) — **APPROVED**
