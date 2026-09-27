# AI Resume Analyzer

A Streamlit career tool that reviews pasted resume content, identifies skills, compares them with a local job catalog, and produces practical improvement and learning suggestions. The app includes a deterministic offline mode, so the complete demo works without an API key or internet connection.

## Features

- Resume summary, technical skills, soft skills, and experience assessment
- Illustrative role matches against five local profiles, with matching and missing skills
- Equal-weight skill-overlap scores; profiles below 30% are omitted
- Learning suggestions and actionable resume improvements
- JSON report download
- User-selectable offline analysis or OpenAI-powered narrative analysis
- Per-submission acknowledgment before resume text is sent to OpenAI
- Strictly schema-validated OpenAI responses; job matching uses locally detected technical skills
- SQLite-backed, seeded role catalog; submitted resumes are not written to the database
- Input limits, safe provider errors, and tests that make no network requests

## Architecture

`app/main.py` owns the Streamlit interface. `app/services/resume_service.py` validates input, performs offline or OpenAI analysis, and ranks local role profiles. `app/services/job_catalog.py` initializes and queries the SQLite role catalog. Settings and prompt text are isolated under `app/config` and `app/prompts`.

## Requirements

- Python 3.11 or newer
- An OpenAI API key only when AI-assisted narrative analysis is desired

## Installation

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux or macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

To make OpenAI-powered analysis available, put your key in `.env` as `OPENAI_API_KEY=...`. Keep `.env` private; it is excluded from Git. When a key is configured, choose either Offline or OpenAI-powered analysis in the sidebar. Offline is the default. OpenAI submissions require a separate acknowledgment for the current resume; changing the resume or mode clears that acknowledgment. Without a key, only Offline analysis is available.

## Run

```bash
streamlit run app/main.py
```

The first launch creates `data/job_catalog.sqlite3` and seeds the local role profiles. This database contains role information only, not submitted resumes.

## Run Tests

```bash
python -m pytest
```

Tests use temporary SQLite databases and an injected OpenAI mock. They do not need an API key or internet access.

## Environment Variables

| Variable                | Purpose                        | Default                    |
| ----------------------- | ------------------------------ | -------------------------- |
| `OPENAI_API_KEY`        | Makes OpenAI mode available    | unset (offline only)       |
| `OPENAI_MODEL`          | OpenAI chat model              | `gpt-4o-mini`              |
| `DATABASE_PATH`         | SQLite job catalog path        | `data/job_catalog.sqlite3` |
| `MAX_RESUME_CHARACTERS` | Maximum accepted resume length | `30000`                    |
| `LOG_LEVEL`             | Application log level          | `INFO`                     |

## Troubleshooting

- If PowerShell blocks environment activation, use `Set-ExecutionPolicy -Scope Process RemoteSigned` for the current terminal, or invoke `.venv\Scripts\python.exe` directly.
- If `streamlit` is not found, activate the virtual environment and reinstall requirements.
- If AI-assisted analysis fails, verify the API key and model; the app displays a generic provider error and does not log resume content.
- The offline mode works without an OpenAI key and uses local rules for summary, skills, experience assessment, and matching, so its feedback is intentionally heuristic. Role matches are not live job vacancies. Their score is the share of a profile's listed skills detected in the resume; all skills have equal weight and results below 30% are hidden.

## Security and Privacy

Do not commit `.env` or share real resumes in public demos. The current resume is held in Streamlit session state while the session is active; it is not written to SQLite or application logs. Use **Clear current resume/session data** to blank the resume and remove the current analysis, consent acknowledgment, and any session report state. The report download is generated from the current analysis and is not separately persisted by the app.

Offline analysis uses local rules and does not send resume text to OpenAI. OpenAI-powered analysis is available only when `OPENAI_API_KEY` is configured, and each submission requires a visible acknowledgment. When acknowledged, resume text is sent to the configured OpenAI provider; submit only content you are authorized to share and review the provider's data policies. Treat generated career guidance as suggestions, not hiring decisions.

## Future Enhancements

- PDF/DOCX ingestion with local parsing and explicit user consent
- Counselor review and configurable role catalogs
- User-controlled export formats and accessibility review
- Expanded validation and privacy impact assessment before production use
