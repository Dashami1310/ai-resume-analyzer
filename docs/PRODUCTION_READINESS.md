# Production Readiness Review

## Verdict

**Suitable for a controlled workshop/demo; not ready for public production deployment with real candidate resumes.** The current implementation demonstrates the end-to-end flow and has a deterministic Offline path, but it does not include public-service access control, usage controls, production privacy governance, or operational testing.

## Requirements Coverage

| Area                        | Current status                                                                                     |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| Resume submission           | Pasted text area, built-in sample, character counter and limit                                     |
| Analysis modes              | Offline default; optional OpenAI mode when a key is configured, with per-submission acknowledgment |
| Summary, skills, experience | Present; Offline output is rule-based and OpenAI narrative is generated text                       |
| Job recommendations         | Matches against five static role profiles, not live vacancies                                      |
| Missing skills and learning | Generated from the returned role profiles and a limited local learning map/OpenAI response         |
| Resume improvements         | OpenAI suggestions or local generic suggestions                                                    |
| Report                      | JSON download generated from the current analysis                                                  |
| Resume persistence          | No SQLite resume storage or resume logging; session state is cleared by the user action            |

## Area Assessment

### Architecture

The Streamlit entry point, presentation module, settings, analysis service, prompt, role catalog, and state helper are separated. This is a reasonable small-monolith architecture. SQLite is used only for a small static role catalog. Streamlit script reruns and initialization behavior should be reviewed under concurrent use.

### UI/UX

The interface presents input, analysis mode, consent, results, role matches, roadmap, improvements, and report download. It is a single-page Streamlit experience; accessibility and responsive behavior have not been certified with a formal audit.

### Testing

The suite has unit and AppTest coverage and currently reports 30 passing tests. The AppTest download assertion checks the generated JSON download element/URL; it is not a cross-browser file-save test. No live OpenAI, load, penetration, or hosted-environment tests are present.

### Security and Privacy

The API key is environment-backed, `.env` is ignored by Git, resume text is not written to SQLite/logs, and the OpenAI path requires acknowledgment. There is no authentication, authorization, per-user quota, or provider spend limit. The app does not establish provider retention terms, a privacy impact assessment, or session-memory expiry policy.

### Performance

The role catalog is small and local. OpenAI requests are synchronous with a 30-second timeout and one retry. There is no load test, request queue, rate limiter, caching strategy for multi-user deployment, or latency target.

### Maintainability

Configuration, prompt, service, UI, and tests are separated; CI is defined. The skills vocabulary, learning map, role catalog, match threshold, and role score are code-defined. Changes to these need review and tests. The SQLite seed uses `INSERT OR IGNORE`, so there is no general migration/update process for changed role records.

### Documentation and DevOps

The root README documents setup, operation, environment variables, and data handling. The GitHub Actions workflow runs tests and compilation on Python 3.11 for pushes and pull requests targeting `main`. No deployment workflow or infrastructure definition is included.

## Known Limitations

- Five illustrative profiles only; there are no live job listings or employer integrations.
- Skill detection is limited to the vocabulary embedded in the service; Offline experience and summary are heuristic.
- OpenAI schema validation enforces response shape, not factual accuracy or evidence.
- Resume files are not uploaded or parsed; input is pasted text.
- The app has no user accounts, candidate history, counselor roles, or administrative catalog editor.
- SQLite is not configured as a production multi-tenant database.
- No production monitoring, alerting, backup/restore, deployment, or incident-response setup is provided.

## Workshop/Demo Readiness

The project is appropriate for an instructional demo of requirements, architecture, code generation, reviews, mocked testing, consent-aware optional AI use, local role matching, and a downloadable report. Offline mode supports demonstrations without a real key or network request. Current tests pass and the CI workflow is present.

## Required Before Real Production Deployment

1. Add authentication/authorization, per-user rate limits, usage quotas, and OpenAI spend controls.
2. Complete privacy/legal review for resume processing, provider transfer, retention, deletion, and user consent.
3. Define session expiry and verify clearing behavior across browser disconnects, server restarts, and multiple users.
4. Add evidence/provenance to AI-generated claims, adversarial prompt tests, and human review expectations.
5. Decide whether static illustrative roles meet the product need. If real jobs are required, add an approved, maintained job data source and update matching requirements.
6. Define production deployment topology, TLS, secret storage/rotation, health checks, logs/metrics, backup/restore, and incident response.
7. Load-test concurrent use and catalog behavior; consider a managed database if role/user data grows.
8. Add accessibility checks and browser-level tests for mode selection, consent, clear/reset, and actual downloaded report contents.
9. Add dependency/security scanning and release controls to CI before handling real candidate data.
