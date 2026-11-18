import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict
from app.models.schemas import CandidateContact, CandidateEducation, EducationEntry, ExtractionConfidence

EMAIL_REGEX = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')
PHONE_REGEX = re.compile(r'(?:(?:\+?(\d{1,3}))?[-.\s]?)?(?:\(?(\d{3})\)?[-.\s]?)?(\d{3})[-.\s]?(\d{4})(?:\s*(?:ext|x|ext.)\s*(\d+))?')
LINKEDIN_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)', re.IGNORECASE)
GITHUB_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', re.IGNORECASE)

EDUCATION_PATTERNS = [
    (r'\b(ph\.?d\.?|doctor of philosophy|doctorate)\b', "Ph.D.", 1.0),
    (r'\b(master of science|m\.?s\.?|master of technology|m\.?tech\.?|msc|mba|master of arts|m\.?a\.?|master\'s|masters|mca)\b', "Master's Degree", 0.95),
    (r'\b(bachelor of science|b\.?s\.?|bachelor of technology|b\.?tech\.?|b\.?e\.?|bsc|bba|bachelor of arts|b\.?a\.?|bachelor\'s|bachelors|bca)\b', "Bachelor's Degree", 0.85),
    (r'\b(associate degree|associate of science|associate of arts|diploma)\b', "Associate / Diploma", 0.70),
    (r'\b(high school|secondary education|ged|12th standard)\b', "High School", 0.50),
]

NON_NAME_WORDS = {
    "resume", "curriculum", "vitae", "cv", "summary", "profile", "contact",
    "experience", "education", "skills", "projects", "work", "page", "phone",
    "email", "address", "developer", "engineer", "designer", "senior", "junior",
    "lead", "software", "portfolio", "objective", "certifications", "strengths"
}

def extract_name(text: str, filename: str = "") -> Tuple[str, str]:
    """
    Extract candidate name from first few lines or fallback to filename.
    Returns: (name, confidence_level: 'High' | 'Medium' | 'Low')
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines[:8]:
        # Strip bullets/punctuation from beginning of line
        clean_line = re.sub(r'^[^\w]+', '', line).strip()
        words = clean_line.split()

        # Name is typically 2 to 4 words, alphabetic, not containing section headers
        if 2 <= len(words) <= 4:
            lower_words = [w.lower() for w in words]
            if not any(w in NON_NAME_WORDS for w in lower_words):
                if all(re.match(r'^[a-zA-Z\.\'-]+$', w) for w in words):
                    return " ".join(words).title(), "High"

    # Fallback to filename if formatted as candidate name
    if filename:
        base = filename.rsplit(".", 1)[0]
        base = re.sub(r'[_\-]+', ' ', base)
        base = re.sub(r'(?i)(resume|cv|profile|final|updated|202\d|v\d+)', '', base).strip()
        words = base.split()
        if 2 <= len(words) <= 4 and all(re.match(r'^[a-zA-Z\.\'-]+$', w) for w in words):
            return base.title(), "Medium"
        elif len(words) >= 1:
            return base.title(), "Low"

    return "Candidate", "Low"

def extract_contact(text: str, filename: str = "") -> Tuple[CandidateContact, Dict[str, str]]:
    """Extract candidate contact details with field-level confidence ratings."""
    name, name_conf = extract_name(text, filename)

    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0) if email_match else None
    email_conf = "High" if email else "Low"

    # Find phone numbers (validating digit count between 10 and 15)
    phone = None
    phone_conf = "Low"
    for match in PHONE_REGEX.finditer(text):
        candidate_phone = match.group(0).strip()
        digits = re.sub(r'\D', '', candidate_phone)
        if 10 <= len(digits) <= 15:
            phone = candidate_phone
            phone_conf = "High"
            break

    linkedin_match = LINKEDIN_REGEX.search(text)
    linkedin = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None

    github_match = GITHUB_REGEX.search(text)
    github = f"https://github.com/{github_match.group(1)}" if github_match else None

    # Estimate location
    location = None
    loc_match = re.search(r'\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\b|\b[A-Z][a-zA-Z\s]+,\s*(?:USA|Canada|India|UK|Germany|Singapore))\b', text)
    if loc_match:
        location = loc_match.group(0).strip()

    confidence = {
        "name": name_conf,
        "email": email_conf,
        "phone": phone_conf,
        "contact": "High" if (email and phone) else ("Medium" if (email or phone) else "Low")
    }

    contact = CandidateContact(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        location=location
    )
    return contact, confidence

def extract_graduation_year(text: str) -> Optional[int]:
    """Look for realistic graduation years between 1980 and current_year + 5."""
    current_year = datetime.now().year
    years = re.findall(r'\b(19[89]\d|20[012]\d|2030)\b', text)
    valid_years = [int(y) for y in years if 1980 <= int(y) <= current_year + 4]
    return max(valid_years) if valid_years else None

def extract_education(text: str) -> Tuple[CandidateEducation, str]:
    """
    Detect candidate education without inventing unearned qualifications.
    Returns: (CandidateEducation, confidence: 'High' | 'Medium' | 'Low')
    """
    lower_text = text.lower()
    detected_entries: List[EducationEntry] = []
    highest_degree = "Not Specified"
    highest_score = 0.50
    is_detected = False

    # Check for degrees across the text
    for pattern, degree_label, score in EDUCATION_PATTERNS:
        match = re.search(pattern, lower_text, re.IGNORECASE)
        if match:
            if not is_detected:
                highest_degree = degree_label
                highest_score = score
                is_detected = True
            
            # Find associated institution near this degree mention
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(text), match.end() + 150)
            snippet = text[start_pos:end_pos]

            univ_match = re.search(r'([A-Za-z\s]+(University|Institute|College|Academy|Polytechnic)[A-Za-z\s]*)', snippet, re.IGNORECASE)
            inst = univ_match.group(1).strip()[:60] if univ_match else None
            grad_year = extract_graduation_year(snippet)

            detected_entries.append(EducationEntry(
                degree=degree_label,
                institution=inst,
                graduation_year=grad_year
            ))

    # General university fallback if specific degree snippet had none
    general_institution = None
    univ_search = re.search(r'([A-Za-z\s]+(University|Institute|College|Academy|School of [A-Za-z]+)[A-Za-z\s]*)', text, re.IGNORECASE)
    if univ_search:
        general_institution = univ_search.group(1).strip()[:60]

    # Assign primary institution
    primary_institution = detected_entries[0].institution if detected_entries and detected_entries[0].institution else general_institution
    grad_year = detected_entries[0].graduation_year if detected_entries else extract_graduation_year(text)

    # Determine confidence
    if is_detected and primary_institution:
        confidence = "High"
    elif is_detected or primary_institution:
        confidence = "Medium"
    else:
        confidence = "Low"

    edu = CandidateEducation(
        highest_degree=highest_degree,
        institution=primary_institution,
        graduation_year=grad_year,
        entries=detected_entries,
        is_detected=is_detected,
        score=highest_score if is_detected else 0.50
    )
    return edu, confidence
