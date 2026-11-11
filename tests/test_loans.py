"""
TC-LOAN tests: the Head Librarian can see who has each checked-out title and when it is due,
check titles out to students, and returns close the loan.
"""

import time

import pytest

from src.loan_manager import LoanManager, DAY_SECONDS

CLEAN_CODE = "978-0132350884"          # CheckedOut, has an Active hold by PES1UG24AM084
CLEAN_ARCH = "978-0134494166"          # Available
HEAD_FIRST = "978-0596007126"          # Available


@pytest.fixture
def loan_manager(in_memory_db, audit_service, fine_manager):
    return LoanManager(in_memory_db, audit_service, fine_manager)


class TestLoanTracking:

    def test_tc_loan_01_every_checked_out_title_has_borrower_and_due_date(self, loan_manager, in_memory_db):
        checked_out = in_memory_db.fetchone("SELECT COUNT(*) FROM titles WHERE status = 'CheckedOut'")[0]
        loans = loan_manager.get_current_loans()
        assert len(loans) == checked_out > 0
        for loan in loans:
            assert loan["member_id"] and loan["member_name"] and loan["member_email"]
            assert loan["due_at"] > loan["checked_out_at"]

    def test_tc_loan_02_seeded_loans_include_overdue_and_due_soon(self, loan_manager):
        summary = loan_manager.get_summary()
        assert summary["overdue"] >= 1
        assert summary["due_soon"] >= 1
        assert summary["unknown_borrower"] == 0

        overdue = loan_manager.get_current_loans("overdue")
        assert overdue and all(l["is_overdue"] and l["overdue_days"] >= 1 for l in overdue)
        assert all(l["est_fine"] == l["overdue_days"] * 1.00 for l in overdue)

        soon = loan_manager.get_current_loans("due_soon")
        assert all(not l["is_overdue"] and l["days_left"] < 3 for l in soon)

    def test_tc_loan_03_overdue_loans_listed_first(self, loan_manager):
        loans = loan_manager.get_current_loans()
        dues = [l["due_at"] for l in loans]
        assert dues == sorted(dues)
        assert loans[0]["is_overdue"]

    def test_tc_loan_04_borrower_is_not_someone_waiting_in_the_hold_queue(self, loan_manager):
        loan = next(l for l in loan_manager.get_current_loans() if l["isbn"] == CLEAN_CODE)
        assert loan["member_id"] != "PES1UG24AM084"
        assert loan["queue_length"] == 1

    def test_tc_loan_05_search_by_borrower_or_title(self, loan_manager):
        some = loan_manager.get_current_loans()[0]
        by_name = loan_manager.get_current_loans(query=some["member_name"])
        assert by_name and all(l["member_name"] == some["member_name"] for l in by_name)
        by_title = loan_manager.get_current_loans(query="Clean Code")
        assert [l["isbn"] for l in by_title] == [CLEAN_CODE]
        assert loan_manager.get_current_loans(query="zzz-no-such-thing") == []


