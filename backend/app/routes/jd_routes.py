import json
import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from app.models.schemas import ParsedJobDescription, JobDescriptionInput
from app.extractor.jd_extractor import parse_job_description
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.text_cleaner import clean_text

router = APIRouter(prefix="/api/jd", tags=["Job Description"])

SAMPLE_JDS = [
    {
        "id": "full-stack-python-react",
        "title": "Senior Full Stack Developer (Python & React)",
        "experience": "4+ years",
        "description": """Job Title: Senior Full Stack Developer (Python & React)
Location: Remote / Hybrid
Experience Required: 4+ years of professional full-stack software development experience.

About the Role:
We are looking for a skilled Senior Full Stack Developer to architect and deliver scalable web applications. You will be responsible for building robust APIs in Python (FastAPI/Django), developing dynamic user interfaces in React.js, and managing PostgreSQL databases.

Key Responsibilities:
- Design, develop, and maintain responsive web applications using React.js and modern TypeScript.
- Build clean, high-performance REST APIs and microservices using Python and FastAPI.
- Model, optimize, and maintain relational databases using PostgreSQL and SQLAlchemy.
- Implement CI/CD pipelines, containerize applications with Docker, and deploy to AWS.
- Collaborate with cross-functional teams in an Agile scrum environment.
- Write unit tests and maintain high code quality standards.

Required Qualifications & Skills:
- 4+ years experience in full-stack software development.
- Strong proficiency in Python, FastAPI or Django.
- Hands-on experience with modern JavaScript / TypeScript, React.js, HTML5, and Tailwind CSS.
- Solid understanding of SQL and relational databases (PostgreSQL or MySQL).
- Familiarity with Docker, Git, CI/CD, and AWS cloud services.
- Bachelor's or Master's degree in Computer Science, Software Engineering, or related field."""
    },
    {
        "id": "backend-java-spring",
        "title": "Java Backend Engineer (Spring Boot & Microservices)",
        "experience": "3+ years",
        "description": """Job Title: Java Backend Engineer
Location: San Francisco, CA / Hybrid
Experience Required: 3+ years in enterprise software engineering.

Overview:
We are seeking a talented Java Backend Engineer to design high-throughput distributed microservices. You will work on mission-critical banking and transactional services requiring extreme reliability.

Requirements:
- 3+ years of professional backend engineering experience with Java (Java 11 / 17).
- Deep expertise in Spring Boot, Spring Data, and microservices architecture.
- Proficient in SQL, relational database design (PostgreSQL, MySQL), and Redis caching.
- Experience building and consuming REST APIs.
- Familiarity with Docker, Kubernetes, and cloud infrastructure (AWS or GCP).
- Experience with unit testing (JUnit, Mockito) and Agile methodologies.
- Bachelor's Degree in Computer Science or related technical discipline."""
    },
    {
        "id": "ai-nlp-engineer",
        "title": "AI / NLP Machine Learning Engineer",
        "experience": "2+ years",
        "description": """Job Title: AI / NLP Machine Learning Engineer
Location: New York, NY / Remote
Experience Required: 2+ years working with machine learning models and NLP pipelines.

Role Summary:
Join our AI team to build state-of-the-art NLP and document understanding systems. You will work with Sentence Transformers, LLMs, and semantic search algorithms.

Key Requirements:
- 2+ years experience in Python, PyTorch, and Scikit-Learn.
- Demonstrated experience in Natural Language Processing (NLP), spaCy, and Hugging Face Transformers.
- Experience with vector embeddings, Sentence Transformers, and semantic similarity.
- Experience deploying ML models as REST APIs using FastAPI or Flask.
- Knowledge of Docker, Git, and cloud services (AWS or Azure).
- Bachelor's or Master's degree in Computer Science, Data Science, or AI."""
    }
]

@router.post("/parse", response_model=ParsedJobDescription)
async def parse_jd_endpoint(payload: JobDescriptionInput):
    """Parse text job description into structured requirements."""
    if not payload.text or len(payload.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Job description text is too short or empty.")

    return parse_job_description(
        text=payload.text,
        custom_title=payload.title if payload.title != "Job Position" else None,
        custom_skills=payload.required_skills,
        custom_min_exp=payload.min_experience_years
    )

@router.post("/upload", response_model=ParsedJobDescription)
async def upload_jd_file(file: UploadFile = File(...)):
    """Upload JD file (.pdf, .docx, .txt) and parse requirements."""
    filename = file.filename or ""
    content = await file.read()

    if filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(content)
    elif filename.lower().endswith((".docx", ".doc")):
        text = extract_text_from_docx(content)
    else:
        text = clean_text(content.decode("utf-8", errors="ignore"))

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")

    return parse_job_description(text=text)

@router.get("/samples")
def get_sample_jds():
    """Return pre-configured sample job descriptions."""
    return SAMPLE_JDS
