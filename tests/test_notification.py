"""
Unit and Integration Tests for Notification Component.
Verifies:
- TC-NOTF-01: Return held title & hold-ready email dispatch (72-hour window)
- TC-NOTF-02: 24-hour expiration reminder notification
- TC-NOTF-03: Delivery retry policy (3 attempts) & failure logging
"""

import pytest
from src.notification import NotificationService
from src.reservation_manager import ReservationManager


class TestNotification:

    def test_tc_notf_01_notify_hold_ready(self, notification_service: NotificationService):
        """TC-NOTF-01: When held title becomes Ready, email naming title and 72h window reaches member."""
        member_id = "PES1UG24AM428"
        isbn = "978-0132350884"

        ok, msg = notification_service.notify_hold_ready(member_id, isbn)
        assert ok is True
        assert msg == "DELIVERED"
        assert len(notification_service.sent_messages) == 1

        sent = notification_service.sent_messages[0]
        assert sent["recipient"] == "abbey6128@gmail.com"
        assert "Clean Code" in sent["subject"]
        assert "72 hours" in sent["body"]

    def test_tc_notf_02_send_expiry_reminder(self, reservation_manager: ReservationManager, notification_service: NotificationService):
        """TC-NOTF-02: Reminder sent 24 hours before Ready hold expires; none sent for cancelled holds."""
        isbn = "978-0135974445"
        member_id = "PES1UG24AM094"

        # Place hold
        ok_hold, res, _ = reservation_manager.place_hold(isbn, member_id)
        hold_id = res["holdId"]

        # Attempt reminder on Active hold: should be rejected
        ok_rem_active, err = notification_service.send_expiry_reminder(hold_id)
        assert ok_rem_active is False
        assert "HOLD_STATE_NOT_READY" in err

        # Mark title returned to promote to Ready
        reservation_manager.mark_title_returned(isbn, "LIB-HEAD-001")

        # Now send reminder: should succeed!
        ok_rem, msg = notification_service.send_expiry_reminder(hold_id)
        assert ok_rem is True
        assert msg == "DELIVERED"

        # Cancel hold
        reservation_manager.cancel_hold(hold_id, member_id)

        # Attempt reminder on Cancelled hold: should be rejected
        ok_rem_canc, err_canc = notification_service.send_expiry_reminder(hold_id)
        assert ok_rem_canc is False
        assert "HOLD_STATE_NOT_READY_Cancelled" in err_canc

    def test_tc_notf_03_retry_policy_on_failure(self, in_memory_db, audit_service):
        """TC-NOTF-03 (Sprint update): Retries 3 times on SMTP failure, then logs failure to audit trail."""
        failing_notifier = NotificationService(in_memory_db, audit_service, simulate_smtp_failure=True)

        ok, msg = failing_notifier.notify_hold_ready("PES1UG24AM084", "978-0132350884")
        assert ok is False
        assert msg == "DELIVERY_FAILED_LOGGED"

        # Verify 3 attempts occurred
        assert len(failing_notifier.sent_messages) == 1
        record = failing_notifier.sent_messages[0]
        assert record["attempts"] == 3
        assert record["status"] == "DELIVERY_FAILED"

        # Verify logged in audit trail
        logs = audit_service.get_logs(action="EMAIL_HOLD_READY_FAILED")
        assert len(logs) >= 1
        assert "Delivery failed after 3 attempts" in logs[0]["details"]
