"""
Unit and Integration Tests for Reservation Manager Component.
Verifies:
- TC-HOLD-01: Place hold on CheckedOut book and return queue position
- TC-HOLD-02: Rejection of holds on Available titles & duplicate holds
- TC-HOLD-03: View and cancel member active holds
- TC-HOLD-04: Queue progression after cancellation
- TC-HOLD-05: 5 active holds limit enforcement
- TC-HOLD-06: 72-hour Ready hold expiration & automatic cascade promotion
"""

import time
import pytest
from src.reservation_manager import ReservationManager


class TestReservationManager:

    def test_tc_hold_01_place_hold_checkedout_title(self, reservation_manager: ReservationManager):
        """TC-HOLD-01: Place a hold on a CheckedOut title, returns queue position."""
        # Book '978-0201633610' is CheckedOut
        ok, res, err = reservation_manager.place_hold("978-0201633610", "PES1UG24AM094")
        assert ok is True
        assert err is None
        assert res["holdId"] is not None
        assert res["position"] >= 1
        assert res["state"] == "Active"

    def test_tc_hold_02_reject_available_and_duplicate(self, reservation_manager: ReservationManager):
        """TC-HOLD-02: Reject hold on Available title, and reject duplicate hold by same user."""
        # 1. Hold on Available book ('978-0134494166')
        ok, res, err = reservation_manager.place_hold("978-0134494166", "PES1UG24AM094")
        assert ok is False
        assert err == "TITLE_AVAILABLE"

        # 2. Place valid hold on CheckedOut book
        ok1, res1, _ = reservation_manager.place_hold("978-0321125217", "PES1UG24AM094")
        assert ok1 is True

        # Attempt second hold on same book by same member
        ok2, res2, err2 = reservation_manager.place_hold("978-0321125217", "PES1UG24AM094")
        assert ok2 is False
        assert err2 == "DUPLICATE_HOLD"

    def test_tc_hold_03_view_and_cancel_active_hold(self, reservation_manager: ReservationManager):
        """TC-HOLD-03: View member holds and cancel active hold."""
        member_id = "PES1UG24AM087"
        isbn = "978-1449373320"

        ok, hold_info, _ = reservation_manager.place_hold(isbn, member_id)
        assert ok is True
        hold_id = hold_info["holdId"]

        # View holds
        my_holds = reservation_manager.get_member_holds(member_id)
        assert any(h["holdId"] == hold_id for h in my_holds)

        # Cancel hold
        cancel_ok, err = reservation_manager.cancel_hold(hold_id, member_id)
        assert cancel_ok is True

        # Verify hold is no longer active in member view
        my_holds_after = reservation_manager.get_member_holds(member_id)
        assert not any(h["holdId"] == hold_id for h in my_holds_after)

    def test_tc_hold_04_queue_position_progression_after_cancellation(self, reservation_manager: ReservationManager):
        """TC-HOLD-04: Positions behind a cancelled hold move up by 1."""
        isbn = "978-0321751041"  # CheckedOut book

        # Three students queue up
        ok1, res1, _ = reservation_manager.place_hold(isbn, "PES1UG24AM084")
        ok2, res2, _ = reservation_manager.place_hold(isbn, "PES1UG24AM094")
        ok3, res3, _ = reservation_manager.place_hold(isbn, "PES1UG24AM087")

        assert res1["position"] == 1
        assert res2["position"] == 2
        assert res3["position"] == 3

        # First student cancels hold
        cancel_ok, _ = reservation_manager.cancel_hold(res1["holdId"], "PES1UG24AM084")
        assert cancel_ok is True

        # Second student should now be #1, third student should now be #2
        holds2 = reservation_manager.get_member_holds("PES1UG24AM094")
        target2 = next(h for h in holds2 if h["holdId"] == res2["holdId"])
        assert target2["position"] == 1

        holds3 = reservation_manager.get_member_holds("PES1UG24AM087")
        target3 = next(h for h in holds3 if h["holdId"] == res3["holdId"])
        assert target3["position"] == 2

    def test_tc_hold_05_five_hold_limit(self, reservation_manager: ReservationManager):
        """TC-HOLD-05: 6th active hold request is rejected with limit message."""
        member_id = "PES1UG24AM094"

        # Checked out titles:
        checked_out_isbns = [
            "978-0132350884",
            "978-0201633610",
            "978-0321125217",
            "978-0135974445",
            "978-1449373320"
        ]

        # Place 5 holds
        for isbn in checked_out_isbns:
            ok, res, _ = reservation_manager.place_hold(isbn, member_id)
            assert ok is True

        # Attempt 6th hold on '978-0321751041'
        ok6, res6, err6 = reservation_manager.place_hold("978-0321751041", member_id)
        assert ok6 is False
        assert err6 == "HOLD_LIMIT_REACHED"

    def test_tc_hold_06_ready_expiration_and_cascade_promotion(self, reservation_manager: ReservationManager):
        """TC-HOLD-06 (Sprint-3): Ready holds older than 72 hours expire, auto-promoting next student."""
        isbn = "978-0130661029"

        # Queue student 1 and student 2
        ok1, res1, _ = reservation_manager.place_hold(isbn, "PES1UG24AM084")
        ok2, res2, _ = reservation_manager.place_hold(isbn, "PES1UG24AM094")

        # Librarian marks book returned, promoting student 1 to Ready
        reservation_manager.mark_title_returned(isbn, "LIB-HEAD-001")

        # Verify student 1 hold is 'Ready'
        with reservation_manager.db.get_connection() as conn:
            cur = conn.execute("SELECT state FROM holds WHERE id = ?", (res1["holdId"],))
            assert cur.fetchone()["state"] == "Ready"

            # Simulate expiration: fast-forward time past 72 hours
            conn.execute(
                "UPDATE holds SET ready_until = ? WHERE id = ?",
                (time.time() - 100, res1["holdId"])
            )
            conn.commit()

        # Run background expiry maintenance
        expired = reservation_manager.expire_overdue_ready_holds()
        assert len(expired) == 1
        assert expired[0]["expired_hold_id"] == res1["holdId"]

        # Student 2 should now be promoted to Ready
        with reservation_manager.db.get_connection() as conn:
            cur2 = conn.execute("SELECT state FROM holds WHERE id = ?", (res2["holdId"],))
            assert cur2.fetchone()["state"] == "Ready"

    def test_hold_nonexistent_title(self, reservation_manager: ReservationManager):
        ok, res, err = reservation_manager.place_hold("978-0000000000", "PES1UG24AM094")
        assert ok is False
        assert err == "TITLE_NOT_FOUND"

    def test_cancel_nonexistent_hold(self, reservation_manager: ReservationManager):
        ok, err = reservation_manager.cancel_hold(999999, "PES1UG24AM094")
        assert ok is False
        assert err == "HOLD_NOT_FOUND"

    def test_cancel_other_member_hold_unauthorized(self, reservation_manager: ReservationManager):
        ok, res, _ = reservation_manager.place_hold("978-0201633610", "PES1UG24AM084")
        hold_id = res["holdId"]

        # Member PES1UG24AM094 attempts to cancel PES1UG24AM084's hold
        ok_cancel, err = reservation_manager.cancel_hold(hold_id, "PES1UG24AM094", is_admin=False)
        assert ok_cancel is False
        assert err == "FORBIDDEN_NOT_OWNER"
