"""
Authentication & Access Control Component (IAuthentication) for LRG.
Implements:
- LRG-F-010: Campus SSO authentication
- LRG-F-011: Guest access for searching, login required for holds
- LRG-F-012: RBAC role separation (Head Librarian vs Student Member)
- LRG-F-013: Session management & 30-minute idle expiry
- LRG-SR-002: No stored passwords
- LRG-SR-005: 5 failed attempts lockout for 15 minutes + security logging
"""

import secrets
import time
from typing import Any, Dict, Optional, Tuple
from src.database import Database
from src.audit import AuditService


SESSION_IDLE_TIMEOUT = 30 * 60  # 30 minutes in seconds
LOCKOUT_DURATION = 15 * 60     # 15 minutes in seconds
MAX_FAILED_ATTEMPTS = 5


class AuthenticationManager:
    """Handles campus SSO validation, session life-cycle, role authorization and lockout protection."""

    def __init__(self, db: Database, audit: AuditService):
        self.db = db
        self.audit = audit

    def authenticate_sso(self, member_id: str, sso_token: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Authenticate via Campus SSO token.
        Returns: (success, session_token_or_none, error_message_or_none)
        """
        now = time.time()
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT id, name, role, failed_attempts, locked_until FROM members WHERE id = ?", (member_id,))
            member = cur.fetchone()

            if not member:
                # Unknown member
                return False, None, "INVALID_CREDENTIALS"

            # Check if currently locked out (LRG-SR-005)
            if member["locked_until"] and member["locked_until"] > now:
                remaining_sec = int(member["locked_until"] - now)
                self.audit.log_event(member_id, "LOGIN_BLOCKED", "AUTH", f"Locked out account attempt. Remaining: {remaining_sec}s")
                return False, None, f"ACCOUNT_LOCKED_TRY_LATER_{remaining_sec}S"

            # Validate SSO token (mock campus OpenID Connect verification)
            # In campus SSO, token must be valid format (e.g. valid SSO ticket)
            is_valid_token = (sso_token and sso_token.startswith("sso_valid_") and len(sso_token) > 12)

            if not is_valid_token:
                # Increment failed attempts
                attempts = member["failed_attempts"] + 1
                locked_until = 0.0
                if attempts >= MAX_FAILED_ATTEMPTS:
                    locked_until = now + LOCKOUT_DURATION
                    self.audit.log_event(member_id, "LOCKOUT_TRIGGERED", "AUTH", f"User locked out for 15 minutes after {attempts} failed attempts")
                else:
                    self.audit.log_event(member_id, "LOGIN_FAILED", "AUTH", f"Failed login attempt #{attempts}")

                conn.execute(
                    "UPDATE members SET failed_attempts = ?, locked_until = ? WHERE id = ?",
                    (attempts, locked_until, member_id)
                )
                conn.commit()

                if attempts >= MAX_FAILED_ATTEMPTS:
                    return False, None, "ACCOUNT_LOCKED_TOO_MANY_ATTEMPTS"
                return False, None, "INVALID_CREDENTIALS"

            # Successful login: reset failed attempts & generate secure session token
            conn.execute(
                "UPDATE members SET failed_attempts = 0, locked_until = 0 WHERE id = ?",
                (member_id,)
            )

            token = secrets.token_hex(24)
            conn.execute(
                "INSERT INTO sessions (token, member_id, created_at, last_active) VALUES (?, ?, ?, ?)",
                (token, member_id, now, now)
            )
            conn.commit()

            self.audit.log_event(member_id, "LOGIN_SUCCESS", "AUTH", f"SSO session initiated with role {member['role']}")
            return True, token, None

    def validate_session(self, token: Optional[str]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate active session token.
        Enforces 30-minute idle expiry (LRG-F-013).
        """
        if not token:
            return False, None, "NO_SESSION_PROVIDED"

        now = time.time()
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT s.token, s.member_id, s.created_at, s.last_active, m.name, m.email, m.role
                FROM sessions s
                JOIN members m ON s.member_id = m.id
                WHERE s.token = ?
                """,
                (token,)
            )
            session = cur.fetchone()

            if not session:
                return False, None, "INVALID_SESSION"

            # Check idle timeout (30 minutes)
            if now - session["last_active"] > SESSION_IDLE_TIMEOUT:
                # Destroy expired session
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                self.audit.log_event(session["member_id"], "SESSION_EXPIRED", "AUTH", "Session expired due to 30 min inactivity")
                return False, None, "SESSION_EXPIRED_IDLE"

            # Update last_active timestamp
            conn.execute("UPDATE sessions SET last_active = ? WHERE token = ?", (now, token))
            conn.commit()

            user_data = {
                "member_id": session["member_id"],
                "name": session["name"],
                "email": session["email"],
                "role": session["role"],
                "token": session["token"]
            }
            return True, user_data, None

    def logout(self, token: str) -> bool:
        """Destroy session (LRG-F-013)."""
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT member_id FROM sessions WHERE token = ?", (token,))
            row = cur.fetchone()
            if row:
                self.audit.log_event(row["member_id"], "LOGOUT", "AUTH", "User successfully logged out")
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                conn.commit()
                return True
            return False

    def require_role(self, token: Optional[str], required_role: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Role-based access check (LRG-F-012, LRG-SR-003).
        Returns: (authorized, user_info, error_status)
        """
        valid, user, err = self.validate_session(token)
        if not valid or not user:
            return False, None, err or "UNAUTHORIZED"

        if user["role"] != required_role:
            self.audit.log_event(
                user["member_id"],
                "UNAUTHORIZED_ACCESS_ATTEMPT",
                "AUTH",
                f"Required {required_role}, found {user['role']}"
            )
            return False, user, "FORBIDDEN"

        return True, user, None
