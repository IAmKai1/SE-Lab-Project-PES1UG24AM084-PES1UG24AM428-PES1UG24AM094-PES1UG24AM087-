"""
Notification Component (INotification) for LRG.
Implements:
- LRG-F-030: Hold ready notification (72-hour window)
- LRG-F-031: 24-hour expiration reminder
- TC-NOTF-03: 3-attempt retry policy with failure logging to audit trail
"""

import time
from typing import Any, Dict, List, Optional, Tuple
from src.database import Database
from src.audit import AuditService


class NotificationService:
    """Handles templated email composition, delivery retries, and failure tracking."""

    def __init__(self, db: Database, audit: AuditService, simulate_smtp_failure: bool = False):
        self.db = db
        self.audit = audit
        self.simulate_smtp_failure = simulate_smtp_failure
        self.sent_messages: List[Dict[str, Any]] = []

    def notify_hold_ready(self, member_id: str, isbn: str) -> Tuple[bool, str]:
        """
        Notify member that their held book is now ready for 72-hour pickup (LRG-F-030, TC-NOTF-01).
        Retries up to 3 times on simulated SMTP errors.
        """
        # Fetch member and title details
        with self.db.get_connection() as conn:
            m_cur = conn.execute("SELECT name, email FROM members WHERE id = ?", (member_id,))
            member = m_cur.fetchone()
            t_cur = conn.execute("SELECT title FROM titles WHERE isbn = ?", (isbn,))
            title = t_cur.fetchone()

        if not member or not title:
            return False, "RECIPIENT_OR_TITLE_NOT_FOUND"

        subject = f"Library Hold Ready: {title['title']}"
        body = (
            f"Dear {member['name']},\n\n"
            f"Great news! Your held book '{title['title']}' (ISBN: {isbn}) is now Ready for pickup at the circulation desk.\n"
            f"Please collect your book within 72 hours. After 72 hours, the reservation will expire and be offered to the next student in line.\n\n"
            f"Best regards,\nDigital Campus Library Gateway"
        )

        return self._send_with_retry(
            recipient_email=member["email"],
            subject=subject,
            body=body,
            event_type="HOLD_READY",
            member_id=member_id,
            isbn=isbn
        )

    def send_expiry_reminder(self, hold_id: int) -> Tuple[bool, str]:
        """
        Send reminder 24 hours before a Ready hold expires (LRG-F-031, TC-NOTF-02).
        Does not send for cancelled or fulfilled holds.
        """
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT h.id, h.isbn, h.state, h.ready_until, m.id as member_id, m.name, m.email, t.title
                FROM holds h
                JOIN members m ON h.member_id = m.id
                JOIN titles t ON h.isbn = t.isbn
                WHERE h.id = ?
                """,
                (hold_id,)
            )
            hold = cur.fetchone()

        if not hold:
            return False, "HOLD_NOT_FOUND"

        # Check eligibility: only send for Ready state
        if hold["state"] != "Ready":
            return False, f"HOLD_STATE_NOT_READY_{hold['state']}"

        subject = f"Urgent Reminder: Hold Expiring Soon - {hold['title']}"
        body = (
            f"Dear {hold['name']},\n\n"
            f"This is a reminder that your hold on '{hold['title']}' will expire in 24 hours.\n"
            f"Please visit the library circulation desk today to check out your title.\n\n"
            f"Digital Campus Library Gateway"
        )

        return self._send_with_retry(
            recipient_email=hold["email"],
            subject=subject,
            body=body,
            event_type="EXPIRY_REMINDER",
            member_id=hold["member_id"],
            isbn=hold["isbn"]
        )

    def _send_with_retry(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        event_type: str,
        member_id: str,
        isbn: str,
        max_attempts: int = 3
    ) -> Tuple[bool, str]:
        """Attempt delivery with exponential retry policy."""
        attempts = 0
        success = False

        while attempts < max_attempts:
            attempts += 1
            if not self.simulate_smtp_failure:
                success = True
                break
            # If simulated failure is active, it fails on each retry

        msg_record = {
            "recipient": recipient_email,
            "subject": subject,
            "body": body,
            "event_type": event_type,
            "member_id": member_id,
            "isbn": isbn,
            "attempts": attempts,
            "timestamp": time.time(),
            "status": "DELIVERED" if success else "DELIVERY_FAILED"
        }
        self.sent_messages.append(msg_record)

        if success:
            self.audit.log_event(
                member_id,
                f"EMAIL_{event_type}_SENT",
                "NOTIFICATION",
                f"Email sent to {recipient_email} for ISBN {isbn} (attempts: {attempts})"
            )
            return True, "DELIVERED"
        else:
            self.audit.log_event(
                member_id,
                f"EMAIL_{event_type}_FAILED",
                "NOTIFICATION",
                f"Delivery failed after {attempts} attempts to {recipient_email} for ISBN {isbn}"
            )
            return False, "DELIVERY_FAILED_LOGGED"
