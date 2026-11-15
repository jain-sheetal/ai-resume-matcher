import re
from typing import List, Optional
from app.extractor.skill_extractor import extract_skills_from_text
from app.models.schemas import ParsedJobDescription

EXP_PATTERNS = [
    r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
    r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp|relevant)',
    r'(?:minimum|at least|req(?:uire)?(?:d|s)?)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
    r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s+minimum',
]

EDU_PATTERNS = [
    (r'\b(ph\.?d|doctorate)\b', "Ph.D. required or preferred"),
    (r'\b(master\'?s?|m\.?s|m\.?tech|mba)\b', "Master's Degree preferred"),
    (r'\b(bachelor\'?s?|b\.?s|b\.?tech|b\.?e|degree in computer science)\b', "Bachelor's Degree required"),
]

def extract_job_title(text: str) -> str:
    """Heuristic to detect the Job Title from text."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        title_match = re.search(r'^(?:Job\s+Title|Position|Role|Title)\s*[:\-]\s*(.+)$', line, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
    if lines:
        first = lines[0]
        if len(first) < 80 and not any(w in first.lower() for w in ["about us", "overview", "company", "description"]):
            return first
    return "Software Engineer"

def extract_min_experience(text: str) -> float:
    """Extract required minimum years of experience from JD."""
    for pat in EXP_PATTERNS:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                # If range "3 to 5 years", take the lower bound as minimum required
                return float(match.group(1))
            except (ValueError, IndexError):
                pass
    return 2.0  # Industry default benchmark if not explicitly stated

def extract_required_education(text: str) -> str:
    """Extract education expectation from JD."""
    for pat, label in EDU_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return label
    return "Bachelor's Degree or equivalent practical experience"

def parse_job_description(text: str, custom_title: Optional[str] = None, custom_skills: Optional[List[str]] = None, custom_min_exp: Optional[float] = None) -> ParsedJobDescription:
    """Full parsing pipeline for a Job Description."""
    title = custom_title or extract_job_title(text)
    min_exp = custom_min_exp if custom_min_exp is not None else extract_min_experience(text)
    education = extract_required_education(text)

    # Extract skills
    auto_skills = extract_skills_from_text(text)
    if custom_skills:
        # Merge and deduplicate
        combined_skills = sorted(list(set(auto_skills + [s.title() for s in custom_skills])))
    else:
        combined_skills = auto_skills

    # Extract bullet points / responsibilities
    responsibilities = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith(("-", "*", "•", "–")) and len(line) > 15:
            responsibilities.append(line.lstrip("-*•– ").strip())

    return ParsedJobDescription(
        title=title,
        raw_text=text,
        required_skills=combined_skills,
        preferred_skills=[],
        min_experience_years=min_exp,
        required_education=education,
        key_responsibilities=responsibilities[:8]
    )
