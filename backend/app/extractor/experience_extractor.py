import re
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from app.models.schemas import CandidateExperience, CandidateEducation, EmploymentEntry

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "oct": 10, "october": 10,
    "nov": 11, "november": 11, "dec": 12, "december": 12
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}

ROLE_PATTERNS = [
    r'\b(?:senior|lead|staff|principal|junior|associate)?\s*(?:software|full[- ]?stack|frontend|backend|cloud|devops|data|machine learning|ai|nlp|systems|mobile|android|ios|qa|test|security|embedded)?\s*(?:engineering|research)?\s*(?:engineer|developer|architect|specialist|analyst|scientist|intern|consultant)\b'
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

EDUCATION_PATTERNS = [
    re.compile(r'\b(?:b\.?tech|btech|b\.?e|be|b\.?s|bs|b\.?sc|bsc|bca|bachelor|bachelors|undergraduate)\b', re.IGNORECASE),
    re.compile(r'\b(?:m\.?tech|mtech|m\.?e|me|m\.?s|ms|m\.?sc|msc|mca|master|masters|mba|pgdm|postgraduate)\b', re.IGNORECASE),
    re.compile(r'\b(?:diploma|polytechnic)\b', re.IGNORECASE),
    re.compile(r'\b(?:ph\.?d|phd|doctorate|doctor of philosophy)\b', re.IGNORECASE),
    re.compile(r'\b(?:cgpa|gpa|percentage|\bmarks\b|grades?)\b', re.IGNORECASE),
    re.compile(r'\b(?:university|college|institute of technology|institute|academy)\b', re.IGNORECASE),
    re.compile(r'\b(?:school|high school|matriculation|cbse|icse|class xii|class x|class 12|class 10|intermediate|secondary|higher secondary|state board)\b', re.IGNORECASE),
    re.compile(r'\b(?:degree in|major in|minor in|batch of|class of|expected graduation|scholastic|academic qualifications|educational qualifications)\b', re.IGNORECASE)
]

def is_education_line(line: str) -> bool:
    """Return True if line contains education, degree, diploma, school, or college markers."""
    return any(p.search(line) for p in EDUCATION_PATTERNS)

def clean_header_line(line: str) -> str:
    """Strip markdown hashes, numbering, bullets, and punctuation from section headers."""
    cleaned = re.sub(r'^[#\*\-–—\d\.\s\[\]\(|)]+', '', line).strip()
    cleaned = re.sub(r'[#\*\-–—\:\.\[\]\(\)|]+$', '', cleaned).strip()
    return cleaned

def is_sentence(cleaned: str) -> bool:
    """Check if line is a descriptive prose sentence rather than a section title."""
    if cleaned.endswith((".", "!", "?", ";")):
        return True
    sentence_markers = r'\b(i|my|we|our|am|was|were|worked|working|have|has|had|include|includes|including|such as|proficient in|responsible for|looking for)\b'
    return bool(re.search(sentence_markers, cleaned, re.IGNORECASE))

def is_experience_header(header_line: str) -> bool:
    """
    Check if line is an Experience section header across all resume conventions.
    Extract experience dates only from Employment History, Work Experience,
    Professional Experience, and relevant Internship sections.
    """
    cleaned = clean_header_line(header_line)
    if not cleaned or len(cleaned) > 55 or len(cleaned.split()) > 7 or is_sentence(cleaned):
        return False
    # Must NOT mention education / qualifications / degrees / school / college
    if re.search(r'\b(education|academic|academics|degree|university|college|school|diploma|b\.?tech|m\.?tech|mba|certification|certificate|courses?)\b', cleaned, re.IGNORECASE):
        return False
    return bool(re.search(
        r'\b(employment\s+history|work\s+experience|professional\s+experience|relevant\s+experience|relevant\s+internships?|internships?|internship\s+experience|work\s+history|job\s+history|career\s+history|industrial\s+training|professional\s+background|experience|experiences|employment)\b',
        cleaned,
        re.IGNORECASE
    ))

def is_other_header(header_line: str) -> bool:
    """
    Check if line is a Non-Experience header that demarcates other sections.
    Ignores dates appearing in Education, Academic Qualifications, Projects, etc.
    """
    cleaned = clean_header_line(header_line)
    if not cleaned or len(cleaned) > 55 or len(cleaned.split()) > 7 or is_sentence(cleaned):
        return False
    if is_experience_header(header_line):
        return False
    other_pattern = (
        r'\b(education|academic|academics|scholastic|qualifications?|educational\s+qualifications|academic\s+qualifications|'
        r'skills?|competencies|proficiencies|tech\s+stack|'
        r'projects?|personal\s+projects?|academic\s+projects?|'
        r'certifications?|certificates?|licenses?|courses?|'
        r'achievements?|awards?|honors?|publications?|patents?|'
        r'extracurricular|volunteer|leadership|activities|'
        r'interests?|hobbies|languages?|references?|declaration|'
        r'profile|summary|professional\s+summary|executive\s+summary|objective|career\s+objective|about\s+me)\b'
    )
    return bool(re.search(other_pattern, cleaned, re.IGNORECASE))

def isolate_experience_sections(text: str) -> str:
    """
    Isolate ONLY verifiable Employment History, Work Experience, Professional Experience,
    and relevant Internship sections. Ignore all dates in Education or Academic Qualifications.
    """
    raw_lines = text.split("\n")
    in_exp = False
    recognized_headers = set()
    exp_lines = []
    is_split_column_mode = False
    col_sections = [None, None]

    for raw_line in raw_lines:
        line_str = raw_line.strip()
        if not line_str:
            continue

        parts = re.split(r'\s{4,}|\t', raw_line)
        if len(parts) >= 2 and any(is_experience_header(p) for p in parts) and any(is_other_header(p) for p in parts):
            is_split_column_mode = True
            for c_idx, part in enumerate(parts[:2]):
                pt = part.strip()
                if is_experience_header(pt):
                    col_sections[c_idx] = "EXP"
                    recognized_headers.add("EXP")
                elif is_other_header(pt):
                    col_sections[c_idx] = "NON_EXP"
                    recognized_headers.add("NON_EXP")
            continue

        if is_split_column_mode:
            col_parts = re.split(r'\s{3,}|\t', raw_line)
            for c_idx, part in enumerate(col_parts[:2]):
                pt = part.strip()
                if not pt:
                    continue
                if is_experience_header(pt):
                    col_sections[c_idx] = "EXP"
                    recognized_headers.add("EXP")
                    continue
                elif is_other_header(pt):
                    col_sections[c_idx] = "NON_EXP"
                    recognized_headers.add("NON_EXP")
                    continue

                if c_idx < len(col_sections) and col_sections[c_idx] == "EXP":
                    if not is_education_line(pt):
                        exp_lines.append(pt)
        else:
            if is_experience_header(line_str):
                in_exp = True
                recognized_headers.add("EXP")
                continue
            elif is_other_header(line_str):
                in_exp = False
                recognized_headers.add("NON_EXP")
                continue

            if in_exp:
                if is_education_line(line_str):
                    subparts = re.split(r'\s{3,}|\s*\|\s*', line_str)
                    for sp in subparts:
                        s_strip = sp.strip()
                        if s_strip and not is_education_line(s_strip):
                            exp_lines.append(s_strip)
                else:
                    exp_lines.append(line_str)

    # If document has section headers (EDUCATION, SKILLS, PROJECTS) but NO experience header,
    # the candidate has 0 years professional experience (Fresher).
    if "NON_EXP" in recognized_headers and "EXP" not in recognized_headers:
        return ""

    if exp_lines:
        return "\n".join(exp_lines)

    # Unstructured text fallback (only if NO headers of any kind were found in the document)
    fallback_lines = []
    lines_list = [l.strip() for l in raw_lines if l.strip()]
    for i, line in enumerate(lines_list):
        if is_education_line(line):
            continue
        window = lines_list[max(0, i-2):min(len(lines_list), i+3)]
        if any(is_education_line(w) for w in window):
            if re.search(r'^\s*(?:19|20)\d\d\s*[-–—]\s*(?:19|20)\d\d\s*$', line):
                continue
        fallback_lines.append(line)

    return "\n".join(fallback_lines)

def parse_month_year(m_str: Optional[str], y_str: str, default_month: int) -> Tuple[int, int]:
    """Parse year and month (1-12) from matched string tokens."""
    year = int(y_str)
    month = default_month
    if m_str:
        clean = m_str.strip().lower()
        if clean in MONTHS:
            month = MONTHS[clean]
        elif clean.isdigit() and 1 <= int(clean) <= 12:
            month = int(clean)
    return year, month

def extract_month_intervals(text: str) -> List[Tuple[int, int]]:
    """
    Extract exact joining and leaving month intervals:
    - Joining date to leaving date: (start_month, start_year) to (end_month, end_year)
    - If currently working ('present', 'current', 'now', 'ongoing', 'till date'):
      calculate experience up to the current date (current month and year).
    Returns: List of (start_month_index, end_month_index) where month_index = year * 12 + month.
    """
    now = datetime.now()
    curr_year = now.year
    curr_month = now.month

    date_regex = re.compile(
        r'(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2}|present|current|now|ongoing|till\s+date)',
        re.IGNORECASE
    )

    intervals = []
    for match in date_regex.finditer(text):
        m1_str, y1_str, m2_str, y2_str = match.groups()
        try:
            if y2_str.lower() in ("present", "current", "now", "ongoing") or "till" in y2_str.lower():
                start_y, start_m = parse_month_year(m1_str, y1_str, 1)
                end_y = curr_year
                end_m = curr_month
                start_idx = start_y * 12 + start_m
                end_idx = end_y * 12 + end_m
            elif m1_str is None and m2_str is None:
                # Year-only range, e.g. "2022 - 2024" represents exactly (end_y - start_y) years
                start_y = int(y1_str)
                end_y = int(y2_str)
                diff_years = max(1, end_y - start_y)
                start_idx = start_y * 12 + 1
                end_idx = start_idx + (diff_years * 12) - 1
            else:
                start_y, start_m = parse_month_year(m1_str, y1_str, 1)
                end_y, end_m = parse_month_year(m2_str, y2_str, 12)
                # If start month and end month are identical across years (e.g., "Jan 2023 - Jan 2024"),
                # it denotes exactly N full years (12 * N months) rather than N yrs + 1 month.
                if m1_str and m2_str and start_m == end_m and end_y > start_y:
                    start_idx = start_y * 12 + start_m
                    end_idx = start_idx + ((end_y - start_y) * 12) - 1
                else:
                    start_idx = start_y * 12 + start_m
                    end_idx = end_y * 12 + end_m

            if start_idx <= end_idx and start_y >= 1980 and end_y <= curr_year + 1:
                duration_months = end_idx - start_idx + 1
                if duration_months <= 360:  # Cap at 30 years
                    intervals.append((start_idx, end_idx))
        except Exception:
            continue

    return intervals

def merge_month_intervals(intervals: List[Tuple[int, int]]) -> Tuple[int, int, int]:
    """
    Merge multiple overlapping jobs so overlapping months are NOT double-counted.
    Returns: (total_unique_months, years, remaining_months)
    """
    if not intervals:
        return 0, 0, 0

    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    curr_start, curr_end = sorted_intervals[0]

    for next_start, next_end in sorted_intervals[1:]:
        if next_start <= curr_end + 1:
            curr_end = max(curr_end, next_end)
        else:
            merged.append((curr_start, curr_end))
            curr_start, curr_end = next_start, next_end
    merged.append((curr_start, curr_end))

    total_months = sum((end - start + 1) for start, end in merged)
    years = total_months // 12
    remaining_months = total_months % 12
    return total_months, years, remaining_months

def extract_structured_employment_entries(text: str) -> List[EmploymentEntry]:
    """
    Extract structured employment history entries with title, company, dates, and type.
    Flags incomplete or ambiguous dates for verification without inventing dates.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    entries: List[EmploymentEntry] = []

    date_regex = re.compile(
        r'(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(?:(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?|\d{1,2})[\/\s\.,-]+)?(20\d{2}|19\d{2}|present|current|now|ongoing|till\s+date)',
        re.IGNORECASE
    )

    now = datetime.now()
    curr_year = now.year
    curr_month = now.month

    for line in lines:
        match = date_regex.search(line)
        if match:
            date_str = match.group(0).strip()
            m1_str, y1_str, m2_str, y2_str = match.groups()

            # Job title detection
            title = "Professional Role"
            for rpat in ROLE_PATTERNS:
                rm = re.search(rpat, line, re.IGNORECASE)
                if rm:
                    title = rm.group(0).strip().title()
                    break

            # Company name detection
            company = None
            comp_match = re.search(r'(?:at|@|—|–|-|\|)\s*([A-Z][A-Za-z0-9\s,\.&]{2,40})', line)
            if comp_match:
                company = comp_match.group(1).strip()
                # Clean up date leaks from company name
                company = re.sub(r'\(.*?\)', '', company).strip()

            # Employment type
            emp_type = "Full-time"
            if re.search(r'\b(intern|internship|trainee)\b', line, re.IGNORECASE):
                emp_type = "Internship"
            elif re.search(r'\b(part[- ]time|contract|freelance)\b', line, re.IGNORECASE):
                emp_type = "Part-time"

            is_current = bool(re.search(r'\b(present|current|now|ongoing|till date)\b', date_str, re.IGNORECASE))

            try:
                start_y, start_m = parse_month_year(m1_str, y1_str, 1)
                start_date_str = f"{MONTH_NAMES.get(start_m, '')} {start_y}".strip()

                if is_current:
                    end_y = curr_year
                    end_m = curr_month
                    end_date_str = "Present"
                    dur_months = (end_y * 12 + end_m) - (start_y * 12 + start_m) + 1
                elif m1_str is None and m2_str is None:
                    end_y = int(y2_str)
                    end_date_str = str(end_y)
                    dur_months = max(1, end_y - start_y) * 12
                else:
                    end_y, end_m = parse_month_year(m2_str, y2_str, 12)
                    end_date_str = f"{MONTH_NAMES.get(end_m, '')} {end_y}".strip()
                    if m1_str and m2_str and start_m == end_m and end_y > start_y:
                        dur_months = (end_y - start_y) * 12
                    else:
                        dur_months = (end_y * 12 + end_m) - (start_y * 12 + start_m) + 1
                if dur_months < 0:
                    dur_months = 0
                    verification_flag = "Ambiguous date range - start year exceeds end year"
                else:
                    verification_flag = None

                dur_y = dur_months // 12
                dur_m = dur_months % 12
                if dur_y > 0 and dur_m > 0:
                    dur_formatted = f"{dur_y} yr{'s' if dur_y > 1 else ''} {dur_m} mo{'s' if dur_m > 1 else ''}"
                elif dur_y > 0:
                    dur_formatted = f"{dur_y} year{'s' if dur_y > 1 else ''}"
                else:
                    dur_formatted = f"{dur_months} month{'s' if dur_months != 1 else ''}"

                entries.append(EmploymentEntry(
                    company_name=company,
                    job_title=title,
                    employment_type=emp_type,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    duration_months=dur_months,
                    duration_formatted=dur_formatted,
                    is_current=is_current,
                    verification_flag=verification_flag
                ))
            except Exception:
                continue

    return entries

def merge_intervals(intervals: List[Tuple[float, float]]) -> float:
    """Float interval merger for backwards compatibility with tests."""
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

def extract_date_ranges(text: str, grad_years: Optional[List[int]] = None) -> List[Tuple[float, float]]:
    """Float date range intervals for backwards compatibility with existing pipelines."""
    month_intervals = extract_month_intervals(text)
    float_intervals = []
    for s_idx, e_idx in month_intervals:
        s_y = (s_idx - 1) // 12
        s_m = (s_idx - 1) % 12 + 1
        e_y = (e_idx - 1) // 12
        e_m = (e_idx - 1) % 12 + 1

        start_time = s_y + (s_m - 1) / 12.0
        end_time = e_y + e_m / 12.0
        float_intervals.append((start_time, end_time))
    return float_intervals

def extract_years_from_explicit_mentions(text: str) -> List[float]:
    """Look for statements like '5+ years of experience', '3.5 years of hands-on experience'."""
    patterns = [
        r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+(?:hands-on|professional|industry|relevant|practical|work))?\s+(?:experience|exp|background|expertise)',
        r'(?:experience|exp):\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)',
        r'over\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
    ]
    found = []
    for line in text.split("\n"):
        if is_education_line(line):
            continue
        for pat in patterns:
            for match in re.finditer(pat, line, re.IGNORECASE):
                try:
                    yrs = float(match.group(1))
                    if 0.5 <= yrs <= 45:
                        found.append(yrs)
                except ValueError:
                    pass
    return found

def extract_projects(text: str) -> List[str]:
    """Extract named technical projects from resumes."""
    projects = []
    proj_section_match = re.search(r'(?i)(?:projects|technical projects|key projects)[\s\:\-]+(.*?)(?:education|experience|skills|certifications|$)', text, re.DOTALL)
    if proj_section_match:
        section_text = proj_section_match.group(1)
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

def format_professional_experience(total_months: int, years: int, remaining_months: int) -> Tuple[str, str, float]:
    """
    Format professional experience adhering strictly to requirements:
    - 0 months: '0 years (Fresher)' or '0 years'
    - 9 months: '9 months (0.75 years)' -> decimal exact 0.75 yrs
    - 12 months: '1 year' (1.0 yrs)
    - 18 months: '1.5 years (18 months)' (or '1 year 6 months')
    - 24 months: '2 years' (2.0 yrs)
    Returns: (formatted_experience, years_months_str, total_years_float)
    """
    if total_months == 0:
        return "0 years", "0 years 0 months", 0.0

    total_years_float = round(total_months / 12.0, 2)
    # Simplify 1.00 -> 1.0, 2.00 -> 2.0, 0.75 -> 0.75
    if total_years_float == int(total_years_float):
        total_years_float = round(total_years_float, 1)

    years_months_str = f"{years} years {remaining_months} months"

    if total_months < 12:
        formatted_experience = f"{total_months} months"
    elif remaining_months == 0:
        formatted_experience = f"{years} year" if years == 1 else f"{years} years"
    elif total_months == 18:
        formatted_experience = "1.5 years (18 months)"
    else:
        y_str = f"{years} year" if years == 1 else f"{years} years"
        m_str = f"{remaining_months} month" if remaining_months == 1 else f"{remaining_months} months"
        formatted_experience = f"{y_str} {m_str}"

    return formatted_experience, years_months_str, total_years_float

def calculate_professional_experience(
    text: str,
    education: Optional[CandidateEducation] = None
) -> Tuple[CandidateExperience, str]:
    """
    Centralized professional experience calculation function.
    Requirements:
    1. Calculate experience ONLY from actual professional employment history.
    2. Do NOT include B.Tech, M.Tech, MBA, diploma, school, college, or any other education duration.
    3. Ignore dates appearing in the Education and Academic Qualifications sections.
    4. Extract experience dates only from Employment History, Work Experience, Professional Experience, and relevant Internship sections.
    5. Calculate total experience using joining and leaving dates.
    6. If multiple jobs overlap, do not double-count overlapping months.
    7. If candidate is currently working, calculate experience up to current date.
    8. If no professional experience is mentioned, display 0 years (Fresher).

    Expected output:
    - Total Professional Experience: X years Y months
    - Education Duration: Excluded
    - Experience Status: Fresher / Experienced
    """
    # 1. Isolate ONLY Employment History, Work Experience, and Internship sections
    exp_section_text = isolate_experience_sections(text)

    # 2. Extract joining and leaving month intervals
    month_intervals = extract_month_intervals(exp_section_text)
    total_months, years, remaining_months = merge_month_intervals(month_intervals)

    # 3. Explicit mentions in summary (e.g. "5+ years of experience")
    explicit_years = extract_years_from_explicit_mentions(text)
    explicit_claimed = max(explicit_years) if explicit_years else None

    # Calculate exact total years float and formatted text
    if total_months > 0:
        formatted_experience, years_months_str, total_years = format_professional_experience(total_months, years, remaining_months)
        confidence = "High"
    elif explicit_claimed is not None and explicit_claimed > 0:
        total_years = explicit_claimed
        years = int(explicit_claimed)
        remaining_months = int(round((explicit_claimed - years) * 12))
        total_months = years * 12 + remaining_months
        formatted_experience, years_months_str, total_years = format_professional_experience(total_months, years, remaining_months)
        confidence = "Medium"
    else:
        total_years = 0.0
        total_months = 0
        years = 0
        remaining_months = 0
        formatted_experience = "0 years"
        years_months_str = "0 years 0 months"
        confidence = "Low"

    education_duration = "Excluded"
    experience_status = "Experienced" if total_months >= 12 else "Fresher"

    # Extract detected roles
    roles = []
    for pat in ROLE_PATTERNS:
        for match in re.finditer(pat, exp_section_text, re.IGNORECASE):
            r = match.group(0).strip().title()
            if r not in roles:
                roles.append(r)

    if not roles and total_years > 0:
        for pat in ROLE_PATTERNS:
            for match in re.finditer(pat, text, re.IGNORECASE):
                r = match.group(0).strip().title()
                if r not in roles:
                    roles.append(r)

    # Extract structured employment history entries
    employment_entries = extract_structured_employment_entries(exp_section_text)

    projects = extract_projects(text)
    certifications = extract_certifications(text)

    summary = (
        f"Total Professional Experience: {formatted_experience} | "
        f"Education Duration: {education_duration} | "
        f"Experience Status: {experience_status}"
    )

    exp = CandidateExperience(
        total_years=total_years,
        total_months=total_months,
        years=years,
        months=remaining_months,
        formatted_experience=formatted_experience,
        years_months=years_months_str,
        education_duration=education_duration,
        experience_status=experience_status,
        employment_history=employment_entries,
        calculated_years=total_years,
        explicit_claimed_years=explicit_claimed,
        role_titles=roles[:6],
        companies=[],
        projects=projects,
        certifications=certifications,
        confidence=confidence,
        summary=summary
    )
    return exp, confidence

# Alias extract_experience to the centralized calculate_professional_experience function
extract_experience = calculate_professional_experience
