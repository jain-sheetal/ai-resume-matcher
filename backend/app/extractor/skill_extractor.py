import re
from typing import List, Set, Dict, Tuple, Optional, Any
from app.extractor.skill_taxonomy import ALIAS_MAP, SKILL_TAXONOMY, get_canonical_skill

SORTED_TERMS = sorted(ALIAS_MAP.keys(), key=lambda x: len(x), reverse=True)

def find_evidence_snippet(text: str, term: str) -> Optional[str]:
    """Extract a clean 1-2 sentence evidence snippet where the skill term was mentioned."""
    escaped = re.escape(term)
    pattern = r'(?<![a-zA-Z0-9])' + escaped + r'(?![a-zA-Z0-9])'

    # Search paragraph by paragraph or sentence by sentence
    sentences = re.split(r'(?<=[.!?\n])\s+', text)
    for sent in sentences:
        clean_sent = sent.strip()
        if re.search(pattern, clean_sent, re.IGNORECASE) and len(clean_sent) > 15:
            # Clean up bullet markers and excessive spaces
            clean_sent = re.sub(r'^[•\-\*–\s]+', '', clean_sent)
            return clean_sent[:180].strip()

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
    Extract skills along with frequency, matched alias term, and evidence snippets.
    Returns:
        (canonical_skills_list, evidence_map: {canonical: {"term": str, "frequency": int, "snippet": str}})
    """
    if not text:
        return [], {}

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
            if canonical not in evidence_map:
                snippet = find_evidence_snippet(text, term)
                evidence_map[canonical] = {
                    "matched_term": term,
                    "frequency": len(matches),
                    "snippet": snippet
                }
            else:
                evidence_map[canonical]["frequency"] += len(matches)

    return sorted(list(matched_skills)), evidence_map

def extract_skills_from_text(text: str) -> List[str]:
    """Extract canonical unique skills from text."""
    skills, _ = extract_skills_with_evidence(text)
    return skills
