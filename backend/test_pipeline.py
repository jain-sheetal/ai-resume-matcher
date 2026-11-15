import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.routes.jd_routes import SAMPLE_JDS
from app.extractor.jd_extractor import parse_job_description
from app.routes.resume_routes import process_single_resume
from app.routes.match_routes import evaluate_candidates, MatchExecutionRequest

def run_test():
    print("=== Testing Resume Matching Pipeline ===")

    # 1. Parse JD
    jd_raw = SAMPLE_JDS[0]["description"]
    parsed_jd = parse_job_description(jd_raw)
    print(f"JD Title: {parsed_jd.title}")
    print(f"Required Skills ({len(parsed_jd.required_skills)}): {parsed_jd.required_skills}")
    print(f"Min Experience: {parsed_jd.min_experience_years} years\n")

    # 2. Load 12 resumes
    resumes_dir = os.path.join(os.path.dirname(__file__), "sample_data", "resumes")
    files = sorted(os.listdir(resumes_dir))
    extracted_resumes = []
    for fn in files:
        if fn.endswith((".pdf", ".docx")):
            full_path = os.path.join(resumes_dir, fn)
            with open(full_path, "rb") as f:
                content = f.read()
            res = process_single_resume(fn, content)
            extracted_resumes.append(res)
            print(f"Parsed: {res.contact.name:20s} | Exp: {res.experience.total_years} yrs | Skills: {len(res.extracted_skills)}")

    print(f"\nTotal Resumes Loaded: {len(extracted_resumes)}")

    # 3. Match and Rank
    import asyncio
    req = MatchExecutionRequest(job_description=parsed_jd, resumes=extracted_resumes)
    response = asyncio.run(evaluate_candidates(req))

    print("\n=== Candidate Ranking Dashboard ===")
    print(f"{'Rank':<5} {'Candidate':<20} {'Match %':<10} {'Experience':<12} {'Matched Skills'}")
    print("-" * 80)
    for c in response.results:
        matched_str = ", ".join(c.matched_skills[:4])
        print(f"#{c.rank:<4} {c.name:<20} {c.overall_score:<9.1f}% {c.experience_years:<4.1f} years   {matched_str}")

    top = response.results[0]
    print(f"\nTop Candidate Details: {top.name} ({top.overall_score}%)")
    print(f"Score Breakdown: Skills={top.score_breakdown.skills_score}%, Semantic={top.score_breakdown.semantic_score}%, Exp={top.score_breakdown.experience_score}%")
    print(f"Verdict: {top.explanation.verdict}")
    print("Strengths:")
    for s in top.explanation.strengths:
        print(f"  + {s}")
    if top.explanation.gaps:
        print("Gaps:")
        for g in top.explanation.gaps:
            print(f"  - {g}")

if __name__ == "__main__":
    run_test()
