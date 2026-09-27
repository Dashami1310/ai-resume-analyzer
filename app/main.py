"""Streamlit entry point for the AI Resume Analyzer."""

from dataclasses import replace

import streamlit as st

from app.config.settings import Settings
from app.services.job_catalog import JobCatalog
from app.services.resume_service import ResumeAnalysisError, ResumeAnalyzer
from app.utils.analysis_state import OpenAIConsentRequired, analyze_and_replace
from app.utils.logging_config import configure_logging
from app.ui import apply_design_system, render_analysis, render_hero, render_resume_input, render_sidebar

DEMO_RESUME = """John Smith
Python Developer

Skills:
Python, FastAPI, Git, Docker, MySQL, REST APIs

Experience:
2 Years Experience Building Backend Applications.
Developed APIs for E-Commerce Systems.

Education:
Bachelor of Engineering in Computer Science."""

settings = Settings.from_environment()
configure_logging(settings.log_level)
catalog = JobCatalog(settings.database_path)
openai_analyzer = ResumeAnalyzer(settings, catalog)
offline_analyzer = ResumeAnalyzer(replace(settings, openai_api_key=None), catalog)

st.set_page_config(page_title="AI Resume Analyzer", page_icon="▤", layout="wide")
apply_design_system()
openai_selected = render_sidebar(bool(settings.openai_api_key))
render_hero()
submitted, resume_text, consent_acknowledged = render_resume_input(
    settings.max_resume_characters,
    openai_selected,
    DEMO_RESUME,
)

if submitted:
    try:
        with st.spinner("Analyzing your resume..."):
            selected_analyzer = openai_analyzer if openai_selected else offline_analyzer
            analyze_and_replace(
                resume_text,
                selected_analyzer.analyze,
                st.session_state,
                require_openai_consent=openai_selected,
                consent_acknowledged=consent_acknowledged,
            )
    except OpenAIConsentRequired as error:
        st.warning(str(error))
    except ResumeAnalysisError as error:
        st.error(str(error))

render_analysis(st.session_state.get("analysis"))