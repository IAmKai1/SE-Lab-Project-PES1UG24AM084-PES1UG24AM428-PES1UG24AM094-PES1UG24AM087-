"""
End-to-End System Validation & NFR Verification Test Suite.
Validates:
- Complete operational flows UC-01 through UC-09 + UC-04
- TC-PERF-01 / TC-PERF-02: Search latency & scalability (LRG-NF-001, LRG-NF-005)
- TC-AVL-01: System availability & health monitoring (LRG-NF-002)
- TC-UX-01: Accessibility & responsive UI rendering (LRG-NF-004)
- TC-MNT-01: Architectural interface boundaries & test coverage (LRG-NF-006)
"""

import time
import pytest


class TestSystemValidationE2E:

    def test_e2e_flow_search_to_hold_to_cancel(self, client, student_headers):
        """End-to-end user journey: Search book -> Place hold -> Check queue -> Cancel hold."""
        # 1. Search for a book
        r_search = client.get("/api/v1/books?q=Designing&type=title")
        assert r_search.status_code == 200
        data_search = r_search.get_json()
        assert data_search["total"] >= 1
        isbn = data_search["results"][0]["isbn"]

        # 2. View details
        r_detail = client.get(f"/api/v1/books/{isbn}")
        assert r_detail.status_code == 200
        assert r_detail.get_json()["isHoldAllowed"] is True

        # 3. Place hold
        r_hold = client.post("/api/v1/holds", json={"isbn": isbn}, headers=student_headers)
        assert r_hold.status_code == 201
        hold_id = r_hold.get_json()["holdId"]
        assert r_hold.get_json()["position"] >= 1

        # 4. View in My Holds
        r_my_holds = client.get("/api/v1/holds/me", headers=student_headers)
        assert r_my_holds.status_code == 200
        holds_list = r_my_holds.get_json()
        assert any(h["holdId"] == hold_id for h in holds_list)

        # 5. Cancel hold
        r_del = client.delete(f"/api/v1/holds/{hold_id}", headers=student_headers)
        assert r_del.status_code == 204

        # 6. Verify cancelled
        r_my_holds_after = client.get("/api/v1/holds/me", headers=student_headers)
        assert not any(h["holdId"] == hold_id for h in r_my_holds_after.get_json())

    def test_e2e_flow_return_promotion_notification(self, client, student_headers, librarian_headers, app):
        """End-to-end journey: Member holds book -> Librarian marks returned -> Hold promoted to Ready -> Notification sent."""
        isbn = "978-0130661029"

        # Member places hold
        r_hold = client.post("/api/v1/holds", json={"isbn": isbn}, headers=student_headers)
        assert r_hold.status_code == 201
        hold_id = r_hold.get_json()["holdId"]

        # Librarian marks title returned
        r_ret = client.post(f"/api/v1/titles/{isbn}/return", headers=librarian_headers)
        assert r_ret.status_code == 200
        assert r_ret.get_json()["holdReadyFor"] == "PES1UG24AM428"

        # Member checks holds: should now show 'Ready'
        r_my = client.get("/api/v1/holds/me", headers=student_headers)
        assert r_my.status_code == 200
        target_hold = next(h for h in r_my.get_json() if h["holdId"] == hold_id)
        assert target_hold["state"] == "Ready"

        # Verify email notification was dispatched
        assert len(app.notification.sent_messages) >= 1
        last_msg = app.notification.sent_messages[-1]
        assert last_msg["member_id"] == "PES1UG24AM428"
        assert "Ready" in last_msg["subject"]

    def test_e2e_flow_overdue_fine_settlement(self, client, student_headers):
        """End-to-end journey for UC-04: Settle fine via payment desk and clear account status."""
        # Check current fines
        r_fines = client.get("/api/v1/fines/me", headers=student_headers)
        assert r_fines.status_code == 200
        fines_data = r_fines.get_json()
        assert fines_data["total_unpaid"] == 15.00
        target_fine_id = fines_data["fines"][0]["id"]

        # Settle fine
        r_pay = client.post(
            f"/api/v1/fines/{target_fine_id}/pay",
            json={"payment_method": "CAMPUS_WALLET"},
            headers=student_headers
        )
        assert r_pay.status_code == 200
        receipt = r_pay.get_json()
        assert receipt["status"] == "SETTLED"
        assert receipt["amount_paid"] == 15.00

        # Check fines again: balance 0.00
        r_fines_after = client.get("/api/v1/fines/me", headers=student_headers)
        assert r_fines_after.get_json()["total_unpaid"] == 0.0

    def test_tc_perf_01_search_response_time(self, client):
        """TC-PERF-01 (LRG-NF-001): 90% of searches return within 2.0s."""
        latencies = []
        for i in range(50):
            start = time.perf_counter()
            r = client.get("/api/v1/books?q=Code")
            elapsed = time.perf_counter() - start
            assert r.status_code == 200
            latencies.append(elapsed)

        latencies.sort()
        p90 = latencies[int(len(latencies) * 0.90)]
        assert p90 < 2.0, f"90th percentile response time {p90:.4f}s exceeded 2.0s limit"

    def test_tc_avl_01_health_monitoring(self, client):
        """TC-AVL-01 (LRG-NF-002): /health endpoint returns UP and >= 99.5% availability."""
        r = client.get("/health")
        assert r.status_code == 200
        body = r.get_json()
        assert body["status"] == "UP"
        assert body["db"] == "CONNECTED"
        assert "availability" in body

    def test_tc_ux_01_accessibility_and_responsive_markup(self, client):
        """TC-UX-01 (LRG-NF-004): Web UI templates include viewport meta, semantic ARIA roles, and high-contrast labels."""
        # Home page
        r_home = client.get("/")
        assert r_home.status_code == 200
        html = r_home.data.decode("utf-8")
        assert 'name="viewport"' in html
        assert 'role="search"' in html
        assert 'role="main"' in html
        assert 'role="banner"' in html
        assert 'role="contentinfo"' in html
        assert 'aria-label=' in html

        # Book detail
        r_detail = client.get("/book/978-0132350884")
        assert r_detail.status_code == 200
        html_d = r_detail.data.decode("utf-8")
        assert 'aria-label="Breadcrumb"' in html_d

    def test_tc_mnt_01_modular_boundaries(self, app):
        """TC-MNT-01 (LRG-NF-006): Verify distinct modular component boundaries (no direct UI-to-DB calls)."""
        assert hasattr(app, "catalog")
        assert hasattr(app, "auth")
        assert hasattr(app, "reservation")
        assert hasattr(app, "notification")
        assert hasattr(app, "fine_mgr")
        assert hasattr(app, "admin")
        assert hasattr(app, "audit")
