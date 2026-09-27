"""SQLite-backed catalog of job profiles used for local recommendations."""

from collections.abc import Iterator
from contextlib import contextmanager
import sqlite3
from pathlib import Path
from threading import RLock


JOB_PROFILES: tuple[tuple[str, str, str], ...] = (
    ("Backend Developer", "Python, REST APIs, SQL, Git, Docker", "Builds and maintains server-side applications and APIs."),
    ("Data Analyst", "SQL, Python, Excel, statistics, data visualization", "Turns business data into useful reports and insights."),
    ("Cloud Engineer", "Linux, Docker, Kubernetes, AWS, CI/CD", "Deploys and operates reliable cloud infrastructure."),
    ("Full-Stack Developer", "JavaScript, React, REST APIs, SQL, Git", "Builds user-facing applications and their backend services."),
    ("QA Automation Engineer", "Python, testing, Selenium, Git, CI/CD", "Creates automated checks that improve software quality."),
)


class JobCatalog:
    """Initialize and query a small SQLite catalog without storing resume data."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._memory_connection: sqlite3.Connection | None = None
        self._memory_lock = RLock()
        if str(database_path) == ":memory:":
            self._memory_connection = sqlite3.connect(":memory:", check_same_thread=False)
        else:
            database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        if self._memory_connection is not None:
            with self._memory_lock:
                with self._memory_connection as connection:
                    yield connection
            return

        connection = sqlite3.connect(str(self.database_path))
        try:
            with connection as managed_connection:
                yield managed_connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS job_profiles (
                    title TEXT PRIMARY KEY,
                    skills TEXT NOT NULL,
                    description TEXT NOT NULL
                )"""
            )
            connection.executemany(
                "INSERT OR IGNORE INTO job_profiles(title, skills, description) VALUES (?, ?, ?)",
                JOB_PROFILES,
            )

    def all_profiles(self) -> list[dict[str, str]]:
        """Return catalog profiles in a stable title order."""
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT title, skills, description FROM job_profiles ORDER BY title"
            ).fetchall()
        return [
            {"title": title, "skills": skills, "description": description}
            for title, skills, description in rows
        ]