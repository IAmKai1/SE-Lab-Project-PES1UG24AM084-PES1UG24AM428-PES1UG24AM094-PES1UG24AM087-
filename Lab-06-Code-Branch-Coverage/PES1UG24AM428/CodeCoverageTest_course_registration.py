import pytest
from course_registration import can_register, waitlist_position, late_fee

# ==============================================================================
# Code Coverage Test Suite (Statement / Line Coverage Focus >= 90%)
# ==============================================================================

def test_can_register_valid():
    assert can_register('regular', 16, 4, True) == 'registered'

def test_can_register_unknown_status():
    with pytest.raises(ValueError, match='unknown status'):
        can_register('freshman', 10, 4, True)

def test_can_register_invalid_credits():
    with pytest.raises(ValueError, match='invalid course credits'):
        can_register('regular', 10, -2, True)

def test_can_register_missing_prereqs():
    assert can_register('regular', 10, 4, False) == 'prerequisites missing'

def test_can_register_credit_limit_exceeded():
    assert can_register('regular', 22, 4, True) == 'credit limit exceeded'

def test_waitlist_invalid_capacity():
    with pytest.raises(ValueError, match='invalid capacity'):
        waitlist_position(10, 0, 0)

def test_waitlist_seat_available():
    assert waitlist_position(20, 30, 0) == 0

def test_waitlist_full():
    assert waitlist_position(30, 30, 10) == -1

def test_waitlist_placed():
    assert waitlist_position(30, 30, 4) == 5

def test_late_fee_on_time():
    assert late_fee(0, 15, False) == 0

def test_late_fee_waiver():
    assert late_fee(5, 15, True) == 0

def test_late_fee_week_one():
    assert late_fee(5, 15, False) == 500

def test_late_fee_beyond_week_one_with_surcharge_capped():
    # days_late=25, credits=25 -> fee = 500 + 1800 + 250 = 2550 -> capped to 2000
    assert late_fee(25, 25, False) == 2000
