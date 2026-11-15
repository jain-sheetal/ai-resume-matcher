import time
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.models.schemas import (
    ParsedJobDescription, ExtractedResume, CandidateMatchResult,
    MatchResponse, ScoringWeights, ScoreBreakdown
)
from app.config import DEFAULT_WEIGHTS
from app.matcher.skill_matcher import evaluate_skills
from app.matcher.experience_matcher import evaluate_experience
from app.matcher.embedding_engine import embedding_engine
from app.matcher.scorer import calculate_overall_score
from app.matcher.explainer import generate_match_explanation

router = APIRouter(prefix="/api/match", tags=["Matching & Ranking"])

class MatchExecutionRequest(BaseModel):
    job_description: ParsedJobDescription
    resumes: List[ExtractedResume]
    weights: Optional[ScoringWeights] = None

@router.post("/evaluate", response_model=MatchResponse)
async def evaluate_candidates(payload: MatchExecutionRequest):
    """
    Core AI matching pipeline:
    1. Compares each resume with the provided JD using contextual Sentence Transformers.
    2. Calculates skill overlaps (matched & missing).
    3. Evaluates years of experience against JD minimum requirements.
    4. Computes multi-criteria score (0-100) and sorts candidates by rank.
    5. Generates Explainable AI reasoning for every candidate.
    """
    start_time = time.time()
    jd = payload.job_description
    resumes = payload.resumes
    weights = payload.weights or DEFAULT_WEIGHTS

    if not resumes:
        raise HTTPException(status_code=400, detail="At least 1 resume is required to perform matching.")

    # Prepare JD embedding context
    jd_core_text = f"{jd.title}\nRequired Skills: {', '.join(jd.required_skills)}\nExperience: {jd.min_experience_years} years.\n{jd.raw_text[:1000]}"

    results: List[CandidateMatchResult] = []

    for resume in resumes:
        # 1. Skill Matching
        matched_skills, missing_skills, additional_skills, skill_score = evaluate_skills(
            candidate_skills=resume.extracted_skills,
            required_skills=jd.required_skills
        )

        # 2. Experience Matching
        cand_years = resume.experience.total_years
        exp_score = evaluate_experience(
            candidate_years=cand_years,
            required_years=jd.min_experience_years
        )

        # 3. Semantic Similarity using Sentence Transformers
        resume_core_text = f"Candidate: {resume.contact.name}\nSkills: {', '.join(resume.extracted_skills)}\nExperience: {cand_years} years.\n{resume.raw_text[:1200]}"
        sim_ratio = embedding_engine.calculate_similarity(jd_core_text, resume_core_text)
        # Scale to 0-100%
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

        # 6. Generate Explainable AI Reasoning
        explanation = generate_match_explanation(
            candidate_name=resume.contact.name,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            additional_skills=additional_skills,
            candidate_years=cand_years,
            required_years=jd.min_experience_years,
            breakdown=breakdown,
            degree_name=resume.education.highest_degree
        )

        # Snippet of raw text
        snippet = resume.raw_text[:500] + "..." if len(resume.raw_text) > 500 else resume.raw_text

        results.append(
            CandidateMatchResult(
                rank=1, # Will be set after sorting
                candidate_id=resume.id,
                filename=resume.filename,
                name=resume.contact.name,
                email=resume.contact.email,
                phone=resume.contact.phone,
                experience_years=cand_years,
                overall_score=breakdown.overall_score,
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                additional_skills=additional_skills,
                score_breakdown=breakdown,
                explanation=explanation,
                raw_text_snippet=snippet
            )
        )

    # Sort descending by overall_score
    results.sort(key=lambda x: x.overall_score, reverse=True)

    # Assign ranks
    for idx, candidate in enumerate(results):
        candidate.rank = idx + 1

    proc_time = round((time.time() - start_time) * 1000, 1)
    avg_score = round(sum(r.overall_score for r in results) / len(results), 1) if results else 0.0

    return MatchResponse(
        job_description=jd,
        results=results,
        total_resumes_processed=len(results),
        top_candidate_name=results[0].name if results else None,
        average_score=avg_score,
        processing_time_ms=proc_time
    )

@router.post("/export-csv")
async def export_ranking_csv(payload: MatchExecutionRequest):
    """Generate a downloadable CSV ranking table."""
    match_response = await evaluate_candidates(payload)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rank", "Candidate Name", "Match %", "Experience (Years)", "Matched Skills", "Missing Skills", "Email", "Phone", "Filename"])

    for c in match_response.results:
        writer.writerow([
            c.rank,
            c.name,
            f"{c.overall_score}%",
            f"{c.experience_years} years",
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
        headers={"Content-Disposition": f"attachment; filename=Candidate_Rankings_{int(time.time())}.csv"}
    )
