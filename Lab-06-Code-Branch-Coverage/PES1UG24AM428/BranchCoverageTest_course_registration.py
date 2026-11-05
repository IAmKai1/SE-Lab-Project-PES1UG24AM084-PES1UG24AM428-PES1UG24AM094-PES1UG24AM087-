# -*- coding: utf-8 -*-
"""
Branch Coverage Test Suite for course_registration.py
Department of Computer Science & Engineering (AIML), PES University
Student: Dharshini V (PES1UG24AM428)
Course: Software Engineering Lab - Lab 6

Comprehensive branch testing targeting 100% Branch and Line coverage across
all conditional pathways, decision gates, equivalence partitions, and boundary values.
"""

import pytest
from course_registration import can_register, waitlist_position, late_fee


# ==============================================================================
# 1. can_register() - Decision & Branch Coverage
# ==============================================================================

class TestCanRegisterBranchCoverage:
    """Evaluates every decision gate of can_register() to both True and False."""

    def test_status_invalid_raises_value_error(self):
        """Branch: student_status not in MAX_CREDITS -> True"""
        with pytest.raises(ValueError, match="unknown status"):
            can_register("exchange", 10, 4, True)

    def test_status_valid_regular_proceeds(self):
        """Branch: student_status in MAX_CREDITS -> False for 'regular'"""
        assert can_register("regular", 12, 4, True) == "registered"

    def test_status_valid_probation_proceeds(self):
        """Branch: student_status in MAX_CREDITS -> False for 'probation' (limit 16)"""
        assert can_register("probation", 10, 4, True) == "registered"

    def test_status_valid_honors_proceeds(self):
        """Branch: student_status in MAX_CREDITS -> False for 'honors' (limit 28)"""
        assert can_register("honors", 20, 4, True) == "registered"

    def test_course_credits_zero_raises_value_error(self):
        """Branch: course_credits <= 0 -> True (boundary: 0)"""
        with pytest.raises(ValueError, match="invalid course credits"):
            can_register("regular", 12, 0, True)

    def test_course_credits_negative_raises_value_error(self):
        """Branch: course_credits <= 0 -> True (negative value)"""
        with pytest.raises(ValueError, match="invalid course credits"):
            can_register("regular", 12, -3, True)

    def test_course_credits_positive_proceeds(self):
        """Branch: course_credits <= 0 -> False"""
        assert can_register("regular", 10, 2, True) == "registered"

    def test_prerequisites_missing_returns_missing(self):
        """Branch: not prerequisites_met -> True"""
        assert can_register("regular", 12, 4, False) == "prerequisites missing"

    def test_prerequisites_met_proceeds(self):
        """Branch: not prerequisites_met -> False"""
        assert can_register("regular", 12, 4, True) == "registered"

    def test_credit_limit_exceeded_regular(self):
        """Branch: current + course > MAX_CREDITS -> True (21 + 4 = 25 > 24)"""
        assert can_register("regular", 21, 4, True) == "credit limit exceeded"

    def test_credit_limit_exact_boundary_regular(self):
        """Branch: current + course == MAX_CREDITS -> False (20 + 4 = 24 <= 24)"""
        assert can_register("regular", 20, 4, True) == "registered"

    def test_credit_limit_exceeded_probation(self):
        """Branch: current + course > MAX_CREDITS -> True (14 + 4 = 18 > 16)"""
        assert can_register("probation", 14, 4, True) == "credit limit exceeded"

    def test_credit_limit_exact_boundary_probation(self):
        """Branch: current + course == MAX_CREDITS -> False (12 + 4 = 16 <= 16)"""
        assert can_register("probation", 12, 4, True) == "registered"

    def test_credit_limit_exceeded_honors(self):
        """Branch: current + course > MAX_CREDITS -> True (26 + 4 = 30 > 28)"""
        assert can_register("honors", 26, 4, True) == "credit limit exceeded"

    def test_credit_limit_exact_boundary_honors(self):
        """Branch: current + course == MAX_CREDITS -> False (24 + 4 = 28 <= 28)"""
        assert can_register("honors", 24, 4, True) == "registered"


# ==============================================================================
# 2. waitlist_position() - Decision & Branch Coverage
# ==============================================================================

