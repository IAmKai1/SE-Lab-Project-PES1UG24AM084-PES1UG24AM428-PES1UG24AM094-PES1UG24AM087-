"""
Unit & System Validation Tests for ALL Use Cases (UC-01 through UC-09 + UC-04b)
Digital Campus Library Reservation Gateway (LRG)

Exhaustively maps and validates all use cases across all 4 team members:
- Dhareen G (PES1UG24AM084): UC-01 Search ISBN Catalog, UC-06 Update Availability Status, UC-07 Notify Next Member
- Dhruv Talavat (PES1UG24AM087): UC-02 View Book Details, UC-03 Place Hold Request, UC-04 View & Cancel Holds
- Divyansh (PES1UG24AM094): UC-01 Search Catalog, UC-08 Manage Catalog Entries, UC-09 View Hold Demand Report
- Dharshini V (PES1UG24AM428): UC-04b Pay Overdue Fine & Settle Dues, UC-03 Eligibility Gatekeeper & System Integration
"""

import pytest
import time
from src.auth import AuthenticationManager, SESSION_IDLE_TIMEOUT
from src.catalog_search import CatalogSearchService
from src.reservation_manager import ReservationManager
from src.fine_manager import FineManager
from src.admin import LibrarianAdminService
from src.notification import NotificationService


# ==============================================================================
# UC-01: Search ISBN Catalog (Assigned: Dhareen G & Divyansh)
# Requirements: LRG-F-001, LRG-F-002, LRG-F-003, LRG-F-005
# ==============================================================================
class TestUseCase01_SearchISBNCatalog:
    def test_uc01_positive_exact_and_normalized_isbn_search(self, catalog_service: CatalogSearchService):
        """UC-01 [Positive]: Search by ISBN-13 returns exact matching title and availability."""
        isbn = "978-0132350884"
        ok, res, err = catalog_service.search(query=isbn, search_type="isbn")
        assert ok is True
        assert err is None
        assert res["total"] == 1
        assert res["results"][0]["isbn"] == isbn
        assert "Clean Code" in res["results"][0]["title"]
        assert res["results"][0]["status"] == "CheckedOut"

        # Hyphen-free search matches normalized record
        ok_norm, res_norm, _ = catalog_service.search(query="9780132350884", search_type="isbn")
        assert ok_norm is True
        assert res_norm["total"] == 1

    def test_uc01_positive_partial_title_and_author_search(self, catalog_service: CatalogSearchService):
        """UC-01 [Positive]: Substring title or author searches retrieve all matching titles."""
        ok, res, _ = catalog_service.search(query="Pragmatic", search_type="title")
        assert ok is True
        assert res["total"] >= 1
        assert any("Pragmatic" in b["title"] for b in res["results"])

        ok_auth, res_auth, _ = catalog_service.search(query="Martin", search_type="author")
        assert ok_auth is True
        assert res_auth["total"] >= 1
        assert any("Martin" in b["author"] for b in res_auth["results"])

    def test_uc01_negative_empty_and_whitespace_rejection(self, catalog_service: CatalogSearchService):
        """UC-01 [Negative]: Empty or blank search term rejected before DB query execution."""
        ok_empty, res, err = catalog_service.search(query="", search_type="title")
        assert ok_empty is False
        assert err == "SEARCH_QUERY_CANNOT_BE_EMPTY"

        ok_ws, _, err_ws = catalog_service.search(query="     ", search_type="title")
        assert ok_ws is False
        assert err_ws == "SEARCH_QUERY_CANNOT_BE_EMPTY"

    def test_uc01_boundary_zero_matching_titles_guidance(self, catalog_service: CatalogSearchService):
        """UC-01 [Boundary]: Non-matching query returns zero results with guidance message."""
        ok, res, err = catalog_service.search(query="NonExistentBookXYZ999", search_type="title")
        assert ok is True
        assert err is None
        assert res["total"] == 0
        assert len(res["results"]) == 0
        assert "message" in res
        assert "no results found" in res["message"].lower()


