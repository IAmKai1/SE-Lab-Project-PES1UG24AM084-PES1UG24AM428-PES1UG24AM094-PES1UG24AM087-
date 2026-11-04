"""
Reservation Manager Component (IReservation) for LRG.
Implements:
- LRG-F-020: Place hold on CheckedOut title with queue position
- LRG-F-021: Reject hold on Available title or duplicate active hold
- LRG-F-022: View & cancel member's active holds
- LRG-F-023: Dynamic queue position calculation and progression
- LRG-F-024: 5 active holds limit per member
- LRG-F-040: Return title and promote first hold to Ready (72-hour pickup window)
- LRG-F-041: Hold demand report ranking titles by queue length
- TC-HOLD-06: Automatic 72-hour Ready expiration & cascade promotion
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from src.database import Database
from src.audit import AuditService
from src.notification import NotificationService
from src.fine_manager import FineManager


MAX_ACTIVE_HOLDS = 5
READY_HOLD_WINDOW = 72 * 3600  # 72 hours in seconds


class ReservationManager:
    """Coordinates hold placements, queue sequencing, status transitions, and hold reports."""

    def __init__(
        self,
        db: Database,
        audit: AuditService,
        notification: NotificationService,
        fine_manager: Optional[FineManager] = None
    ):
        self.db = db
        self.audit = audit
        self.notification = notification
        self.fine_manager = fine_manager

    def place_hold(self, isbn: str, member_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Place a hold on a checked-out book (LRG-F-020, TC-HOLD-01).
        Enforces:
        - Book must exist (404)
        - Book must be CheckedOut (LRG-F-021: reject Available)
        - Member cannot have duplicate active/ready hold on same title (LRG-F-021)
        - Member active holds <= 5 (LRG-F-024)
        - Member must not be blocked by unpaid fines (UC-04)
        """
        now = time.time()
        with self.db.get_connection() as conn:
            # 1. Check title existence & status
            t_cur = conn.execute("SELECT isbn, title, status FROM titles WHERE isbn = ?", (isbn,))
            title = t_cur.fetchone()
            if not title:
                # Try normalized match
                clean = isbn.strip().replace("-", "").replace(" ", "")
                t_cur = conn.execute("SELECT isbn, title, status FROM titles WHERE REPLACE(REPLACE(isbn, '-', ''), ' ', '') = ?", (clean,))
                title = t_cur.fetchone()

            if not title:
                return False, None, "TITLE_NOT_FOUND"

            if title["status"] == "Available":
                return False, None, "TITLE_AVAILABLE"

            canonical_isbn = title["isbn"]

            # 2. Check fine block if fine_manager is active
            if self.fine_manager:
                fine_info = self.fine_manager.get_member_fines(member_id)
                if fine_info["is_hold_blocked"]:
                    return False, None, "HOLD_BLOCKED_UNPAID_FINES"

            # 3. Check duplicate active/ready hold
            dup_cur = conn.execute(
                "SELECT id FROM holds WHERE isbn = ? AND member_id = ? AND state IN ('Active', 'Ready')",
                (canonical_isbn, member_id)
            )
            if dup_cur.fetchone():
                return False, None, "DUPLICATE_HOLD"

            # 4. Check active hold count limit (max 5)
            cnt_cur = conn.execute(
                "SELECT COUNT(*) FROM holds WHERE member_id = ? AND state IN ('Active', 'Ready')",
                (member_id,)
            )
            active_count = cnt_cur.fetchone()[0]
            if active_count >= MAX_ACTIVE_HOLDS:
                return False, None, "HOLD_LIMIT_REACHED"

            # 5. Insert hold
            ins_cur = conn.execute(
                "INSERT INTO holds (isbn, member_id, state, created_at) VALUES (?, ?, 'Active', ?)",
                (canonical_isbn, member_id, now)
            )
            hold_id = ins_cur.lastrowid

            # 6. Calculate queue position
            pos = self._get_queue_position(conn, canonical_isbn, hold_id)
            conn.commit()

            self.audit.log_event(
                member_id,
                "HOLD_PLACED",
                "HOLDS",
                f"Hold #{hold_id} placed on ISBN {canonical_isbn} (queue position {pos})"
            )

            result = {
                "holdId": hold_id,
                "isbn": canonical_isbn,
                "title": title["title"],
                "position": pos,
                "state": "Active",
                "createdAt": now
            }
            return True, result, None

    def cancel_hold(self, hold_id: int, member_id: str, is_admin: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Cancel an active hold (LRG-F-022, TC-HOLD-03).
        Checks ownership unless is_admin is True.
        """
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT id, isbn, member_id, state FROM holds WHERE id = ?", (hold_id,))
            hold = cur.fetchone()

            if not hold:
                return False, "HOLD_NOT_FOUND"

            # Ownership check (LRG-SR-003, TC-SEC-06)
            if not is_admin and hold["member_id"] != member_id:
                self.audit.log_event(
                    member_id,
                    "UNAUTHORIZED_HOLD_CANCELLATION",
                    "HOLDS",
                    f"Member attempted to cancel hold {hold_id} belonging to {hold['member_id']}"
                )
                return False, "FORBIDDEN_NOT_OWNER"

            if hold["state"] not in ("Active", "Ready"):
                return False, f"CANNOT_CANCEL_{hold['state']}"

            # Cancel hold
            conn.execute("UPDATE holds SET state = 'Cancelled' WHERE id = ?", (hold_id,))
            conn.commit()

            self.audit.log_event(
                member_id,
                "HOLD_CANCELLED",
                "HOLDS",
                f"Hold #{hold_id} on {hold['isbn']} cancelled by {'librarian' if is_admin else 'member'}"
            )

            # If the cancelled hold was 'Ready', automatically promote the next in line
            if hold["state"] == "Ready":
                self._promote_next_hold(conn, hold["isbn"])
                conn.commit()

            return True, None

    def get_member_holds(self, member_id: str) -> List[Dict[str, Any]]:
        """Retrieve all active & ready holds for a given member with queue positions (LRG-F-022, TC-HOLD-03)."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT h.id as holdId, h.isbn, t.title, t.author, h.state, h.created_at, h.ready_until
                FROM holds h
                JOIN titles t ON h.isbn = t.isbn
                WHERE h.member_id = ? AND h.state IN ('Active', 'Ready')
                ORDER BY h.created_at ASC
                """,
                (member_id,)
            )
            rows = cur.fetchall()
            results = []
            for r in rows:
                item = dict(r)
                if item["state"] == "Ready":
                    item["position"] = 1
                else:
                    item["position"] = self._get_queue_position(conn, item["isbn"], item["holdId"])
                results.append(item)
            return results

    def mark_title_returned(self, isbn: str, librarian_id: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Librarian marks title returned (LRG-F-040, TC-ADM-01).
        Sets title Available and promotes first active hold to Ready (72-hour window).
        Notifies student via email (LRG-F-030, TC-NOTF-01).
        """
        now = time.time()
        with self.db.get_connection() as conn:
            t_cur = conn.execute("SELECT isbn, title, status FROM titles WHERE isbn = ?", (isbn,))
            title = t_cur.fetchone()

            if not title:
                return False, None, "TITLE_NOT_FOUND"

            # Check if there are active holds waiting in queue
            hold_cur = conn.execute(
                "SELECT id, member_id FROM holds WHERE isbn = ? AND state = 'Active' ORDER BY created_at ASC LIMIT 1",
                (isbn,)
            )
            first_hold = hold_cur.fetchone()

            ready_member_id = None
            if first_hold:
                ready_until = now + READY_HOLD_WINDOW
                conn.execute(
                    "UPDATE holds SET state = 'Ready', ready_until = ? WHERE id = ?",
                    (ready_until, first_hold["id"])
                )
                ready_member_id = first_hold["member_id"]
                # Send hold-ready notification (LRG-F-030)
                self.notification.notify_hold_ready(ready_member_id, isbn)

            # Mark title status Available
            conn.execute("UPDATE titles SET status = 'Available' WHERE isbn = ?", (isbn,))
            conn.commit()

            self.audit.log_event(
                librarian_id,
                "TITLE_RETURNED",
                "TITLES",
                f"Title {isbn} marked returned. Promoted hold: {first_hold['id'] if first_hold else 'None'}"
            )

            result = {
                "isbn": isbn,
                "status": "Available",
                "holdReadyFor": ready_member_id,
                "promotedHoldId": first_hold["id"] if first_hold else None
            }
            return True, result, None

    def get_demand_report(self) -> List[Dict[str, Any]]:
        """
        Generate Hold Demand Report (LRG-F-041, TC-ADM-02).
        Ranks titles in descending order of active hold queue length.
        """
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT t.isbn, t.title, t.author, t.status,
                       COUNT(h.id) as queueLength
                FROM titles t
                LEFT JOIN holds h ON t.isbn = h.isbn AND h.state IN ('Active', 'Ready')
                GROUP BY t.isbn, t.title, t.author, t.status
                ORDER BY queueLength DESC, t.title ASC
                """
            )
            return [dict(r) for r in cur.fetchall()]

    def expire_overdue_ready_holds(self) -> List[Dict[str, Any]]:
        """
        Sprint-3 Feature (TC-HOLD-06):
        Background maintenance job: checks Ready holds that have exceeded their 72-hour window.
        Marks them 'Expired' and automatically promotes the next student in queue.
        """
        now = time.time()
        expired_records = []
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT id, isbn, member_id FROM holds WHERE state = 'Ready' AND ready_until < ?",
                (now,)
            )
            rows = cur.fetchall()
            for r in rows:
                conn.execute("UPDATE holds SET state = 'Expired' WHERE id = ?", (r["id"],))
                self.audit.log_event(
                    r["member_id"],
                    "HOLD_EXPIRED",
                    "HOLDS",
                    f"Ready hold #{r['id']} on ISBN {r['isbn']} expired after 72 hours"
                )
                # Cascade promotion
                promoted = self._promote_next_hold(conn, r["isbn"])
                expired_records.append({
                    "expired_hold_id": r["id"],
                    "isbn": r["isbn"],
                    "member_id": r["member_id"],
                    "promoted_hold": promoted
                })
            conn.commit()
        return expired_records

    def _get_queue_position(self, conn, isbn: str, hold_id: int) -> int:
        """Calculate 1-based FIFO position of an active hold."""
        # Find created_at for target hold
        cur = conn.execute("SELECT created_at FROM holds WHERE id = ?", (hold_id,))
        row = cur.fetchone()
        if not row:
            return 0
        t = row["created_at"]
        cnt_cur = conn.execute(
            "SELECT COUNT(*) FROM holds WHERE isbn = ? AND state IN ('Active', 'Ready') AND created_at <= ?",
            (isbn, t)
        )
        return cnt_cur.fetchone()[0]

    def _promote_next_hold(self, conn, isbn: str) -> Optional[Dict[str, Any]]:
        """Internal helper to promote the next active hold in line."""
        now = time.time()
        cur = conn.execute(
            "SELECT id, member_id FROM holds WHERE isbn = ? AND state = 'Active' ORDER BY created_at ASC LIMIT 1",
            (isbn,)
        )
        nxt = cur.fetchone()
        if nxt:
            ready_until = now + READY_HOLD_WINDOW
            conn.execute(
                "UPDATE holds SET state = 'Ready', ready_until = ? WHERE id = ?",
                (ready_until, nxt["id"])
            )
            self.notification.notify_hold_ready(nxt["member_id"], isbn)
            self.audit.log_event(
                nxt["member_id"],
                "HOLD_PROMOTED_CASCADE",
                "HOLDS",
                f"Hold #{nxt['id']} on {isbn} promoted to Ready"
            )
            return {"holdId": nxt["id"], "member_id": nxt["member_id"]}
        return None
