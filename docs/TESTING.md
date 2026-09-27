# Testing Strategy

## Strategy

The project uses pytest. The suite combines isolated service/config/catalog tests with Streamlit `AppTest` flows. Tests are deterministic, use temporary SQLite paths, and do not require a real API key or network access.

## Unit Tests

`tests/test_resume_service.py` covers:

- Offline result fields, deterministic role/skill summary, and experience assessment
- Minimum and configured maximum resume length
- Skill-token boundaries and zero/low role matches
- Offline date-range and quantified-impact assessment behavior
- Stale-analysis invalidation on validation or analysis failures
- Consent gate behavior and session clearing
- OpenAI response success, strict response-format request, unsupported model technical skill exclusion from matching, malformed JSON, incomplete fields, invalid field types, and provider failure handling

`tests/test_settings.py` checks invalid and below-minimum `MAX_RESUME_CHARACTERS` settings.

`tests/test_job_catalog.py` checks repeatable seed data and the in-memory SQLite catalog.

## Integration and UI Tests

`tests/test_app.py` uses Streamlit `AppTest` to run the real `app/main.py` script and cover:

- Application startup with the sample resume and Offline mode
- Sample Resume button behavior
- Empty submission validation
- The text-area `max_chars` limit and character counter
- Offline analysis and the rendered summary, skills, experience, roles, gaps, roadmap, and improvements
- JSON download-button generation with a `.json` media URL
- Clear/reset behavior for resume, analysis, report, and mode state
- OpenAI mode disclosure and consent blocking

The AppTest OpenAI case uses a dummy key and submits without consent. The consent helper test also verifies that the analyzer callback is not invoked before acknowledgment. No live OpenAI integration test is run. SQLite used by tests is isolated in temporary paths (or in-memory for the catalog edge case).

## Mocking Strategy

The OpenAI service tests inject a small fake client/response object. They exercise response parsing and error behavior without constructing a live request. AppTest sets environment variables per test and uses the actual UI flow. The OpenAI consent AppTest key is a nonfunctional placeholder; because consent is absent, the service callback is not called.

## Test Execution

From the repository root, with the project environment activated:

```bash
python -m pytest
python -m compileall -q app tests
```

On Windows PowerShell, the same commands work after activating `.venv`:

```powershell
python -m pytest
python -m compileall -q app tests
```

## Current Test Results

Last verified locally on 2026-09-27: **30 passed**. Python compilation completed successfully. The GitHub Actions workflow uses Python 3.11, installs `requirements.txt`, runs pytest, and compiles the application/tests with `OPENAI_API_KEY` set to an empty string.
