from typing import List, Dict, Any, Optional
from app.models.schemas import ScoreBreakdown, ScoringWeights
from app.config import DEFAULT_WEIGHTS
from app.extractor.skill_taxonomy import AI_ML_CORE_SKILLS, GENAI_CORE_SKILLS, TOOLS_DEPLOYMENT_CORE_SKILLS

def calculate_ai_ml_score(candidate_skills: List[str], evidence_map: Optional[Dict[str, Any]] = None) -> float:
    """
    Evaluate candidate proficiency specifically across the AI/ML core stack:
    TensorFlow, PyTorch, Scikit-learn, CNN, NLP, Python, Deep Learning, NumPy, Pandas.
    Awards bonus for practical demonstration in projects or work history.
    """
    evidence_map = evidence_map or {}
    cand_set = {s.lower() for s in candidate_skills}

    # Stack component weights (sum to 100)
    ai_ml_weights = {
        "python": 18.0,
        "pytorch": 18.0,
        "tensorflow": 14.0,
        "scikit-learn": 14.0,
        "cnn": 10.0,
        "nlp": 10.0,
        "deep learning": 6.0,
        "machine learning": 6.0,
        "numpy": 2.0,
        "pandas": 2.0
    }

    score = 0.0
    for skill_key, max_pts in ai_ml_weights.items():
        if skill_key in cand_set or any(skill_key in s for s in cand_set):
            evi = evidence_map.get(skill_key.title(), evidence_map.get(skill_key, {}))
            demo_sec = evi.get("demonstration_section", "Skills Only")
            if demo_sec == "Experience":
                multiplier = 1.0
            elif demo_sec == "Projects":
                multiplier = 0.90
            else:
                multiplier = 0.50
            score += (max_pts * multiplier)

    return round(min(100.0, score), 1)

def calculate_genai_score(candidate_skills: List[str], evidence_map: Optional[Dict[str, Any]] = None) -> float:
    """Evaluate candidate proficiency in Generative AI, LLMs, RAG, and Prompt Engineering."""
    evidence_map = evidence_map or {}
    cand_set = {s.lower() for s in candidate_skills}

    genai_weights = {
        "generative ai": 20.0,
        "llms": 25.0,
        "rag": 25.0,
        "prompt engineering": 15.0,
        "hugging face": 10.0,
        "langchain": 5.0
    }

    score = 0.0
    for skill_key, max_pts in genai_weights.items():
        if skill_key in cand_set or any(skill_key in s for s in cand_set):
            evi = evidence_map.get(skill_key.title(), evidence_map.get(skill_key, {}))
            demo_sec = evi.get("demonstration_section", "Skills Only")
            multiplier = 1.0 if demo_sec in ("Experience", "Projects") else 0.55
            score += (max_pts * multiplier)

    return round(min(100.0, score), 1)

def calculate_tools_deployment_score(candidate_skills: List[str], evidence_map: Optional[Dict[str, Any]] = None) -> float:
    """Evaluate software engineering, API development, and deployment tools."""
    evidence_map = evidence_map or {}
    cand_set = {s.lower() for s in candidate_skills}

    tools_weights = {
        "fastapi": 20.0,
        "rest apis": 20.0,
        "docker": 18.0,
        "git": 12.0,
        "ci/cd": 10.0,
        "aws": 10.0,
        "postgresql": 5.0,
        "redis": 5.0
    }

    score = 0.0
    for skill_key, max_pts in tools_weights.items():
        if skill_key in cand_set or any(skill_key in s for s in cand_set):
            evi = evidence_map.get(skill_key.title(), evidence_map.get(skill_key, {}))
            demo_sec = evi.get("demonstration_section", "Skills Only")
            multiplier = 1.0 if demo_sec in ("Experience", "Projects") else 0.60
            score += (max_pts * multiplier)

    return round(min(100.0, score), 1)

