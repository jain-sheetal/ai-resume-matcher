import re
from typing import Dict, List, Tuple, Set

AI_ML_KEYWORDS = {
    "pytorch", "tensorflow", "scikit-learn", "sklearn", "cnn", "nlp", "computer vision",
    "deep learning", "machine learning", "rag", "llm", "llms", "prompt engineering",
    "huggingface", "transformers", "opencv", "spacy", "keras", "bert", "sbert"
}

PRODUCTION_KEYWORDS = {
    "fastapi", "flask", "docker", "rest api", "rest apis", "restful", "kubernetes",
    "ci/cd", "deployment", "aws", "gcp", "azure", "accuracy", "f1-score", "f1",
    "latency", "throughput", "precision", "recall", "microservices"
}

def extract_project_descriptions(text: str) -> List[str]:
    """Extract individual project blocks from resume text."""
    lines = text.split("\n")
    in_proj = False
    proj_lines = []
    current_proj = []

    for line in lines:
        cleaned = line.strip().lower()
        if not cleaned:
            continue

        # Header detection
        if len(cleaned) < 50 and not cleaned.endswith((".", ",")):
            if re.search(r'\b(projects?|technical\s+projects?|personal\s+projects?|key\s+projects?)\b', cleaned):
                in_proj = True
                continue
            elif in_proj and re.search(r'\b(work\s+experience|employment|skills|education|certifications?|awards?)\b', cleaned):
                in_proj = False
                if current_proj:
                    proj_lines.append("\n".join(current_proj))
                    current_proj = []
                break

        if in_proj:
            # Check for new project title indicated by bullet or bold-like short line
            if len(cleaned) < 60 and not line.startswith((" ", "\t", "-", "•", "*")):
                if current_proj:
                    proj_lines.append("\n".join(current_proj))
                    current_proj = []
            current_proj.append(line)

    if current_proj:
        proj_lines.append("\n".join(current_proj))

    # Fallback: if no project header was found, scan for paragraphs containing project keywords
    if not proj_lines:
        paras = text.split("\n\n")
        for p in paras:
            pl = p.lower()
            if any(k in pl for k in ["project", "developed", "built a", "trained a model", "implemented"]):
                if len(p.strip()) > 40:
                    proj_lines.append(p.strip())

    return proj_lines

def evaluate_projects(
    resume_text: str,
    extracted_skills: List[str]
) -> Tuple[float, int, List[str]]:
    """
    Evaluate candidate projects depth, AI/ML complexity, and production engineering practices.
    Returns:
        (projects_score_0_to_100, project_count, project_highlights)
    """
    proj_blocks = extract_project_descriptions(resume_text)
    combined_proj_text = " ".join(proj_blocks).lower()
    full_text_lower = resume_text.lower()

    project_count = max(len(proj_blocks), 1 if any(k in full_text_lower for k in ["project", "github.com", "developed"]) else 0)

    # Base score by project presence
    if project_count == 0:
        return 40.0, 0, []

    base_score = min(60.0, 35.0 + (project_count * 12.0))

    # Evaluate AI/ML depth in projects
    ai_ml_hits = [k for k in AI_ML_KEYWORDS if k in combined_proj_text or (k in full_text_lower and "project" in full_text_lower)]
    ai_score_add = min(25.0, len(ai_ml_hits) * 5.0)

    # Evaluate production engineering practices (APIs, metrics, deployment)
    prod_hits = [k for k in PRODUCTION_KEYWORDS if k in combined_proj_text or (k in full_text_lower and "project" in full_text_lower)]
    prod_score_add = min(15.0, len(prod_hits) * 3.5)

    final_score = min(100.0, base_score + ai_score_add + prod_score_add)

    # Generate highlights
    highlights = []
    if any(k in combined_proj_text for k in ["cnn", "computer vision", "opencv"]):
        highlights.append("Computer Vision & CNN deep learning project demonstrated")
    if any(k in combined_proj_text for k in ["nlp", "transformers", "bert", "spacy"]):
        highlights.append("NLP and text processing pipeline implemented")
    if any(k in combined_proj_text for k in ["rag", "llm", "prompt engineering"]):
        highlights.append("Generative AI & LLM workflow constructed")
    if any(k in combined_proj_text for k in ["fastapi", "flask", "docker", "rest api"]):
        highlights.append("Production REST API / containerization integrated into projects")

    return round(final_score, 1), project_count, highlights
