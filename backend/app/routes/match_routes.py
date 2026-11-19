import time
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.models.schemas import (
    ParsedJobDescription, ExtractedResume, CandidateMatchResult,
    MatchResponse, ScoringWeights, ScoreBreakdown, EngineDiagnostics
)
from app.config import DEFAULT_WEIGHTS
from app.matcher.skill_matcher import evaluate_skills_detailed
from app.matcher.experience_matcher import evaluate_experience
from app.matcher.embedding_engine import embedding_engine
from app.matcher.scorer import calculate_overall_score
from app.matcher.explainer import generate_match_explanation
from app.extractor.skill_extractor import extract_skills_with_evidence

router = APIRouter(prefix="/api/match", tags=["Matching & Ranking"])

class MatchExecutionRequest(BaseModel):
    job_description: ParsedJobDescription
    resumes: List[ExtractedResume]
    weights: Optional[ScoringWeights] = None

@router.get("/diagnostics", response_model=EngineDiagnostics)
def get_engine_diagnostics():
    """Expose active NLP matching engine, model name, and fallback state for auditability."""
    return embedding_engine.get_diagnostics()

@router.post("/evaluate", response_model=MatchResponse)
async def evaluate_candidates(payload: MatchExecutionRequest):
    """
    Core AI matching pipeline:
    1. Compares each resume with the provided JD using contextual Sentence Transformers.
    2. Calculates skill overlaps (matched & missing) with context evidence.
    3. Evaluates years of experience against JD minimum requirements.
    4. Computes multi-criteria score (0-100) and sorts candidates by rank.
    5. Generates Explainable AI reasoning with extraction confidence for every candidate.
    """
    start_time = time.time()
    jd = payload.job_description
    resumes = payload.resumes
    weights = payload.weights or DEFAULT_WEIGHTS

    if not resumes:
        raise HTTPException(status_code=400, detail="At least 1 resume is required to perform matching.")

    # Prepare JD embedding context
    all_jd_skills = jd.required_skills + (jd.preferred_skills or [])
    jd_core_text = (
        f"{jd.title}\n"
        f"Required Skills: {', '.join(jd.required_skills)}\n"
        f"Preferred Skills: {', '.join(jd.preferred_skills or [])}\n"
        f"Minimum Experience: {jd.min_experience_years} years.\n"
        f"Education: {jd.required_education}\n"
        f"{jd.raw_text[:1200]}"
    )

    results: List[CandidateMatchResult] = []

    for resume in resumes:
        # Extract evidence map from raw text for contextual verification
        _, evidence_map = extract_skills_with_evidence(resume.raw_text)

        # 1. Context-Aware Skill Matching with Evidence
        matched_skills, missing_skills, additional_skills, skill_evidences, skill_score = evaluate_skills_detailed(
            candidate_skills=resume.extracted_skills,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills or [],
            evidence_map=evidence_map
        )

        # 2. Experience Matching
        cand_years = resume.experience.total_years
        exp_score = evaluate_experience(
            candidate_years=cand_years,
            required_years=jd.min_experience_years
        )

        # 3. Contextual Semantic Similarity using Sentence Transformers
        resume_sections = {
            "skills": ", ".join(resume.extracted_skills),
            "experience": resume.experience.summary + " " + " ".join(resume.experience.role_titles),
            "projects": " ".join(resume.experience.projects),
            "raw": resume.raw_text[:1200]
        }
        
        # Calculate holistic similarity
        resume_summary_text = (
            f"Candidate: {resume.contact.name}\n"
            f"Roles: {', '.join(resume.experience.role_titles)}\n"
            f"Skills: {', '.join(resume.extracted_skills)}\n"
            f"Experience: {cand_years} years.\n"
            f"{resume.raw_text[:1200]}"
        )
        sim_ratio = embedding_engine.calculate_similarity(jd_core_text, resume_summary_text)
        semantic_score = round(sim_ratio * 100.0, 1)

        # 4. Education Score
        edu_score = round(resume.education.score * 100.0, 1)

        # 5. Calculate Weighted Final Score
        breakdown = calculate_overall_score(
            skill_score=skill_score,
            semantic_score=semantic_score,
            experience_score=exp_score,
            education_score=edu_score,
            weights=weights
        )

        # 6. Generate Explainable AI Reasoning with Evidence
        explanation = generate_match_explanation(
            candidate_name=resume.contact.name,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            additional_skills=additional_skills,
            candidate_years=cand_years,
            required_years=jd.min_experience_years,
            breakdown=breakdown,
            degree_name=resume.education.highest_degree,
            skill_evidences=skill_evidences,
            confidence=resume.confidence,
            formatted_experience=getattr(resume.experience, "formatted_experience", None)
        )

        snippet = resume.raw_text[:500] + "..." if len(resume.raw_text) > 500 else resume.raw_text

        results.append(
            CandidateMatchResult(
                rank=1,
                candidate_id=resume.id,
                filename=resume.filename,
                name=resume.contact.name,
                email=resume.contact.email,
                phone=resume.contact.phone,
                experience_years=cand_years,
                total_months=getattr(resume.experience, "total_months", int(cand_years * 12)),
                formatted_experience=getattr(resume.experience, "formatted_experience", f"{cand_years:.1f} yrs"),
                experience_status=getattr(resume.experience, "experience_status", "Experienced" if cand_years >= 1.0 else "Fresher"),
                education_duration=getattr(resume.experience, "education_duration", "Excluded"),
                overall_score=breakdown.overall_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                additional_skills=additional_skills,
                skill_evidences=skill_evidences,
                score_breakdown=breakdown,
                explanation=explanation,
                confidence=resume.confidence,
                raw_text_snippet=snippet,
                employment_history=getattr(resume.experience, "employment_history", [])
            )
        )

    # Sort candidates strictly descending by overall matching score
    results.sort(key=lambda x: x.overall_score, reverse=True)

    # Assign sequential ranks
    for idx, cand in enumerate(results, start=1):
        cand.rank = idx

    elapsed_ms = round((time.time() - start_time) * 1000.0, 1)
    avg_score = round(sum(c.overall_score for c in results) / len(results), 1) if results else 0.0

    return MatchResponse(
        job_description=jd,
        results=results,
        total_resumes_processed=len(results),
        top_candidate_name=results[0].name if results else None,
        average_score=avg_score,
        processing_time_ms=elapsed_ms,
        engine_diagnostics=embedding_engine.get_diagnostics()
    )

