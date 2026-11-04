"""
Additional security and coverage helper tests.
"""

import pytest
from src.security import RateLimiter, sanitize_search_query, validate_isbn, sanitize_input, verify_no_passwords


def test_rate_limiter_reset_and_isolation():
    rl = RateLimiter(max_requests=2, window_seconds=10.0)
    assert rl.is_allowed("ip1") is True
    assert rl.is_allowed("ip1") is True
    assert rl.is_allowed("ip1") is False  # rate limited

    # ip2 is isolated
    assert rl.is_allowed("ip2") is True

    # reset ip1
    rl.reset("ip1")
    assert rl.is_allowed("ip1") is True

    # reset all
    rl.reset()
    assert len(rl.requests) == 0


def test_security_helpers_edge_cases(audit_service):
    # validate_isbn edge cases
    assert validate_isbn(None) is False
    assert validate_isbn("") is False
    assert validate_isbn("12345") is False
    assert validate_isbn("978-0132350884") is True
    assert validate_isbn("0201633612") is True  # 10 digits
    assert validate_isbn("020163361X") is True  # 10 digits with X
    assert validate_isbn("abcdefghij") is False

    # sanitize_search_query
    assert sanitize_search_query("") == ""
    assert sanitize_search_query("   ") == ""
    assert sanitize_search_query("Clean' OR '1'='1;") == "Clean OR 1=1"

    # sanitize_input
    assert sanitize_input(None) == ""
    assert sanitize_input("   ") == ""
    assert sanitize_input("<style>body{color:red}</style>Hello") == "Hello"

    # verify_no_passwords
    assert verify_no_passwords("Safe query text") is True
    assert verify_no_passwords("Leak: password=secret123") is False
    assert verify_no_passwords("Bearer_Token_Raw=abcd") is False

    # Audit log retention check
    assert audit_service.verify_retention_window() is True
    # Filtered audit log query
    logs = audit_service.get_logs(limit=10, action="LOGIN_SUCCESS")
    assert isinstance(logs, list)
    logs_user = audit_service.get_logs(limit=10, user_id="SYSTEM")
    assert isinstance(logs_user, list)
