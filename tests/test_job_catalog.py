"""Tests for local job profile catalog persistence."""

from pathlib import Path

from app.services.job_catalog import JobCatalog


def test_catalog_is_seeded_and_repeatable(tmp_path):
    catalog_path = tmp_path / "catalog.sqlite3"

    first = JobCatalog(catalog_path)
    second = JobCatalog(catalog_path)

    profiles = second.all_profiles()
    assert len(profiles) >= 5
    assert len({profile["title"] for profile in profiles}) == len(profiles)
    assert any(profile["title"] == "Backend Developer" for profile in profiles)


def test_in_memory_catalog_remains_available_across_connections():
    catalog = JobCatalog(Path(":memory:"))

    profiles = catalog.all_profiles()

    assert any(profile["title"] == "Backend Developer" for profile in profiles)