"""
TC-BRWS tests: browsing the full catalog without a search term,
filtering by subject, difficulty and availability, and sorting.
"""

import math
import sqlite3

from src.catalog_seed import EXTENDED_TITLES
from src.database import Database, INITIAL_TITLES, TITLE_CLASSIFICATION

# Expected counts are derived from the seed data so adding books never breaks these tests.
TOTAL_TITLES = len(INITIAL_TITLES) + len(EXTENDED_TITLES)
SUBJECT_OF = dict(TITLE_CLASSIFICATION)
SUBJECT_OF.update({e[0]: (e[5], e[6]) for e in EXTENDED_TITLES})


def expected_count(subject=None, difficulty=None):
    return sum(
        1 for subj, diff in SUBJECT_OF.values()
        if (subject is None or subj == subject) and (difficulty is None or diff == difficulty)
    )


class TestBrowseCatalog:

    def test_tc_brws_01_browse_lists_all_titles_without_query(self, catalog_service):
        assert TOTAL_TITLES >= 100
        result = catalog_service.browse(page_size=100)
        assert result["total"] == TOTAL_TITLES
        assert len(result["results"]) == 100
        # Every result carries subject and difficulty for display
        assert all(r["subject"] and r["difficulty"] for r in result["results"])

    def test_tc_brws_02_browse_paginates(self, catalog_service):
        pages = math.ceil(TOTAL_TITLES / 12)
        p1 = catalog_service.browse(page=1)
        last = catalog_service.browse(page=pages)
        assert p1["totalPages"] == pages
        assert len(p1["results"]) == 12
        assert len(last["results"]) == TOTAL_TITLES - 12 * (pages - 1)
        assert not {r["isbn"] for r in p1["results"]} & {r["isbn"] for r in last["results"]}
        # Page past the end clamps to the last page
        assert catalog_service.browse(page=999)["page"] == pages

    def test_tc_brws_03_filter_by_subject(self, catalog_service):
        result = catalog_service.browse(subject="Software Testing", page_size=100)
        titles = {r["title"] for r in result["results"]}
        assert result["total"] == expected_count(subject="Software Testing") > 2
        assert all(r["subject"] == "Software Testing" for r in result["results"])
        assert "Test-Driven Development: By Example" in titles

    def test_tc_brws_04_filter_by_difficulty_and_availability(self, catalog_service):
        beginner = catalog_service.browse(difficulty="beginner", page_size=100)
        assert beginner["filters"]["difficulty"] == "Beginner"
        assert all(r["difficulty"] == "Beginner" for r in beginner["results"])

        combined = catalog_service.browse(difficulty="Beginner", availability="Available", page_size=100)
        assert combined["total"] >= 1
        assert all(r["status"] == "Available" and r["difficulty"] == "Beginner" for r in combined["results"])

    def test_tc_brws_05_invalid_filters_are_ignored(self, catalog_service):
        result = catalog_service.browse(difficulty="Impossible", availability="Lost", sort="1; DROP TABLE titles")
        assert result["total"] == TOTAL_TITLES
        assert result["sort"] == "title"
        assert result["filters"] == {"subject": "", "difficulty": "", "availability": ""}

    def test_tc_brws_06_sort_orders(self, catalog_service):
        newest = catalog_service.browse(sort="newest", page_size=100)["results"]
        assert [r["year"] for r in newest] == sorted((r["year"] for r in newest), reverse=True)

        easiest = catalog_service.browse(sort="difficulty", page_size=100)["results"]
        rank = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        assert [rank[r["difficulty"]] for r in easiest] == sorted(rank[r["difficulty"]] for r in easiest)

    def test_tc_brws_07_facets_count_every_title(self, catalog_service):
        facets = catalog_service.get_facets()
        assert sum(s["count"] for s in facets["subjects"]) == TOTAL_TITLES
        assert len(facets["subjects"]) == len({subj for subj, _ in SUBJECT_OF.values()})
        assert [d["name"] for d in facets["difficulties"]] == ["Beginner", "Intermediate", "Advanced"]
        assert sum(d["count"] for d in facets["difficulties"]) == TOTAL_TITLES
        assert sum(a["count"] for a in facets["availability"]) == TOTAL_TITLES

    def test_tc_brws_08_add_and_edit_title_with_subject(self, catalog_service):
        ok, isbn, _ = catalog_service.add_title(
            "978-1593275846", "Eloquent JavaScript (2nd Ed.)", "Marijn Haverbeke", "No Starch Press", 2014,
            subject="Programming Languages", difficulty="Intermediate"
        )
        assert ok
        _, book, _ = catalog_service.get_book_details(isbn)
        assert book["subject"] == "Programming Languages"

        ok, _ = catalog_service.edit_title(isbn, "Eloquent JavaScript (2nd Ed.)", "Marijn Haverbeke", "No Starch Press", 2014,
                                           difficulty="Advanced")
        assert ok
        _, book, _ = catalog_service.get_book_details(isbn)
        assert book["difficulty"] == "Advanced"
        assert book["subject"] == "Programming Languages"

        # Defaults when not given / invalid
        catalog_service.add_title("978-0596517748", "JavaScript: The Good Parts", "Douglas Crockford",
                                  "O'Reilly", 2008, difficulty="Wizard")
        _, book, _ = catalog_service.get_book_details("978-0596517748")
        assert book["subject"] == "General" and book["difficulty"] == "Intermediate"

    def test_tc_brws_09_old_database_file_is_migrated(self, tmp_path):
        """A database created before subject/difficulty existed gains the columns on startup."""
        path = str(tmp_path / "old.db")
        conn = sqlite3.connect(path)
        conn.executescript("""
            CREATE TABLE titles (isbn TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL,
                                 publisher TEXT, year INTEGER, status TEXT NOT NULL DEFAULT 'Available');
            INSERT INTO titles VALUES ('978-0321146533', 'TDD', 'Kent Beck', 'AW', 2002, 'Available');
            CREATE TABLE members (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL,
                                  role TEXT NOT NULL DEFAULT 'student',
                                  failed_attempts INTEGER NOT NULL DEFAULT 0, locked_until REAL DEFAULT 0);
            INSERT INTO members (id, name, email) VALUES ('S1', 'Student', 's1@example.edu');
        """)
        conn.commit()
        conn.close()

        db = Database(db_path=path)
        row = db.fetchone("SELECT subject, difficulty FROM titles WHERE isbn = ?", ("978-0321146533",))
        assert (row["subject"], row["difficulty"]) == TITLE_CLASSIFICATION["978-0321146533"]


