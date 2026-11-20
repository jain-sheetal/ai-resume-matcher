import re
from typing import List, Optional, Tuple, Union
from app.models.schemas import EmploymentEntry

# Relevant domain role patterns
HIGH_RELEVANCE_PATTERNS = [
    r'\b(ai|artificial\s+intelligence|machine\s+learning|ml|deep\s+learning|dl)\s+(engineer|developer|scientist|researcher|specialist|intern)\b',
    r'\b(data\s+scientist|data\s+science\s+intern|nlp\s+engineer|computer\s+vision\s+engineer|mlops\s+engineer)\b',
    r'\b(algorithm\s+engineer|research\s+fellow|ai\s+researcher)\b'
]

MEDIUM_RELEVANCE_PATTERNS = [
    r'\b(software\s+engineer|software\s+developer|backend\s+developer|python\s+developer|full\s*stack\s+developer)\b',
    r'\b(data\s+engineer|data\s+analyst|software\s+engineering\s+intern|developer\s+intern|sde|sde\s+[123])\b',
    r'\b(systems\s+engineer|cloud\s+engineer|devops\s+engineer)\b'
]

LOW_RELEVANCE_PATTERNS = [
    r'\b(qa\s+engineer|test\s+engineer|manual\s+tester|quality\s+assurance)\b',
    r'\b(it\s+support|helpdesk|technical\s+support|system\s+administrator)\b',
    r'\b(sales|marketing|recruiter|coordinator|executive|analyst\s+trainee)\b'
]

def calculate_role_relevance_weight(job_title: str, target_role: str = "AI / ML Engineer") -> float:
    """Determine role relevance weight (0.2 to 1.0) based on title alignment with target position."""
    clean_title = (job_title or "").lower().strip()
    clean_target = (target_role or "").lower()
    is_ai_target = any(term in clean_target for term in ["ai", "machine learning", "ml", "data science"])

    if is_ai_target:
        for pat in HIGH_RELEVANCE_PATTERNS:
            if re.search(pat, clean_title, re.IGNORECASE):
                return 1.0
        for pat in MEDIUM_RELEVANCE_PATTERNS:
            if re.search(pat, clean_title, re.IGNORECASE):
                return 0.85
        for pat in LOW_RELEVANCE_PATTERNS:
            if re.search(pat, clean_title, re.IGNORECASE):
                return 0.25
        return 0.70  # General technical default
    else:
        # General software engineering role
        for pat in MEDIUM_RELEVANCE_PATTERNS + HIGH_RELEVANCE_PATTERNS:
            if re.search(pat, clean_title, re.IGNORECASE):
                return 1.0
        for pat in LOW_RELEVANCE_PATTERNS:
            if re.search(pat, clean_title, re.IGNORECASE):
                return 0.30
        return 0.75

def calculate_relevant_experience_years(
    employment_history: List[EmploymentEntry],
    total_years: float,
    target_role: str = "AI / ML Engineer"
) -> float:
    """
    Calculate relevant professional experience years rather than blind total employment tenure.
    Excludes academic degree duration strictly.
    """
    if not employment_history:
        return round(total_years, 2)

    total_weighted_months = 0.0
    for emp in employment_history:
        weight = calculate_role_relevance_weight(emp.job_title, target_role)
        months = emp.duration_months if emp.duration_months > 0 else 0
        total_weighted_months += (months * weight)

    rel_years = round(total_weighted_months / 12.0, 2)
    # Ensure relevant years does not exceed total verified professional years
    return min(total_years, max(0.0, rel_years))

def evaluate_experience(
    candidate_years: float,
    required_years: float,
    employment_history: Optional[List[EmploymentEntry]] = None,
    target_role: str = "AI / Machine Learning Engineer",
    projects_score: float = 80.0,
    return_details: bool = False
) -> Union[float, Tuple[float, float]]:
    """
    Evaluate candidate experience considering relevant experience, job seniority, and fresher eligibility.
    If return_details is True, returns (score, relevant_years).
    If return_details is False (default), returns score for backwards compatibility.
    """
    employment_history = employment_history or []
    rel_years = calculate_relevant_experience_years(employment_history, candidate_years, target_role)

    # 1. Fresher / Entry-Level Role Eligibility (min required <= 1.0 year or 0 years)
    if required_years <= 1.0:
        # The position explicitly welcomes entry-level freshers (0–1 years).
        # Freshers with solid projects and internships must NOT be penalized for lack of 5-year corporate tenure.
        if rel_years >= 0.5:
            # Substantial entry-level internship/experience (e.g. 6-month AI internship)
            score = min(100.0, 90.0 + (rel_years * 15.0))
        elif rel_years > 0.0:
            # Brief internship
            score = 85.0
        else:
            # 0 years professional experience (fresher): evaluated on project readiness baseline
            score = min(80.0, 65.0 + (projects_score * 0.15))
        final_score = round(score, 1)
        return (final_score, rel_years) if return_details else final_score

    # 2. Mid / Senior Level Role (min required >= 2.0 years)
    if candidate_years == 0.0 and rel_years == 0.0:
        # Candidate has 0 years against mid/senior requirement
        score = 10.0
    elif rel_years >= required_years:
        # Fully meets or exceeds relevant experience requirements
        seniority_bonus = min(5.0, (rel_years - required_years) * 1.5)
        score = min(100.0, 95.0 + seniority_bonus)
    else:
        # Prorated on relevant experience completion
        ratio = max(0.0, rel_years / required_years)
        # Smooth progressive curve: 1.0/4.0 yrs gives ~30%
        score = (ratio ** 0.85) * 100.0
        score = min(92.0, max(10.0, score))

    final_score = round(score, 1)
    return (final_score, rel_years) if return_details else final_score

