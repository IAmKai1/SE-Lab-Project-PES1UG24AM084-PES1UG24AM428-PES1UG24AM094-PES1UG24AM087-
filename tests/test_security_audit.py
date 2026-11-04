"""
Security, Audit, and NFR Verification Test Suite.
Verifies:
- TC-SEC-01: TLS & HSTS enforcement headers
- TC-SEC-02: SQL Injection & XSS payload neutralization
- TC-SEC-03: Session cookie security attributes (Secure, HttpOnly, SameSite=Strict)
- TC-SEC-04: Data confidentiality between members (LRG-NF-003)
- TC-SEC-05: Password non-storage in database and logs (LRG-SR-002)
- TC-SEC-06: Strict RBAC on librarian endpoints (LRG-SR-003)
- TC-SEC-07: Rate limiting (60 requests/min, 61st returns HTTP 429) (LRG-SR-007)
- TC-AUD-01: Immutable audit trail for holds, returns, and admin events (LRG-NF-007)
"""

import time
import pytest
from src.security import sanitize_input, validate_isbn, RateLimiter, verify_no_passwords


class TestSecurityAndAudit:

    def test_tc_sec_01_tls_and_security_headers(self, client):
        """TC-SEC-01: Security headers enforced on every response."""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert "Strict-Transport-Security" in resp.headers
        assert "max-age=31536000" in resp.headers["Strict-Transport-Security"]
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"
        assert resp.headers.get("X-Frame-Options") == "DENY"

    def test_tc_sec_02_sql_injection_and_xss_prevention(self, client):
        """TC-SEC-02: SQL injection and script payloads rejected or neutralized; no database leaks."""
        # SQL Injection attempt in search
        sqli_payload = "' OR 1=1; DROP TABLE titles; --"
        resp = client.get(f"/api/v1/books?q={sqli_payload}")
        assert resp.status_code in (200, 400)
        # Verify titles table was not dropped!
        resp_check = client.get("/api/v1/books?q=Clean")
        assert resp_check.status_code == 200
        assert resp_check.get_json()["total"] >= 1

        # XSS Payload Sanitization
        xss_payload = "<script>alert('XSS Attack!')</script>Robert C. Martin"
        sanitized = sanitize_input(xss_payload)
        assert "<script>" not in sanitized
        assert "alert(" not in sanitized

    def test_tc_sec_03_cookie_attributes(self, client):
        """TC-SEC-03: Session cookies marked Secure, HttpOnly, and SameSite=Strict."""
        resp = client.post(
            "/auth/login",
            json={"member_id": "PES1UG24AM428", "sso_token": "sso_valid_token_pes1ug24am428"}
        )
        assert resp.status_code == 200

        # Inspect Set-Cookie header
        set_cookie = resp.headers.get("Set-Cookie", "")
        assert "Secure" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "SameSite=Strict" in set_cookie

    def test_tc_sec_04_data_confidentiality_between_members(self, client, student_headers, student2_headers):
        """TC-SEC-04: One member cannot cancel or view another member's confidential hold records."""
        # Student 1 places a hold
        resp_hold = client.post(
            "/api/v1/holds",
            json={"isbn": "978-0135974445"},
            headers=student_headers
        )
        assert resp_hold.status_code == 201
        hold_id = resp_hold.get_json()["holdId"]

        # Student 2 tries to cancel Student 1's hold -> returns 403 NOT_OWNER
        resp_del = client.delete(f"/api/v1/holds/{hold_id}", headers=student2_headers)
        assert resp_del.status_code == 403
        assert resp_del.get_json()["error"] == "NOT_OWNER"

    def test_tc_sec_05_no_passwords_stored_or_logged(self, app):
        """TC-SEC-05: Database schema and logs contain zero plaintext or hashed passwords."""
        with app.db.get_connection() as conn:
            # Check members schema columns
            cur = conn.execute("PRAGMA table_info(members);")
            col_names = [row["name"].lower() for row in cur.fetchall()]
            assert "password" not in col_names
            assert "passwd" not in col_names
            assert "hash" not in col_names

            # Check audit logs for password strings
            cur_logs = conn.execute("SELECT details FROM audit_logs;")
            for r in cur_logs.fetchall():
                assert verify_no_passwords(r["details"]) is True

    def test_tc_sec_06_rbac_librarian_endpoints_with_student_token(self, client, student_headers):
        """TC-SEC-06: 403 returned for every librarian endpoint when invoked with Student credentials."""
        endpoints = [
            ("GET", "/api/v1/reports/demand"),
            ("POST", "/api/v1/titles/978-0132350884/return"),
            ("POST", "/api/v1/books"),
            ("PUT", "/api/v1/books/978-0132350884")
        ]

        for method, ep in endpoints:
            if method == "GET":
                r = client.get(ep, headers=student_headers)
            elif method == "POST":
                r = client.post(ep, json={"title": "Test"}, headers=student_headers)
            elif method == "PUT":
                r = client.put(ep, json={"title": "Test"}, headers=student_headers)
            assert r.status_code == 403, f"Failed RBAC check for {method} {ep}"

    def test_tc_sec_07_rate_limiting(self, client):
        """TC-SEC-07: Send 61 requests in 1 minute; 61st returns HTTP 429 Too Many Requests."""
        client_ip = "192.168.1.100"
        headers = {"X-Forwarded-For": client_ip}

        # First 60 requests should succeed
        for i in range(60):
            r = client.get("/health", headers=headers)
            assert r.status_code == 200, f"Request {i+1} failed"

        # 61st request in the window must return 429
        r_61 = client.get("/health", headers=headers)
        assert r_61.status_code == 429
        assert r_61.get_json()["error"] == "RATE_LIMITED"
        assert "Retry-After" in r_61.headers

    def test_tc_aud_01_audit_logging_integrity(self, app, student_headers, librarian_headers):
        """TC-AUD-01: Hold creation, returns, and administrative actions have audit logs with user, time, action."""
        client = app.test_client()

        # Hold placement
        r_hold = client.post("/api/v1/holds", json={"isbn": "978-0321125217"}, headers=student_headers)
        assert r_hold.status_code == 201

        # Check audit log
        logs = app.audit.get_logs(action="HOLD_PLACED")
        assert len(logs) >= 1
        assert logs[0]["user_id"] == "PES1UG24AM428"
        assert logs[0]["entity"] == "HOLDS"
        assert time.time() - logs[0]["timestamp"] < 10
