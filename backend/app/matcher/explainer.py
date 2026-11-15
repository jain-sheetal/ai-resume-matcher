from typing import List
from app.models.schemas import MatchExplanation, ScoreBreakdown

def generate_match_explanation(
    candidate_name: str,
    matched_skills: List[str],
    missing_skills: List[str],
    additional_skills: List[str],
    candidate_years: float,
    required_years: float,
    breakdown: ScoreBreakdown,
    degree_name: str
) -> MatchExplanation:
    """Generate transparent Explainable AI reasoning behind the candidate's match score."""
    strengths = []
    gaps = []

    # 1. Experience Analysis
    exp_diff = candidate_years - required_years
    if exp_diff >= 0:
        if exp_diff >= 2.0:
            strengths.append(f"Substantial experience: {candidate_years:.1f} years vs {required_years:.1f} years required (+{exp_diff:.1f} yrs senior buffer).")
            exp_text = f"Candidate comfortably exceeds the minimum tenure requirement by {exp_diff:.1f} years."
        else:
            strengths.append(f"Meets experience criteria: {candidate_years:.1f} years vs {required_years:.1f} years required.")
            exp_text = f"Candidate fully satisfies the expected {required_years:.1f} years minimum experience."
    else:
        gap_yrs = abs(exp_diff)
        gaps.append(f"Experience shortfall: {candidate_years:.1f} years vs {required_years:.1f} years required (-{gap_yrs:.1f} yrs gap).")
        exp_text = f"Candidate has {candidate_years:.1f} years of relevant experience, which is below the desired {required_years:.1f} years."

    # 2. Skill Overlap Analysis
    total_req = len(matched_skills) + len(missing_skills)
    if total_req > 0:
        pct = (len(matched_skills) / total_req) * 100
        if matched_skills:
            top_matched = ", ".join(matched_skills[:5])
            strengths.append(f"Possesses {len(matched_skills)} of {total_req} core skills ({pct:.0f}%): {top_matched}.")
        if missing_skills:
            top_missing = ", ".join(missing_skills[:5])
            gaps.append(f"Lacks {len(missing_skills)} required skill(s): {top_missing}.")

        if additional_skills:
            top_add = ", ".join(additional_skills[:4])
            strengths.append(f"Offers bonus technical proficiencies: {top_add}.")

        skill_text = f"Candidate covers {pct:.0f}% of technical requirements with strong capability in {', '.join(matched_skills[:3]) if matched_skills else 'general software'}."
    else:
        skill_text = "No specific mandatory skills were isolated in the job description."

    # 3. Semantic Similarity Context
    if breakdown.semantic_score >= 80.0:
        strengths.append(f"High contextual semantic match ({breakdown.semantic_score:.1f}%): Resume vocabulary and project narratives closely match the job expectations.")
        sem_text = "Contextual embeddings indicate deep domain alignment across candidate projects and role objectives."
    elif breakdown.semantic_score >= 65.0:
        sem_text = f"Moderate semantic alignment ({breakdown.semantic_score:.1f}%): Candidate works in a related domain with transferable engineering terminology."
    else:
        gaps.append(f"Lower semantic overlap ({breakdown.semantic_score:.1f}%): Resume focus shows divergent responsibilities or tech stack from the target role.")
        sem_text = "Contextual embedding similarity suggests different industry domain or non-overlapping project focus."

    # 4. Education
    if breakdown.education_score >= 85:
        strengths.append(f"Educational qualification aligned: {degree_name}.")

    # 5. Overall Verdict
    overall = breakdown.overall_score
    if overall >= 85.0:
        verdict = "Strong Match — Priority Candidate"
    elif overall >= 72.0:
        verdict = "Good Potential — Recommended for Screening"
    elif overall >= 55.0:
        verdict = "Moderate Fit — Relevant Skills with Some Gaps"
    else:
        verdict = "Low Alignment — Significant Skill/Experience Mismatch"

    return MatchExplanation(
        verdict=verdict,
        strengths=strengths,
        gaps=gaps,
        experience_analysis=exp_text,
        skill_analysis=skill_text,
        semantic_alignment=sem_text
    )
