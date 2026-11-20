import re
from typing import List, Set, Dict, Tuple, Optional, Any
from app.extractor.skill_taxonomy import ALIAS_MAP, SKILL_TAXONOMY, get_canonical_skill

SORTED_TERMS = sorted(ALIAS_MAP.keys(), key=lambda x: len(x), reverse=True)

def partition_resume_sections(text: str) -> Dict[str, str]:
    """
    Partition raw resume text into distinct semantic sections:
    - experience: Work Experience, Employment History, Professional Experience, Internships
    - projects: Technical Projects, Personal Projects, Academic Projects
    - skills: Technical Skills, Core Competencies, Tech Stack
    - education: Education, Degrees, Academic Qualifications
    - other: Summary, Profile, Objective, Certifications
    """
    sections = {
        "experience": [],
        "projects": [],
        "skills": [],
        "education": [],
        "other": []
    }

    lines = text.split("\n")
    current_sec = "other"

    for line in lines:
        cleaned = line.strip().lower()
        if not cleaned:
            continue

        # Header detection: short standalone line
        if len(cleaned) < 55 and not cleaned.endswith((".", ",")):
            if re.search(r'\b(work\s+experience|employment(\s+history)?|professional\s+experience|internships?|experience)\b', cleaned):
                current_sec = "experience"
                continue
            elif re.search(r'\b(projects?|technical\s+projects?|personal\s+projects?|academic\s+projects?|key\s+projects?)\b', cleaned):
                current_sec = "projects"
                continue
            elif re.search(r'\b(skills?|technical\s+skills?|core\s+competencies|tech\s+stack|proficiencies|tools)\b', cleaned):
                current_sec = "skills"
                continue
            elif re.search(r'\b(education|academic|qualifications?|academics|scholastic)\b', cleaned):
                current_sec = "education"
                continue
            elif re.search(r'\b(certifications?|awards?|publications?|summary|profile|about|objective)\b', cleaned):
                current_sec = "other"
                continue

        sections[current_sec].append(line)

    return {k: "\n".join(v) for k, v in sections.items()}

def find_evidence_snippet(text: str, term: str) -> Optional[str]:
    """Extract a clean 1-2 sentence evidence snippet where the skill term was mentioned."""
    escaped = re.escape(term)
    pattern = r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])'

    # Search paragraph by paragraph or sentence by sentence
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    # Prefer longer, action-oriented sentences over bare keyword lists
    candidates = []
    for sent in sentences:
        clean_sent = sent.strip()
        if re.search(pattern, clean_sent, re.IGNORECASE) and len(clean_sent) > 15:
            clean_sent = re.sub(r'^[•\-\*–\s]+', '', clean_sent)
            # Penalize lines that are just comma-separated skill lists
            if clean_sent.lower().startswith(("skills:", "technical skills:", "technologies:", "tools:")) or clean_sent.count(",") > 4:
                candidates.append((0, clean_sent[:180].strip()))
            else:
                candidates.append((1, clean_sent[:180].strip()))

    if candidates:
        # Pick best action-oriented sentence first
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    # Fallback to character window
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 70)
        snippet = text[start:end].replace("\n", " ").strip()
        return f"...{snippet}..."
    return None

def extract_skills_with_evidence(text: str) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    """
    Extract skills along with frequency, matched alias term, section provenance,
    and evidence snippets. Prevents keyword stuffing by tracking demonstration section.
    Returns:
        (canonical_skills_list, evidence_map: {
            canonical: {
                "matched_term": str,
                "frequency": int,
                "snippet": str,
                "demonstration_section": "Experience" | "Projects" | "Skills Only",
                "is_demonstrated": bool
            }
        })
    """
    if not text:
        return [], {}

    sections = partition_resume_sections(text)
    lower_text = " " + text.lower() + " "
    matched_skills: Set[str] = set()
    evidence_map: Dict[str, Dict[str, Any]] = {}

    for term in SORTED_TERMS:
        canonical = ALIAS_MAP[term]
        escaped_term = re.escape(term)
        pattern = r'(?<![a-zA-Z0-9])' + escaped_term + r'(?![a-zA-Z0-9])'

        matches = list(re.finditer(pattern, lower_text))
        if matches:
            matched_skills.add(canonical)

            # Check where the skill was demonstrated
            in_exp = bool(re.search(pattern, sections["experience"], re.IGNORECASE))
            in_proj = bool(re.search(pattern, sections["projects"], re.IGNORECASE))

            if in_exp:
                demo_sec = "Experience"
                is_demo = True
                snippet = find_evidence_snippet(sections["experience"], term) or find_evidence_snippet(text, term)
            elif in_proj:
                demo_sec = "Projects"
                is_demo = True
                snippet = find_evidence_snippet(sections["projects"], term) or find_evidence_snippet(text, term)
            else:
                demo_sec = "Skills Only"
                is_demo = False
                snippet = find_evidence_snippet(sections["skills"] or text, term)

            if canonical not in evidence_map:
                evidence_map[canonical] = {
                    "matched_term": term,
                    "frequency": len(matches),
                    "snippet": snippet,
                    "demonstration_section": demo_sec,
                    "is_demonstrated": is_demo
                }
            else:
                evidence_map[canonical]["frequency"] += len(matches)
                # Upgrade demonstration section if found in experience or projects later
                if is_demo and not evidence_map[canonical].get("is_demonstrated", False):
                    evidence_map[canonical]["demonstration_section"] = demo_sec
                    evidence_map[canonical]["is_demonstrated"] = True
                    evidence_map[canonical]["snippet"] = snippet

    return sorted(list(matched_skills)), evidence_map

    return sorted(list(matched_skills)), evidence_map

def extract_skills_from_text(text: str) -> List[str]:
    """Extract canonical unique skills from text."""
    skills, _ = extract_skills_with_evidence(text)
    return skills
