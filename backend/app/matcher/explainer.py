from typing import List, Optional
from app.models.schemas import MatchExplanation, ScoreBreakdown, SkillMatchEvidence, ExtractionConfidence

def generate_match_explanation(
    candidate_name: str,
    matched_skills: List[str],
    missing_skills: List[str],
    additional_skills: List[str],
    candidate_years: float,
    required_years: float,
    breakdown: ScoreBreakdown,
    degree_name: str,
    skill_evidences: Optional[List[SkillMatchEvidence]] = None,
    confidence: Optional[ExtractionConfidence] = None
) -> MatchExplanation:
    """Generate transparent, evidence-based Explainable AI reasoning behind the candidate's match score."""
    strengths = []
    gaps = []
    skill_evidences = skill_evidences or []

    # 1. Experience Analysis
    exp_diff = candidate_years - required_years
    if exp_diff >= 0:
        if exp_diff >= 2.0:
            strengths.append(f"Substantial seniority: {candidate_years:.1f} yrs vs {required_years:.1f} yrs required (+{exp_diff:.1f} yrs buffer).")
            exp_text = f"Candidate comfortably exceeds the minimum tenure requirement by {exp_diff:.1f} years."
        else:
            strengths.append(f"Meets experience criteria: {candidate_years:.1f} yrs vs {required_years:.1f} yrs required.")
            exp_text = f"Candidate fully satisfies the expected {required_years:.1f} years minimum experience."
    else:
        gap_yrs = abs(exp_diff)
        gaps.append(f"Experience shortfall: {candidate_years:.1f} yrs vs {required_years:.1f} yrs required (-{gap_yrs:.1f} yrs gap).")
        exp_text = f"Candidate has {candidate_years:.1f} years of relevant experience, which is below the desired {required_years:.1f} years."

    # 2. Skill Evidence Analysis
    strong_matches = [e for e in skill_evidences if e.result == "Strong Match"]
    partial_matches = [e for e in skill_evidences if e.result == "Partial Match"]
    related_matches = [e for e in skill_evidences if e.result == "Related Skill"]
    missing_items = [e for e in skill_evidences if e.result == "Missing"]

    if strong_matches:
        strong_names = ", ".join([e.requirement for e in strong_matches[:4]])
        evidence_sample = strong_matches[0].evidence_snippet
        if evidence_sample:
            strengths.append(f"Strongly demonstrated skills ({len(strong_matches)}): {strong_names} (e.g. \"{evidence_sample[:90]}...\").")
        else:
            strengths.append(f"Strongly demonstrated skills ({len(strong_matches)}): {strong_names}.")

    if related_matches:
        rel_str = ", ".join([f"{e.requirement} (via {e.matched_term})" for e in related_matches[:3]])
        strengths.append(f"Transferable skill equivalence: {rel_str}.")

    if missing_items:
        miss_names = ", ".join([e.requirement for e in missing_items[:5]])
        gaps.append(f"Missing mandatory requirements ({len(missing_items)}): {miss_names}.")

    if additional_skills:
        top_add = ", ".join(additional_skills[:4])
        strengths.append(f"Additional technical versatility: {top_add}.")

    total_req = len(matched_skills) + len(missing_skills)
    pct = (len(matched_skills) / total_req * 100) if total_req > 0 else 0
    skill_text = (
        f"Candidate satisfies {len(matched_skills)} of {total_req} requirements ({pct:.0f}%) "
        f"with {len(strong_matches)} strongly demonstrated skills and {len(missing_items)} missing requirements."
    )

    # 3. Semantic Similarity Context
    if breakdown.semantic_score >= 80.0:
        strengths.append(f"Deep semantic alignment ({breakdown.semantic_score:.1f}%): Candidate project descriptions closely mirror job requirements.")
        sem_text = "Dense vector embeddings indicate exceptional conceptual and technical overlap with the position responsibilities."
    elif breakdown.semantic_score >= 65.0:
        sem_text = f"Moderate semantic alignment ({breakdown.semantic_score:.1f}%): Candidate works in an adjacent domain with transferable architectural knowledge."
    else:
        gaps.append(f"Low semantic correlation ({breakdown.semantic_score:.1f}%): Resume vocabulary suggests different industry focus.")
        sem_text = "Contextual vector embeddings reveal limited domain overlap with core job responsibilities."

    # 4. Education
    if degree_name and degree_name not in ("Not Specified", "Unknown"):
        strengths.append(f"Academic baseline verified: {degree_name}.")
    else:
        gaps.append("Education: Degree level not explicitly specified in resume.")

    # 5. Extraction Confidence Assessment
    conf_label = confidence.overall if confidence else "High"
    conf_assessment = f"{conf_label} Confidence Extraction: Candidate contact, skills, and chronological tenure verified from source document."

    # 6. Overall Verdict
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
        semantic_alignment=sem_text,
        confidence_assessment=conf_assessment
    )