# ==============================================================================
# UC-02: View Book Details (Assigned: Dhruv Talavat & Divyansh)
# Requirements: LRG-F-004
# ==============================================================================
class TestUseCase02_ViewBookDetails:
    def test_uc02_positive_available_vs_checkedout_hold_eligibility(self, catalog_service: CatalogSearchService):
        """UC-02 [Positive]: Book detail displays copy count and allows hold only when CheckedOut."""
        # 1. CheckedOut book -> Hold button eligible
        ok1, book_out, err1 = catalog_service.get_book_details("978-0132350884")
        assert ok1 is True
        assert book_out["status"] == "CheckedOut"
        assert book_out["isHoldAllowed"] is True
        assert book_out["queueLength"] >= 1

        # 2. Available book -> Hold button not eligible
        ok2, book_avail, err2 = catalog_service.get_book_details("978-0134494166")
        assert ok2 is True
        assert book_avail["status"] == "Available"
        assert book_avail["isHoldAllowed"] is False

    def test_uc02_negative_nonexistent_isbn_returns_none(self, catalog_service: CatalogSearchService):
        """UC-02 [Negative]: Querying nonexistent ISBN returns BOOK_NOT_FOUND error."""
        ok, book, err = catalog_service.get_book_details("978-9999999999")
        assert ok is False
        assert book is None
        assert err == "BOOK_NOT_FOUND"


# ==============================================================================
# UC-03: Place Hold Request (Assigned: Dhruv Talavat & Dharshini V)
# Requirements: LRG-F-020, LRG-F-021, LRG-F-024
# ==============================================================================
class TestUseCase03_PlaceHoldRequest:
    def test_uc03_positive_fifo_queue_allocation(self, reservation_manager: ReservationManager):
        """UC-03 [Positive]: Placing hold on CheckedOut title appends student to FIFO queue."""
        isbn = "978-0201633610"  # Design Patterns (CheckedOut)
        ok1, res1, err1 = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok1 is True
        assert res1["position"] >= 1
        pos1 = res1["position"]

        # Next student is placed directly behind
        ok2, res2, err2 = reservation_manager.place_hold(isbn, "PES1UG24AM094")
        assert ok2 is True
        assert res2["position"] == pos1 + 1

    def test_uc03_negative_reject_hold_on_available_book(self, reservation_manager: ReservationManager):
        """UC-03 [Negative]: Rejects hold placement on available title with TITLE_AVAILABLE."""
        isbn_avail = "978-0134494166"
        ok, res, err = reservation_manager.place_hold(isbn_avail, "PES1UG24AM087")
        assert ok is False
        assert err == "TITLE_AVAILABLE"

    def test_uc03_negative_reject_duplicate_hold(self, reservation_manager: ReservationManager):
        """UC-03 [Negative]: Member cannot place two active holds on the same title."""
        isbn = "978-0321125217"
        ok1, _, _ = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok1 is True

        ok2, _, err2 = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok2 is False
        assert err2 == "DUPLICATE_HOLD"

    def test_uc03_boundary_enforce_five_active_holds_cap(self, reservation_manager: ReservationManager, in_memory_db):
        """UC-03 [Boundary]: Rejects 6th hold request when member reaches 5 active holds."""
        member_id = "PES1UG24AM087"
        # Seed extra checked-out titles
        conn = in_memory_db.get_connection()
        for i in range(1, 7):
            conn.execute(
                "INSERT OR IGNORE INTO titles (isbn, title, author, publisher, year, status) VALUES (?, ?, 'Author', 'Pub', 2020, 'CheckedOut')",
                (f"978-00000000{i}0", f"Volume {i}")
            )
        conn.commit()

        # Place 5 holds
        for i in range(1, 6):
            ok, _, _ = reservation_manager.place_hold(f"978-00000000{i}0", member_id)
            assert ok is True

        # 6th hold fails
        ok6, _, err6 = reservation_manager.place_hold("978-0000000060", member_id)
        assert ok6 is False
        assert err6 == "HOLD_LIMIT_REACHED"


