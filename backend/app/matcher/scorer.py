from app.models.schemas import ScoreBreakdown, ScoringWeights
from app.config import DEFAULT_WEIGHTS

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
    weights: ScoringWeights = DEFAULT_WEIGHTS
) -> ScoreBreakdown:
    """
    Calculate the deterministic weighted matching score (0.0 to 100.0) and component breakdown.
    Formula:
        Overall = (w_skills * S_skill) + (w_semantic * S_sem) + (w_exp * S_exp) + (w_edu * S_edu)
    """
    clean_weights = validate_and_normalize_weights(weights)

    # Ensure component scores are strictly clamped between 0 and 100
    c_skill = max(0.0, min(100.0, float(skill_score)))
    c_sem = max(0.0, min(100.0, float(semantic_score)))
    c_exp = max(0.0, min(100.0, float(experience_score)))
    c_edu = max(0.0, min(100.0, float(education_score)))

    raw_overall = (
        (clean_weights.skills * c_skill) +
        (clean_weights.semantic * c_sem) +
        (clean_weights.experience * c_exp) +
        (clean_weights.education * c_edu)
    )

    clamped_overall = round(max(0.0, min(100.0, raw_overall)), 1)

    return ScoreBreakdown(
        overall_score=clamped_overall,
        skills_score=round(c_skill, 1),
        semantic_score=round(c_sem, 1),
        experience_score=round(c_exp, 1),
        education_score=round(c_edu, 1)
    )
