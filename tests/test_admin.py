"""
Unit and Integration Tests for Librarian Administration Component.
Verifies:
- TC-ADM-01: Mark title returned, status to Available, first hold promoted to Ready
- TC-ADM-02: Hold demand report ranking titles by queue length
- TC-ADM-03: Add and edit catalog entries
- RBAC validation: student role blocked with 403 Forbidden
"""

import pytest
from src.admin import LibrarianAdminService
from src.reservation_manager import ReservationManager


class TestLibrarianAdmin:

    def test_tc_adm_01_mark_returned_and_promote_hold(self, admin_service: LibrarianAdminService, librarian_token: str):
        """TC-ADM-01: Marking a title returned sets status Available and promotes first hold to Ready."""
        isbn = "978-0132350884"

        # The seeded database has one active hold on Clean Code by PES1UG24AM084
        ok, res, err = admin_service.mark_returned(isbn, token=librarian_token)
        assert ok is True
        assert err is None
        assert res["status"] == "Available"
        assert res["holdReadyFor"] == "PES1UG24AM084"

    def test_tc_adm_02_hold_demand_report(self, admin_service: LibrarianAdminService, librarian_token: str):
        """TC-ADM-02: Demand report lists titles ranked by descending queue length."""
        ok, report, err = admin_service.get_demand_report(token=librarian_token)
        assert ok is True
        assert err is None
        assert len(report) >= 10

        # Verify sorted descending by queue length
        for i in range(len(report) - 1):
            assert report[i]["queueLength"] >= report[i + 1]["queueLength"]

    def test_tc_adm_03_add_and_edit_catalog_entry(self, admin_service: LibrarianAdminService, librarian_token: str):
        """TC-ADM-03: Add new entry and edit existing entry; saved and searchable."""
        new_isbn = "978-0134757599"
        title = "Refactoring: Improving the Design of Existing Code (2nd Ed.)"
        author = "Martin Fowler"
        publisher = "Addison-Wesley"
        year = 2018

        # Add title
        add_ok, res_isbn, _ = admin_service.add_book(
            isbn=new_isbn,
            title=title,
            author=author,
            publisher=publisher,
            year=year,
            status="Available",
            token=librarian_token
        )
        assert add_ok is True
        assert res_isbn == new_isbn

        # Search new title
        search_ok, search_res, _ = admin_service.catalog.search(query=new_isbn, search_type="isbn")
        assert search_ok is True
        assert search_res["results"][0]["title"] == title

        # Edit title
        updated_title = "Refactoring: Improving Code Design (Updated Ed.)"
        edit_ok, _ = admin_service.edit_book(
            isbn=new_isbn,
            title=updated_title,
            author=author,
            publisher=publisher,
            year=2019,
            token=librarian_token
        )
        assert edit_ok is True

        # Verify edit persisted
        _, detail, _ = admin_service.catalog.get_book_details(new_isbn)
        assert detail["title"] == updated_title
        assert detail["year"] == 2019

    def test_admin_rbac_blocked_for_student(self, admin_service: LibrarianAdminService, student_token: str):
        """Student token rejected with 403 / FORBIDDEN for administrative actions."""
        # Student tries to mark returned
        ok, res, err = admin_service.mark_returned("978-0132350884", token=student_token)
        assert ok is False
        assert err == "FORBIDDEN"

        # Student tries to add book
        add_ok, _, add_err = admin_service.add_book(
            isbn="978-1111111111",
            title="Unauthorized Book",
            author="Hacker",
            publisher="None",
            year=2026,
            status="Available",
            token=student_token
        )
        assert add_ok is False
        assert add_err == "FORBIDDEN"
