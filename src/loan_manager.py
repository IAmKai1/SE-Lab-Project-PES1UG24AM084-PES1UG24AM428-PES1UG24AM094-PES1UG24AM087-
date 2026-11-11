"""
Loan (Circulation) Component for LRG.
Gives the Head Librarian visibility of who has borrowed which title and when it is due back.
Implements:
- Check out an Available title to a student (default 14-day loan)
- Close the open loan when a title is returned
- Current-loans report with borrower, checkout date, due date, overdue status and estimated fine
- Loan summary counts (checked out / overdue / due soon)
"""

import time
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

from src.audit import AuditService
from src.database import Database, DEFAULT_LOAN_DAYS
from src.fine_manager import DAILY_OVERDUE_RATE, FineManager

DAY_SECONDS = 86400
DUE_SOON_DAYS = 3
ALLOWED_LOAN_DAYS = (7, 14, 21, 28)
LOAN_FILTERS = ("all", "overdue", "due_soon")


def calendar_days_between(start_ts: float, end_ts: float) -> int:
    """Whole calendar days from start to end (local dates), e.g. due 06 Nov, today 11 Nov -> 5."""
    return (date.fromtimestamp(end_ts) - date.fromtimestamp(start_ts)).days


def close_open_loan(conn, isbn: str, now: float) -> Optional[Dict[str, Any]]:
    """Mark the open loan for a title as returned. Returns who had it and how late it was."""
    loan = conn.execute(
        """
        SELECT l.id, l.member_id, l.due_at, m.name
        FROM loans l LEFT JOIN members m ON m.id = l.member_id
        WHERE l.isbn = ? AND l.returned_at IS NULL
        ORDER BY l.checked_out_at DESC LIMIT 1
        """,
        (isbn,)
    ).fetchone()
    if not loan:
        return None
    conn.execute("UPDATE loans SET returned_at = ? WHERE isbn = ? AND returned_at IS NULL", (now, isbn))
    overdue_days = max(calendar_days_between(loan["due_at"], now), 0)
    return {
        "loanId": loan["id"],
        "memberId": loan["member_id"],
        "memberName": loan["name"],
        "overdueDays": overdue_days,
    }


