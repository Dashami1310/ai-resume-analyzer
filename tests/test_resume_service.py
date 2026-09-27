"""Deterministic tests for resume validation and analysis."""

import json
from types import SimpleNamespace

import pytest

from app.config.settings import Settings
from app.services.job_catalog import JobCatalog
from app.services.resume_service import ResumeAnalysisError, ResumeAnalyzer


DEMO_RESUME = """Python Developer. Python, FastAPI, Git, Docker, MySQL, REST APIs.
2 Years Experience Building Backend Applications. Developed APIs for E-Commerce Systems.
Bachelor of Engineering in Computer Science."""


def make_analyzer(tmp_path, api_key=None, client=None, max_characters=30000):
    settings = Settings(
        openai_api_key=api_key,
        openai_model="test-model",
        database_path=tmp_path / "catalog.sqlite3",
        max_resume_characters=max_characters,
        log_level="INFO",
    )
    return ResumeAnalyzer(settings, JobCatalog(settings.database_path), client)


def test_offline_analysis_produces_all_expected_sections(tmp_path):
    result = make_analyzer(tmp_path).analyze(DEMO_RESUME)

    assert result.provider == "Offline"
    assert "Python" in result.technical_skills
    assert result.experience_assessment.startswith("The resume states 2 years")
    assert result.job_recommendations[0].title == "Backend Developer"
    assert result.missing_skills
    assert result.learning_suggestions
    assert result.resume_improvements
    assert set(result.to_dict()) == {
        "summary", "technical_skills", "soft_skills", "experience_assessment",
        "job_recommendations", "missing_skills", "learning_suggestions",
        "resume_improvements", "provider",
    }


@pytest.mark.parametrize("resume", ["", "   ", "too short"])
def test_rejects_empty_or_short_resume(tmp_path, resume):
    with pytest.raises(ResumeAnalysisError, match="at least 30 characters"):
        make_analyzer(tmp_path).analyze(resume)


def test_rejects_resume_over_configured_limit(tmp_path):
    with pytest.raises(ResumeAnalysisError, match="character limit"):
        make_analyzer(tmp_path, max_characters=500).analyze("A" * 501)


def test_skill_detection_uses_word_boundaries():
    detected = ResumeAnalyzer._extract_skills(
        "Built JavaScript applications with MySQL.",
        ("Java", "JavaScript", "SQL", "MySQL"),
    )

    assert detected == ["JavaScript", "MySQL"]


def test_openai_path_uses_injected_client_and_returns_structured_result(tmp_path):
    payload = {
        "summary": "Backend developer with API experience.",
        "technical_skills": ["Python", "FastAPI", "REST APIs", "Git", "Docker", "MySQL"],
        "soft_skills": ["teamwork"],
        "experience_assessment": "Two years building APIs.",
        "learning_suggestions": ["Study cloud deployments."],
        "resume_improvements": ["Add quantified business results."],
    }
    message = SimpleNamespace(content=json.dumps(payload))
    response = SimpleNamespace(choices=[SimpleNamespace(message=message)])
    client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kwargs: response)
        )
    )

    result = make_analyzer(tmp_path, api_key="test-key", client=client).analyze(DEMO_RESUME)

    assert result.provider == "OpenAI"
    assert result.summary == payload["summary"]
    assert result.soft_skills == ["teamwork"]
    assert result.learning_suggestions == payload["learning_suggestions"]


def test_provider_failure_returns_safe_error_without_leaking_details(tmp_path):
    def fail(**kwargs):
        raise RuntimeError("private provider detail")

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    analyzer = make_analyzer(tmp_path, api_key="test-key", client=client)

    with pytest.raises(ResumeAnalysisError) as error:
        analyzer.analyze(DEMO_RESUME)

    assert "private provider detail" not in str(error.value)
    assert "temporarily unavailable" in str(error.value)