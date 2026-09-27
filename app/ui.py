"""Streamlit presentation components for the resume analyzer."""

from html import escape
import json

import streamlit as st

from app.services.resume_service import ResumeAnalysis


DESIGN_CSS = """
<style>
:root {
    --ink: #172b26;
    --muted: #63746e;
    --canvas: #f3f6f3;
    --surface: #ffffff;
    --line: #dce5de;
    --primary: #176b52;
    --primary-dark: #105640;
    --primary-soft: #e6f1eb;
    --soft-skill: #edf1f4;
    --gap: #fff0e9;
    --gap-ink: #9e4f38;
}

html, body, [class*="css"] {
    color: var(--ink);
    font-family: "Aptos", "Segoe UI Variable", "Segoe UI", sans-serif;
}
.stApp { background: var(--canvas); }
[data-testid="stSidebar"] {
    background: #edf2ee;
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
.block-container { max-width: 1180px; padding: 1.8rem 2rem 4rem; }
.hero {
    background: linear-gradient(112deg, #e7f0e9 0%, #f8faf7 74%);
    border: 1px solid #d9e5dc;
    border-left: 4px solid var(--primary);
    border-radius: 8px;
    padding: 1.8rem 2rem 1.5rem;
    margin-bottom: 1.7rem;
}
.hero-kicker, .eyebrow, .step-label {
    color: var(--primary);
    font-size: .72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
}
.hero h1 {
    color: var(--ink);
    font-family: Georgia, "Times New Roman", serif;
    font-size: 2.7rem;
    font-weight: 500;
    line-height: 1.08;
    margin: .5rem 0 .45rem;
}
.hero-promise { color: var(--primary-dark); font-size: 1.15rem; font-weight: 650; margin: 0; }
.hero-support { color: var(--muted); font-size: .98rem; margin: .4rem 0 1.1rem; max-width: 720px; }
.workflow { display: flex; flex-wrap: wrap; gap: .55rem; }
.workflow-step {
    background: rgba(255,255,255,.72);
    border: 1px solid #d8e4dc;
    border-radius: 999px;
    color: #43564e;
    font-size: .78rem;
    padding: .35rem .7rem;
}
.section-heading { margin: 1.5rem 0 .7rem; }
.section-heading h2 { font-size: 1.32rem; margin: 0; }
.section-heading p { color: var(--muted); margin: .15rem 0 0; }
.brand-mark {
    align-items: center;
    background: var(--primary);
    border-radius: 7px;
    color: #fff;
    display: inline-flex;
    font-size: .82rem;
    font-weight: 700;
    height: 34px;
    justify-content: center;
    margin-bottom: .6rem;
    width: 34px;
}
.sidebar-product { font-size: 1.05rem; font-weight: 700; line-height: 1.2; }
.sidebar-kicker { color: var(--muted); font-size: .7rem; text-transform: uppercase; }
.skill-list { display: flex; flex-wrap: wrap; gap: .45rem; margin: .5rem 0 .8rem; }
.skill-chip {
    border: 1px solid #cfe1d5;
    border-radius: 999px;
    color: #245c45;
    display: inline-block;
    font-size: .82rem;
    line-height: 1.35;
    padding: .28rem .62rem;
}
.skill-chip--soft { background: var(--soft-skill); border-color: #dbe2e8; color: #405468; }
.skill-chip--gap { background: var(--gap); border-color: #f0d6ca; color: var(--gap-ink); }
.skill-chip--current { background: var(--primary-soft); }
.roadmap-arrow { color: #8b9b92; font-size: .8rem; text-align: center; }
.improvement-number { color: var(--primary); font-size: .72rem; font-weight: 700; }
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(24, 50, 38, .035);
    padding: .9rem 1rem;
}
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--primary-dark); font-size: 1.55rem; }
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border-color: var(--line);
    border-radius: 8px;
}
.stButton > button, .stDownloadButton > button {
    border-radius: 6px;
    min-height: 2.7rem;
    transition: background-color .16s ease, border-color .16s ease, transform .16s ease;
}
.stButton > button[kind="primary"] {
    background: var(--primary);
    border-color: var(--primary);
}
.stButton > button[kind="primary"]:hover {
    background: var(--primary-dark);
    border-color: var(--primary-dark);
    transform: translateY(-1px);
}
textarea { border-radius: 6px !important; }
[data-testid="stProgress"] > div > div { background-color: var(--primary); }
@media (max-width: 760px) {
    .block-container { padding: 1rem .85rem 2.5rem; }
    .hero { padding: 1.25rem 1.1rem; }
    .hero h1 { font-size: 2.15rem; }
    div[data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: .7rem; }
    div[data-testid="column"] { flex: 1 1 230px; min-width: 0; }
}
</style>
"""


def apply_design_system() -> None:
    """Install the centralized visual system for the Streamlit page."""
    st.markdown(DESIGN_CSS, unsafe_allow_html=True)


