"""
Unit and Integration Tests for Catalog Search Component.
Verifies:
- TC-SRCH-01: Valid ISBN search
- TC-SRCH-02: Partial title and author searches
- TC-SRCH-03: Empty and malformed search input rejection
- TC-SRCH-04: Pagination and result field formatting
- TC-SRCH-05: Book detail view & hold eligibility check
- TC-SRCH-06: Zero-match search guidance
- TC-SRCH-07: ISBN normalization & hyphen handling
"""

import pytest
from src.catalog_search import CatalogSearchService
from src.security import validate_isbn


class TestCatalogSearch:

    def test_tc_srch_01_valid_isbn_search(self, catalog_service: CatalogSearchService):
        """TC-SRCH-01: Search by a valid ISBN returns matching title and availability."""
        isbn = "978-0132350884"
        ok, res, err = catalog_service.search(query=isbn, search_type="isbn")
        assert ok is True
        assert err is None
        assert res["total"] == 1
        assert res["results"][0]["isbn"] == isbn
        assert res["results"][0]["title"] == "Clean Code: A Handbook of Agile Software Craftsmanship"
        assert res["results"][0]["status"] == "CheckedOut"

    def test_tc_srch_02_partial_title_and_author_search(self, catalog_service: CatalogSearchService):
        """TC-SRCH-02: Search by partial title and by author returns all matching records."""
        # Partial title search
        ok, res_title, _ = catalog_service.search(query="Design", search_type="title")
        assert ok is True
        assert res_title["total"] >= 3
        for book in res_title["results"]:
            assert "design" in book["title"].lower()

        # Author search
        ok, res_author, _ = catalog_service.search(query="Martin", search_type="author")
        assert ok is True
        assert res_author["total"] >= 2
        for book in res_author["results"]:
            assert "Martin" in book["author"]

    def test_tc_srch_03_empty_and_malformed_input(self, catalog_service: CatalogSearchService):
        """TC-SRCH-03: Empty or malformed input rejected before database query."""
        # Empty string
        ok, res, err = catalog_service.search(query="")
        assert ok is False
        assert err == "SEARCH_QUERY_CANNOT_BE_EMPTY"

        # Whitespace only
        ok, res, err = catalog_service.search(query="   ")
        assert ok is False
        assert err == "SEARCH_QUERY_CANNOT_BE_EMPTY"

        # Malformed ISBN
        ok, res, err = catalog_service.search(query="invalid-isbn-123", search_type="isbn")
        assert ok is False
        assert err == "INVALID_ISBN_FORMAT"

        # Invalid search type
        ok, res, err = catalog_service.search(query="Patterns", search_type="nonexistent_type")
        assert ok is False
        assert err == "INVALID_SEARCH_TYPE"

    def test_tc_srch_04_pagination_and_result_fields(self, catalog_service: CatalogSearchService):
        """TC-SRCH-04: Results returned in pages of 10 with all four required fields."""
        ok, res, _ = catalog_service.search(query="", search_type="all") if False else catalog_service.search(query="a", search_type="all", page=1, page_size=10)
        assert ok is True
        assert res["pageSize"] == 10
        assert len(res["results"]) <= 10

        # Verify all mandatory fields exist
        for item in res["results"]:
            assert "isbn" in item
            assert "title" in item
            assert "author" in item
            assert "status" in item
            assert item["status"] in ("Available", "CheckedOut")

    def test_tc_srch_05_book_detail_and_hold_eligibility(self, catalog_service: CatalogSearchService):
        """TC-SRCH-05: Detail page lists metadata; hold option appears only for CheckedOut titles."""
        # Checked-out title
        ok, book_checked_out, _ = catalog_service.get_book_details("978-0132350884")
        assert ok is True
        assert book_checked_out["status"] == "CheckedOut"
        assert book_checked_out["isHoldAllowed"] is True
        assert book_checked_out["queueLength"] >= 1

        # Available title
        ok, book_available, _ = catalog_service.get_book_details("978-0134494166")
        assert ok is True
        assert book_available["status"] == "Available"
        assert book_available["isHoldAllowed"] is False

    def test_tc_srch_06_no_matches_guidance(self, catalog_service: CatalogSearchService):
        """TC-SRCH-06: Zero matches display advice and empty result array."""
        ok, res, _ = catalog_service.search(query="NonExistentTitleXYZ999", search_type="title")
        assert ok is True
        assert res["total"] == 0
        assert len(res["results"]) == 0
        assert "No results found" in res["message"]

    def test_tc_srch_07_isbn_normalization(self, catalog_service: CatalogSearchService):
        """TC-SRCH-07: Search by ISBN handles hyphens and spaces consistently."""
        # Unhyphenated search matching hyphenated database entry
        raw_isbn = "9780132350884"
        ok, res, _ = catalog_service.search(query=raw_isbn, search_type="isbn")
        assert ok is True
        assert res["total"] == 1
        assert res["results"][0]["title"] == "Clean Code: A Handbook of Agile Software Craftsmanship"

    def test_book_detail_not_found(self, catalog_service: CatalogSearchService):
        ok, book, err = catalog_service.get_book_details("978-9999999999")
        assert ok is False
        assert err == "BOOK_NOT_FOUND"

    def test_book_detail_empty_param(self, catalog_service: CatalogSearchService):
        ok, book, err = catalog_service.get_book_details("")
        assert ok is False
        assert err == "ISBN_REQUIRED"
