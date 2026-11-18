import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import ExtractedResume, ExtractionConfidence
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.docx_parser import extract_text_from_docx
from app.parsers.text_cleaner import clean_text
from app.extractor.contact_extractor import extract_contact, extract_education
from app.extractor.experience_extractor import extract_experience
from app.extractor.skill_extractor import extract_skills_with_evidence

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB per file
MAX_BATCH_SIZE = 30                     # Max 30 files in one batch
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def calculate_overall_confidence(
    name_conf: str,
    contact_conf: str,
    exp_conf: str,
    edu_conf: str,
    skill_count: int,
    is_scanned: bool
) -> ExtractionConfidence:
    """Compute verified, evidence-based extraction confidence levels."""
    if is_scanned:
        return ExtractionConfidence(
            name="Low", contact="Low", experience="Low",
            education="Low", skills="Low", overall="Low (Scanned/Empty Document)"
        )

    skills_conf = "High" if skill_count >= 5 else ("Medium" if skill_count >= 2 else "Low")

    # Overall calculation
    high_count = sum(1 for c in [name_conf, contact_conf, exp_conf, edu_conf, skills_conf] if c == "High")
    if high_count >= 4:
        overall = "High"
    elif high_count >= 2:
        overall = "Medium"
    else:
        overall = "Low"

    return ExtractionConfidence(
        name=name_conf,
        contact=contact_conf,
        experience=exp_conf,
        education=edu_conf,
        skills=skills_conf,
        overall=overall
    )

def process_single_resume(filename: str, content: bytes) -> ExtractedResume:
    """Parse a single resume file (PDF, DOCX, or TXT) into ExtractedResume schema."""
    lower_fn = filename.lower()
    ext = os.path.splitext(lower_fn)[1]

    # Explicit format validation
    if ext == ".doc":
        raise ValueError(f"'{filename}': Legacy binary .doc format is not supported. Please convert to modern .docx or .pdf.")
    elif ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"'{filename}': Unsupported file format '{ext}'. Supported formats: .pdf, .docx, .txt.")

    # Size check
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"'{filename}': File size ({len(content) / (1024*1024):.1f}MB) exceeds maximum 10MB limit.")

    # Text extraction
    if ext == ".pdf":
        text = extract_text_from_pdf(content)
    elif ext == ".docx":
        text = extract_text_from_docx(content)
    else:
        text = clean_text(content.decode("utf-8", errors="ignore"))

    # Empty / scanned detection
    is_scanned_or_empty = False
    if not text.strip() or len(text.strip()) < 30:
        is_scanned_or_empty = True
        text = f"Scanned or Image-only Resume Document: {filename}"

    # Extract entities
    contact, contact_confs = extract_contact(text, filename)
    education, edu_conf = extract_education(text)
    experience, exp_conf = extract_experience(text)
    skills, _ = extract_skills_with_evidence(text)

    confidence = calculate_overall_confidence(
        name_conf=contact_confs.get("name", "Medium"),
        contact_conf=contact_confs.get("contact", "Medium"),
        exp_conf=exp_conf,
        edu_conf=edu_conf,
        skill_count=len(skills),
        is_scanned=is_scanned_or_empty
    )

    return ExtractedResume(
        id=str(uuid.uuid4())[:8],
        filename=filename,
        contact=contact,
        education=education,
        experience=experience,
        extracted_skills=skills,
        confidence=confidence,
        raw_text=text,
        is_scanned_or_empty=is_scanned_or_empty
    )

@router.post("/upload", response_model=List[ExtractedResume])
async def upload_batch_resumes(files: List[UploadFile] = File(...)):
    """
    Upload batch resumes (supports PDF and DOCX formats).
    Strictly validates file size, extensions, and batch volume limits.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No resume files were provided.")

    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size limit exceeded. Upload up to {MAX_BATCH_SIZE} resumes at once (received {len(files)})."
        )

    extracted_resumes: List[ExtractedResume] = []
    errors = []

    for file in files:
        try:
            content = await file.read()
            if not content:
                errors.append(f"'{file.filename}': File is empty (0 bytes).")
                continue
            resume = process_single_resume(file.filename or "resume.pdf", content)
            extracted_resumes.append(resume)
        except ValueError as ve:
            errors.append(str(ve))
        except Exception as e:
            errors.append(f"'{file.filename}': Extraction failed ({str(e)}).")

    if not extracted_resumes and errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    return extracted_resumes

@router.get("/samples", response_model=List[ExtractedResume])
def get_sample_resumes():
    """Load pre-generated realistic synthetic resumes (PDF & DOCX) for 1-click evaluation."""
    sample_dir = os.path.join(os.path.dirname(__file__), "../../sample_data/resumes")
    if not os.path.exists(sample_dir):
        return []

    sample_files = sorted(os.listdir(sample_dir))
    extracted = []

    for fn in sample_files:
        if fn.endswith((".pdf", ".docx")):
            fp = os.path.join(sample_dir, fn)
            try:
                with open(fp, "rb") as f:
                    content = f.read()
                resume = process_single_resume(fn, content)
                extracted.append(resume)
            except Exception as e:
                print(f"Error loading sample resume {fn}: {e}")

    return extracted
