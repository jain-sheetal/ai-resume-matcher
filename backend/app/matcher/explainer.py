from typing import List, Optional, Tuple
from app.models.schemas import MatchExplanation, ScoreBreakdown, SkillMatchEvidence, ExtractionConfidence

def calculate_experience_gap(candidate_months: int, required_years: float) -> Tuple[int, str]:
    """Calculate the exact experience gap in months and human-readable text."""
    required_months = int(round(required_years * 12))
    gap_months = max(0, required_months - candidate_months)
    if gap_months == 0:
        return 0, "No gap (Requirement met)"

    gap_years = gap_months // 12
    gap_rem_months = gap_months % 12

    parts = []
    if gap_years > 0:
        parts.append(f"{gap_years} year{'s' if gap_years != 1 else ''}")
    if gap_rem_months > 0:
        parts.append(f"{gap_rem_months} month{'s' if gap_rem_months != 1 else ''}")

    formatted_gap = " and ".join(parts) if len(parts) == 2 else parts[0]
    return gap_months, formatted_gap

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
    confidence: Optional[ExtractionConfidence] = None,
    formatted_experience: Optional[str] = None
) -> MatchExplanation:
    """Generate transparent, evidence-based Explainable AI reasoning behind the candidate's match score."""
    strengths = []
    gaps = []
    skill_evidences = skill_evidences or []

    # 1. Experience Analysis adhering strictly to professional employment (academic excluded)
    cand_months = int(round(candidate_years * 12))
    req_months = int(round(required_years * 12))
    exp_display = formatted_experience or (f"{candidate_years:.2f} years" if candidate_years > 0 else "0 years (Fresher)")

    if required_years <= 0:
        strengths.append(f"Entry-level role (0 yrs min): Candidate brings {exp_display} of verified professional experience.")
        exp_text = f"Position is open to entry-level candidates / freshers (0 years minimum). Candidate offers {exp_display} of verified professional experience (Academic duration strictly excluded)."
    elif cand_months >= req_months:
        excess_months = cand_months - req_months
        if excess_months >= 24:
            strengths.append(f"Substantial seniority: {exp_display} vs {required_years:.1f} yrs required (+{round(excess_months / 12.0, 1)} yrs buffer).")
            exp_text = f"Candidate comfortably exceeds the minimum tenure requirement with {exp_display} of verified professional employment (Education duration strictly excluded)."
        else:
            strengths.append(f"Meets experience criteria: {exp_display} vs {required_years:.1f} yrs required.")
            exp_text = f"Candidate fully satisfies the expected {required_years:.1f} years minimum experience with {exp_display} of professional employment (Education duration strictly excluded)."
    else:
        gap_months, formatted_gap = calculate_experience_gap(cand_months, required_years)
        gaps.append(f"Experience shortfall: {exp_display} vs {required_years:.1f} yrs required (Experience gap: {formatted_gap}).")
        exp_text = f"Candidate has {exp_display} of verified professional experience, which is below the desired {required_years:.1f} years (Experience gap: {formatted_gap}). Academic duration (e.g., B.Tech degree) is strictly excluded."

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
        rel_str = ", ".join([f"{e.requirement}" for e in related_matches[:3]])
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
        strengths.append(f"Academic baseline verified: {degree_name} (Duration excluded from work tenure).")
    else:
        gaps.append("Education: Degree level not explicitly specified in resume.")

    # 5. Extraction Confidence Assessment
    conf_label = confidence.overall if confidence else "High"
    conf_assessment = f"{conf_label} Confidence Extraction: Candidate contact, skills, and chronological tenure verified from source document."

    # 6. Overall Verdict (Consistent with match percentage scale)
    overall = breakdown.overall_score
    if overall >= 80.0:
        verdict = "Strong Match — Priority Candidate"
    elif overall >= 65.0:
        verdict = "Good Match — Recommended for Screening"
    elif overall >= 50.0:
        verdict = "Moderate Match — Relevant Skills with Some Gaps"
    else:
        verdict = "Low Match — Significant Skill/Experience Mismatch"

    # 7. Transparent Ranking Explanation
    weaknesses = list(gaps)
    aiml_txt = f"{getattr(breakdown, 'ai_ml_score', breakdown.skills_score):.1f}%"
    proj_txt = f"{getattr(breakdown, 'projects_score', breakdown.semantic_score):.1f}%"
    exp_txt_score = f"{breakdown.experience_score:.1f}%"

    ranking_explanation = (
        f"Evaluated with an overall match score of {overall:.1f}% ({verdict.split('—')[0].strip()}). "
        f"Demonstrated {len(matched_skills)} matched technical skills with an AI/ML competency score of {aiml_txt} "
        f"and hands-on project score of {proj_txt}. Experience score is {exp_txt_score} based on verified professional "
        f"history ({exp_display}), with academic degree duration strictly excluded."
    )

    return MatchExplanation(
        verdict=verdict,
        strengths=strengths,
        gaps=gaps,
        weaknesses=weaknesses,
        ranking_explanation=ranking_explanation,
        experience_analysis=exp_text,
        skill_analysis=skill_text,
        semantic_alignment=sem_text,
        confidence_assessment=conf_assessment
    )
