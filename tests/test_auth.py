"""
Unit and Integration Tests for Authentication Component.
Verifies:
- TC-AUTH-01: Valid Campus SSO login and session creation
- TC-AUTH-02: Brute-force lockout after 5 failed attempts (LRG-SR-005)
- TC-AUTH-03: Guest access to search and protected hold barriers (LRG-F-011)
- TC-AUTH-04: RBAC restriction of librarian functions to Head Librarian (LRG-F-012)
- TC-AUTH-05: Session logout and 30-minute idle expiration (LRG-F-013)
- TC-AUTH-06: Token tampering and unauthorized session handling
"""

import time
import pytest
from src.auth import AuthenticationManager, SESSION_IDLE_TIMEOUT


class TestAuthentication:

    def test_tc_auth_01_valid_sso_login(self, auth_manager: AuthenticationManager):
        """TC-AUTH-01: Valid campus credentials create a session and return member data."""
        ok, token, err = auth_manager.authenticate_sso("PES1UG24AM428", "sso_valid_token_dharshini")
        assert ok is True
        assert token is not None
        assert err is None

        valid, user, _ = auth_manager.validate_session(token)
        assert valid is True
        assert user["member_id"] == "PES1UG24AM428"
        assert user["name"] == "Dharshini V"
        assert user["role"] == "student"

    def test_tc_auth_02_lockout_after_five_failed_logins(self, auth_manager: AuthenticationManager):
        """TC-AUTH-02: After 5 failed logins within 15 min, 6th attempt is blocked and logged."""
        member_id = "PES1UG24AM094"

        # 5 consecutive failures with bad token
        for attempt in range(1, 6):
            ok, token, err = auth_manager.authenticate_sso(member_id, "invalid_bad_token")
            assert ok is False
            assert token is None

        # 6th attempt should now be completely locked out
        ok, token, err = auth_manager.authenticate_sso(member_id, "sso_valid_token_even_if_correct_now")
        assert ok is False
        assert "ACCOUNT_LOCKED" in (err or "")

    def test_tc_auth_03_guest_search_vs_hold_gate(self, client):
        """TC-AUTH-03: Guest can search without login; placing a hold requires authentication."""
        # Guest search is 200 OK
        resp_search = client.get("/api/v1/books?q=Clean")
        assert resp_search.status_code == 200

        # Guest attempting hold without session returns 401
        resp_hold = client.post("/api/v1/holds", json={"isbn": "978-0132350884"})
        assert resp_hold.status_code == 401
        assert resp_hold.get_json()["error"] == "NOT_LOGGED_IN"

    def test_tc_auth_04_student_attempts_librarian_endpoint(self, app, student_headers):
        """TC-AUTH-04: Student role calling librarian endpoints returns 403 Forbidden."""
        client = app.test_client()
        # Student calls /api/v1/reports/demand
        resp = client.get("/api/v1/reports/demand", headers=student_headers)
        assert resp.status_code == 403
        assert resp.get_json()["error"] == "FORBIDDEN"

        # Student calls mark_returned endpoint
        resp_ret = client.post("/api/v1/titles/978-0132350884/return", headers=student_headers)
        assert resp_ret.status_code == 403

    def test_tc_auth_05_logout_and_idle_timeout(self, auth_manager: AuthenticationManager):
        """TC-AUTH-05: Session logout destroys token; idle session expires after 30 minutes."""
        ok, token, _ = auth_manager.authenticate_sso("PES1UG24AM087", "sso_valid_token_dhruv")
        assert ok is True

        # Verify active
        valid, _, _ = auth_manager.validate_session(token)
        assert valid is True

        # Simulate 31 minutes of inactivity
        with auth_manager.db.get_connection() as conn:
            conn.execute(
                "UPDATE sessions SET last_active = ? WHERE token = ?",
                (time.time() - (SESSION_IDLE_TIMEOUT + 60), token)
            )
            conn.commit()

        # Session should be expired
        valid, _, err = auth_manager.validate_session(token)
        assert valid is False
        assert err == "SESSION_EXPIRED_IDLE"

        # Explicit logout
        ok2, token2, _ = auth_manager.authenticate_sso("PES1UG24AM087", "sso_valid_token_dhruv")
        assert ok2 is True
        assert auth_manager.logout(token2) is True
        valid2, _, _ = auth_manager.validate_session(token2)
        assert valid2 is False

    def test_tc_auth_unknown_member(self, auth_manager: AuthenticationManager):
        ok, token, err = auth_manager.authenticate_sso("NON_EXISTENT_SRN", "sso_valid_token")
        assert ok is False
        assert err == "INVALID_CREDENTIALS"

    def test_tc_auth_invalid_session_token(self, auth_manager: AuthenticationManager):
        valid, user, err = auth_manager.validate_session("fabricated_bogus_token")
        assert valid is False
        assert err == "INVALID_SESSION"
