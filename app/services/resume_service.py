"""Resume validation, analysis, and catalog-based job matching."""

from dataclasses import asdict, dataclass
import json
import logging
import re
from typing import Any

from app.config.settings import Settings
from app.prompts.resume_prompt import SYSTEM_PROMPT, build_resume_prompt
from app.services.job_catalog import JobCatalog

logger = logging.getLogger(__name__)

TECHNICAL_SKILLS = (
    "Python", "FastAPI", "Flask", "Django", "REST APIs", "SQL", "MySQL",
    "PostgreSQL", "SQLite", "Git", "Docker", "Kubernetes", "AWS", "Azure",
    "Linux", "JavaScript", "React", "Excel", "statistics", "data visualization",
    "testing", "Selenium", "CI/CD", "Java", "C++",
)
SOFT_SKILLS = (
    "communication", "leadership", "teamwork", "problem-solving", "collaboration",
    "adaptability", "time management", "mentoring", "analytical thinking",
)
LEARNING_BY_SKILL = {
    "Kubernetes": "Practice deploying a containerized service to a local Kubernetes cluster.",
    "AWS": "Build a small project using AWS fundamentals such as IAM, S3, and a serverless function.",
    "testing": "Add unit and integration tests to a project and run them in a CI pipeline.",
    "SQL": "Practice joins, grouping, and query optimization using a sample relational dataset.",
    "Docker": "Containerize an application and learn image versioning and multi-stage builds.",
    "REST APIs": "Design and document an API, including validation and consistent error responses.",
    "Git": "Practice feature branches, pull requests, and resolving a merge conflict.",
    "data visualization": "Create a concise dashboard that explains a dataset with clear chart choices.",
}


@dataclass(frozen=True)
class JobRecommendation:
    """A job profile ranked by resume skill overlap."""

    title: str
    match_percentage: int
    rationale: str
    matching_skills: list[str]
    missing_skills: list[str]


@dataclass(frozen=True)
class ResumeAnalysis:
    """Structured resume analysis shown in the UI and downloadable report."""

    summary: str
    technical_skills: list[str]
    soft_skills: list[str]
    experience_assessment: str
    job_recommendations: list[JobRecommendation]
    missing_skills: list[str]
    learning_suggestions: list[str]
    resume_improvements: list[str]
    provider: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return asdict(self)


class ResumeAnalysisError(ValueError):
    """Raised when resume input or an AI response is invalid."""


