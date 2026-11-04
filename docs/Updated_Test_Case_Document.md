# Digital Campus Library Reservation Gateway (LRG)
## Updated Test Case Document (Deliverable 1.a & 1.b)
### Software Test Plan (STP) Version 2.0 – Post-Sprint Refinements

**Document Version**: 2.0  
**Effective Date**: 4th November 2026 (Reflecting Sprints 1, 2, and 3)  
**Authors**:
- Dhareen G (`PES1UG24AM084`) – QA Lead
- Dharshini V (`PES1UG24AM428`) – Dev Lead & UC-04 Fine Module Owner
- Divyansh (`PES1UG24AM094`) – Backend & Search Engineer
- Dhruv Talavat (`PES1UG24AM087`) – Database & Security Engineer

---

## 1. Document Overview & Change Summary

During the execution of **Sprint 1 (19th Oct to 23rd Oct)**, **Sprint 2 (26th Oct to 30th Oct)**, and **Sprint 3 (2nd Nov to 6th Nov)**, several architectural enhancements, boundary edge cases, and feature integrations were identified and implemented.

In accordance with Deliverable 1:
> *1.a. Update the test cases written by you earlier based on the changes made during the sprints.*  
> *1.b. Update the Test Case Document accordingly.*

This document details the exact modifications made to the original Test Case Catalogue (STP v1.0 Appendix A), establishes traceability to the functional and non-functional requirements, and documents test execution outcomes.

### Summary of Sprint Refinements & Added Test Cases:
1. **UC-04 Overdue Fine Payment Integration** (`TC-FINE-01` to `TC-FINE-05`):
   - Added test coverage for overdue fine assessment (\$1.00/day), payment gateway settlement via Campus Wallet/UPI, digital receipt generation (`TXN-` ID), and automated hold blocking when balance exceeds \$20.
2. **Ready Hold 72-Hour Auto-Expiration & Cascade Promotion** (`TC-HOLD-06`):
   - In Sprint 2, Ready holds were manually managed. In Sprint 3, an automated maintenance worker was implemented to expire Ready holds past 72 hours and auto-promote the next waiting hold. `TC-HOLD-06` verifies this cascade.
3. **ISBN Normalization & Hyphen Flexibility** (`TC-SRCH-07`):
   - User testing revealed students frequently enter 10-digit or 13-digit ISBNs without hyphens. The search engine was upgraded to normalize queries; `TC-SRCH-07` validates unhyphenated searches matching hyphenated records.
4. **Notification Delivery Retry Policy** (`TC-NOTF-03`):
   - To mitigate temporary SMTP failures, a 3-attempt exponential retry policy was added. `TC-NOTF-03` verifies retry execution and dead-letter audit logging.
5. **Rate Limiting Sliding-Window Reset & Isolation** (`TC-SEC-08`):
   - Verified that client IPs are isolated in rate limiting and that windows roll over accurately without permanently blocking legitimate clients.

---

## 2. Updated Test Case Catalogue (Appendix A – v2.0)

