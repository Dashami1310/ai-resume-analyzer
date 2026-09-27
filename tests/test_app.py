"""Streamlit AppTest coverage for resume submission and privacy controls."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_FILE = Path(__file__).resolve().parents[1] / "app" / "main.py"
DEMO_RESUME = """John Smith
Python Developer

Skills:
Python, FastAPI, Git, Docker, MySQL, REST APIs

Experience:
2 Years Experience Building Backend Applications.
Developed APIs for E-Commerce Systems.

Education:
Bachelor of Engineering in Computer Science."""


def launch_app(monkeypatch, tmp_path, api_key=""):
    monkeypatch.setenv("OPENAI_API_KEY", api_key)
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "job-catalog.sqlite3"))
    monkeypatch.setenv("MAX_RESUME_CHARACTERS", "500")
    monkeypatch.setenv("LOG_LEVEL", "CRITICAL")
    return AppTest.from_file(str(APP_FILE)).run()


def click_button(app, label):
    button = next(button for button in app.button if button.label == label)
    return button.click().run()


def rendered_text(app):
    element_types = ("markdown", "caption", "info", "warning", "error", "success")
    return "\n".join(
        str(element.value)
        for element_type in element_types
        for element in app.get(element_type)
    )


def test_app_starts_with_sample_resume_and_offline_mode(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)

    assert not app.exception
    assert app.text_area[0].value == DEMO_RESUME
    assert "Offline analysis" in rendered_text(app)
    assert any(button.label == "Analyze resume" for button in app.button)


def test_sample_resume_button_restores_demo_content(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)
    app.text_area[0].set_value("An alternate resume with different content.").run()

    click_button(app, "Insert sample resume")

    assert app.text_area[0].value == DEMO_RESUME


def test_empty_resume_submission_is_rejected(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)
    app.text_area[0].set_value("").run()

    click_button(app, "Analyze resume")

    assert any("at least 30 characters" in error.value for error in app.error)
    assert "analysis" not in app.session_state


def test_resume_character_limit_is_applied_by_input_widget(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)
    text_area = app.text_area[0]

    assert text_area.proto.max_chars == 500
    text_area.set_value("X" * 501).run()

    assert len(app.text_area[0].value) == 500
    assert "500 / 500 characters" in rendered_text(app)


def test_offline_analysis_renders_all_sections_and_json_download(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)

    click_button(app, "Analyze resume")

    assert not app.exception
    assert app.session_state["analysis"].provider == "Offline"
    output = rendered_text(app)
    for section in (
        "Resume summary",
        "Skills detected",
        "Technical skills",
        "Soft skills",
        "Experience assessment",
        "Job recommendations",
        "Missing skills",
        "Learning roadmap",
        "Resume improvements",
    ):
        assert section in output
    for result in (
        "Python Developer",
        "Python",
        "2 years of experience",
        "Backend Developer",
        "JavaScript",
        "Recommended learning",
        "Lead each experience bullet",
    ):
        assert result in output

    downloads = app.get("download_button")
    assert len(downloads) == 1
    assert downloads[0].label == "Download analysis report"
    assert downloads[0].proto.url.endswith(".json")


def test_clear_action_removes_resume_analysis_and_report(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path)
    click_button(app, "Analyze resume")
    assert "analysis" in app.session_state
    assert len(app.get("download_button")) == 1

    click_button(app, "Clear current resume/session data")

    assert app.text_area[0].value == ""
    assert "analysis" not in app.session_state
    assert "analysis_report" not in app.session_state
    assert "openai_consent" not in app.session_state
    assert app.session_state["analysis_mode"] == "Offline analysis"
    assert len(app.get("download_button")) == 0
    assert "Your analysis will appear here" in rendered_text(app)


def test_openai_mode_requires_consent_before_submission(monkeypatch, tmp_path):
    app = launch_app(monkeypatch, tmp_path, api_key="app-test-dummy-key")

    app.radio[0].set_value("OpenAI-powered analysis").run()

    assert "OpenAI mode sends the resume text above to OpenAI" in rendered_text(app)
    assert len(app.checkbox) == 1
    assert app.checkbox[0].value is False

    click_button(app, "Analyze resume")

    assert any("Acknowledge that your resume will be sent to OpenAI" in warning.value for warning in app.warning)
    assert "analysis" not in app.session_state
    assert not app.exception