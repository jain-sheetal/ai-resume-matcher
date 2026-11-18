from typing import List, Tuple, Set, Dict, Any, Optional
from app.models.schemas import SkillMatchEvidence
from app.matcher.embedding_engine import CONTROLLED_EQUIVALENCES

def classify_skill_result(
    req_canonical: str,
    cand_skills_lower: Set[str],
    evidence_map: Dict[str, Dict[str, Any]]
) -> Tuple[str, Optional[str], int, Optional[str]]:
    """
    Classify match tier for a single required skill:
    - Strong Match: Demonstrated in project/experience snippet or frequency >= 2
    - Partial Match: Found in skills list but only 1 brief mention
    - Related Skill: Matched via controlled semantic equivalence
    - Missing: Not present in candidate profile
    - Insufficient Evidence: Ambiguous or extremely brief mention
    """
    req_lower = req_canonical.lower()

    # Exact canonical match
    if req_lower in cand_skills_lower:
        evi = evidence_map.get(req_canonical, {})
        freq = evi.get("frequency", 1)
        snippet = evi.get("snippet")
        term = evi.get("matched_term", req_canonical)

        # If no evidence map passed (direct skill list) or demonstrated in text with snippet/freq
        if not evidence_map or freq >= 2 or (snippet and len(snippet) > 40 and not snippet.lower().startswith("skills:")):
            return "Strong Match", snippet, max(freq, 1), term
        elif freq >= 1:
            return "Partial Match", snippet, freq, term
        else:
            return "Insufficient Evidence", snippet, freq, term

    # Check controlled equivalences (e.g. React.js <-> React, Machine Learning <-> ML)
    equiv_terms = CONTROLLED_EQUIVALENCES.get(req_lower, [])
    for eq in equiv_terms:
        if eq in cand_skills_lower or any(eq in k.lower() for k in cand_skills_lower):
            matched_key = next((k for k in cand_skills_lower if eq in k.lower()), eq)
            evi = evidence_map.get(matched_key.title(), {})
            snippet = evi.get("snippet")
            return "Related Skill", snippet, evi.get("frequency", 1), eq

    return "Missing", None, 0, None

def evaluate_skills_detailed(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
    evidence_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> Tuple[List[str], List[str], List[str], List[SkillMatchEvidence], float]:
    """
    Context-aware skill evaluation distinguishing mandatory and preferred skills.
    Returns:
        (matched_skills, missing_skills, additional_skills, skill_evidences, skill_score_0_to_100)
    """
    evidence_map = evidence_map or {}
    preferred_skills = preferred_skills or []
    cand_lower_set = {s.strip().lower() for s in candidate_skills}

    matched_skills = []
    missing_skills = []
    skill_evidences: List[SkillMatchEvidence] = []

    # Score calculation variables
    mandatory_score = 0.0
    preferred_score = 0.0

    # 1. Evaluate Mandatory Skills
    for req in required_skills:
        result, snippet, freq, term = classify_skill_result(req, cand_lower_set, evidence_map)
        skill_evidences.append(SkillMatchEvidence(
            requirement=req,
            category="Mandatory",
            result=result,
            evidence_snippet=snippet,
            frequency=freq,
            matched_term=term
        ))

        if result == "Strong Match":
            matched_skills.append(req)
            mandatory_score += 1.0
        elif result == "Partial Match":
            matched_skills.append(req)
            mandatory_score += 0.85
        elif result == "Related Skill":
            matched_skills.append(f"{req} (via {term})")
            mandatory_score += 0.75
        else:
            missing_skills.append(req)

    # 2. Evaluate Preferred Skills
    for pref in preferred_skills:
        result, snippet, freq, term = classify_skill_result(pref, cand_lower_set, evidence_map)
        skill_evidences.append(SkillMatchEvidence(
            requirement=pref,
            category="Preferred",
            result=result,
            evidence_snippet=snippet,
            frequency=freq,
            matched_term=term
        ))

        if result in ("Strong Match", "Partial Match", "Related Skill"):
            matched_skills.append(pref)
            preferred_score += 1.0

    # 3. Calculate Overall Skill Score (0-100)
    total_mandatory = len(required_skills)
    total_preferred = len(preferred_skills)

    if total_mandatory > 0:
        base_mandatory_pct = (mandatory_score / total_mandatory) * 85.0
    else:
        base_mandatory_pct = 85.0 if candidate_skills else 0.0

    if total_preferred > 0:
        pref_pct = (preferred_score / total_preferred) * 15.0
    else:
        pref_pct = 15.0 if mandatory_score > 0 else 0.0

    raw_skill_score = base_mandatory_pct + pref_pct

    # Additional skills versatility bonus (up to +5%) ONLY if at least one mandatory skill is matched
    req_all_lower = {s.lower() for s in required_skills + preferred_skills}
    additional_skills = sorted([s for s in candidate_skills if s.lower() not in req_all_lower])

    if mandatory_score > 0 and additional_skills and raw_skill_score < 100.0:
        bonus = min(5.0, len(additional_skills) * 0.5)
        final_score = min(100.0, raw_skill_score + bonus)
    elif mandatory_score == 0 and total_mandatory > 0:
        final_score = 0.0
    else:
        final_score = min(100.0, raw_skill_score)

    return sorted(list(set(matched_skills))), sorted(missing_skills), additional_skills, skill_evidences, round(final_score, 1)

# Backward-compatible wrapper
def evaluate_skills(candidate_skills: List[str], required_skills: List[str]) -> Tuple[List[str], List[str], List[str], float]:
    matched, missing, additional, _, score = evaluate_skills_detailed(
        candidate_skills=candidate_skills,
        required_skills=required_skills
    )
    return matched, missing, additional, score
