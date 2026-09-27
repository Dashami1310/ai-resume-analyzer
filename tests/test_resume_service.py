"""Deterministic tests for resume validation and analysis."""

import json
from types import SimpleNamespace

import pytest

from app.config.settings import Settings
from app.services.job_catalog import JobCatalog
from app.services.resume_service import ResumeAnalysisError, ResumeAnalyzer
from app.utils.analysis_state import analyze_and_replace


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
    assert "Python Developer" in result.summary
    assert "MySQL" in result.summary
    assert "Bachelor of Engineering" in result.summary
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


def test_failed_submission_invalidates_previous_analysis(tmp_path):
    analyzer = make_analyzer(tmp_path)
    session_state = {"analysis": object()}

    with pytest.raises(ResumeAnalysisError):
        analyze_and_replace("too short", analyzer.analyze, session_state)

    assert "analysis" not in session_state


def test_analysis_failure_invalidates_previous_analysis():
    session_state = {"analysis": object()}

    def fail_analysis(resume_text):
        raise ResumeAnalysisError("analysis failed")

    with pytest.raises(ResumeAnalysisError, match="analysis failed"):
        analyze_and_replace(DEMO_RESUME, fail_analysis, session_state)

    assert "analysis" not in session_state


def test_rejects_resume_over_configured_limit(tmp_path):
    with pytest.raises(ResumeAnalysisError, match="character limit"):
        make_analyzer(tmp_path, max_characters=500).analyze("A" * 501)


def test_skill_detection_uses_word_boundaries():
    detected = ResumeAnalyzer._extract_skills(
        "Built JavaScript applications with MySQL.",
        ("Java", "JavaScript", "SQL", "MySQL"),
    )

    assert detected == ["JavaScript", "MySQL"]


def test_low_and_zero_role_matches_are_not_recommended(tmp_path):
    analyzer = make_analyzer(tmp_path)

    low_match = analyzer.analyze("Selenium is the only listed skill in this resume.")
    no_match = analyzer.analyze("A content writer with editorial and publishing experience.")

    assert low_match.job_recommendations == []
    assert no_match.job_recommendations == []


def test_offline_experience_assessment_uses_date_ranges_without_guessing_duration(tmp_path):
    resume = "Backend engineer. Employment: 2020-2024. Built internal services."

    result = make_analyzer(tmp_path).analyze(resume)

    assert "2020-2024" in result.experience_assessment
    assert "Dated experience entries include 2020-2024" in result.summary
    assert "total duration is not inferred" in result.experience_assessment
    assert "measurable outcomes" in result.experience_assessment


def test_offline_experience_assessment_recognizes_quantified_impact(tmp_path):
    resume = "Backend engineer. Reduced response time by 24% across production services."

    result = make_analyzer(tmp_path).analyze(resume)

    assert "Review each result for its baseline" in result.experience_assessment


def make_openai_client(content, captured_requests=None):
    message = SimpleNamespace(content=content)
    response = SimpleNamespace(choices=[SimpleNamespace(message=message)])

    def create(**kwargs):
        if captured_requests is not None:
            captured_requests.append(kwargs)
        return response

    return SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=create)
        )
    )


def test_openai_path_uses_injected_client_and_returns_structured_result(tmp_path):
    captured_requests = []
    payload = {
        "summary": "Backend developer with API experience.",
        "technical_skills": ["Python", "FastAPI", "REST APIs", "Git", "Docker", "MySQL", "Kubernetes"],
        "soft_skills": ["teamwork"],
        "experience_assessment": "Two years building APIs.",
        "learning_suggestions": ["Study cloud deployments."],
        "resume_improvements": ["Add quantified business results."],
    }
    result = make_analyzer(
        tmp_path,
        api_key="test-key",
        client=make_openai_client(json.dumps(payload), captured_requests),
    ).analyze(DEMO_RESUME)

    assert result.provider == "OpenAI"
    assert result.summary == payload["summary"]
    assert result.soft_skills == ["teamwork"]
    assert result.learning_suggestions == payload["learning_suggestions"]
    assert "Kubernetes" not in result.technical_skills
    assert all("Kubernetes" not in job.matching_skills for job in result.job_recommendations)
    response_format = captured_requests[0]["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    assert "resume_improvements" in response_format["json_schema"]["schema"]["required"]


def test_malformed_openai_json_returns_safe_error(tmp_path):
    analyzer = make_analyzer(
        tmp_path,
        api_key="test-key",
        client=make_openai_client("{not valid json"),
    )

    with pytest.raises(ResumeAnalysisError, match="temporarily unavailable"):
        analyzer.analyze(DEMO_RESUME)


def test_incomplete_openai_response_returns_safe_error(tmp_path):
    incomplete = {
        "summary": "Backend developer.",
        "technical_skills": ["Python"],
        "soft_skills": [],
        "experience_assessment": "Experience listed.",
        "learning_suggestions": [],
    }
    analyzer = make_analyzer(
        tmp_path,
        api_key="test-key",
        client=make_openai_client(json.dumps(incomplete)),
    )

    with pytest.raises(ResumeAnalysisError, match="temporarily unavailable"):
        analyzer.analyze(DEMO_RESUME)


def test_openai_response_rejects_invalid_field_types(tmp_path):
    invalid_types = {
        "summary": "Backend developer.",
        "technical_skills": "Python",
        "soft_skills": [],
        "experience_assessment": "Experience listed.",
        "learning_suggestions": [],
        "resume_improvements": [],
    }
    analyzer = make_analyzer(
        tmp_path,
        api_key="test-key",
        client=make_openai_client(json.dumps(invalid_types)),
    )

    with pytest.raises(ResumeAnalysisError, match="temporarily unavailable"):
        analyzer.analyze(DEMO_RESUME)


def test_provider_failure_returns_safe_error_without_leaking_details(tmp_path):
    def fail(**kwargs):
        raise RuntimeError("private provider detail")

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    analyzer = make_analyzer(tmp_path, api_key="test-key", client=client)

    with pytest.raises(ResumeAnalysisError) as error:
        analyzer.analyze(DEMO_RESUME)

    assert "private provider detail" not in str(error.value)
    assert "temporarily unavailable" in str(error.value)