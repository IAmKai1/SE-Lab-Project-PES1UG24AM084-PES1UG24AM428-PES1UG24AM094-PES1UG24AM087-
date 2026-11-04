"""
Fine Management Component (UC-04: Pay Overdue Fine) for LRG.
Assigned to: Dharshini V (PES1UG24AM428).
Implements:
- TC-FINE-01: Calculate & retrieve overdue fines for student members
- TC-FINE-02: Secure fine payment processing via external Payment Gateway stub
- TC-FINE-03: Receipt generation and hold block clearance
"""

import secrets
import time
from typing import Any, Dict, List, Optional, Tuple
from src.database import Database
from src.audit import AuditService


DAILY_OVERDUE_RATE = 1.00  # $1.00 per overdue day
MAX_FINE_BEFORE_HOLD_BLOCK = 20.00  # Block new reservations if unpaid fine >= $20


class FineManager:
    """Manages overdue fines, fee settlement, receipt issuance, and financial audit logs."""

    def __init__(self, db: Database, audit: AuditService):
        self.db = db
        self.audit = audit

    def get_member_fines(self, member_id: str) -> Dict[str, Any]:
        """Fetch all fines, total outstanding balance, and settlement status."""
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT f.id, f.isbn, t.title, f.amount, f.status, f.transaction_id, f.paid_at
                FROM fines f
                JOIN titles t ON f.isbn = t.isbn
                WHERE f.member_id = ?
                ORDER BY f.id DESC
                """,
                (member_id,)
            )
            rows = [dict(r) for r in cur.fetchall()]

            total_unpaid = sum(r["amount"] for r in rows if r["status"] == "Unpaid")
            is_blocked = total_unpaid >= MAX_FINE_BEFORE_HOLD_BLOCK

            return {
                "member_id": member_id,
                "fines": rows,
                "total_unpaid": round(total_unpaid, 2),
                "is_hold_blocked": is_blocked,
                "threshold": MAX_FINE_BEFORE_HOLD_BLOCK
            }

    def assess_overdue_fine(self, member_id: str, isbn: str, overdue_days: int) -> int:
        """Calculate and register new overdue fine based on days overdue (TC-FINE-01)."""
        if overdue_days <= 0:
            return 0
        amount = round(overdue_days * DAILY_OVERDUE_RATE, 2)
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO fines (member_id, isbn, amount, status) VALUES (?, ?, ?, 'Unpaid')",
                (member_id, isbn, amount)
            )
            conn.commit()
            fine_id = cur.lastrowid

        self.audit.log_event(
            member_id,
            "FINE_ASSESSED",
            "FINES",
            f"Assessed fine of ${amount:.2f} for ISBN {isbn} ({overdue_days} days overdue)"
        )
        return fine_id

    def pay_fine(
        self,
        fine_id: int,
        member_id: str,
        payment_method: str = "CAMPUS_WALLET",
        card_number: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Process fine settlement (TC-FINE-02, TC-FINE-03).
        Interacts with payment gateway stub, verifies ownership, updates database, and returns receipt.
        """
        now = time.time()
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT id, member_id, isbn, amount, status FROM fines WHERE id = ?",
                (fine_id,)
            )
            fine = cur.fetchone()

            if not fine:
                return False, None, "FINE_NOT_FOUND"

            # Check ownership (LRG-SR-003)
            if fine["member_id"] != member_id:
                self.audit.log_event(
                    member_id,
                    "FINE_PAYMENT_UNAUTHORIZED",
                    "FINES",
                    f"Attempted to pay fine {fine_id} belonging to {fine['member_id']}"
                )
                return False, None, "FORBIDDEN_NOT_FINE_OWNER"

            if fine["status"] == "Paid":
                return False, None, "FINE_ALREADY_PAID"

            # Payment validation (simulate gateway interaction)
            if payment_method not in ("CAMPUS_WALLET", "UPI", "CREDIT_CARD"):
                return False, None, "INVALID_PAYMENT_METHOD"

            tx_id = f"TXN-{secrets.token_hex(6).upper()}"

            conn.execute(
                "UPDATE fines SET status = 'Paid', transaction_id = ?, paid_at = ? WHERE id = ?",
                (tx_id, now, fine_id)
            )
            conn.commit()

            receipt = {
                "fine_id": fine_id,
                "member_id": member_id,
                "isbn": fine["isbn"],
                "amount_paid": fine["amount"],
                "payment_method": payment_method,
                "transaction_id": tx_id,
                "paid_at": now,
                "status": "SETTLED"
            }

            self.audit.log_event(
                member_id,
                "FINE_SETTLED",
                "FINES",
                f"Settled fine {fine_id} of ${fine['amount']:.2f} via {payment_method} (Tx: {tx_id})"
            )

            return True, receipt, None