# ==============================================================================
# UC-04: View & Cancel My Holds (Assigned: Dhruv Talavat)
# Requirements: LRG-F-022, LRG-F-023
# ==============================================================================
class TestUseCase04_ViewAndCancelHolds:
    def test_uc04_positive_view_my_active_holds(self, reservation_manager: ReservationManager):
        """UC-04 [Positive]: Student views active holds with correct dynamic queue position."""
        member_id = "PES1UG24AM087"
        reservation_manager.place_hold("978-0201633610", member_id)

        holds = reservation_manager.get_member_holds(member_id)
        assert len(holds) >= 1
        assert any(h["isbn"] == "978-0201633610" for h in holds)
        assert all(h["state"] in ["Active", "Ready"] for h in holds)

    def test_uc04_positive_cancel_hold_and_shift_queue_up(self, reservation_manager: ReservationManager):
        """UC-04 [Positive]: Cancelling hold shifts queue positions behind it up by 1."""
        isbn = "978-0135974445"
        # Member 087 at pos 1, Member 094 at pos 2
        ok1, res1, _ = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok1 is True
        ok2, res2, _ = reservation_manager.place_hold(isbn, "PES1UG24AM094")
        assert ok2 is True
        pos2_before = res2["position"]

        # Cancel Member 087's hold
        ok_cancel, err_cancel = reservation_manager.cancel_hold(res1["holdId"], "PES1UG24AM087")
        assert ok_cancel is True
        assert err_cancel is None

        # Member 094 must now be shifted up by 1
        holds_094 = reservation_manager.get_member_holds("PES1UG24AM094")
        hold_094 = next(h for h in holds_094 if h["holdId"] == res2["holdId"])
        assert hold_094["position"] == pos2_before - 1

    def test_uc04_security_prevent_cancelling_other_members_hold(self, reservation_manager: ReservationManager):
        """UC-04 [Security]: Student A cannot cancel Student B's hold."""
        isbn = "978-0135974445"
        ok, res, _ = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok is True

        # Student 094 attempts to cancel Student 087's hold
        ok_bad, err = reservation_manager.cancel_hold(res["holdId"], "PES1UG24AM094", is_admin=False)
        assert ok_bad is False
        assert err == "FORBIDDEN_NOT_OWNER"


# ==============================================================================
# UC-04b / UC-FINE: Pay Overdue Fine & Settle Dues (Assigned: Dharshini V)
# Requirements: LRG-F-050, LRG-F-051, LRG-F-052
# ==============================================================================
class TestUseCase04b_PayOverdueFine:
    def test_uc04b_positive_fine_assessment_calculation(self, fine_manager: FineManager):
        """UC-04b [Positive]: Fine assessed at standard $1.00 per overdue day."""
        member_id = "PES1UG24AM094"
        isbn = "978-0132350884"
        fine_id = fine_manager.assess_overdue_fine(member_id, isbn, overdue_days=7)
        assert fine_id > 0

        info = fine_manager.get_member_fines(member_id)
        assert info["total_unpaid"] == 7.00
        assert info["is_hold_blocked"] is False

    def test_uc04b_positive_settle_fine_via_wallet_and_receipt(self, fine_manager: FineManager):
        """UC-04b [Positive]: Settle fine via Campus Wallet, produces TXN- receipt."""
        member_id = "PES1UG24AM428"  # Seeded with $15.00 unpaid fine
        fines = fine_manager.get_member_fines(member_id)["fines"]
        assert len(fines) > 0
        target_fine = fines[0]

        ok, receipt, err = fine_manager.pay_fine(target_fine["id"], member_id, "CAMPUS_WALLET")
        assert ok is True
        assert err is None
        assert receipt["transaction_id"].startswith("TXN-")
        assert receipt["status"] == "SETTLED"
        assert receipt["amount_paid"] == target_fine["amount"]

    def test_uc04b_boundary_hold_blocked_when_fine_exceeds_threshold(
        self, fine_manager: FineManager, reservation_manager: ReservationManager
    ):
        """UC-04b [Boundary]: Fine >= $20 blocks hold creation until settled."""
        member_id = "PES1UG24AM084"
        isbn = "978-0201633610"

        # Assess 22 days overdue fine = $22.00 (> $20 cap)
        fine_manager.assess_overdue_fine(member_id, "978-0132350884", overdue_days=22)

        info = fine_manager.get_member_fines(member_id)
        assert info["is_hold_blocked"] is True

        # Placing hold must be rejected
        ok_hold, _, err_hold = reservation_manager.place_hold(isbn, member_id)
        assert ok_hold is False
        assert err_hold == "HOLD_BLOCKED_UNPAID_FINES"

        # Settle fine
        fine_to_pay = info["fines"][0]
        ok_pay, _, _ = fine_manager.pay_fine(fine_to_pay["id"], member_id, "CAMPUS_WALLET")
        assert ok_pay is True

        # Hold creation now succeeds
        ok_hold_after, res_after, _ = reservation_manager.place_hold(isbn, member_id)
        assert ok_hold_after is True
        assert res_after["position"] >= 1


