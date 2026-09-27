"""Helpers for keeping Streamlit analysis state tied to the latest submission."""

from collections.abc import Callable, MutableMapping
from typing import TypeVar

Result = TypeVar("Result")


def analyze_and_replace(
    resume_text: str,
    analyze: Callable[[str], Result],
    session_state: MutableMapping[str, object],
) -> Result:
    """Remove stale output, then store only a successful analysis result."""
    session_state.pop("analysis", None)
    result = analyze(resume_text)
    session_state["analysis"] = result
    return result