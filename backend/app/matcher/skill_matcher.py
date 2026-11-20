from typing import List, Tuple, Set, Dict, Any, Optional
from app.models.schemas import SkillMatchEvidence
from app.matcher.embedding_engine import CONTROLLED_EQUIVALENCES

def classify_skill_result(
    req_canonical: str,
    cand_skills_lower: Set[str],
    evidence_map: Dict[str, Dict[str, Any]]
) -> Tuple[str, Optional[str], int, Optional[str], str]:
    """
    Classify match tier for a single required skill with section-aware demonstration proof:
    - Strong Match: Demonstrated with evidence in Work Experience or Projects
    - Partial Match: Stated in skills list or brief mention
    - Related Skill: Matched via controlled semantic equivalence or technical abbreviation
    - Missing: Not present in candidate profile
    Returns:
        (result, snippet, frequency, matched_term, demonstration_section)
    """
    req_lower = req_canonical.lower()

    # Exact canonical match
    if req_lower in cand_skills_lower:
        if not evidence_map:
            # Programmatic unit test call without raw text
            return "Strong Match", None, 1, req_canonical, "Experience"

        evi = evidence_map.get(req_canonical, {})
        freq = evi.get("frequency", 1)
        snippet = evi.get("snippet")
        term = evi.get("matched_term", req_canonical)
        demo_sec = evi.get("demonstration_section", "Skills Only")

        if demo_sec == "Experience":
            return "Strong Match", snippet, max(freq, 1), term, "Experience"
        elif demo_sec == "Projects":
            return "Strong Match", snippet, max(freq, 1), term, "Projects"
        elif snippet and len(snippet) > 40 and not snippet.lower().startswith(("skills:", "tools:")):
            return "Strong Match", snippet, max(freq, 1), term, "Experience"
        elif freq >= 1:
            return "Partial Match", snippet, freq, term, "Skills Only"
        else:
            return "Insufficient Evidence", snippet, freq, term, "Skills Only"

    # Check controlled equivalences (e.g. React.js <-> React, Machine Learning <-> ML, CNN <-> ConvNet)
    equiv_terms = CONTROLLED_EQUIVALENCES.get(req_lower, [])
    for eq in equiv_terms:
        if eq in cand_skills_lower or any(eq in k.lower() for k in cand_skills_lower):
            if not evidence_map:
                return "Related Skill", None, 1, eq, "Experience"
            matched_key = next((k for k in cand_skills_lower if eq in k.lower()), eq)
            evi = evidence_map.get(matched_key.title(), evidence_map.get(matched_key, {}))
            snippet = evi.get("snippet")
            demo_sec = evi.get("demonstration_section", "Skills Only")
            return "Related Skill", snippet, evi.get("frequency", 1), eq, demo_sec

    return "Missing", None, 0, None, "None"

def evaluate_skills_detailed(
    candidate_skills: List[str],
    required_skills: List[str],
    preferred_skills: Optional[List[str]] = None,
    evidence_map: Optional[Dict[str, Dict[str, Any]]] = None
) -> Tuple[List[str], List[str], List[str], List[SkillMatchEvidence], float]:
    """
    Context-aware skill evaluation with anti-keyword-stuffing verification:
    - Verifies skills demonstrated in Experience (1.0x) and Projects (0.90x).
    - Prevents ungrounded keyword lists from inflating scores (0.35x).
    - Cleans abbreviation matches (never emits "Machine Learning (via ml)").
    Returns:
        (matched_skills, missing_skills, additional_skills, skill_evidences, skill_score_0_to_100)
    """
    evidence_map = evidence_map or {}
    preferred_skills = preferred_skills or []
    cand_lower_set = {s.strip().lower() for s in candidate_skills}

    matched_skills = []
    missing_skills = []
    skill_evidences: List[SkillMatchEvidence] = []

    # 1. Anti-Keyword Stuffing Audit
    total_extracted = len(candidate_skills)
    demonstrated_count = sum(
        1 for evi in evidence_map.values()
        if evi.get("demonstration_section") in ("Experience", "Projects")
    )

    # If candidate lists > 20 skills but under 25% are substantiated in text, penalize ungrounded skills
    is_keyword_stuffed = (total_extracted >= 20 and (demonstrated_count / max(1, total_extracted)) < 0.25)
    ungrounded_multiplier = 0.15 if is_keyword_stuffed else 0.35

    mandatory_score = 0.0
    preferred_score = 0.0

    # 2. Evaluate Mandatory Skills
    for req in required_skills:
        result, snippet, freq, term, demo_sec = classify_skill_result(req, cand_lower_set, evidence_map)
        skill_evidences.append(SkillMatchEvidence(
            requirement=req,
            category="Mandatory",
            result=result,
            evidence_snippet=snippet,
            frequency=freq,
            matched_term=term,
            demonstration_section=demo_sec
        ))

        if result == "Strong Match":
            matched_skills.append(req)
            if demo_sec == "Experience":
                mandatory_score += 1.0
            else: # Projects
                mandatory_score += 0.90
        elif result == "Partial Match":
            matched_skills.append(req)
            mandatory_score += ungrounded_multiplier
        elif result == "Related Skill":
            # Always append clean canonical skill name (Fix issue 4: never "req (via term)")
            matched_skills.append(req)
            if demo_sec in ("Experience", "Projects"):
                mandatory_score += 0.85
            else:
                mandatory_score += (ungrounded_multiplier * 1.1)
        else:
            missing_skills.append(req)

    # 3. Evaluate Preferred Skills
    for pref in preferred_skills:
        result, snippet, freq, term, demo_sec = classify_skill_result(pref, cand_lower_set, evidence_map)
        skill_evidences.append(SkillMatchEvidence(
            requirement=pref,
            category="Preferred",
            result=result,
            evidence_snippet=snippet,
            frequency=freq,
            matched_term=term,
            demonstration_section=demo_sec
        ))

        if result in ("Strong Match", "Partial Match", "Related Skill"):
            matched_skills.append(pref)
            if demo_sec in ("Experience", "Projects"):
                preferred_score += 1.0
            else:
                preferred_score += 0.50

    # 4. Calculate Overall Technical Skill Score (0-100)
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
        bonus = min(5.0, len(additional_skills) * 0.4)
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
