import re
from typing import List, Set
from app.extractor.skill_taxonomy import ALIAS_MAP, SKILL_TAXONOMY, get_canonical_skill

# Pre-compile multi-word and symbol-safe patterns
# Sorted by length descending so longer terms match first
SORTED_TERMS = sorted(ALIAS_MAP.keys(), key=lambda x: len(x), reverse=True)

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract skills from text using phrase-aware matching with symbol safety (C++, C#, .NET, etc.).
    Returns a sorted list of unique canonical skill names.
    """
    if not text:
        return []

    lower_text = " " + text.lower() + " "
    matched_skills: Set[str] = set()

    for term in SORTED_TERMS:
        canonical = ALIAS_MAP[term]
        if canonical in matched_skills:
            continue

        # Build regex with boundary handling for special chars (+, #, ., /)
        escaped_term = re.escape(term)
        # Leading boundary: whitespace, punctuation or start
        pattern = r'(?<![a-zA-Z0-9])' + escaped_term + r'(?![a-zA-Z0-9])'

        if re.search(pattern, lower_text):
            matched_skills.add(canonical)

    return sorted(list(matched_skills))
