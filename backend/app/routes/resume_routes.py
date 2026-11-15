import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import ExtractedResume
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.text_cleaner import clean_text
from app.extractor.contact_extractor import extract_contact, extract_education
from app.extractor.experience_extractor import extract_experience
from app.extractor.skill_extractor import extract_skills_from_text

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

def process_single_resume(filename: str, content: bytes) -> ExtractedResume:
    """Parse a single resume file (PDF or DOCX) into ExtractedResume schema."""
    lower_fn = filename.lower()
    if lower_fn.endswith(".pdf"):
        text = extract_text_from_pdf(content)
    elif lower_fn.endswith((".docx", ".doc")):
        text = extract_text_from_docx(content)
    else:
        text = clean_text(content.decode("utf-8", errors="ignore"))

    if not text.strip():
        text = f"Candidate Resume ({filename})"

    contact = extract_contact(text, filename)
    education = extract_education(text)
    experience = extract_experience(text)
    skills = extract_skills_from_text(text)

    return ExtractedResume(
        id=str(uuid.uuid4())[:8],
        filename=filename,
        contact=contact,
        education=education,
        experience=experience,
        extracted_skills=skills,
        raw_text=text
    )

@router.post("/upload", response_model=List[ExtractedResume])
async def upload_batch_resumes(files: List[UploadFile] = File(...)):
    """
    Upload batch resumes (supports PDF and DOCX formats).
    Easily handles 10+ resumes in a single batch.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No resume files were provided.")

    extracted_resumes: List[ExtractedResume] = []
    errors = []

    for file in files:
        try:
            content = await file.read()
            resume = process_single_resume(file.filename or "resume.pdf", content)
            extracted_resumes.append(resume)
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    if not extracted_resumes and errors:
        raise HTTPException(status_code=400, detail=f"Failed to process uploaded files: {', '.join(errors)}")

    return extracted_resumes

@router.get("/samples", response_model=List[ExtractedResume])
def get_sample_resumes():
    """Load pre-bundled synthetic sample resumes for 1-click test evaluation."""
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sample_data", "resumes")
    if not os.path.exists(sample_dir):
        return []

    resumes = []
    for fn in sorted(os.listdir(sample_dir)):
        if fn.lower().endswith((".pdf", ".docx", ".txt")):
            full_path = os.path.join(sample_dir, fn)
            try:
                with open(full_path, "rb") as f:
                    content = f.read()
                resumes.append(process_single_resume(fn, content))
            except Exception as e:
                print(f"Error loading sample {fn}: {e}")

    return resumes