# ==============================================================================
# UC-05: Log In (Campus SSO Authentication & Session Control)
# Requirements: LRG-F-010, LRG-F-011, LRG-F-012, LRG-F-013, LRG-SR-005
# ==============================================================================
class TestUseCase05_CampusSSOLogin:
    def test_uc05_positive_valid_sso_login_and_role_attribution(self, auth_manager: AuthenticationManager):
        """UC-05 [Positive]: Valid credentials establish session with student/librarian role."""
        # Student login
        ok_s, token_s, _ = auth_manager.authenticate_sso("PES1UG24AM428", "sso_valid_token_dharshini")
        assert ok_s is True
        assert token_s is not None
        v_s, user_s, _ = auth_manager.validate_session(token_s)
        assert v_s is True
        assert user_s["role"] == "student"

        # Librarian login
        ok_l, token_l, _ = auth_manager.authenticate_sso("LIB-HEAD-001", "sso_valid_token_librarian")
        assert ok_l is True
        v_l, user_l, _ = auth_manager.validate_session(token_l)
        assert v_l is True
        assert user_l["role"] == "librarian"

    def test_uc05_security_brute_force_lockout_after_five_failed_attempts(self, auth_manager: AuthenticationManager):
        """UC-05 [Security]: 5 consecutive bad tokens triggers 15-minute account lockout."""
        member_id = "PES1UG24AM087"
        for _ in range(5):
            ok, _, _ = auth_manager.authenticate_sso(member_id, "invalid_bad_token")
            assert ok is False

        # 6th attempt is locked out
        ok6, _, err6 = auth_manager.authenticate_sso(member_id, "even_if_valid_now")
        assert ok6 is False
        assert "ACCOUNT_LOCKED" in (err6 or "")

    def test_uc05_security_idle_session_expiry_30_minutes(self, auth_manager: AuthenticationManager, in_memory_db):
        """UC-05 [Security]: Session inactivity past 30 minutes triggers SESSION_EXPIRED_IDLE."""
        ok, token, _ = auth_manager.authenticate_sso("PES1UG24AM428", "sso_valid_token_dharshini")
        assert ok is True

        # Simulate 31 minutes of idle time
        past_time = time.time() - (SESSION_IDLE_TIMEOUT + 60)
        conn = in_memory_db.get_connection()
        conn.execute("UPDATE sessions SET last_active = ? WHERE token = ?", (past_time, token))
        conn.commit()

        valid, _, err = auth_manager.validate_session(token)
        assert valid is False
        assert err == "SESSION_EXPIRED_IDLE"


# ==============================================================================
# UC-06: Update Availability Status (Assigned: Dhareen G)
# Requirements: LRG-F-040
# ==============================================================================
class TestUseCase06_UpdateAvailabilityStatus:
    def test_uc06_positive_mark_returned_and_promote_hold(
        self, admin_service: LibrarianAdminService, librarian_token: str
    ):
        """UC-06 [Positive]: Librarian marks returned; status becomes Available, hold becomes Ready."""
        isbn = "978-0132350884"
        ok, res, err = admin_service.mark_returned(isbn, token=librarian_token)
        assert ok is True
        assert err is None
        assert res["status"] == "Available"
        assert res["holdReadyFor"] == "PES1UG24AM084"

    def test_uc06_boundary_ready_hold_auto_expires_and_cascade_promotes(
        self, reservation_manager: ReservationManager, in_memory_db
    ):
        """UC-06 [Boundary]: 72h expired Ready hold auto-expires and promotes next waiting hold."""
        isbn = "978-0201633610"
        # Two holds
        ok1, res1, _ = reservation_manager.place_hold(isbn, "PES1UG24AM084")
        ok2, res2, _ = reservation_manager.place_hold(isbn, "PES1UG24AM087")
        assert ok1 and ok2

        # Manually promote first hold to Ready and simulate 73 hours past expiry
        past_expiry = time.time() - 3600
        conn = in_memory_db.get_connection()
        conn.execute(
            "UPDATE holds SET state = 'Ready', created_at = ?, ready_until = ? WHERE id = ?",
            (past_expiry - (72 * 3600), past_expiry, res1["holdId"])
        )
        conn.commit()

        # Run automated expiration sweeper
        expired_records = reservation_manager.expire_overdue_ready_holds()
        assert len(expired_records) >= 1

        # Check second member promoted to Ready
        holds_087 = reservation_manager.get_member_holds("PES1UG24AM087")
        target_087 = next(h for h in holds_087 if h["holdId"] == res2["holdId"])
        assert target_087["state"] == "Ready"


