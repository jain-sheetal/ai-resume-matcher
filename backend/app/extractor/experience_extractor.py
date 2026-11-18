import re
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import CandidateExperience

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

ROLE_PATTERNS = [
    r'\b(?:senior|lead|staff|principal|junior|associate)?\s*(?:software|full[- ]?stack|frontend|backend|cloud|devops|data|machine learning|ai|nlp|systems|mobile|android|ios|qa|test|security|embedded)?\s*(?:engineer|developer|architect|specialist|analyst|scientist|intern|consultant)\b'
]

CERTIFICATION_PATTERNS = [
    r'\b(?:aws|azure|gcp|google cloud)\s+certified\s+[a-zA-Z\s]+',
    r'\b(?:cka|ckad|cks)\b',
    r'\b(?:certified kubernetes administrator|certified kubernetes application developer)\b',
    r'\b(?:pmp|prince2|scrum master|csm|psm)\b',
    r'\b(?:comptia\s+[a-zA-Z\+]+)\b',
    r'\b(?:cisco\s+certified|ccna|ccnp)\b',
    r'\b(?:tensorflow\s+developer|meta\s+front-end|deeplearning\.ai)\b'
]

def get_current_year_and_fraction() -> Tuple[int, float]:
    """Get dynamic current year and month fraction (e.g., 2026.85)."""
    now = datetime.now()
    year = now.year
    month_fraction = (now.month - 1) / 12.0
    return year, year + month_fraction

def extract_years_from_explicit_mentions(text: str) -> List[float]:
    """Look for statements like '5+ years of experience', '3 years working with...'"""
    patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp|background|expertise)',
        r'(?:experience|exp):\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        r'over\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
    ]
    found = []
    for pat in patterns:
        for match in re.finditer(pat, text, re.IGNORECASE):
            try:
                yrs = float(match.group(1))
                if 0.5 <= yrs <= 45:
                    found.append(yrs)
            except ValueError:
                pass
    return found

def extract_date_ranges(text: str) -> List[Tuple[float, float]]:
    """
    Extract date intervals like:
    - 2020 - 2024
    - Jan 2019 - Present
    - 03/2018 - 11/2022
    """
    current_year, current_fraction = get_current_year_and_fraction()

    date_regex = re.compile(
        r'(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2}|present|current|now)',
        re.IGNORECASE
    )

    intervals = []
    for match in date_regex.finditer(text):
        m1_str, y1_str, m2_str, y2_str = match.groups()
        try:
            start_year = float(y1_str)
            start_month = 1
            if m1_str:
                clean_m1 = m1_str.strip().lower()
                if clean_m1 in MONTHS:
                    start_month = MONTHS[clean_m1]
                elif clean_m1.isdigit() and 1 <= int(clean_m1) <= 12:
                    start_month = int(clean_m1)

            start_time = start_year + (start_month - 1) / 12.0

            if y2_str.lower() in ("present", "current", "now"):
                end_time = current_fraction
            else:
                end_year = float(y2_str)
                end_month = 12
                if m2_str:
                    clean_m2 = m2_str.strip().lower()
                    if clean_m2 in MONTHS:
                        end_month = MONTHS[clean_m2]
                    elif clean_m2.isdigit() and 1 <= int(clean_m2) <= 12:
                        end_month = int(clean_m2)
                end_time = end_year + (end_month - 1) / 12.0

            # Validate range bounds
            if 1980 <= start_time <= end_time <= current_year + 1.5:
                duration = end_time - start_time
                if duration <= 30.0: # filter unrealistic outlier durations
                    intervals.append((start_time, end_time))
        except Exception:
            continue

    return intervals

def merge_intervals(intervals: List[Tuple[float, float]]) -> float:
    """Merge overlapping intervals to avoid double-counting years."""
    if not intervals:
        return 0.0

    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    curr_start, curr_end = sorted_intervals[0]

    for next_start, next_end in sorted_intervals[1:]:
        if next_start <= curr_end:
            curr_end = max(curr_end, next_end)
        else:
            merged.append((curr_start, curr_end))
            curr_start, curr_end = next_start, next_end
    merged.append((curr_start, curr_end))

    total = sum(end - start for start, end in merged)
    return round(total, 1)

def extract_projects(text: str) -> List[str]:
    """Extract named technical projects from resumes."""
    projects = []
    # Identify Project section
    proj_section_match = re.search(r'(?i)(?:projects|technical projects|key projects)[\s\:\-]+(.*?)(?:education|experience|skills|certifications|$)', text, re.DOTALL)
    if proj_section_match:
        section_text = proj_section_match.group(1)
        # Look for project titles (e.g. "Project Name - Description" or "• E-Commerce Platform")
        lines = section_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("-", "*", "•", "–")) and len(line) > 10:
                projects.append(line.lstrip("-*•– ").strip()[:100])
            elif re.match(r'^[A-Z][a-zA-Z0-9\s\-_]{3,40}(?:\s*[\:\|\-]\s*|\s*\(20\d\d\))', line):
                projects.append(line[:100])
    return projects[:6]

def extract_certifications(text: str) -> List[str]:
    """Extract recognized technical certifications."""
    certs = []
    for pat in CERTIFICATION_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            cert_name = match.group(0).strip().title()
            if cert_name not in certs:
                certs.append(cert_name)
    return certs[:5]

def extract_experience(text: str) -> Tuple[CandidateExperience, str]:
    """
    Combine explicit mentions and chronological timeline to deduce experience.
    Returns: (CandidateExperience, confidence: 'High' | 'Medium' | 'Low')
    """
    explicit_years = extract_years_from_explicit_mentions(text)
    timeline_intervals = extract_date_ranges(text)
    timeline_years = merge_intervals(timeline_intervals)

    explicit_claimed = max(explicit_years) if explicit_years else None

    # Reconcile experience
    if timeline_years > 0 and explicit_claimed is not None:
        total_years = max(timeline_years, explicit_claimed)
        confidence = "High"
    elif timeline_years > 0:
        total_years = timeline_years
        confidence = "High"
    elif explicit_claimed is not None:
        total_years = explicit_claimed
        confidence = "Medium"
    else:
        # Check if intern / entry-level keywords appear
        if re.search(r'\b(intern|internship|graduate|student|entry[- ]level)\b', text, re.IGNORECASE):
            total_years = 0.5
            confidence = "Low"
        else:
            total_years = 0.0 # DO NOT invent experience if none found!
            confidence = "Low"

    # Extract detected roles
    roles = []
    for pat in ROLE_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            r = match.group(0).strip().title()
            if r not in roles:
                roles.append(r)

    projects = extract_projects(text)
    certifications = extract_certifications(text)

    summary = (
        f"{total_years:.1f} years total professional experience "
        f"({timeline_years:.1f} yrs chronological, {len(roles)} roles identified)."
        if total_years > 0 else "No verified professional experience tenure found."
    )

    exp = CandidateExperience(
        total_years=round(total_years, 1),
        calculated_years=round(timeline_years, 1),
        explicit_claimed_years=explicit_claimed,
        role_titles=roles[:6],
        companies=[],
        projects=projects,
        certifications=certifications,
        summary=summary
    )
    return exp, confidence