class TestCheckoutAndReturn:

    def test_tc_loan_06_checkout_creates_loan_and_marks_checked_out(self, loan_manager, in_memory_db):
        ok, loan, err = loan_manager.checkout(CLEAN_ARCH, "PES1UG24AM094", "LIB-HEAD-001", loan_days=21)
        assert ok, err
        assert loan["memberName"] == "Divyansh"
        assert abs((loan["dueAt"] - loan["checkedOutAt"]) - 21 * DAY_SECONDS) < 1
        status = in_memory_db.fetchone("SELECT status FROM titles WHERE isbn = ?", (CLEAN_ARCH,))[0]
        assert status == "CheckedOut"
        current = [l for l in loan_manager.get_current_loans() if l["isbn"] == CLEAN_ARCH]
        assert current[0]["member_id"] == "PES1UG24AM094" and current[0]["days_left"] == 21

    def test_tc_loan_07_checkout_rules(self, loan_manager):
        assert loan_manager.checkout("978-9999999999", "PES1UG24AM094", "LIB")[2] == "TITLE_NOT_FOUND"
        assert loan_manager.checkout(CLEAN_ARCH, "NOBODY", "LIB")[2] == "MEMBER_NOT_FOUND"
        assert loan_manager.checkout(CLEAN_ARCH, "LIB-HEAD-001", "LIB")[2] == "MEMBER_NOT_FOUND"
        assert loan_manager.checkout(CLEAN_CODE, "PES1UG24AM094", "LIB")[2] == "TITLE_ALREADY_CHECKED_OUT"
        # Invalid loan period falls back to 14 days; hyphen-less ISBN is accepted
        ok, loan, _ = loan_manager.checkout("9780134494166", "PES1UG24AM094", "LIB", loan_days=999)
        assert ok and loan["loanDays"] == 14 and loan["isbn"] == CLEAN_ARCH

    def test_tc_loan_08_fine_blocked_student_cannot_borrow(self, loan_manager, fine_manager):
        fine_manager.assess_overdue_fine("PES1UG24AM087", CLEAN_CODE, 25)
        assert loan_manager.checkout(HEAD_FIRST, "PES1UG24AM087", "LIB")[2] == "BORROWER_BLOCKED_UNPAID_FINES"

    def test_tc_loan_09_return_closes_loan_and_ready_hold_is_reserved(
        self, loan_manager, reservation_manager, in_memory_db
    ):
        borrower = next(l for l in loan_manager.get_current_loans() if l["isbn"] == CLEAN_CODE)["member_id"]
        ok, res, _ = reservation_manager.mark_title_returned(CLEAN_CODE, "LIB-HEAD-001")
        assert ok
        assert res["returnedBy"] == borrower
        assert res["holdReadyFor"] == "PES1UG24AM084"
        assert not [l for l in loan_manager.get_current_loans() if l["isbn"] == CLEAN_CODE]
        open_loans = in_memory_db.fetchone(
            "SELECT COUNT(*) FROM loans WHERE isbn = ? AND returned_at IS NULL", (CLEAN_CODE,))[0]
        assert open_loans == 0

        # The Ready hold reserves the copy for PES1UG24AM084 only
        assert loan_manager.checkout(CLEAN_CODE, "PES1UG24AM094", "LIB")[2] == "RESERVED_FOR_ANOTHER_MEMBER"
        ok, loan, _ = loan_manager.checkout(CLEAN_CODE, "PES1UG24AM084", "LIB")
        assert ok and loan["holdFulfilled"]
        state = in_memory_db.fetchone(
            "SELECT state FROM holds WHERE isbn = ? AND member_id = 'PES1UG24AM084'", (CLEAN_CODE,))[0]
        assert state == "Fulfilled"

    def test_tc_loan_10_late_return_reports_overdue_days(self, loan_manager, reservation_manager, in_memory_db):
        loan_manager.checkout(HEAD_FIRST, "PES1UG24AM094", "LIB")
        in_memory_db.execute(
            "UPDATE loans SET due_at = ? WHERE isbn = ? AND returned_at IS NULL",
            (time.time() - 4 * DAY_SECONDS, HEAD_FIRST)
        )
        _, res, _ = reservation_manager.mark_title_returned(HEAD_FIRST, "LIB-HEAD-001")
        assert res["returnedBy"] == "PES1UG24AM094" and res["overdueDays"] == 4

    def test_tc_loan_11_admin_methods_require_librarian(self, admin_service, librarian_token, student_token):
        assert admin_service.get_current_loans(student_token)[2] == "FORBIDDEN"
        assert admin_service.get_loan_summary(student_token)[2] == "FORBIDDEN"
        assert admin_service.checkout_book(CLEAN_ARCH, "PES1UG24AM094", student_token)[2] == "FORBIDDEN"

        ok, loans, _ = admin_service.get_current_loans(librarian_token, "overdue")
        assert ok and all(l["is_overdue"] for l in loans)
        assert admin_service.get_loan_summary(librarian_token)[0]
        ok, loan, _ = admin_service.checkout_book(CLEAN_ARCH, "PES1UG24AM094", librarian_token)
        assert ok and loan["memberId"] == "PES1UG24AM094"


class TestLoanRoutes:

    def test_dashboard_shows_current_loans(self, client, librarian_headers):
        r = client.get("/admin/dashboard", headers=librarian_headers)
        html = r.data.decode("utf-8")
        assert r.status_code == 200
        assert "Current Loans: Who Has What" in html
        assert "Overdue" in html and "Est. fine" in html
        assert "Check Out Book to Student" in html

    def test_dashboard_overdue_filter_and_search(self, client, librarian_headers):
        r = client.get("/admin/dashboard?loans=overdue", headers=librarian_headers)
        assert b"that are overdue" in r.data
        r = client.get("/admin/dashboard?lq=Clean+Code", headers=librarian_headers)
        assert b"Showing 1 loan(s) matching" in r.data

    def test_api_loans_and_checkout(self, client, librarian_headers, student_headers):
        assert client.get("/api/v1/loans", headers=student_headers).status_code == 403
        r = client.get("/api/v1/loans?filter=overdue", headers=librarian_headers)
        body = r.get_json()
        assert r.status_code == 200 and body["summary"]["overdue"] == len(body["loans"])

        assert client.post("/api/v1/loans", json={"isbn": CLEAN_ARCH, "memberId": "PES1UG24AM094"},
                           headers=student_headers).status_code == 403
        r = client.post("/api/v1/loans", json={"isbn": CLEAN_ARCH, "memberId": "PES1UG24AM094", "days": "x"},
                        headers=librarian_headers)
        assert r.status_code == 201 and r.get_json()["loanDays"] == 14
        r = client.post("/api/v1/loans", json={"isbn": CLEAN_ARCH, "memberId": "PES1UG24AM094"},
                        headers=librarian_headers)
        assert r.status_code == 409 and r.get_json()["error"] == "TITLE_ALREADY_CHECKED_OUT"
        r = client.post("/api/v1/loans", json={"isbn": HEAD_FIRST, "memberId": "NOBODY"},
                        headers=librarian_headers)
        assert r.status_code == 404

    def test_return_route_reports_borrower(self, client, librarian_headers):
        r = client.post(f"/api/v1/titles/{CLEAN_CODE}/return", headers=librarian_headers)
        body = r.get_json()
        assert r.status_code == 200 and body["returnedBy"] and body["returnedByName"]