# ==============================================================================
# UC-07: Notify Next Member (Assigned: Dhareen G)
# Requirements: LRG-F-030, LRG-F-031
# ==============================================================================
class TestUseCase07_NotifyNextMember:
    def test_uc07_positive_hold_ready_dispatch_email_contents(self, notification_service: NotificationService):
        """UC-07 [Positive]: Dispatches email with title and 72-hour pickup window."""
        ok, msg = notification_service.notify_hold_ready("PES1UG24AM428", "978-0132350884")
        assert ok is True
        assert msg == "DELIVERED"
        assert len(notification_service.sent_messages) >= 1

        sent = notification_service.sent_messages[-1]
        assert "Clean Code" in sent["subject"]
        assert "72 hours" in sent["body"]

    def test_uc07_positive_send_24h_expiry_reminder(
        self, reservation_manager: ReservationManager, notification_service: NotificationService, admin_service: LibrarianAdminService, librarian_token: str
    ):
        """UC-07 [Positive]: 24-hour reminder email dispatched for Ready holds."""
        # Clean Code has a hold for PES1UG24AM084; mark it returned to make it Ready
        ok, res, _ = admin_service.mark_returned("978-0132350884", token=librarian_token)
        assert ok is True
        holds = reservation_manager.get_member_holds("PES1UG24AM084")
        ready_hold = next(h for h in holds if h["state"] == "Ready")

        ok_rem, msg_rem = notification_service.send_expiry_reminder(ready_hold["holdId"])
        assert ok_rem is True
        assert msg_rem == "DELIVERED"


# ==============================================================================
# UC-08: Manage Catalog Entries (Assigned: Divyansh & Dhareen G)
# Requirements: LRG-F-042
# ==============================================================================
class TestUseCase08_ManageCatalogEntries:
    def test_uc08_positive_librarian_add_and_update_book(
        self, admin_service: LibrarianAdminService, catalog_service: CatalogSearchService, librarian_token: str
    ):
        """UC-08 [Positive]: Librarian adds new book and updates existing book record."""
        # 1. Add book
        ok_add, isbn_res, err_add = admin_service.add_book(
            isbn="978-0596517748",
            title="JavaScript: The Good Parts",
            author="Douglas Crockford",
            publisher="O'Reilly Media",
            year=2008,
            status="Available",
            token=librarian_token
        )
        assert ok_add is True
        assert err_add is None

        # Verify searchable
        ok_s, res_s, _ = catalog_service.search("Douglas", search_type="author")
        assert ok_s is True
        assert any(b["isbn"] == "978-0596517748" for b in res_s["results"])

        # 2. Update title
        ok_upd, err_upd = admin_service.edit_book(
            isbn="978-0596517748",
            title="JavaScript: The Good Parts (Updated)",
            author="Douglas Crockford",
            publisher="O'Reilly Media",
            year=2008,
            token=librarian_token
        )
        assert ok_upd is True
        assert err_upd is None

        ok_dtl, detail, _ = catalog_service.get_book_details("978-0596517748")
        assert ok_dtl is True
        assert detail["title"] == "JavaScript: The Good Parts (Updated)"

    def test_uc08_security_student_role_blocked_from_adding_book(
        self, admin_service: LibrarianAdminService, student_token: str
    ):
        """UC-08 [Security]: Student token rejected with FORBIDDEN when attempting to add books."""
        ok, _, err = admin_service.add_book(
            isbn="978-0000000099",
            title="Hacker Book",
            author="Attacker",
            publisher="DarkWeb",
            year=2026,
            status="Available",
            token=student_token
        )
        assert ok is False
        assert err == "FORBIDDEN"


# ==============================================================================
# UC-09: View Hold Demand Report (Assigned: Divyansh)
# Requirements: LRG-F-041
# ==============================================================================
class TestUseCase09_ViewHoldDemandReport:
    def test_uc09_positive_demand_report_ranked_by_queue_length(
        self, admin_service: LibrarianAdminService, librarian_token: str
    ):
        """UC-09 [Positive]: Report ranks books in descending order of waiting holds."""
        ok, report, err = admin_service.get_demand_report(token=librarian_token)
        assert ok is True
        assert err is None
        assert len(report) >= 5

        # Verify sorted descending
        for i in range(len(report) - 1):
            assert report[i]["queueLength"] >= report[i + 1]["queueLength"]

    def test_uc09_security_student_blocked_from_demand_report(
        self, admin_service: LibrarianAdminService, student_token: str
    ):
        """UC-09 [Security]: Students cannot view the administrative hold demand report."""
        ok, _, err = admin_service.get_demand_report(token=student_token)
        assert ok is False
        assert err == "FORBIDDEN"
