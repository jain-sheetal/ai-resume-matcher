from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ScoringWeights(BaseModel):
    skills: float = Field(default=0.40, description="Weight for skill overlap (0.0 - 1.0)")
    semantic: float = Field(default=0.35, description="Weight for semantic similarity (0.0 - 1.0)")
    experience: float = Field(default=0.20, description="Weight for experience evaluation (0.0 - 1.0)")
    education: float = Field(default=0.05, description="Weight for education match (0.0 - 1.0)")

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

class CandidateContact(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None

class CandidateEducation(BaseModel):
    highest_degree: str
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    score: float = 1.0

class CandidateExperience(BaseModel):
    total_years: float
    role_titles: List[str] = []
    companies: List[str] = []
    summary: str = ""

class ExtractedResume(BaseModel):
    id: str
    filename: str
    contact: CandidateContact
    education: CandidateEducation
    experience: CandidateExperience
    extracted_skills: List[str]
    raw_text: str

class ScoreBreakdown(BaseModel):
    overall_score: float
    skills_score: float
    semantic_score: float
    experience_score: float
    education_score: float

class MatchExplanation(BaseModel):
    verdict: str
    strengths: List[str]
    gaps: List[str]
    experience_analysis: str
    skill_analysis: str
    semantic_alignment: str

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
    score_breakdown: ScoreBreakdown
    explanation: MatchExplanation
    raw_text_snippet: Optional[str] = None

class MatchResponse(BaseModel):
    job_description: ParsedJobDescription
    results: List[CandidateMatchResult]
    total_resumes_processed: int
    top_candidate_name: Optional[str] = None
    average_score: float
    processing_time_ms: float
