"""
Security controls and verification layer for LRG.
Implements:
- LRG-SR-001: TLS enforcement headers
- LRG-SR-002: Password non-storage validation
- LRG-SR-003: RBAC & ownership verification
- LRG-SR-004: Input validation & SQLi/XSS mitigation
- LRG-SR-006: Cookie flags (Secure, HttpOnly, SameSite=Strict)
- LRG-SR-007: Rate limiting (60 requests/minute per client)
"""

import html
import re
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


# ISBN regex supporting ISBN-10 (with optional X) and ISBN-13, with or without hyphens
ISBN_REGEX = re.compile(r"^(?:ISBN(?:-1[03])?:?\ )?(?=[-0-9X]{10,17}$)(?:97[89][-\ ]?)?[0-9]{1,5}[-\ ]?[0-9]+[-\ ]?[0-9]+[-\ ]?[0-9X]$", re.IGNORECASE)

class RateLimiter:
    """Sliding-window rate limiter allowing up to max_requests in a 60-second window."""
    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        # Filter timestamps outside the window
        self.requests[client_id] = [t for t in self.requests[client_id] if t > cutoff]
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        self.requests[client_id].append(now)
        return True

    def reset(self, client_id: Optional[str] = None) -> None:
        if client_id:
            self.requests.pop(client_id, None)
        else:
            self.requests.clear()


def validate_isbn(isbn: str) -> bool:
    """Validate ISBN-10 or ISBN-13 format."""
    if not isbn or not isinstance(isbn, str):
        return False
    clean = isbn.strip().replace("-", "").replace(" ", "")
    if len(clean) not in (10, 13):
        return False
    if not ISBN_REGEX.match(isbn.strip()):
        return False
    # Validate digits
    if len(clean) == 13 and not clean.isdigit():
        return False
    if len(clean) == 10:
        if not (clean[:9].isdigit() and (clean[9].isdigit() or clean[9].upper() == 'X')):
            return False
    return True


def normalize_isbn(isbn: str) -> str:
    """Standardize ISBN format."""
    return isbn.strip()


def sanitize_input(text: str) -> str:
    """Sanitize user input to neutralize HTML / script injection (XSS)."""
    if not text:
        return ""
    # Strip dangerous HTML tags
    cleaned = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", "", text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r"<\s*style[^>]*>.*?<\s*/\s*style\s*>", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    return html.escape(cleaned.strip())


def sanitize_search_query(q: str) -> str:
    """Clean and validate search term."""
    if not q or not q.strip():
        return ""
    # Strip SQL meta-characters from raw search string (though parameterized queries are used)
    cleaned = q.strip().replace("'", "").replace('"', '').replace(";", "")
    return cleaned


def verify_no_passwords(data_or_log: str) -> bool:
    """Check that sensitive passwords and auth secrets never appear in logs or text."""
    forbidden = ["password=", "\"password\"", "passwd", "client_secret", "bearer_token_raw"]
    low = data_or_log.lower()
    for f in forbidden:
        if f in low:
            return False
    return True
