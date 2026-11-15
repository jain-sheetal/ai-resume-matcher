import re
from typing import Optional, Tuple
from app.models.schemas import CandidateContact, CandidateEducation

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:(?:\+?(\d{1,3}))?[-.\s]?)?(?:\(?(\d{3})\)?[-.\s]?)?(\d{3})[-.\s]?(\d{4})(?:\s*(?:ext|x|ext.)\s*(\d+))?')
LINKEDIN_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9_-]+)', re.IGNORECASE)
GITHUB_REGEX = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)', re.IGNORECASE)

EDUCATION_PATTERNS = [
    (r'\b(ph\.?d\.?|doctor of philosophy|doctorate)\b', "Ph.D.", 1.0),
    (r'\b(master of science|m\.?s\.?|master of technology|m\.?tech\.?|msc|mba|master of arts|m\.?a\.?|master\'s|masters)\b', "Master's Degree", 0.95),
    (r'\b(bachelor of science|b\.?s\.?|bachelor of technology|b\.?tech\.?|b\.?e\.?|bsc|bba|bachelor of arts|b\.?a\.?|bachelor\'s|bachelors|bca|mca)\b', "Bachelor's Degree", 0.85),
    (r'\b(associate degree|associate of science|associate of arts|diploma)\b', "Associate / Diploma", 0.70),
]

NON_NAME_WORDS = {
    "resume", "curriculum", "vitae", "cv", "summary", "profile", "contact",
    "experience", "education", "skills", "projects", "work", "page", "phone",
    "email", "address", "developer", "engineer", "designer", "senior", "junior"
}

def extract_name(text: str, filename: str = "") -> str:
    """Extract candidate name from first few lines or fallback to filename."""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines[:6]:
        # Strip bullets/punctuation
        clean_line = re.sub(r'^[^\w]+', '', line).strip()
        words = clean_line.split()

        # Name is usually 2 to 4 words, letters only, not containing obvious header keywords
        if 2 <= len(words) <= 4:
            lower_words = [w.lower() for w in words]
            if not any(w in NON_NAME_WORDS for w in lower_words):
                if all(re.match(r'^[a-zA-Z\.\'-]+$', w) for w in words):
                    return " ".join(words).title()

    # Fallback to filename if reasonable
    if filename:
        base = filename.rsplit(".", 1)[0]
        base = re.sub(r'[_\-]+', ' ', base)
        base = re.sub(r'(?i)(resume|cv|profile|final|updated|202\d)', '', base).strip()
        if len(base.split()) >= 1:
            return base.title()

    return "Candidate"

def extract_contact(text: str, filename: str = "") -> CandidateContact:
    """Extract candidate contact details."""
    name = extract_name(text, filename)

    email_match = EMAIL_REGEX.search(text)
    email = email_match.group(0) if email_match else None

    # Find phone numbers (look for sequences of 10-14 digits/dashes)
    phone = None
    for match in PHONE_REGEX.finditer(text):
        candidate_phone = match.group(0).strip()
        # Ensure it has at least 10 digits
        digits = re.sub(r'\D', '', candidate_phone)
        if 10 <= len(digits) <= 15:
            phone = candidate_phone
            break

    linkedin_match = LINKEDIN_REGEX.search(text)
    linkedin = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None

    github_match = GITHUB_REGEX.search(text)
    github = f"https://github.com/{github_match.group(1)}" if github_match else None

    return CandidateContact(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github
    )

def extract_education(text: str) -> CandidateEducation:
    """Detect highest education qualification."""
    lower_text = text.lower()
    highest_degree = "Bachelor's Degree" # Sensible industry baseline
    highest_score = 0.85

    for pattern, degree_label, score in EDUCATION_PATTERNS:
        if re.search(pattern, lower_text, re.IGNORECASE):
            highest_degree = degree_label
            highest_score = score
            break

    # Look for university name keywords
    institution = None
    univ_match = re.search(r'([A-Za-z\s]+(University|Institute|College|Academy)[A-Za-z\s]*)', text, re.IGNORECASE)
    if univ_match:
        institution = univ_match.group(1).strip()[:50]

    return CandidateEducation(
        highest_degree=highest_degree,
        institution=institution,
        score=highest_score
    )
