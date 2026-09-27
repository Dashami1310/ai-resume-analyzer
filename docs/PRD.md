# Product Requirements Document

## Problem Statement

Students and job seekers need practical feedback before applying for roles. Resume review may be difficult to access consistently, and candidates may not know which skills are visible in their resume or what to improve next.

This application provides a workshop-scale resume review tool. A user pastes resume text and receives a summary, recognized skills, an experience assessment, illustrative role matches, skill gaps, learning suggestions, and resume improvements.

## Target Users

- Students and fresh graduates preparing resumes
- Job seekers reviewing their resume before applying
- Career counselors and placement officers demonstrating resume feedback
- Workshop participants learning an AI-assisted software delivery lifecycle

The current application is a single-user-session demo. It does not provide counselor accounts, placement-cell administration, or shared candidate records.

## Goals

- Accept pasted resume text and provide useful feedback in one Streamlit workflow.
- Make a deterministic Offline mode available without an API key or network call.
- Offer optional OpenAI-powered narrative analysis when an API key is configured and the user acknowledges the transfer for that submission.
- Make role matches, skill gaps, learning suggestions, and resume improvements easy to review.
- Avoid persisting resume content in SQLite or application logs.
- Provide a downloadable JSON analysis report.

## Functional Requirements

| ID    | Requirement                         | Current behavior                                                                                                                                                                         |
| ----- | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| FR-1  | Accept resume text                  | A Streamlit text area accepts pasted content and initially contains a sample resume.                                                                                                     |
| FR-2  | Provide a sample resume action      | The sample button restores the built-in John Smith resume.                                                                                                                               |
| FR-3  | Validate resume length              | The UI has a configurable character limit (default 30,000); the service requires at least 30 characters and enforces the configured maximum.                                             |
| FR-4  | Offer analysis modes                | Offline analysis is the default. OpenAI-powered mode is available only when `OPENAI_API_KEY` is configured.                                                                              |
| FR-5  | Require OpenAI acknowledgment       | OpenAI mode displays a transfer notice and requires a checkbox acknowledgment for the current resume submission. Editing the resume or changing modes clears the acknowledgment.         |
| FR-6  | Summarize and assess a resume       | The service returns a resume summary and experience assessment. Offline results use local heuristics; OpenAI mode uses a schema-validated model response for narrative fields.           |
| FR-7  | Extract skills                      | Technical skills are detected from a fixed local vocabulary. Soft skills are detected locally in Offline mode and may come from the validated OpenAI response in OpenAI mode.            |
| FR-8  | Recommend roles                     | The service compares locally detected technical skills with five seeded SQLite role profiles. Skills are equally weighted; matches below 30% are omitted and at most three are returned. |
| FR-9  | Identify skill gaps                 | Missing skills are collected from the returned role matches.                                                                                                                             |
| FR-10 | Suggest learning                    | Learning suggestions come from the OpenAI response, a limited local skill-to-learning map, or a generic fallback.                                                                        |
| FR-11 | Suggest resume improvements         | Suggestions come from the OpenAI response or a small set of local generic recommendations.                                                                                               |
| FR-12 | Download a report                   | The current analysis is serialized as JSON and offered through a Streamlit download button. It is not separately persisted by the application.                                           |
| FR-13 | Clear current data                  | The clear action blanks the current resume, removes analysis/report state and consent, and selects Offline mode.                                                                         |
| FR-14 | Keep resumes out of SQLite and logs | SQLite stores seeded role profiles only. Operational logs do not include resume text.                                                                                                    |

## Non-Functional Requirements

- **Privacy:** Keep the active resume in Streamlit session state only; explain and gate OpenAI transfer.
- **Security:** Read the API key from environment configuration; do not hardcode secrets. Return generic provider errors and do not log resume bodies.
- **Reliability:** OpenAI responses must follow the required JSON schema and Pydantic response model. Offline analysis must work without an API key.
- **Performance:** Reject input outside configured length limits. OpenAI requests use a 30-second timeout and one retry; no load or concurrency target is currently defined.
- **Maintainability:** Separate Streamlit entry-point, UI, settings, analysis service, prompt, role catalog, and utility code.
- **Testability:** Run pytest without a real API key or network dependency. Use temporary SQLite databases and mocked provider responses.
- **Compatibility:** Support Python 3.11 or newer as declared by project metadata; CI currently tests Python 3.11.

## User Stories

- As a student, I want to paste my resume and see its recognized strengths so I can decide what to improve.
- As a job seeker, I want to see illustrative role matches and their skill overlap so I can choose a direction to explore.
- As a user, I want to understand whether analysis is Offline or sends text to OpenAI before I submit it.
- As a user, I want to clear the current resume and its derived analysis when I finish.
- As a counselor or placement officer, I want to use a sample resume to demonstrate the workflow without a real API key.
- As a user, I want to download the current analysis as JSON for my own review.

## Acceptance Criteria

- A blank or too-short submission is rejected with a validation message; text beyond the configured maximum is rejected by the service.
- The sample action restores the built-in sample resume.
- With no API key, the app uses Offline analysis and does not invoke OpenAI.
- With an API key, Offline remains the default; selecting OpenAI mode shows a notice and no OpenAI request can proceed without acknowledgment.
- Changing the resume or mode invalidates previous analysis and consent.
- Analysis results include the supported summary, skill, experience, role-match, gap, learning, and improvement fields.
- Role match scores are equal-weight skill overlap against the static catalog; profiles below 30% are not displayed.
- The JSON download is available only while a current analysis exists.
- Clearing session data leaves an empty editor, no current analysis/report, and Offline mode selected.
- Resume text is not written to the SQLite role catalog or application logs.

## Out of Scope for the Current Application

- PDF or DOCX upload and parsing
- Live job vacancies, employer feeds, location filtering, or labor-market data
- User accounts, counselor workflows, candidate history, or administrative catalog editing
- Resume persistence, collaborative review, and non-JSON report formats
