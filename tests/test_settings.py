"""Tests for environment-backed configuration validation."""

import pytest

from app.config.settings import Settings


def test_settings_reject_non_integer_resume_limit(monkeypatch):
    monkeypatch.setenv("MAX_RESUME_CHARACTERS", "many")

    with pytest.raises(ValueError, match="must be an integer"):
        Settings.from_environment()


def test_settings_reject_resume_limit_below_minimum(monkeypatch):
    monkeypatch.setenv("MAX_RESUME_CHARACTERS", "499")

    with pytest.raises(ValueError, match="at least 500"):
        Settings.from_environment()