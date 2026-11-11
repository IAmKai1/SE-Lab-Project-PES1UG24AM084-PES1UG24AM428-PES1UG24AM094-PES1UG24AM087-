"""
Librarian Administration Component for LRG.
Implements:
- LRG-F-040: Mark title returned & promote hold
- LRG-F-041: Hold demand report
- LRG-F-042: Add and edit catalog entries
- LRG-F-012: Enforce Head Librarian role (Student calls return 403 Forbidden)
- LRG-NF-007: Audit trail inspection
"""

from typing import Any, Dict, List, Optional, Tuple
from src.catalog_search import CatalogSearchService
from src.reservation_manager import ReservationManager
from src.audit import AuditService
from src.auth import AuthenticationManager
from src.loan_manager import LoanManager


class LibrarianAdminService:
    """Consolidates administrative actions for the Head Librarian with strict role checks."""

    def __init__(
        self,
        catalog_service: CatalogSearchService,
        reservation_manager: ReservationManager,
        audit_service: AuditService,
        auth_manager: AuthenticationManager,
        loan_manager: Optional[LoanManager] = None
    ):
        self.catalog = catalog_service
        self.reservation = reservation_manager
        self.audit = audit_service
        self.auth = auth_manager
        self.loans = loan_manager or LoanManager(
            reservation_manager.db, audit_service, reservation_manager.fine_manager
        )

    def _verify_librarian(self, token: Optional[str]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Verify session and enforce Head Librarian role (LRG-F-012, LRG-SR-003)."""
        valid, user, err = self.auth.require_role(token, "librarian")
        if not valid:
            return False, None, err
        return True, user, None

    def mark_returned(self, isbn: str, token: Optional[str]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Librarian endpoint: Return title and advance queue (LRG-F-040, TC-ADM-01)."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err

        return self.reservation.mark_title_returned(isbn, user["member_id"])

    def add_book(
        self,
        isbn: str,
        title: str,
        author: str,
        publisher: str,
        year: int,
        status: str,
        token: Optional[str],
        subject: str = "General",
        difficulty: str = "Intermediate"
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Librarian endpoint: Add new title to catalog (LRG-F-042, TC-ADM-03)."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err

        ok, isbn_res, add_err = self.catalog.add_title(
            isbn, title, author, publisher, year, status, subject=subject, difficulty=difficulty
        )
        if ok:
            self.audit.log_event(user["member_id"], "ADD_CATALOG_ENTRY", "TITLES", f"Added '{title}' (ISBN: {isbn})")
        return ok, isbn_res, add_err

    def edit_book(
        self,
        isbn: str,
        title: str,
        author: str,
        publisher: str,
        year: int,
        token: Optional[str],
        subject: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Librarian endpoint: Edit existing title metadata (LRG-F-042, TC-ADM-03)."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, err

        ok, edit_err = self.catalog.edit_title(
            isbn, title, author, publisher, year, subject=subject, difficulty=difficulty
        )
        if ok:
            self.audit.log_event(user["member_id"], "EDIT_CATALOG_ENTRY", "TITLES", f"Updated metadata for ISBN {isbn}")
        return ok, edit_err

    def get_demand_report(self, token: Optional[str]) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """Librarian endpoint: Retrieve hold demand rankings (LRG-F-041, TC-ADM-02)."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err

        report = self.reservation.get_demand_report()
        return True, report, None

    def get_audit_trail(self, token: Optional[str], limit: int = 100) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """Librarian endpoint: View system audit trail (LRG-NF-007, TC-AUD-01)."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err

        logs = self.audit.get_logs(limit=limit)
        return True, logs, None

    def get_current_loans(
        self,
        token: Optional[str],
        status_filter: str = "all",
        query: str = ""
    ) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """Librarian endpoint: who has each checked-out title and when it is due back."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err
        return True, self.loans.get_current_loans(status_filter, query), None

    def get_loan_summary(self, token: Optional[str]) -> Tuple[bool, Optional[Dict[str, int]], Optional[str]]:
        """Librarian endpoint: counts of checked-out, overdue and due-soon titles."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err
        return True, self.loans.get_summary(), None

    def checkout_book(
        self,
        isbn: str,
        member_id: str,
        token: Optional[str],
        loan_days: int = 14
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Librarian endpoint: lend an Available title to a student."""
        auth_ok, user, err = self._verify_librarian(token)
        if not auth_ok:
            return False, None, err
        return self.loans.checkout(isbn, member_id, user["member_id"], loan_days)