class LoanManager:
    """Tracks checkouts and returns so librarians can see who has what and when it is due."""

    def __init__(self, db: Database, audit: AuditService, fine_manager: Optional[FineManager] = None):
        self.db = db
        self.audit = audit
        self.fine_manager = fine_manager

    def checkout(
        self,
        isbn: str,
        member_id: str,
        librarian_id: str,
        loan_days: int = DEFAULT_LOAN_DAYS
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Lend an Available title to a student.
        Rules: title must exist and be Available; borrower must be a student;
        a title Ready for another member's hold cannot go to someone else;
        students blocked by unpaid fines cannot borrow. The borrower's own hold is fulfilled.
        """
        isbn = (isbn or "").strip()
        member_id = (member_id or "").strip()
        if loan_days not in ALLOWED_LOAN_DAYS:
            loan_days = DEFAULT_LOAN_DAYS
        now = time.time()

        with self.db.get_connection() as conn:
            title = conn.execute("SELECT isbn, title, status FROM titles WHERE isbn = ?", (isbn,)).fetchone()
            if not title:
                clean = isbn.replace("-", "").replace(" ", "")
                title = conn.execute(
                    "SELECT isbn, title, status FROM titles WHERE REPLACE(REPLACE(isbn, '-', ''), ' ', '') = ?",
                    (clean,)
                ).fetchone()
            if not title:
                return False, None, "TITLE_NOT_FOUND"
            canonical = title["isbn"]

            member = conn.execute("SELECT id, name, email, role FROM members WHERE id = ?", (member_id,)).fetchone()
            if not member or member["role"] != "student":
                return False, None, "MEMBER_NOT_FOUND"

            if title["status"] != "Available":
                return False, None, "TITLE_ALREADY_CHECKED_OUT"

            ready_for_other = conn.execute(
                "SELECT member_id FROM holds WHERE isbn = ? AND state = 'Ready' AND member_id != ?",
                (canonical, member_id)
            ).fetchone()
            if ready_for_other:
                return False, None, "RESERVED_FOR_ANOTHER_MEMBER"

            if self.fine_manager and self.fine_manager.get_member_fines(member_id)["is_hold_blocked"]:
                return False, None, "BORROWER_BLOCKED_UNPAID_FINES"

            due_at = now + loan_days * DAY_SECONDS
            cur = conn.execute(
                "INSERT INTO loans (isbn, member_id, checked_out_at, due_at) VALUES (?, ?, ?, ?)",
                (canonical, member_id, now, due_at)
            )
            loan_id = cur.lastrowid
            conn.execute("UPDATE titles SET status = 'CheckedOut' WHERE isbn = ?", (canonical,))
            fulfilled = conn.execute(
                "UPDATE holds SET state = 'Fulfilled' WHERE isbn = ? AND member_id = ? AND state IN ('Active', 'Ready')",
                (canonical, member_id)
            ).rowcount
            conn.commit()

        self.audit.log_event(
            librarian_id,
            "TITLE_CHECKED_OUT",
            "LOANS",
            f"Loan #{loan_id}: {canonical} checked out to {member_id} for {loan_days} days"
        )
        return True, {
            "loanId": loan_id,
            "isbn": canonical,
            "title": title["title"],
            "memberId": member_id,
            "memberName": member["name"],
            "checkedOutAt": now,
            "dueAt": due_at,
            "loanDays": loan_days,
            "holdFulfilled": fulfilled > 0,
        }, None

    def get_current_loans(self, status_filter: str = "all", query: str = "") -> List[Dict[str, Any]]:
        """
        Every checked-out title with its borrower and due date, most urgent first.
        status_filter: 'all', 'overdue' or 'due_soon' (due within 3 days, not yet overdue).
        query matches title, ISBN, borrower name or borrower ID.
        """
        if status_filter not in LOAN_FILTERS:
            status_filter = "all"
        query = (query or "").strip()
        now = time.time()

        sql = """
            SELECT t.isbn, t.title, t.author,
                   l.id AS loan_id, l.member_id, m.name AS member_name, m.email AS member_email,
                   l.checked_out_at, l.due_at,
                   (SELECT COUNT(*) FROM holds h WHERE h.isbn = t.isbn AND h.state IN ('Active', 'Ready')) AS queue_length
            FROM titles t
            LEFT JOIN loans l ON l.isbn = t.isbn AND l.returned_at IS NULL
            LEFT JOIN members m ON m.id = l.member_id
            WHERE t.status = 'CheckedOut'
        """
        params: List[Any] = []
        if query:
            term = f"%{query}%"
            sql += " AND (t.title LIKE ? OR t.isbn LIKE ? OR m.name LIKE ? OR l.member_id LIKE ?)"
            params.extend([term, term, term, term])
        sql += " ORDER BY (l.due_at IS NULL), l.due_at ASC, t.title ASC"

        with self.db.get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()

        loans = []
        for r in rows:
            item = dict(r)
            due = item["due_at"]
            if due is None:
                item.update(is_overdue=False, overdue_days=0, days_left=None, due_soon=False, est_fine=0.0)
            else:
                # Calendar-day rules: a loan due today is "due today", overdue from tomorrow
                days_to_due = calendar_days_between(now, due)
                overdue = days_to_due < 0
                overdue_days = -days_to_due if overdue else 0
                days_left = None if overdue else days_to_due
                item.update(
                    is_overdue=overdue,
                    overdue_days=overdue_days,
                    days_left=days_left,
                    due_soon=(not overdue and days_left is not None and days_left < DUE_SOON_DAYS),
                    est_fine=round(overdue_days * DAILY_OVERDUE_RATE, 2),
                )
            if status_filter == "overdue" and not item["is_overdue"]:
                continue
            if status_filter == "due_soon" and not item["due_soon"]:
                continue
            loans.append(item)
        return loans

    def get_summary(self) -> Dict[str, int]:
        """Counts for the dashboard tiles."""
        loans = self.get_current_loans()
        return {
            "checked_out": len(loans),
            "overdue": sum(1 for l in loans if l["is_overdue"]),
            "due_soon": sum(1 for l in loans if l["due_soon"]),
            "unknown_borrower": sum(1 for l in loans if l["loan_id"] is None),
        }

    def list_students(self) -> List[Dict[str, str]]:
        """Student IDs and names, for the checkout form's suggestions."""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT id, name FROM members WHERE role = 'student' ORDER BY name").fetchall()
        return [dict(r) for r in rows]
