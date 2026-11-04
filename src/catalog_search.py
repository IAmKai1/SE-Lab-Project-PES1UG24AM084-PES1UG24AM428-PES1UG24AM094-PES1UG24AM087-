"""
Catalog Search Component (ICatalogSearch) for LRG.
Implements:
- LRG-F-001: Search catalog by ISBN, title or author
- LRG-F-002: Validation of search input (reject empty/malformed before DB query)
- LRG-F-003: Paginated search results (10/page) with full book metadata
- LRG-F-004: Book detail view with hold eligibility
- LRG-F-005: "No results found" guidance
- LRG-F-042: Admin catalog addition and modification
- TC-SRCH-07: ISBN normalization & hyphen flexibility
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from src.database import Database
from src.security import validate_isbn, sanitize_search_query


class CatalogSearchService:
    """Provides validated search, pagination, detail retrieval and catalog maintenance."""

    def __init__(self, db: Database):
        self.db = db

    def search(
        self,
        query: str,
        search_type: str = "title",
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Execute catalog search with strict validation and pagination.
        Returns: (success, result_payload, error_message)
        """
        # LRG-F-002 / TC-SRCH-03: Validate input non-empty
        if not query or not query.strip():
            return False, {}, "SEARCH_QUERY_CANNOT_BE_EMPTY"

        cleaned_query = query.strip()
        search_type = search_type.lower().strip()

        if search_type not in ("isbn", "title", "author", "all"):
            return False, {}, "INVALID_SEARCH_TYPE"

        # Validate ISBN formatting if ISBN search type chosen
        if search_type == "isbn":
            if not validate_isbn(cleaned_query):
                return False, {}, "INVALID_ISBN_FORMAT"

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10

        offset = (page - 1) * page_size

        # Perform parameterized query
        with self.db.get_connection() as conn:
            if search_type == "isbn":
                # Normalize ISBN search (remove hyphens and spaces for matching)
                # First try exact match
                cur = conn.execute(
                    "SELECT isbn, title, author, publisher, year, status FROM titles WHERE isbn = ?",
                    (cleaned_query,)
                )
                rows = cur.fetchall()
                if not rows:
                    # Try matching normalized without hyphens
                    clean_digits = cleaned_query.replace("-", "").replace(" ", "")
                    cur = conn.execute(
                        "SELECT isbn, title, author, publisher, year, status FROM titles WHERE REPLACE(REPLACE(isbn, '-', ''), ' ', '') = ?",
                        (clean_digits,)
                    )
                    rows = cur.fetchall()
                total = len(rows)
            elif search_type == "title":
                term = f"%{cleaned_query}%"
                count_cur = conn.execute("SELECT COUNT(*) FROM titles WHERE title LIKE ?", (term,))
                total = count_cur.fetchone()[0]
                cur = conn.execute(
                    "SELECT isbn, title, author, publisher, year, status FROM titles WHERE title LIKE ? ORDER BY title ASC LIMIT ? OFFSET ?",
                    (term, page_size, offset)
                )
                rows = cur.fetchall()
            elif search_type == "author":
                term = f"%{cleaned_query}%"
                count_cur = conn.execute("SELECT COUNT(*) FROM titles WHERE author LIKE ?", (term,))
                total = count_cur.fetchone()[0]
                cur = conn.execute(
                    "SELECT isbn, title, author, publisher, year, status FROM titles WHERE author LIKE ? ORDER BY author ASC LIMIT ? OFFSET ?",
                    (term, page_size, offset)
                )
                rows = cur.fetchall()
            else:  # 'all'
                term = f"%{cleaned_query}%"
                count_cur = conn.execute(
                    "SELECT COUNT(*) FROM titles WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?",
                    (term, term, term)
                )
                total = count_cur.fetchone()[0]
                cur = conn.execute(
                    "SELECT isbn, title, author, publisher, year, status FROM titles WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? ORDER BY title ASC LIMIT ? OFFSET ?",
                    (term, term, term, page_size, offset)
                )
                rows = cur.fetchall()

            total_pages = math.ceil(total / page_size) if total > 0 else 1
            results = [dict(r) for r in rows]

            payload = {
                "query": cleaned_query,
                "type": search_type,
                "page": page,
                "pageSize": page_size,
                "total": total,
                "totalPages": total_pages,
                "results": results,
                "message": "No results found. Please check your spelling or try broader search terms." if total == 0 else f"Found {total} result(s)."
            }
            return True, payload, None

    def get_book_details(self, isbn: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Retrieve details for a single book, including active queue length (LRG-F-004, TC-SRCH-05).
        """
        if not isbn or not isbn.strip():
            return False, None, "ISBN_REQUIRED"

        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT isbn, title, author, publisher, year, status FROM titles WHERE isbn = ?",
                (isbn.strip(),)
            )
            book = cur.fetchone()

            if not book:
                # Try normalized match
                clean = isbn.strip().replace("-", "").replace(" ", "")
                cur = conn.execute(
                    "SELECT isbn, title, author, publisher, year, status FROM titles WHERE REPLACE(REPLACE(isbn, '-', ''), ' ', '') = ?",
                    (clean,)
                )
                book = cur.fetchone()

            if not book:
                return False, None, "BOOK_NOT_FOUND"

            book_dict = dict(book)

            # Query hold queue length
            q_cur = conn.execute(
                "SELECT COUNT(*) FROM holds WHERE isbn = ? AND state IN ('Active', 'Ready')",
                (book_dict["isbn"],)
            )
            book_dict["queueLength"] = q_cur.fetchone()[0]
            book_dict["isHoldAllowed"] = (book_dict["status"] == "CheckedOut")
            return True, book_dict, None

    def add_title(self, isbn: str, title: str, author: str, publisher: str, year: int, status: str = "Available") -> Tuple[bool, Optional[str], Optional[str]]:
        """Librarian function: Add new catalog entry (LRG-F-042, TC-ADM-03)."""
        if not validate_isbn(isbn):
            return False, None, "INVALID_ISBN"
        if not title or not title.strip():
            return False, None, "TITLE_REQUIRED"
        if not author or not author.strip():
            return False, None, "AUTHOR_REQUIRED"
        if status not in ("Available", "CheckedOut"):
            status = "Available"

        with self.db.get_connection() as conn:
            # Check duplicate ISBN
            cur = conn.execute("SELECT isbn FROM titles WHERE isbn = ?", (isbn.strip(),))
            if cur.fetchone():
                return False, None, "DUPLICATE_ISBN"

            conn.execute(
                "INSERT INTO titles (isbn, title, author, publisher, year, status) VALUES (?, ?, ?, ?, ?, ?)",
                (isbn.strip(), title.strip(), author.strip(), publisher.strip() if publisher else "", year, status)
            )
            conn.commit()
            return True, isbn.strip(), None

    def edit_title(self, isbn: str, title: str, author: str, publisher: str, year: int) -> Tuple[bool, Optional[str]]:
        """Librarian function: Edit catalog metadata (LRG-F-042, TC-ADM-03)."""
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT isbn FROM titles WHERE isbn = ?", (isbn.strip(),))
            if not cur.fetchone():
                return False, "BOOK_NOT_FOUND"

            conn.execute(
                "UPDATE titles SET title = ?, author = ?, publisher = ?, year = ? WHERE isbn = ?",
                (title.strip(), author.strip(), publisher.strip(), year, isbn.strip())
            )
            conn.commit()
            return True, None
