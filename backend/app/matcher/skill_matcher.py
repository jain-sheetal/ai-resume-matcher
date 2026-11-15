from typing import List, Tuple, Set

def evaluate_skills(candidate_skills: List[str], required_skills: List[str]) -> Tuple[List[str], List[str], List[str], float]:
    """
    Evaluate candidate skills against job description requirements.
    Returns:
        (matched_skills, missing_skills, additional_skills, skill_score_0_to_100)
    """
    cand_set: Set[str] = {s.strip().lower(): s for s in candidate_skills}
    req_set: Set[str] = {s.strip().lower(): s for s in required_skills}

    matched_keys = cand_set.keys() & req_set.keys()
    missing_keys = req_set.keys() - cand_set.keys()
    additional_keys = cand_set.keys() - req_set.keys()

    matched_skills = sorted([req_set[k] for k in matched_keys])
    missing_skills = sorted([req_set[k] for k in missing_keys])
    additional_skills = sorted([cand_set[k] for k in additional_keys])

    if not required_skills:
        # If JD specified no skills, base score on having any skills
        score = min(100.0, len(candidate_skills) * 10.0)
    else:
        # Base score on percentage of required skills matched
        base_ratio = len(matched_keys) / len(required_skills)
        score = base_ratio * 100.0

        # Small bonus for having additional relevant skills (up to +5%)
        if additional_skills and score < 100.0:
            bonus = min(5.0, len(additional_skills) * 0.5)
            score = min(100.0, score + bonus)

    return matched_skills, missing_skills, additional_skills, round(score, 1)
