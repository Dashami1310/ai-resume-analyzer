"""Environment-backed application settings."""

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables and an optional .env."""

    openai_api_key: str | None
    openai_model: str
    database_path: Path
    max_resume_characters: int
    log_level: str

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load and validate runtime settings."""
        load_dotenv()
        try:
            max_characters = int(os.getenv("MAX_RESUME_CHARACTERS", "30000"))
        except ValueError as error:
            raise ValueError("MAX_RESUME_CHARACTERS must be an integer.") from error
        if max_characters < 500:
            raise ValueError("MAX_RESUME_CHARACTERS must be at least 500.")

        database_path = Path(os.getenv("DATABASE_PATH", "data/job_catalog.sqlite3"))
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            database_path=database_path,
            max_resume_characters=max_characters,
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )