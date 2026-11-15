from app.models.schemas import ScoreBreakdown, ScoringWeights
from app.config import DEFAULT_WEIGHTS

def calculate_overall_score(
    skill_score: float,
    semantic_score: float,
    experience_score: float,
    education_score: float,
    weights: ScoringWeights = DEFAULT_WEIGHTS
) -> ScoreBreakdown:
    """
    Calculate the final weighted matching score (0.0 to 100.0) and component breakdown.
    Formula:
        Overall = (w_skills * S_skill) + (w_semantic * S_sem) + (w_exp * S_exp) + (w_edu * S_edu)
    """
    w_skill = weights.skills
    w_sem = weights.semantic
    w_exp = weights.experience
    w_edu = weights.education

    total_w = w_skill + w_sem + w_exp + w_edu
    if total_w <= 0:
        total_w = 1.0

    raw_overall = (
        (w_skill * skill_score) +
        (w_sem * semantic_score) +
        (w_exp * experience_score) +
        (w_edu * education_score)
    ) / total_w

    clamped_overall = round(max(0.0, min(100.0, raw_overall)), 1)

    return ScoreBreakdown(
        overall_score=clamped_overall,
        skills_score=round(skill_score, 1),
        semantic_score=round(semantic_score, 1),
        experience_score=round(experience_score, 1),
        education_score=round(education_score, 1)
    )