class TestWaitlistPositionBranchCoverage:
    """Evaluates every decision gate of waitlist_position() to both True and False."""

    def test_capacity_zero_raises_value_error(self):
        """Branch: capacity <= 0 -> True (boundary: 0)"""
        with pytest.raises(ValueError, match="invalid capacity"):
            waitlist_position(10, 0, 0)

    def test_capacity_negative_raises_value_error(self):
        """Branch: capacity <= 0 -> True (negative)"""
        with pytest.raises(ValueError, match="invalid capacity"):
            waitlist_position(10, -5, 0)

    def test_capacity_positive_proceeds(self):
        """Branch: capacity <= 0 -> False"""
        assert waitlist_position(15, 30, 0) == 0

    def test_seat_available_enrolled_less_than_capacity(self):
        """Branch: enrolled < capacity -> True"""
        assert waitlist_position(25, 30, 2) == 0

    def test_enrolled_equals_capacity_proceeds_to_waitlist(self):
        """Branch: enrolled < capacity -> False (boundary: enrolled == capacity)"""
        assert waitlist_position(30, 30, 0) == 1

    def test_enrolled_greater_than_capacity_proceeds_to_waitlist(self):
        """Branch: enrolled < capacity -> False (enrolled > capacity)"""
        assert waitlist_position(35, 30, 3) == 4

    def test_waitlist_full_exact_boundary(self):
        """Branch: waitlist_length >= 10 -> True (boundary: 10)"""
        assert waitlist_position(30, 30, 10) == -1

    def test_waitlist_exceeded(self):
        """Branch: waitlist_length >= 10 -> True (greater: 15)"""
        assert waitlist_position(30, 30, 15) == -1

    def test_waitlist_not_full_boundary_nine(self):
        """Branch: waitlist_length >= 10 -> False (boundary: 9)"""
        assert waitlist_position(30, 30, 9) == 10

    def test_waitlist_not_full_zero(self):
        """Branch: waitlist_length >= 10 -> False (empty waitlist: 0)"""
        assert waitlist_position(30, 30, 0) == 1


# ==============================================================================
# 3. late_fee() - Decision & Branch Coverage
# ==============================================================================

class TestLateFeeBranchCoverage:
    """Evaluates every decision gate of late_fee() to both True and False."""

    def test_days_late_zero_returns_zero(self):
        """Branch: days_late <= 0 -> True (boundary: 0)"""
        assert late_fee(0, 15, False) == 0

    def test_days_late_negative_returns_zero(self):
        """Branch: days_late <= 0 -> True (negative days)"""
        assert late_fee(-3, 15, False) == 0

    def test_days_late_positive_proceeds(self):
        """Branch: days_late <= 0 -> False"""
        assert late_fee(1, 15, False) == 500

    def test_has_waiver_returns_zero(self):
        """Branch: has_waiver -> True"""
        assert late_fee(10, 24, True) == 0

    def test_no_waiver_proceeds_to_fee_calculation(self):
        """Branch: has_waiver -> False"""
        assert late_fee(5, 15, False) == 500

    def test_days_late_less_than_seven(self):
        """Branch: days_late <= 7 -> True (middle: 4 days)"""
        assert late_fee(4, 15, False) == 500

    def test_days_late_exact_boundary_seven(self):
        """Branch: days_late <= 7 -> True (boundary: 7 days)"""
        assert late_fee(7, 15, False) == 500

    def test_days_late_exact_boundary_eight(self):
        """Branch: days_late <= 7 -> False (boundary: 8 days -> 500 + 1*100 = 600)"""
        assert late_fee(8, 15, False) == 600

    def test_days_late_beyond_seven_multiple_days(self):
        """Branch: days_late <= 7 -> False (12 days -> 500 + 5*100 = 1000)"""
        assert late_fee(12, 15, False) == 1000

    def test_credits_boundary_twenty_no_surcharge(self):
        """Branch: credits > 20 -> False (boundary: 20)"""
        assert late_fee(5, 20, False) == 500

    def test_credits_low_no_surcharge(self):
        """Branch: credits > 20 -> False (12 credits)"""
        assert late_fee(5, 12, False) == 500

    def test_credits_boundary_twenty_one_with_surcharge(self):
        """Branch: credits > 20 -> True (boundary: 21 credits -> +250)"""
        assert late_fee(5, 21, False) == 750

    def test_credits_high_with_surcharge(self):
        """Branch: credits > 20 -> True (24 credits -> +250)"""
        assert late_fee(8, 24, False) == 850

    def test_fee_exact_boundary_two_thousand_not_capped(self):
        """Branch: fee > 2000 -> False (exact: 22 days, 20 credits -> 500 + 15*100 = 2000)"""
        assert late_fee(22, 20, False) == 2000

    def test_fee_under_two_thousand_not_capped(self):
        """Branch: fee > 2000 -> False (fee = 600 < 2000)"""
        assert late_fee(8, 15, False) == 600

    def test_fee_exceeds_two_thousand_capped(self):
        """Branch: fee > 2000 -> True (25 days, 24 credits -> 500 + 1800 + 250 = 2550 -> 2000)"""
        assert late_fee(25, 24, False) == 2000
