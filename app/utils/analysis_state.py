"""Helpers for keeping Streamlit analysis state tied to the latest submission."""

from collections.abc import Callable, MutableMapping
from typing import TypeVar

Result = TypeVar("Result")


class OpenAIConsentRequired(ValueError):
    """Raised when an OpenAI analysis is submitted without consent."""


def analyze_and_replace(
    resume_text: str,
    analyze: Callable[[str], Result],
    session_state: MutableMapping[str, object],
    *,
    require_openai_consent: bool = False,
    consent_acknowledged: bool = False,
) -> Result:
    """Remove stale output, then store only a successful analysis result."""
    session_state.pop("analysis", None)
    session_state.pop("analysis_report", None)
    if require_openai_consent and not consent_acknowledged:
        raise OpenAIConsentRequired(
            "Acknowledge that your resume will be sent to OpenAI before continuing."
        )
    result = analyze(resume_text)
    session_state["analysis"] = result
    return result


def clear_session_data(session_state: MutableMapping[str, object]) -> None:
    """Clear resume content and derived analysis/report state from the session."""
    session_state["resume_text"] = ""
    session_state["analysis_mode"] = "Offline analysis"
    for key in (
        "analysis",
        "analysis_report",
        "generated_report",
        "report",
        "openai_consent",
    ):
        session_state.pop(key, None)