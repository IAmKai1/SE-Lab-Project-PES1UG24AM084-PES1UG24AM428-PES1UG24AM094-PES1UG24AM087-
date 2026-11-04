"""
Seed script to generate test datasets for LRG.
Generates realistic library titles and dummy student accounts to verify scalability (LRG-NF-005, TC-PERF-02).
"""

import sqlite3
import time
from src.database import SCHEMA_SQL, INITIAL_TITLES, INITIAL_MEMBERS


def seed_large_dataset(db_file: str = "lrg_large_scale.db", total_titles: int = 5000):
    print(f"Creating database {db_file} with {total_titles} titles...")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)

    # Insert initial titles & members
    conn.executemany(
        "INSERT OR IGNORE INTO titles (isbn, title, author, publisher, year, status) VALUES (?, ?, ?, ?, ?, ?);",
        INITIAL_TITLES
    )
    conn.executemany(
        "INSERT OR IGNORE INTO members (id, name, email, role, failed_attempts, locked_until) VALUES (?, ?, ?, ?, 0, 0);",
        INITIAL_MEMBERS
    )

    # Generate synthetic titles for scalability benchmark
    synthetic = []
    statuses = ["Available", "CheckedOut"]
    for i in range(1, total_titles + 1):
        isbn = f"978-{i:010d}"
        title = f"Computer Science & Engineering Volume #{i}"
        author = f"Professor Author {i % 50}"
        publisher = f"Academic Press {i % 10}"
        year = 2000 + (i % 26)
        status = statuses[i % 2]
        synthetic.append((isbn, title, author, publisher, year, status))

    conn.executemany(
        "INSERT OR IGNORE INTO titles (isbn, title, author, publisher, year, status) VALUES (?, ?, ?, ?, ?, ?);",
        synthetic
    )
    conn.commit()
    print(f"Successfully seeded {total_titles + len(INITIAL_TITLES)} titles into {db_file}!")
    conn.close()


if __name__ == "__main__":
    seed_large_dataset()
