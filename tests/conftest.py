"""
Pytest configuration and shared fixtures for LRG test suites.
Ensures single-source-of-truth database sharing across services and Flask app.
"""

import pytest
from src.app import create_app
from src.database import Database
from src.audit import AuditService
from src.auth import AuthenticationManager
from src.catalog_search import CatalogSearchService
from src.notification import NotificationService
from src.fine_manager import FineManager
from src.reservation_manager import ReservationManager
from src.admin import LibrarianAdminService


@pytest.fixture
def in_memory_db():
    """Provides a fresh, isolated in-memory database instance."""
    return Database(db_path=":memory:")


@pytest.fixture
def audit_service(in_memory_db):
    return AuditService(in_memory_db)


@pytest.fixture
def auth_manager(in_memory_db, audit_service):
    return AuthenticationManager(in_memory_db, audit_service)


@pytest.fixture
def catalog_service(in_memory_db):
    return CatalogSearchService(in_memory_db)


@pytest.fixture
def notification_service(in_memory_db, audit_service):
    return NotificationService(in_memory_db, audit_service, simulate_smtp_failure=False)


@pytest.fixture
def fine_manager(in_memory_db, audit_service):
    return FineManager(in_memory_db, audit_service)


@pytest.fixture
def reservation_manager(in_memory_db, audit_service, notification_service, fine_manager):
    return ReservationManager(in_memory_db, audit_service, notification_service, fine_manager)


@pytest.fixture
def admin_service(catalog_service, reservation_manager, audit_service, auth_manager):
    return LibrarianAdminService(catalog_service, reservation_manager, audit_service, auth_manager)


@pytest.fixture
def app(in_memory_db):
    """Provides an isolated Flask application configured for testing with the shared in_memory_db."""
    test_app = create_app(db_path=":memory:", simulate_smtp_failure=False, db=in_memory_db)
    test_app.config["TESTING"] = True
    return test_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student_token(auth_manager):
    """Provides an active session token for student Dharshini V (PES1UG24AM428)."""
    ok, token, _ = auth_manager.authenticate_sso("PES1UG24AM428", "sso_valid_token_pes1ug24am428")
    assert ok and token
    return token


@pytest.fixture
def student_headers(student_token):
    return {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def student2_token(auth_manager):
    """Provides an active session token for student Dhareen G (PES1UG24AM084)."""
    ok, token, _ = auth_manager.authenticate_sso("PES1UG24AM084", "sso_valid_token_pes1ug24am084")
    assert ok and token
    return token


@pytest.fixture
def student2_headers(student2_token):
    return {
        "Authorization": f"Bearer {student2_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def librarian_token(auth_manager):
    """Provides an active session token for Head Librarian (LIB-HEAD-001)."""
    ok, token, _ = auth_manager.authenticate_sso("LIB-HEAD-001", "sso_valid_token_librarian_staff")
    assert ok and token
    return token


@pytest.fixture
def librarian_headers(librarian_token):
    return {
        "Authorization": f"Bearer {librarian_token}",
        "Content-Type": "application/json"
    }
