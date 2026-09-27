"""Streamlit interface for the AI Resume Analyzer."""

import json

import streamlit as st

from app.config.settings import Settings
from app.services.job_catalog import JobCatalog
from app.services.resume_service import ResumeAnalysisError, ResumeAnalyzer
from app.utils.logging_config import configure_logging

DEMO_RESUME = """John Smith
Python Developer

Skills:
Python, FastAPI, Git, Docker, MySQL, REST APIs

Experience:
2 Years Experience Building Backend Applications.
Developed APIs for E-Commerce Systems.

Education:
Bachelor of Engineering in Computer Science."""

st.set_page_config(page_title="Resume Analyzer", page_icon="▤", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&display=swap');
    :root { --ink: #172a27; --muted: #63736f; --paper: #f4f6f1; --line: #dce3dc; --green: #176b52; --lime: #d6eb8a; --coral: #e77c61; }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
    .stApp { background: var(--paper); }
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1160px; padding-top: 2.2rem; padding-bottom: 4rem; }
    .eyebrow { font: 500 11px 'DM Mono', monospace; text-transform: uppercase; color: var(--green); letter-spacing: 0; }
    .hero { border-bottom: 1px solid var(--line); padding: 0 0 1.6rem; margin-bottom: 1.8rem; }
    .hero h1 { font-size: clamp(2rem, 4vw, 3.4rem); line-height: 1.03; letter-spacing: 0; margin: .4rem 0; }
    .hero p { color: var(--muted); max-width: 650px; margin: .65rem 0 0; }
    .panel-title { font-weight: 700; font-size: 1.05rem; margin: 0 0 .35rem; }
    .small-note { color: var(--muted); font-size: .88rem; }
    .role-row { border-top: 1px solid var(--line); padding: .8rem 0; }
    .role-top { display:flex; justify-content:space-between; gap:1rem; font-weight:600; }
    .role-meta { color:var(--muted); font-size:.85rem; margin-top:.25rem; }
    .stButton > button[kind="primary"] { background: var(--green); border-color: var(--green); }
    .stButton > button { border-radius: 4px; }
    [data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); padding: .85rem 1rem; border-radius: 4px; }
    [data-testid="stMetricValue"] { color: var(--green); }
    textarea { border-radius: 4px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = Settings.from_environment()
configure_logging(settings.log_level)
catalog = JobCatalog(settings.database_path)
analyzer = ResumeAnalyzer(settings, catalog)

st.markdown(
    '<div class="hero"><div class="eyebrow">CAREER TOOLKIT / 01</div>'
    '<h1>Make your next move<br>with clearer signals.</h1>'
    '<p>Review your resume, surface strengths, and see which roles are closest to your current skill set.</p></div>',
    unsafe_allow_html=True,
)

with st.form("resume_form"):
    st.markdown('<div class="panel-title">Resume content</div>', unsafe_allow_html=True)
    resume_text = st.text_area(
        "Paste resume text",
        value=DEMO_RESUME,
        height=250,
        max_chars=settings.max_resume_characters,
        label_visibility="collapsed",
        placeholder="Paste the resume text you want to review...",
    )
    left, right = st.columns([1, 4])
    with left:
        submitted = st.form_submit_button("Analyze resume", type="primary", use_container_width=True)
    with right:
        st.caption(
            f"{len(resume_text):,} / {settings.max_resume_characters:,} characters · "
            f"{'AI-assisted' if settings.openai_api_key else 'Offline mode'}"
        )

if submitted:
    try:
        st.session_state["analysis"] = analyzer.analyze(resume_text)
    except ResumeAnalysisError as error:
        st.error(str(error))

analysis = st.session_state.get("analysis")
if analysis:
    st.divider()
    st.markdown('<div class="eyebrow">YOUR ANALYSIS</div>', unsafe_allow_html=True)
    st.subheader("Resume snapshot")
    st.write(analysis.summary)
    metric_columns = st.columns(3)
    metric_columns[0].metric("Technical skills", len(analysis.technical_skills))
    metric_columns[1].metric("Soft skills", len(analysis.soft_skills))
    metric_columns[2].metric("Roles compared", len(analysis.job_recommendations))

    skills_col, experience_col = st.columns([1, 1], gap="large")
    with skills_col:
        st.markdown("#### Skills analysis")
        st.markdown("**Technical**")
        st.write(", ".join(analysis.technical_skills) if analysis.technical_skills else "No known technical skills detected.")
        st.markdown("**Soft skills**")
        st.write(", ".join(analysis.soft_skills) if analysis.soft_skills else "No explicit soft skills detected.")
    with experience_col:
        st.markdown("#### Experience assessment")
        st.write(analysis.experience_assessment)

    st.markdown("#### Role matches")
    for role in analysis.job_recommendations:
        st.markdown(
            f'<div class="role-row"><div class="role-top"><span>{role.title}</span>'
            f'<span>{role.match_percentage}%</span></div><div class="role-meta">{role.rationale}</div>'
            f'<div class="role-meta">Strong matches: {", ".join(role.matching_skills) or "Build foundational skills"}</div></div>',
            unsafe_allow_html=True,
        )

    missing_col, learn_col = st.columns([1, 1], gap="large")
    with missing_col:
        st.markdown("#### Skills to develop")
        if analysis.missing_skills:
            st.write(" · ".join(analysis.missing_skills))
        else:
            st.write("No major gaps surfaced for these role profiles.")
    with learn_col:
        st.markdown("#### Learning suggestions")
        for item in analysis.learning_suggestions:
            st.markdown(f"- {item}")

    st.markdown("#### Resume improvements")
    for item in analysis.resume_improvements:
        st.markdown(f"- {item}")

    report = json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False)
    st.download_button(
        "Download analysis report",
        data=report,
        file_name="resume-analysis.json",
        mime="application/json",
    )
    st.caption(f"Analysis mode: {analysis.provider}. Resume text is not saved to the SQLite catalog.")
else:
    st.info("Your analysis will appear here. Edit the sample resume or paste your own content to begin.")

st.caption("Career guidance is informational. Review recommendations and verify role requirements independently.")