class ResumeAnalyzer:
    """Analyze resumes locally or enrich the analysis with OpenAI."""

    def __init__(
        self,
        settings: Settings,
        job_catalog: JobCatalog,
        openai_client: Any | None = None,
    ) -> None:
        self.settings = settings
        self.job_catalog = job_catalog
        self.openai_client = openai_client

    def analyze(self, resume_text: str) -> ResumeAnalysis:
        """Validate and analyze resume text without persisting the submitted content."""
        text = resume_text.strip()
        if len(text) < 30:
            raise ResumeAnalysisError("Enter at least 30 characters of resume content.")
        if len(text) > self.settings.max_resume_characters:
            raise ResumeAnalysisError(
                f"Resume exceeds the {self.settings.max_resume_characters:,}-character limit."
            )

        detected_technical = self._extract_skills(text, TECHNICAL_SKILLS)
        detected_soft = self._extract_skills(text, SOFT_SKILLS)
        if self.settings.openai_api_key:
            result = self._analyze_with_openai(text)
            technical = self._clean_list(result.get("technical_skills"), 20) or detected_technical
            soft = self._clean_list(result.get("soft_skills"), 12) or detected_soft
            provider = "OpenAI"
        else:
            result = self._analyze_offline(text, detected_technical, detected_soft)
            technical, soft, provider = detected_technical, detected_soft, "Offline"

        recommendations = self._recommend_jobs(technical)
        missing = list(dict.fromkeys(skill for job in recommendations[:3] for skill in job.missing_skills))[:8]
        learning = self._clean_list(result.get("learning_suggestions"), 8)
        if not learning:
            learning = [LEARNING_BY_SKILL[skill] for skill in missing if skill in LEARNING_BY_SKILL][:5]
        if not learning:
            learning = ["Choose one target role and complete a small project that demonstrates its core skills."]

        return ResumeAnalysis(
            summary=self._clean_text(result.get("summary"), "Resume analyzed; review the extracted skills and role matches below."),
            technical_skills=technical,
            soft_skills=soft,
            experience_assessment=self._clean_text(
                result.get("experience_assessment"),
                "Add measurable outcomes and clarify your level of ownership for each project or role.",
            ),
            job_recommendations=recommendations,
            missing_skills=missing,
            learning_suggestions=learning,
            resume_improvements=self._clean_list(result.get("resume_improvements"), 8) or self._default_improvements(text),
            provider=provider,
        )

    def _analyze_with_openai(self, resume_text: str) -> dict[str, Any]:
        try:
            client = self.openai_client
            if client is None:
                from openai import OpenAI

                client = OpenAI(api_key=self.settings.openai_api_key, timeout=30.0, max_retries=1)
            response = client.chat.completions.create(
                model=self.settings.openai_model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_resume_prompt(resume_text)},
                ],
                temperature=0.2,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content or "{}")
            if not isinstance(parsed, dict):
                raise ValueError("The AI response must be a JSON object.")
            return parsed
        except Exception as error:
            logger.warning("Resume analysis provider failed (%s).", type(error).__name__)
            raise ResumeAnalysisError(
                "AI analysis is temporarily unavailable. Check the API configuration and try again."
            ) from error

    @staticmethod
    def _analyze_offline(
        resume_text: str, technical_skills: list[str], soft_skills: list[str]
    ) -> dict[str, Any]:
        words = re.findall(r"\b\w+\b", resume_text)
        summary = (
            f"Resume contains {len(words)} words and {len(technical_skills)} recognizable technical "
            f"skills. The strongest initial role matches are ranked below."
        )
        experience_match = re.search(r"\b(\d+(?:\.\d+)?)\s+years?\b", resume_text, re.IGNORECASE)
        experience = (
            f"The resume states {experience_match.group(1)} years of experience. "
            "Add the scope, technologies, and measurable results for each position or project."
            if experience_match
            else "No clear duration of experience was detected. Add dates and measurable outcomes for roles and projects."
        )
        return {
            "summary": summary,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "experience_assessment": experience,
            "learning_suggestions": [],
            "resume_improvements": ResumeAnalyzer._default_improvements(resume_text),
        }

    def _recommend_jobs(self, skills: list[str]) -> list[JobRecommendation]:
        normalized_skills = {self._normalize(skill) for skill in skills}
        recommendations = []
        for profile in self.job_catalog.all_profiles():
            required = [skill.strip() for skill in profile["skills"].split(",")]
            matching = [
                skill
                for skill in required
                if any(self._skill_matches(skill, candidate) for candidate in normalized_skills)
            ]
            missing = [
                skill
                for skill in required
                if not any(self._skill_matches(skill, candidate) for candidate in normalized_skills)
            ]
            percentage = round(100 * len(matching) / len(required))
            recommendations.append(
                JobRecommendation(
                    title=profile["title"],
                    match_percentage=percentage,
                    rationale=profile["description"],
                    matching_skills=matching,
                    missing_skills=missing,
                )
            )
        return sorted(recommendations, key=lambda item: (-item.match_percentage, item.title))[:3]

    @staticmethod
    def _extract_skills(text: str, known_skills: tuple[str, ...]) -> list[str]:
        padded_text = f" {ResumeAnalyzer._normalize(text)} "
        return [
            skill
            for skill in known_skills
            if f" {ResumeAnalyzer._normalize(skill)} " in padded_text
        ]

    @staticmethod
    def _skill_matches(required_skill: str, candidate_skill: str) -> bool:
        required = ResumeAnalyzer._normalize(required_skill)
        if required == candidate_skill:
            return True
        return required == "sql" and candidate_skill in {"mysql", "postgresql", "sqlite"}

    @staticmethod
    def _normalize(value: str) -> str:
        return re.sub(r"[^a-z0-9+#]+", " ", value.casefold()).strip()

    @staticmethod
    def _clean_list(value: Any, limit: int) -> list[str]:
        if not isinstance(value, list):
            return []
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return list(dict.fromkeys(cleaned))[:limit]

    @staticmethod
    def _clean_text(value: Any, fallback: str) -> str:
        return value.strip()[:2000] if isinstance(value, str) and value.strip() else fallback

    @staticmethod
    def _default_improvements(resume_text: str) -> list[str]:
        improvements = [
            "Lead each experience bullet with an action verb and include a measurable result.",
            "Tailor the skills and project details to the requirements of each target role.",
            "Use consistent dates, headings, and formatting throughout the document.",
        ]
        if not re.search(r"\bhttps?://|\bwww\.", resume_text, re.IGNORECASE):
            improvements.append("Add a professional portfolio, GitHub, or LinkedIn link if relevant.")
        return improvements