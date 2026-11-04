"""
Database layer for the Digital Campus Library Reservation Gateway (LRG).
Implements relational schema, transactional integrity, parameterized queries, and seed data.
"""

import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS titles (
    isbn TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT,
    year INTEGER,
    status TEXT NOT NULL CHECK(status IN ('Available', 'CheckedOut')) DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'librarian')) DEFAULT 'student',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS holds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn TEXT NOT NULL,
    member_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('Active', 'Ready', 'Cancelled', 'Expired', 'Fulfilled')) DEFAULT 'Active',
    created_at REAL NOT NULL,
    ready_until REAL,
    FOREIGN KEY(isbn) REFERENCES titles(isbn) ON DELETE CASCADE,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id TEXT NOT NULL,
    isbn TEXT NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Unpaid', 'Paid')) DEFAULT 'Unpaid',
    transaction_id TEXT,
    paid_at REAL,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY(isbn) REFERENCES titles(isbn) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    details TEXT,
    timestamp REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    member_id TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_active REAL NOT NULL,
    FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
);

-- Indexes for performance (LRG-NF-001, DS-PERF-01)
CREATE INDEX IF NOT EXISTS idx_titles_title ON titles(title);
CREATE INDEX IF NOT EXISTS idx_titles_author ON titles(author);
CREATE INDEX IF NOT EXISTS idx_holds_active ON holds(isbn, member_id, state);
CREATE INDEX IF NOT EXISTS idx_holds_queue ON holds(isbn, state, created_at);
CREATE INDEX IF NOT EXISTS idx_fines_member ON fines(member_id, status);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
"""

INITIAL_TITLES = [
    ("978-0132350884", "Clean Code: A Handbook of Agile Software Craftsmanship", "Robert C. Martin", "Prentice Hall", 2008, "CheckedOut"),
    ("978-0201633610", "Design Patterns: Elements of Reusable Object-Oriented Software", "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides", "Addison-Wesley", 1994, "CheckedOut"),
    ("978-0134494166", "Clean Architecture: A Craftsman's Guide to Software Structure and Design", "Robert C. Martin", "Prentice Hall", 2017, "Available"),
    ("978-0321125217", "Domain-Driven Design: Tackling Complexity in the Heart of Software", "Eric Evans", "Addison-Wesley", 2003, "CheckedOut"),
    ("978-0596007126", "Head First Design Patterns", "Eric Freeman, Elisabeth Robson", "O'Reilly Media", 2004, "Available"),
    ("978-0135974445", "The Pragmatic Programmer: Your Journey To Mastery (20th Anniv. Ed.)", "David Thomas, Andrew Hunt", "Addison-Wesley", 2019, "CheckedOut"),
    ("978-0321146533", "Test-Driven Development: By Example", "Kent Beck", "Addison-Wesley", 2002, "Available"),
    ("978-1449373320", "Designing Data-Intensive Applications", "Martin Kleppmann", "O'Reilly Media", 2017, "CheckedOut"),
    ("978-0262033848", "Introduction to Algorithms (CLRS 3rd Ed.)", "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein", "MIT Press", 2009, "Available"),
    ("978-0131103627", "The C Programming Language (2nd Ed.)", "Brian W. Kernighan, Dennis M. Ritchie", "Prentice Hall", 1988, "Available"),
    ("978-0321751041", "The Art of Computer Programming, Vol 1", "Donald E. Knuth", "Addison-Wesley", 2011, "CheckedOut"),
    ("978-0136291558", "Operating Systems: Design and Implementation", "Andrew S. Tanenbaum, Albert S. Woodhull", "Prentice Hall", 2006, "Available"),
    ("978-0130661029", "Database Systems: The Complete Book", "Hector Garcia-Molina, Jeffrey D. Ullman, Jennifer Widom", "Prentice Hall", 2008, "CheckedOut"),
    ("978-1491950357", "Building Microservices", "Sam Newman", "O'Reilly Media", 2021, "Available"),
    ("978-0321503626", "Growing Object-Oriented Software, Guided by Tests", "Steve Freeman, Nat Pryce", "Addison-Wesley", 2009, "Available")
]

INITIAL_MEMBERS = [
    ("PES1UG24AM084", "Dhareen G", "dhareengnanashekar@gmail.com", "student"),
    ("PES1UG24AM428", "Dharshini V", "abbey6128@gmail.com", "student"),
    ("PES1UG24AM094", "Divyansh", "divyansh2162@gmail.com", "student"),
    ("PES1UG24AM087", "Dhruv Talavat", "dhruvtalavat@gmail.com", "student"),
    ("LIB-HEAD-001", "Dr. A. Sharma (Head Librarian)", "headlibrarian@pes.edu", "librarian")
]


class Database:
    """Encapsulates SQLite connection management and query execution."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_SQL)
            # Check if seed data exists
            cur = conn.execute("SELECT COUNT(*) FROM members;")
            if cur.fetchone()[0] == 0:
                self._seed_data(conn)

    def _seed_data(self, conn: sqlite3.Connection) -> None:
        conn.executemany(
            "INSERT INTO titles (isbn, title, author, publisher, year, status) VALUES (?, ?, ?, ?, ?, ?);",
            INITIAL_TITLES
        )
        conn.executemany(
            "INSERT INTO members (id, name, email, role, failed_attempts, locked_until) VALUES (?, ?, ?, ?, 0, 0);",
            INITIAL_MEMBERS
        )
        # Seed an overdue fine for testing UC-04 for student PES1UG24AM428
        conn.execute(
            "INSERT INTO fines (member_id, isbn, amount, status) VALUES (?, ?, ?, 'Unpaid');",
            ("PES1UG24AM428", "978-0132350884", 15.00)
        )
        # Seed an existing active hold on Clean Code by PES1UG24AM084
        now = time.time()
        conn.execute(
            "INSERT INTO holds (isbn, member_id, state, created_at) VALUES (?, ?, 'Active', ?);",
            ("978-0132350884", "PES1UG24AM084", now - 3600)
        )
        # Seed an audit log entry
        conn.execute(
            "INSERT INTO audit_logs (user_id, action, entity, details, timestamp) VALUES (?, ?, ?, ?, ?);",
            ("SYSTEM", "INITIALIZE", "DATABASE", "Database schema initialized and seeded", now)
        )
        conn.commit()

    def execute(self, sql: str, params: Tuple[Any, ...] = ()) -> sqlite3.Cursor:
        with self.get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur

    def fetchone(self, sql: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
        with self.get_connection() as conn:
            cur = conn.execute(sql, params)
            return cur.fetchone()

    def fetchall(self, sql: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cur = conn.execute(sql, params)
            return cur.fetchall()
