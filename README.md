# AI Resume Analyzer

A Streamlit career tool that reviews pasted resume content, identifies skills, compares them with a local job catalog, and produces practical improvement and learning suggestions. The app includes a deterministic offline mode, so the complete demo works without an API key or internet connection.

## Features

- Resume summary, technical skills, soft skills, and experience assessment
- Illustrative role matches against five local profiles, with matching and missing skills
- Equal-weight skill-overlap scores; profiles below 30% are omitted
- Learning suggestions and actionable resume improvements
- JSON report download
- Optional OpenAI-powered narrative analysis
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

To enable OpenAI, put your key in `.env` as `OPENAI_API_KEY=...`. Keep `.env` private; it is excluded from Git. Leave the key blank to use offline mode.

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
| `OPENAI_API_KEY`        | Enables AI-assisted analysis   | unset (offline mode)       |
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

Do not commit `.env` or share real resumes in public demos. The app does not persist submitted resume text. An OpenAI-enabled run sends resume text to the configured provider for analysis; use only content you are authorized to process and review the provider's data policies. Logs contain operational events only, not resume bodies or credentials. Treat all generated career guidance as suggestions, not hiring decisions.

## Future Enhancements

- PDF/DOCX ingestion with local parsing and explicit user consent
- Counselor review and configurable role catalogs
- User-controlled export formats and accessibility review
- Expanded validation and privacy impact assessment before production use
