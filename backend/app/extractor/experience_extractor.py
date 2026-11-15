import re
from datetime import datetime
from typing import List, Tuple
from app.models.schemas import CandidateExperience

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

CURRENT_YEAR = 2026

ROLE_PATTERNS = [
    r'\b(?:senior|lead|staff|principal|junior|associate)?\s*(?:software|full[- ]?stack|frontend|backend|cloud|devops|data|machine learning|ai|nlp|systems|mobile|android|ios)?\s*(?:engineer|developer|architect|specialist|analyst|scientist|intern)\b'
]

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
                if 0.5 <= yrs <= 40:
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
                end_time = CURRENT_YEAR + 0.5
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

            if 1980 <= start_time <= end_time <= CURRENT_YEAR + 1:
                duration = end_time - start_time
                if duration <= 25: # filter crazy outliers
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

def extract_experience(text: str) -> CandidateExperience:
    """Combine explicit mentions and chronological timeline to deduce experience."""
    explicit_years = extract_years_from_explicit_mentions(text)
    timeline_intervals = extract_date_ranges(text)
    timeline_years = merge_intervals(timeline_intervals)

    # Heuristic resolution:
    if explicit_years:
        # Prefer the maximum explicit claim within reason
        max_explicit = max(explicit_years)
        if timeline_years > 0:
            # Reconcile if timeline is close or higher
            total_years = max(max_explicit, timeline_years)
        else:
            total_years = max_explicit
    elif timeline_years > 0:
        total_years = timeline_years
    else:
        # Check if intern / entry-level keywords appear
        if re.search(r'\b(intern|internship|graduate|student|entry[- ]level)\b', text, re.IGNORECASE):
            total_years = 0.5
        else:
            total_years = 1.0 # Default conservative minimum

    # Extract detected roles
    roles = []
    for pat in ROLE_PATTERNS:
        for match in re.finditer(pat, text, re.IGNORECASE):
            r = match.group(0).strip().title()
            if r not in roles:
                roles.append(r)

    return CandidateExperience(
        total_years=round(total_years, 1),
        role_titles=roles[:6],
        summary=f"{total_years:.1f} years total professional experience across {len(roles)} identified roles."
    )
