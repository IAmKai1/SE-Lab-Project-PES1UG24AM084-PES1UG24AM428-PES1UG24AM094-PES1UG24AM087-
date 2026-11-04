"""
Unit and Integration Tests for Fine Management Component (UC-04: Pay Overdue Fine).
Assigned to: Dharshini V (PES1UG24AM428).
Verifies:
- TC-FINE-01: Overdue fine assessment and balance calculation
- TC-FINE-02: Payment gateway interaction & receipt generation
- TC-FINE-03: Hold restriction enforcement and clearance upon settlement
"""

import pytest
from src.fine_manager import FineManager
from src.reservation_manager import ReservationManager


class TestFineManager:

    def test_tc_fine_01_fine_assessment_and_balance(self, fine_manager: FineManager):
        """TC-FINE-01: Correctly calculate overdue fines ($1.00/day) and retrieve student balance."""
        member_id = "PES1UG24AM094"
        isbn = "978-0132350884"

        # Assess 5 days overdue fine ($5.00)
        fine_id = fine_manager.assess_overdue_fine(member_id, isbn, overdue_days=5)
        assert fine_id > 0

        info = fine_manager.get_member_fines(member_id)
        assert info["total_unpaid"] == 5.00
        assert info["is_hold_blocked"] is False

    def test_tc_fine_02_pay_fine_and_receipt_issuance(self, fine_manager: FineManager):
        """TC-FINE-02: Settle fine via Campus Wallet, return valid digital transaction receipt."""
        member_id = "PES1UG24AM428"

        # Student PES1UG24AM428 has seeded unpaid fine ($15.00)
        info_before = fine_manager.get_member_fines(member_id)
        target_fine = info_before["fines"][0]
        fine_id = target_fine["id"]

        ok, receipt, err = fine_manager.pay_fine(
            fine_id=fine_id,
            member_id=member_id,
            payment_method="CAMPUS_WALLET"
        )
        assert ok is True
        assert err is None
        assert receipt["fine_id"] == fine_id
        assert receipt["status"] == "SETTLED"
        assert receipt["transaction_id"].startswith("TXN-")
        assert receipt["amount_paid"] == target_fine["amount"]

        # Verify balance updated
        info_after = fine_manager.get_member_fines(member_id)
        assert info_after["total_unpaid"] == 0.0

    def test_tc_fine_03_hold_blocking_and_clearance(self, reservation_manager: ReservationManager, fine_manager: FineManager):
        """TC-FINE-03: Unpaid fines exceeding $20 block reservation holds until settled."""
        member_id = "PES1UG24AM087"
        isbn_blocked = "978-0201633610"

        # Assess heavy overdue fine ($25.00 > $20.00 threshold)
        fine_id = fine_manager.assess_overdue_fine(member_id, isbn_blocked, overdue_days=25)
        assert fine_id > 0

        # Attempt to place hold: should be blocked
        ok_hold, res, err = reservation_manager.place_hold(isbn_blocked, member_id)
        assert ok_hold is False
        assert err == "HOLD_BLOCKED_UNPAID_FINES"

        # Pay off fine
        pay_ok, receipt, _ = fine_manager.pay_fine(fine_id, member_id, payment_method="UPI")
        assert pay_ok is True

        # Now place hold: should succeed!
        ok_hold_after, res_after, err_after = reservation_manager.place_hold(isbn_blocked, member_id)
        assert ok_hold_after is True
        assert err_after is None
        assert res_after["position"] >= 1

    def test_pay_fine_not_owner(self, fine_manager: FineManager):
        """Cannot pay or settle a fine on behalf of another student without authorization."""
        # Fine belongs to PES1UG24AM428
        info = fine_manager.get_member_fines("PES1UG24AM428")
        fine_id = info["fines"][0]["id"]

        # PES1UG24AM084 tries to pay PES1UG24AM428's fine
        ok, receipt, err = fine_manager.pay_fine(fine_id, member_id="PES1UG24AM084")
        assert ok is False
        assert err == "FORBIDDEN_NOT_FINE_OWNER"

    def test_pay_nonexistent_fine(self, fine_manager: FineManager):
        ok, receipt, err = fine_manager.pay_fine(999999, "PES1UG24AM428")
        assert ok is False
        assert err == "FINE_NOT_FOUND"
