"""
Comprehensive route testing for Flask API and UI endpoints in src/app.py.
Drives overall statement and branch coverage to exceed 90%.
"""

import pytest


class TestAppRoutes:

    def test_ui_home_search(self, client):
        r = client.get("/?q=Clean&type=title&page=1")
        assert r.status_code == 200
        assert b"Clean Code" in r.data

    def test_ui_book_detail_existing_and_missing(self, client):
        # Existing book
        r = client.get("/book/978-0132350884")
        assert r.status_code == 200
        assert b"Robert C. Martin" in r.data

        # Non-existent book
        r_miss = client.get("/book/978-0000000000")
        assert r_miss.status_code == 200
        assert b"Book not found" in r_miss.data

    def test_ui_login_and_logout_flow(self, client):
        # GET login
        r_get = client.get("/login")
        assert r_get.status_code == 200
        assert b"Campus SSO Authentication" in r_get.data

        # POST invalid login
        r_post_bad = client.post("/login", data={"member_id": "PES1UG24AM428", "sso_token": "bad_token"})
        assert r_post_bad.status_code == 200
        assert b"Authentication Failed" in r_post_bad.data

        # POST valid student login
        r_post_ok = client.post(
            "/login?next=/my-holds",
            data={"member_id": "PES1UG24AM428", "sso_token": "sso_valid_token_pes1ug24am428"}
        )
        assert r_post_ok.status_code == 302
        assert "/my-holds" in r_post_ok.headers["Location"]

        # GET my-holds now accessible
        r_holds = client.get("/my-holds")
        assert r_holds.status_code == 200
        assert b"My Reservation Holds" in r_holds.data

        # GET fines page
        r_fines = client.get("/fines")
        assert r_fines.status_code == 200
        assert b"Overdue Fines" in r_fines.data

        # Logout
        r_logout = client.get("/logout")
        assert r_logout.status_code == 302

    def test_ui_admin_dashboard_gate(self, client, librarian_headers, student_headers):
        # Unauthenticated access redirects to login
        r_unauth = client.get("/admin/dashboard")
        assert r_unauth.status_code == 302
        assert "/login" in r_unauth.headers["Location"]

        # Student access without librarian role redirects with error
        with client.session_transaction() as sess:
            sess["auth_token"] = student_headers["Authorization"].split()[1]
        r_student = client.get("/admin/dashboard")
        assert r_student.status_code == 302

        # Librarian access succeeds
        with client.session_transaction() as sess:
            sess["auth_token"] = librarian_headers["Authorization"].split()[1]
        r_admin = client.get("/admin/dashboard")
        assert r_admin.status_code == 200
        assert b"Head Librarian Administration Center" in r_admin.data

    def test_api_book_crud_by_librarian(self, client, librarian_headers):
        # Valid book addition
        new_book = {
            "isbn": "978-0201485677",
            "title": "Refactoring to Patterns",
            "author": "Joshua Kerievsky",
            "publisher": "Addison-Wesley",
            "year": 2004,
            "status": "Available"
        }
        r_add = client.post("/api/v1/books", json=new_book, headers=librarian_headers)
        assert r_add.status_code == 201
        assert r_add.get_json()["isbn"] == "978-0201485677"

        # Duplicate ISBN check
        r_dup = client.post("/api/v1/books", json=new_book, headers=librarian_headers)
        assert r_dup.status_code == 409

        # Edit book
        r_edit = client.put(
            "/api/v1/books/978-0201485677",
            json={"title": "Refactoring to Patterns (Revised)", "author": "Joshua Kerievsky", "publisher": "AW", "year": 2005},
            headers=librarian_headers
        )
        assert r_edit.status_code == 200

        # Edit non-existent book
        r_edit_none = client.put(
            "/api/v1/books/978-9999999999",
            json={"title": "Non-existent", "author": "Nobody", "publisher": "None", "year": 2026},
            headers=librarian_headers
        )
        assert r_edit_none.status_code == 404

    def test_api_auth_session_and_logout(self, client, student_headers):
        # Session info
        r_sess = client.get("/auth/session", headers=student_headers)
        assert r_sess.status_code == 200
        data = r_sess.get_json()
        assert data["memberId"] == "PES1UG24AM428"
        assert data["role"] == "student"

        # Logout endpoint
        r_logout = client.post("/auth/logout", headers=student_headers)
        assert r_logout.status_code == 204

        # Session invalid after logout
        r_sess_after = client.get("/auth/session", headers=student_headers)
        assert r_sess_after.status_code == 401

    def test_api_validation_errors(self, client, student_headers):
        # Missing q param
        r1 = client.get("/api/v1/books")
        assert r1.status_code == 400

        # Invalid ISBN param
        r2 = client.get("/api/v1/books/bad-isbn-string")
        assert r2.status_code == 400

        # Place hold missing ISBN in body
        r3 = client.post("/api/v1/holds", json={}, headers=student_headers)
        assert r3.status_code == 400

        # Login missing member_id
        r4 = client.post("/auth/login", json={})
        assert r4.status_code == 400