def validate_and_normalize_weights(weights: ScoringWeights) -> ScoringWeights:
    """Validate weights are non-negative and return normalized weights."""
    w_skill = max(0.0, float(weights.skills))
    w_sem = max(0.0, float(weights.semantic))
    w_exp = max(0.0, float(weights.experience))
    w_edu = max(0.0, float(weights.education))

    total = w_skill + w_sem + w_exp + w_edu
    if total <= 0.0001:
        return DEFAULT_WEIGHTS

    return ScoringWeights(
        skills=round(w_skill / total, 4),
        semantic=round(w_sem / total, 4),
        experience=round(w_exp / total, 4),
        education=round(w_edu / total, 4)
    )

def calculate_overall_score(
    skill_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    weights: ScoringWeights = DEFAULT_WEIGHTS,
    ai_ml_score: Optional[float] = None,
    projects_score: Optional[float] = None,
    genai_score: Optional[float] = None,
    tools_deployment_score: Optional[float] = None,
    target_role: str = "AI / Machine Learning Engineer"
) -> ScoreBreakdown:
    """
    Calculate dynamic multi-criteria score (0.0 to 100.0) with transparent component breakdown.
    For AI/ML positions, synthesizes Technical Skills, AI/ML Depth, Project Execution,
    Relevant Experience, GenAI Capabilities, Tools/Deployment, and Education.
    """
    c_tech = max(0.0, min(100.0, float(skill_score)))
    c_sem = max(0.0, min(100.0, float(semantic_score)))
    c_exp = max(0.0, min(100.0, float(experience_score)))
    c_edu = max(0.0, min(100.0, float(education_score)))

    # If called without explicit multi-dimensional domain parameters (e.g. standard unit tests)
    if ai_ml_score is None and genai_score is None and projects_score is None:
        clean_weights = validate_and_normalize_weights(weights)
        raw_overall = (
            (clean_weights.skills * c_tech) +
            (clean_weights.semantic * c_sem) +
            (clean_weights.experience * c_exp) +
            (clean_weights.education * c_edu)
        )
        c_aiml = c_tech
        c_proj = c_sem
        c_genai = c_tech
        c_tools = c_tech
    else:
        c_aiml = max(0.0, min(100.0, float(ai_ml_score if ai_ml_score is not None else skill_score)))
        c_proj = max(0.0, min(100.0, float(projects_score if projects_score is not None else semantic_score)))
        c_genai = max(0.0, min(100.0, float(genai_score if genai_score is not None else 0.0)))
        c_tools = max(0.0, min(100.0, float(tools_deployment_score if tools_deployment_score is not None else 50.0)))

        is_ai_role = any(term in target_role.lower() for term in ["ai", "machine learning", "ml", "data science"])

        if is_ai_role:
            # Dynamic composite formula for AI / ML engineering:
            # Technical Skills: 25%, AI/ML Stack: 25%, Projects: 15%, Relevant Experience: 15%, GenAI: 10%, Tools/Deployment: 5%, Education: 5%
            raw_overall = (
                (0.25 * c_tech) +
                (0.25 * c_aiml) +
                (0.15 * c_proj) +
                (0.15 * c_exp) +
                (0.10 * c_genai) +
                (0.05 * c_tools) +
                (0.05 * c_edu)
            )
        else:
            # General Software Engineering composite
            raw_overall = (
                (0.35 * c_tech) +
                (0.20 * c_tools) +
                (0.20 * c_proj) +
                (0.15 * c_exp) +
                (0.05 * c_sem) +
                (0.05 * c_edu)
            )

    clamped_overall = round(max(0.0, min(100.0, raw_overall)), 1)

    return ScoreBreakdown(
        overall_score=clamped_overall,
        skills_score=round(c_tech, 1),
        technical_skills_score=round(c_tech, 1),
        ai_ml_score=round(c_aiml, 1),
        experience_score=round(c_exp, 1),
        projects_score=round(c_proj, 1),
        genai_score=round(c_genai, 1),
        tools_deployment_score=round(c_tools, 1),
        education_score=round(c_edu, 1),
        semantic_score=round(c_sem, 1)
    )