| TC ID | Test Objective | Requirement(s) | Type | Priority | Expected Result | Post-Sprint Execution Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-SRCH-01** | Search by valid ISBN | `LRG-F-001` | Functional | High | Matching title returned with availability status. | **PASS (100%)** |
| **TC-SRCH-02** | Search by partial title and author | `LRG-F-001` | Functional | High | All titles containing substring or by author returned. | **PASS (100%)** |
| **TC-SRCH-03** | Submit empty/malformed search input | `LRG-F-002` | Functional | High | Validation rejection message; no database query executed. | **PASS (100%)** |
| **TC-SRCH-04** | Check pagination and result schema | `LRG-F-003` | Functional | High | 10 results/page; includes `isbn, title, author, status`. | **PASS (100%)** |
| **TC-SRCH-05** | Book detail & hold button eligibility | `LRG-F-004` | Functional | Medium | Place Hold visible only when book is `CheckedOut`. | **PASS (100%)** |
| **TC-SRCH-06** | Search query with zero matches | `LRG-F-005` | Functional | Low | "No results found" advice returned; empty result array. | **PASS (100%)** |
| **TC-SRCH-07** | *(Updated)* ISBN hyphen normalization | `LRG-F-001` | Functional | Medium | Unhyphenated input successfully matches hyphenated DB entry. | **PASS (100%)** |
| **TC-AUTH-01** | Log in with valid campus SSO token | `LRG-F-010` | Functional | High | Session created; member name and role returned. | **PASS (100%)** |
| **TC-AUTH-02** | Log in with invalid credentials 6 times | `LRG-F-010, LRG-SR-005` | Security | High | 5 failures logged; 6th attempt locked out for 15 minutes. | **PASS (100%)** |
| **TC-AUTH-03** | Guest search vs Place Hold gate | `LRG-F-011` | Functional | Medium | Search works without login; Place Hold returns 401. | **PASS (100%)** |
| **TC-AUTH-04** | Student attempts librarian actions | `LRG-F-012, LRG-SR-003` | Security | High | Access denied (HTTP 403 Forbidden); attempt logged. | **PASS (100%)** |
| **TC-AUTH-05** | Logout and 30-minute idle expiry | `LRG-F-013` | Functional | Medium | Session destroyed; 30+ min idle returns `SESSION_EXPIRED`. | **PASS (100%)** |
| **TC-AUTH-06** | *(Updated)* Tampered session token | `LRG-SR-003` | Security | High | Fabricated or tampered token rejected with 401. | **PASS (100%)** |
| **TC-HOLD-01** | Place hold on CheckedOut title | `LRG-F-020` | Functional | High | Hold created in state 'Active'; queue position assigned. | **PASS (100%)** |
| **TC-HOLD-02** | Reject Available and duplicate holds | `LRG-F-021` | Functional | High | Rejects hold on Available book and duplicate hold by same user. | **PASS (100%)** |
| **TC-HOLD-03** | View and cancel active hold | `LRG-F-022` | Functional | Medium | Hold removed from active list; state updated to 'Cancelled'. | **PASS (100%)** |
| **TC-HOLD-04** | Queue progression on cancellation | `LRG-F-023` | Functional | Low | Positions behind cancelled hold move up by exactly 1. | **PASS (100%)** |
| **TC-HOLD-05** | Enforce 5 active holds limit | `LRG-F-024` | Functional | Medium | 6th hold request rejected with `HOLD_LIMIT_REACHED`. | **PASS (100%)** |
| **TC-HOLD-06** | *(Updated)* Ready hold 72h auto-expire | `LRG-F-020, LRG-F-040` | Functional | High | Ready hold past 72h auto-expires; promotes next in queue. | **PASS (100%)** |
| **TC-FINE-01** | *(Updated)* Overdue fine calculation | `LRG-F-050` *(UC-04)* | Functional | High | Overdue days assessed at \$1.00/day; balance updated. | **PASS (100%)** |
| **TC-FINE-02** | *(Updated)* Settle fine via Campus Wallet | `LRG-F-051` *(UC-04)* | Functional | High | Fine status set to 'Paid'; digital receipt with `TXN-` ID issued. | **PASS (100%)** |
| **TC-FINE-03** | *(Updated)* Hold restriction on fine | `LRG-F-052` *(UC-04)* | Functional | High | Hold blocked when fine $\ge \$20$; unlocked once paid. | **PASS (100%)** |
| **TC-FINE-04** | *(Updated)* Cross-student fine payment | `LRG-SR-003` *(UC-04)* | Security | High | Student A cannot settle Student B's fine (403 Forbidden). | **PASS (100%)** |
| **TC-NOTF-01** | Return held title & notify member | `LRG-F-030` | Functional | Medium | Email naming title and 72h pickup window reaches student. | **PASS (100%)** |
| **TC-NOTF-02** | 24-hour expiration reminder email | `LRG-F-031` | Functional | Low | Reminder sent once 24h before expiry; none for cancelled. | **PASS (100%)** |
| **TC-NOTF-03** | *(Updated)* Retry on SMTP failure | `LRG-F-030` | Reliability | Medium | Retries 3 times on SMTP error; failure logged to audit trail. | **PASS (100%)** |
| **TC-ADM-01** | Librarian marks title returned | `LRG-F-040` | Functional | High | Status set to Available; first hold promoted to Ready. | **PASS (100%)** |
| **TC-ADM-02** | Generate hold demand report | `LRG-F-041` | Functional | Low | Titles ranked in descending order of queue length. | **PASS (100%)** |
| **TC-ADM-03** | Add and edit catalog entry | `LRG-F-042` | Functional | Medium | New entry saved and searchable; edits persisted. | **PASS (100%)** |
| **TC-PERF-01** | 200 concurrent user search time | `LRG-NF-001` | Performance | High | 90th percentile response time $\le 2.0\text{ s}$ (Observed: 0.0051s). | **PASS (100%)** |
| **TC-PERF-02** | Large seeded catalog scalability | `LRG-NF-005` | Performance | Medium | Search performance remains within 2s with large dataset. | **PASS (100%)** |
| **TC-AVL-01** | System uptime & health endpoint | `LRG-NF-002` | Reliability | High | `/health` endpoint returns UP and $\ge 99.5\%$ availability. | **PASS (100%)** |
| **TC-UX-01** | WCAG 2.1 AA accessibility & 360px | `LRG-NF-004` | Usability | Medium | Semantic ARIA tags present; contrast $> 4.5:1$; 360px mobile responsive. | **PASS (100%)** |
| **TC-MNT-01** | Business layer test coverage | `LRG-NF-006` | Maintainability| Medium| Business logic test coverage $\ge 70\%$ (Observed: 93.8%). | **PASS (100%)** |
| **TC-AUD-01** | Audit logging and 1-year retention | `LRG-NF-007` | Functional | High | Every hold, return, and admin action logged with timestamp. | **PASS (100%)** |
| **TC-SEC-01** | TLS 1.2+ & security headers | `LRG-SR-001` | Security | High | HSTS, nosniff, DENY headers present on all responses. | **PASS (100%)** |
| **TC-SEC-02** | SQL injection & XSS neutralization | `LRG-SR-004` | Security | High | Malicious payloads sanitized; parameterized queries protect DB. | **PASS (100%)** |
| **TC-SEC-03** | Inspect cookie security flags | `LRG-SR-006` | Security | Medium | `Secure`, `HttpOnly`, and `SameSite=Strict` present on cookies. | **PASS (100%)** |
| **TC-SEC-04** | Data confidentiality check | `LRG-NF-003` | Security | High | Member cannot view or cancel another member's holds. | **PASS (100%)** |
| **TC-SEC-05** | Inspect DB and logs for passwords | `LRG-SR-002` | Security | High | No passwords stored in database or logged in audit trail. | **PASS (100%)** |
| **TC-SEC-06** | Call librarian endpoints with Student token | `LRG-SR-003` | Security | High | 403 returned for every librarian endpoint. | **PASS (100%)** |
| **TC-SEC-07** | Rate limiting: 61 req in 1 min | `LRG-SR-007` | Security | Medium | Request 61 returns HTTP 429 Too Many Requests. | **PASS (100%)** |
| **TC-SEC-08** | *(Updated)* Rate limiter reset & IP isolation | `LRG-SR-007` | Security | Medium | Client IPs isolated; sliding window resets correctly. | **PASS (100%)** |

---

## 3. Test Traceability Matrix (RTM) Sign-Off

Every requirement defined in the SRS v1.0 and augmented in Sprints 1, 2, and 3 has a direct, verified mapping to an automated test case with **100% acceptance (`A`)**.

- **QA Lead Approval**: Dhareen G (`PES1UG24AM084`) – **APPROVED**
- **Dev Lead Approval**: Dharshini V (`PES1UG24AM428`) – **APPROVED**
