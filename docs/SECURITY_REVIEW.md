# Security Review

## Scope

This is a code-based review of the current workshop application, not a penetration test or legal/privacy assessment. The application is suitable for controlled demonstrations; the controls below are not sufficient to claim production readiness.

## Secrets

- `OPENAI_API_KEY` is read from process environment or `.env` through `Settings.from_environment()`.
- `.env` is listed in `.gitignore`; `.env.example` contains an empty key placeholder.
- The application does not hardcode an API key.
- CI sets `OPENAI_API_KEY` to an empty value and does not reference GitHub secrets.
- OpenAI tests inject a dummy key/client; AppTest uses a nonfunctional dummy key and leaves consent unchecked so the provider is not invoked.

**Assessment:** Appropriate for a local workshop. Public deployment should use the host's managed secret store and rotate credentials if they are exposed.

## API Key Handling and OpenAI Transfer

When a key is configured, the sidebar exposes Offline and OpenAI-powered modes, with Offline as the default. OpenAI mode displays a notice and requires the user to acknowledge that the resume will be sent. Consent is required by `analyze_and_replace()` before the analyzer callback runs and is reset when the resume or mode changes.

When acknowledged, the full resume text is placed in the OpenAI user message. The README and UI disclose this behavior. No resume text or API key is included in the provider error log message; it records the exception type only.

**Residual risk:** The app does not define provider data-retention terms, a data-processing agreement, or an organization-specific approval process. Consent in the UI does not itself establish legal or organizational authorization.

## Resume Privacy and Persistence

- The active resume is held in Streamlit session state while the session is active.
- The clear action blanks the resume and removes current analysis, report/consent state, and resets the mode to Offline.
- SQLite stores only static role profiles; no resume repository or analysis-history table exists.
- The logging formatter records timestamp, severity, logger name, and message. The provider warning uses the exception class name, not the exception message or resume content.
- The JSON report is generated from the current in-memory `ResumeAnalysis` when rendering the download control. The application does not separately persist that report.

**Residual risk:** There is no documented session timeout or server-memory retention guarantee beyond Streamlit session lifecycle. Users must choose the clear action or close the session; hosted operators should define and verify lifecycle behavior.

## Input Validation

- Input is stripped and must contain at least 30 characters.
- The maximum defaults to 30,000 characters and is configurable through `MAX_RESUME_CHARACTERS`; configuration rejects non-integers and values below 500.
- The UI also sets the text-area character limit.
- OpenAI output is requested using a strict JSON schema and validated by Pydantic for required field types and no extra fields.

**Residual risk:** The limit has no configured upper ceiling. Resume content is wrapped in `<resume>` delimiters and described as untrusted in the prompt, but prompt text is not a complete defense against model instruction-following. Output schema validation checks structure, not truth, grounding, or safe career conclusions.

## Error Handling

- Invalid resume length raises `ResumeAnalysisError` and is displayed as a UI error.
- OpenAI/client/JSON/schema failures are converted to a generic provider error.
- The logger records only the exception type for provider failures.
- Consent failures are displayed as a warning and do not call the analyzer.

**Residual risk:** Unexpected database, configuration, or other runtime exceptions outside the known application exceptions are not uniformly translated into an operator-friendly error boundary.

## Logging

Logging is configured with a basic timestamp/level/logger/message format. No resume-specific logging exists in the code path. There are no request IDs, structured audit events, metrics, or log-retention configuration.

## Current Risks and Recommended Future Controls

| Severity | Risk                                                                                                                                                             | Recommended control before public deployment                                                                                                         |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| High     | No application authentication/authorization, rate limits, or per-user OpenAI budget. Public users could submit arbitrary resumes and consume a server-owned key. | Add identity/access control, request and token quotas, provider spend limits, abuse monitoring, and deployment restrictions.                         |
| High     | Resume text is sensitive personal data and is sent to a third party in OpenAI mode.                                                                              | Add organization-approved consent wording, data-processing review, retention/deletion policy, and provider configuration review.                     |
| Medium   | AI narrative and soft-skill output is schema-validated but not evidence-grounded.                                                                                | Display supporting evidence, mark generated claims as suggestions, and require human review for consequential use.                                   |
| Medium   | Prompt injection may influence model narrative despite untrusted-input instructions and delimiters.                                                              | Add adversarial prompt tests, constrain output, avoid rendering untrusted Markdown links, and keep the model without tools or side-effect authority. |
| Medium   | Session memory and generated report lifecycle depend on Streamlit session behavior.                                                                              | Set/verify session expiry, document retention, and add an operational data-clearance procedure.                                                      |
| Medium   | SQLite is a small local catalog; catalog initialization occurs as the Streamlit script runs.                                                                     | Cache/read-optimize catalog access, define schema/seed migrations, and load-test concurrent sessions.                                                |
| Low      | Operational logging/monitoring is minimal.                                                                                                                       | Add privacy-safe request IDs, health/error metrics, alerting, and log retention controls without capturing resume content or secrets.                |

## Logging and Secret Handling Checklist

- Never add resume bodies, OpenAI keys, or provider request/response payloads to logs.
- Keep `.env` out of version control and use managed secrets in hosted environments.
- Keep CI credentials empty unless a separately approved integration test explicitly requires a secret; this project's CI does not.
- Review dependency advisories and rotate any key that may have been committed or exposed.
