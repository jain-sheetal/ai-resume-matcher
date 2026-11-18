from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScoringWeights(BaseModel):
    skills: float = Field(default=0.40, ge=0.0, le=1.0, description="Weight for skill overlap (0.0 - 1.0)")
    semantic: float = Field(default=0.35, ge=0.0, le=1.0, description="Weight for semantic similarity (0.0 - 1.0)")
    experience: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for experience evaluation (0.0 - 1.0)")
    education: float = Field(default=0.05, ge=0.0, le=1.0, description="Weight for education match (0.0 - 1.0)")

class EngineDiagnostics(BaseModel):
    active_engine: str = "sentence-transformers" # "sentence-transformers" | "tfidf-fallback"
    model_name: str = "all-MiniLM-L6-v2"
    is_fallback: bool = False
    device: str = "cpu"
    status: str = "healthy"

class ExtractionConfidence(BaseModel):
    name: str = "Medium"        # High | Medium | Low
    contact: str = "Medium"     # High | Medium | Low
    experience: str = "Medium"  # High | Medium | Low
    education: str = "Medium"   # High | Medium | Low
    skills: str = "High"        # High | Medium | Low
    overall: str = "High"       # High | Medium | Low

class EducationEntry(BaseModel):
    degree: str
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    field_of_study: Optional[str] = None

class CandidateEducation(BaseModel):
    highest_degree: str
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    field_of_study: Optional[str] = None
    entries: List[EducationEntry] = []
    is_detected: bool = True
    score: float = 1.0

class CandidateExperience(BaseModel):
    total_years: float
    calculated_years: float = 0.0
    explicit_claimed_years: Optional[float] = None
    role_titles: List[str] = []
    companies: List[str] = []
    projects: List[str] = []
    certifications: List[str] = []
    summary: str = ""

class CandidateContact(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None

class ExtractedResume(BaseModel):
    id: str
    filename: str
    contact: CandidateContact
    education: CandidateEducation
    experience: CandidateExperience
    extracted_skills: List[str]
    confidence: ExtractionConfidence = Field(default_factory=ExtractionConfidence)
    raw_text: str
    is_scanned_or_empty: bool = False

class JobDescriptionInput(BaseModel):
    title: Optional[str] = "Job Position"
    text: str
    min_experience_years: Optional[float] = None
    required_skills: Optional[List[str]] = None
    weights: Optional[ScoringWeights] = None

class ParsedJobDescription(BaseModel):
    title: str
    raw_text: str
    required_skills: List[str]
    preferred_skills: List[str] = []
    min_experience_years: float
    required_education: str
    key_responsibilities: List[str] = []

class ScoreBreakdown(BaseModel):
    overall_score: float
    skills_score: float
    semantic_score: float
    experience_score: float
    education_score: float

class SkillMatchEvidence(BaseModel):
    requirement: str
    category: str = "Mandatory" # Mandatory | Preferred
    result: str                 # Strong Match | Partial Match | Related Skill | Missing | Insufficient Evidence
    evidence_snippet: Optional[str] = None
    frequency: int = 0
    matched_term: Optional[str] = None

class MatchExplanation(BaseModel):
    verdict: str
    strengths: List[str]
    gaps: List[str]
    experience_analysis: str
    skill_analysis: str
    semantic_alignment: str
    confidence_assessment: str = "High confidence extraction"

class CandidateMatchResult(BaseModel):
    rank: int = 1
    candidate_id: str
    filename: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    experience_years: float
    overall_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str] = []
    skill_evidences: List[SkillMatchEvidence] = []
    score_breakdown: ScoreBreakdown
    explanation: MatchExplanation
    confidence: ExtractionConfidence = Field(default_factory=ExtractionConfidence)
    raw_text_snippet: Optional[str] = None

class MatchResponse(BaseModel):
    job_description: ParsedJobDescription
    results: List[CandidateMatchResult]
    total_resumes_processed: int
    top_candidate_name: Optional[str] = None
    average_score: float
    processing_time_ms: float
    engine_diagnostics: EngineDiagnostics = Field(default_factory=EngineDiagnostics)
