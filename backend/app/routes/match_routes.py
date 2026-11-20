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
from app.matcher.project_matcher import evaluate_projects
from app.matcher.embedding_engine import embedding_engine
from app.matcher.scorer import (
    calculate_overall_score,
    calculate_ai_ml_score,
    calculate_genai_score,
    calculate_tools_deployment_score
)
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
    Advanced AI matching & ranking pipeline:
    1. Anti-keyword-stuffing skill verification with section provenance.
    2. Deep AI/ML stack assessment (TensorFlow, PyTorch, Scikit-learn, CNN, NLP, Python).
    3. Practical project execution depth and production engineering metrics.
    4. Relevant experience scoring accounting for role seniority and fresher eligibility.
    5. Dense semantic embeddings via Sentence Transformers.
    6. Multi-dimensional transparent breakdown and deterministic descending rank sorting.
    """
    start_time = time.time()
    jd = payload.job_description
    resumes = payload.resumes
    weights = payload.weights or DEFAULT_WEIGHTS

    if not resumes:
        raise HTTPException(status_code=400, detail="At least 1 resume is required to perform matching.")

    # Prepare JD embedding context
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
        # Extract evidence map with section provenance (Experience vs Projects vs Skills Only)
        _, evidence_map = extract_skills_with_evidence(resume.raw_text)

        # 1. Context-Aware Skill Matching with Anti-Keyword-Stuffing Verification
        matched_skills, missing_skills, additional_skills, skill_evidences, skill_score = evaluate_skills_detailed(
            candidate_skills=resume.extracted_skills,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills or [],
            evidence_map=evidence_map
        )

        # 2. Hands-on Project Evaluation (Depth, AI/ML models, APIs, metrics)
        projects_score, project_count, project_highlights = evaluate_projects(
            resume_text=resume.raw_text,
            extracted_skills=resume.extracted_skills
        )

        # 3. Relevant Experience Matching (Role relevance + Fresher eligibility, Education excluded)
        cand_years = resume.experience.total_years
        emp_history = getattr(resume.experience, "employment_history", [])
        exp_score, relevant_years = evaluate_experience(
            candidate_years=cand_years,
            required_years=jd.min_experience_years,
            employment_history=emp_history,
            target_role=jd.title,
            projects_score=projects_score,
            return_details=True
        )

        # 4. Domain Stack Scores: AI/ML, GenAI, Tools & Deployment
        ai_ml_score = calculate_ai_ml_score(resume.extracted_skills, evidence_map)
        genai_score = calculate_genai_score(resume.extracted_skills, evidence_map)
        tools_score = calculate_tools_deployment_score(resume.extracted_skills, evidence_map)

        # 5. Contextual Semantic Similarity using Sentence Transformers
        resume_summary_text = (
            f"Candidate: {resume.contact.name}\n"
            f"Roles: {', '.join(resume.experience.role_titles)}\n"
            f"Skills: {', '.join(resume.extracted_skills)}\n"
            f"Experience: {cand_years} years.\n"
            f"{resume.raw_text[:1200]}"
        )
        sim_ratio = embedding_engine.calculate_similarity(jd_core_text, resume_summary_text)
        semantic_score = round(sim_ratio * 100.0, 1)

        # 6. Education Score
        edu_score = round(resume.education.score * 100.0, 1)

        # 7. Calculate Multi-Dimensional Weighted Final Score
        breakdown = calculate_overall_score(
            skill_score=skill_score,
            semantic_score=semantic_score,
            experience_score=exp_score,
            education_score=edu_score,
            weights=weights,
            ai_ml_score=ai_ml_score,
            projects_score=projects_score,
            genai_score=genai_score,
            tools_deployment_score=tools_score,
            target_role=jd.title
        )

        # 8. Generate Explainable AI Reasoning with Evidence
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
                relevant_experience_years=relevant_years,
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
                employment_history=emp_history,
                weaknesses=explanation.weaknesses,
                ranking_explanation=explanation.ranking_explanation
            )
        )

    # Strictly sort candidates descending by actual overall score
    results.sort(key=lambda x: (x.overall_score, x.score_breakdown.skills_score, x.score_breakdown.ai_ml_score), reverse=True)

    # Assign sequential ranks strictly matching sorted order
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

    # Header with transparent scoring dimensions
    writer.writerow([
        "Rank", "Candidate Name", "Overall Match %", "Verdict",
        "Technical Skills %", "AI/ML Score %", "Experience Score %",
        "Projects Score %", "GenAI Score %", "Tools & Deployment %",
        "Education Score %", "Total Professional Exp", "Relevant Exp Years",
        "Experience Status", "Education Duration", "Extraction Confidence",
        "Matched Skills", "Missing Skills", "Explanation", "Email", "Phone", "Filename"
    ])

    for c in evaluation.results:
        sb = c.score_breakdown
        writer.writerow([
            c.rank,
            c.name,
            f"{c.overall_score}%",
            c.explanation.verdict,
            f"{sb.technical_skills_score}%",
            f"{sb.ai_ml_score}%",
            f"{sb.experience_score}%",
            f"{sb.projects_score}%",
            f"{sb.genai_score}%",
            f"{sb.tools_deployment_score}%",
            f"{sb.education_score}%",
            c.formatted_experience or f"{c.experience_years} years",
            f"{c.relevant_experience_years} years",
            c.experience_status or ("Experienced" if c.experience_years >= 1.0 else "Fresher"),
            c.education_duration,
            c.confidence.overall,
            ", ".join(c.matched_skills),
            ", ".join(c.missing_skills),
            c.ranking_explanation or c.explanation.verdict,
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