def render_sidebar(openai_enabled: bool) -> None:
    """Render concise product, workflow, mode, and privacy information."""
    with st.sidebar:
        st.markdown('<div class="brand-mark">AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-product">AI Resume Analyzer</div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-kicker">Career intelligence</div>', unsafe_allow_html=True)
        st.divider()
        st.markdown("**How it works**")
        st.markdown("1. Add resume text\n2. Review skills and experience\n3. Explore illustrative role matches")
        st.divider()
        st.markdown("**Analysis mode**")
        if openai_enabled:
            st.markdown("OpenAI-assisted")
            st.caption("Narrative insights use the configured OpenAI model.")
        else:
            st.markdown("Offline heuristics")
            st.caption("Local rules run without an OpenAI API key.")
        st.divider()
        st.markdown("**Privacy**")
        st.caption("Resume text is not saved to SQLite. OpenAI mode sends submitted text to OpenAI for analysis.")
        st.caption("Streamlit app · Local role catalog")


def render_hero() -> None:
    """Render the product identity and three-step workflow introduction."""
    st.markdown(
        """
        <section class="hero">
            <div class="hero-kicker">Career intelligence</div>
            <h1>AI Resume Analyzer</h1>
            <p class="hero-promise">Turn your resume into your career roadmap.</p>
            <p class="hero-support">Analyze your resume, discover your strongest skills, identify gaps, and find roles worth targeting.</p>
            <div class="workflow">
                <span class="workflow-step">01 &nbsp; Resume input</span>
                <span class="workflow-step">02 &nbsp; AI analysis</span>
                <span class="workflow-step">03 &nbsp; Career insights</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _load_sample_resume(sample_resume: str) -> None:
    st.session_state["resume_text"] = sample_resume
    st.session_state.pop("analysis", None)


def _invalidate_analysis() -> None:
    st.session_state.pop("analysis", None)


def render_resume_input(
    max_characters: int,
    openai_enabled: bool,
    sample_resume: str,
) -> tuple[bool, str]:
    """Render the input editor and return the submit state and current text."""
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = sample_resume

    st.markdown(
        '<div class="section-heading"><div class="eyebrow">01 / Resume input</div>'
        '<h2>Start with your experience</h2>'
        '<p>Paste the text from your resume. You can edit the sample to explore the analysis.</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        header_left, header_right = st.columns([3, 1])
        with header_left:
            st.markdown("**Resume text**")
        with header_right:
            st.button(
                "Insert sample resume",
                on_click=_load_sample_resume,
                args=(sample_resume,),
                use_container_width=True,
            )
        resume_text = st.text_area(
            "Resume text",
            key="resume_text",
            height=270,
            max_chars=max_characters,
            on_change=_invalidate_analysis,
            label_visibility="collapsed",
            placeholder="Paste your resume here. Include role titles, experience, skills, and education for the clearest review.",
        )
        counter_col, mode_col = st.columns([1, 2])
        with counter_col:
            st.caption(f"{len(resume_text):,} / {max_characters:,} characters")
        with mode_col:
            mode_text = (
                "OpenAI-powered narrative analysis"
                if openai_enabled
                else "Offline heuristic analysis; no OpenAI request"
            )
            st.caption(mode_text)
        submitted = st.button(
            "Analyze resume",
            type="primary",
            use_container_width=True,
        )
    return submitted, resume_text


def _section_heading(title: str, description: str | None = None) -> None:
    st.markdown(f"### {title}")
    if description:
        st.caption(description)


def _render_skill_chips(
    skills: list[str],
    variant: str = "current",
    empty_text: str = "No skills detected in this category.",
) -> None:
    if not skills:
        st.caption(empty_text)
        return
    chips = "".join(
        f'<span class="skill-chip skill-chip--{variant}">{escape(skill)}</span>'
        for skill in skills
    )
    st.markdown(f'<div class="skill-list">{chips}</div>', unsafe_allow_html=True)


def _render_skill_section(analysis: ResumeAnalysis) -> None:
    _section_heading("Skills detected", "Recognized from the resume text and analysis response.")
    technical_col, soft_col = st.columns(2, gap="large")
    with technical_col:
        with st.container(border=True):
            st.markdown("**Technical skills**")
            _render_skill_chips(
                analysis.technical_skills,
                "current",
                "No recognized technical skills found.",
            )
    with soft_col:
        with st.container(border=True):
            st.markdown("**Soft skills**")
            _render_skill_chips(analysis.soft_skills, "soft", "No soft skills detected.")


def _render_role_cards(analysis: ResumeAnalysis) -> None:
    _section_heading(
        "Job recommendations",
        "Illustrative matches against local role profiles, not live job vacancies. Scores show the share of listed skills detected; each skill is equally weighted.",
    )
    if not analysis.job_recommendations:
        st.info("No role profile reached the 30% match threshold. Add documented skills or review the resume details.")
        return

    for role in analysis.job_recommendations:
        with st.container(border=True):
            title_col, score_col = st.columns([3, 1])
            with title_col:
                st.markdown(f"#### {role.title}")
                st.caption(role.rationale)
            with score_col:
                st.metric("Skill overlap", f"{role.match_percentage}%")
            st.progress(role.match_percentage / 100)
            matching_col, missing_col = st.columns(2, gap="large")
            with matching_col:
                st.caption("MATCHING SKILLS")
                _render_skill_chips(role.matching_skills, "current", "No listed skills matched.")
            with missing_col:
                st.caption("SKILLS TO BUILD")
                _render_skill_chips(role.missing_skills, "gap", "No listed skill gaps.")
            next_step = (
                f"Prioritize a project or resume bullet that demonstrates {role.missing_skills[0]}."
                if role.missing_skills
                else "Tailor your strongest accomplishment to this role's listed requirements."
            )
            st.caption(f"Suggested next step: {next_step}")


def _render_learning_roadmap(analysis: ResumeAnalysis) -> None:
    primary_role = analysis.job_recommendations[0].title if analysis.job_recommendations else "Role not yet matched"
    stages: list[tuple[str, list[str]]] = [
        ("Current skills", analysis.technical_skills[:5]),
        ("Skill gaps", analysis.missing_skills[:5]),
        ("Recommended learning", analysis.learning_suggestions),
        ("Target role", [primary_role]),
    ]
    columns = st.columns(4, gap="small")
    for index, (title, items) in enumerate(stages, start=1):
        with columns[index - 1]:
            with st.container(border=True):
                st.caption(f"STEP {index:02}")
                st.markdown(f"**{title}**")
                if items:
                    for item in items:
                        st.markdown(f"- {item}")
                else:
                    st.caption("No items identified")


def _render_improvements(analysis: ResumeAnalysis) -> None:
    _section_heading("Resume improvements", "Practical edits to strengthen clarity and evidence.")
    for start in range(0, len(analysis.resume_improvements), 2):
        columns = st.columns(2, gap="medium")
        for offset, suggestion in enumerate(analysis.resume_improvements[start:start + 2]):
            index = start + offset + 1
            with columns[offset]:
                with st.container(border=True):
                    st.markdown(f'<div class="improvement-number">ACTION {index:02}</div>', unsafe_allow_html=True)
                    st.write(suggestion)


def render_analysis(analysis: ResumeAnalysis | None) -> None:
    """Render the complete career-insights dashboard from the service result."""
    st.markdown(
        '<div class="section-heading"><div class="eyebrow">03 / Career insights</div>'
        '<h2>Your resume intelligence</h2></div>',
        unsafe_allow_html=True,
    )
    if analysis is None:
        st.info("Your analysis will appear here after you submit resume text.")
        return

    if analysis.provider == "Offline":
        st.info("Heuristic analysis · Skills and experience are estimated with local rules. No OpenAI request was made.")
    else:
        st.info("OpenAI-assisted analysis · Role matching uses technical skills detected locally in the resume.")

    top_match = max((role.match_percentage for role in analysis.job_recommendations), default=0)
    match_value = f"{top_match}%" if top_match else "No close match"
    metric_columns = st.columns(4, gap="medium")
    metric_columns[0].metric("Top role match", match_value)
    metric_columns[1].metric("Skills detected", len(analysis.technical_skills) + len(analysis.soft_skills))
    metric_columns[2].metric("Role matches", len(analysis.job_recommendations))
    metric_columns[3].metric("Analysis mode", analysis.provider)

    _section_heading("Resume summary")
    with st.container(border=True):
        st.write(analysis.summary)

    _render_skill_section(analysis)

    _section_heading("Experience assessment")
    with st.container(border=True):
        st.write(analysis.experience_assessment)

    _render_role_cards(analysis)

    _section_heading("Missing skills", "Gaps gathered from the recommended illustrative role profiles.")
    with st.container(border=True):
        _render_skill_chips(
            analysis.missing_skills,
            "gap",
            "No target-role gaps are available until a profile matches.",
        )

    _section_heading("Learning roadmap", "Move from current strengths through focused practice toward a target role.")
    _render_learning_roadmap(analysis)

    _render_improvements(analysis)

    st.markdown("### Download report")
    with st.container(border=True):
        report_col, button_col = st.columns([3, 1])
        with report_col:
            st.markdown("**Take your analysis with you**")
            st.caption("Download the complete analysis as a JSON file.")
        with button_col:
            st.download_button(
                "Download analysis report",
                data=json.dumps(analysis.to_dict(), indent=2, ensure_ascii=False),
                file_name="resume-analysis.json",
                mime="application/json",
                use_container_width=True,
            )

    st.caption("Career guidance is informational. Review recommendations and verify role requirements independently.")