@router.post("/export-csv")
async def export_ranking_csv(payload: MatchExecutionRequest):
    """Export detailed candidate matching results as a CSV spreadsheet."""
    evaluation = await evaluate_candidates(payload)
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Rank", "Candidate Name", "Overall Match %", "Verdict",
        "Total Professional Experience", "Experience Status", "Education Duration",
        "Extraction Confidence", "Skills Score %",
        "Semantic Score %", "Experience Score %", "Education Score %",
        "Matched Skills", "Missing Skills", "Email", "Phone", "Filename"
    ])

    for c in evaluation.results:
        writer.writerow([
            c.rank,
            c.name,
            f"{c.overall_score}%",
            c.explanation.verdict,
            c.formatted_experience or f"{c.experience_years} years",
            c.experience_status or ("Experienced" if c.experience_years >= 1.0 else "Fresher"),
            c.education_duration,
            c.confidence.overall,
            f"{c.score_breakdown.skills_score}%",
            f"{c.score_breakdown.semantic_score}%",
            f"{c.score_breakdown.experience_score}%",
            f"{c.score_breakdown.education_score}%",
            ", ".join(c.matched_skills),
            ", ".join(c.missing_skills),
            c.email or "N/A",
            c.phone or "N/A",
            c.filename
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=Candidate_Rankings.csv"}
    )