class TestBrowseRoutes:

    def test_home_shows_all_books_without_search(self, client):
        r = client.get("/")
        html = r.data.decode("utf-8")
        assert r.status_code == 200
        assert "Browse the Catalog" in html
        assert f"Showing 12 of {TOTAL_TITLES} book(s)" in html
        assert "Software Testing" in html  # subject chip

    def test_home_filters_by_subject_and_difficulty(self, client):
        r = client.get("/?subject=Algorithms+%26+Data+Structures&difficulty=Advanced")
        html = r.data.decode("utf-8")
        n = expected_count("Algorithms & Data Structures", "Advanced")
        assert f"Showing {n} of {n} book(s)" in html
        assert "Introduction to Algorithms" in html
        assert "Clean Code: A Handbook" not in html

    def test_home_empty_filter_result_and_bad_page(self, client):
        r = client.get("/?subject=Underwater+Basket+Weaving&page=abc")
        assert r.status_code == 200
        assert b"No books match these filters" in r.data

    def test_api_browse_and_facets(self, client):
        r = client.get("/api/v1/catalog?difficulty=Beginner&sort=title&pageSize=50")
        body = r.get_json()
        assert r.status_code == 200
        assert body["total"] >= 1
        assert all(b["difficulty"] == "Beginner" for b in body["results"])

        f = client.get("/api/v1/catalog/facets").get_json()
        assert {"subjects", "difficulties", "availability"} <= set(f)

    def test_book_detail_shows_subject_and_difficulty(self, client):
        r = client.get("/book/978-0262033848")
        html = r.data.decode("utf-8")
        assert "Algorithms &amp; Data Structures" in html
        assert "Advanced" in html
