import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing API endpoints with TestClient...")

    # 1. Health
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✓ GET /health: OK", res.json())

    # 2. Get Sample JDs
    res = client.get("/api/jd/samples")
    assert res.status_code == 200, f"Sample JDs failed: {res.text}"
    samples = res.json()
    assert len(samples) >= 3, "Expected at least 3 sample JDs"
    print(f"✓ GET /api/jd/samples: OK ({len(samples)} samples returned)")

    # 3. Parse JD
    res = client.post("/api/jd/parse", json={"text": samples[0]["description"], "title": samples[0]["title"]})
    assert res.status_code == 200, f"Parse JD failed: {res.text}"
    parsed_jd = res.json()
    print(f"✓ POST /api/jd/parse: OK (Extracted {len(parsed_jd['required_skills'])} skills, {parsed_jd['min_experience_years']} yrs exp)")

    # 4. Get Sample Resumes
    res = client.get("/api/resumes/samples")
    assert res.status_code == 200, f"Sample resumes failed: {res.text}"
    sample_resumes = res.json()
    assert len(sample_resumes) == 12, f"Expected 12 resumes, got {len(sample_resumes)}"
    print(f"✓ GET /api/resumes/samples: OK (Loaded {len(sample_resumes)} sample resumes)")

    # 5. Evaluate Match
    res = client.post("/api/match/evaluate", json={
        "job_description": parsed_jd,
        "resumes": sample_resumes
    })
    assert res.status_code == 200, f"Match evaluate failed: {res.text}"
    match_result = res.json()
    print(f"✓ POST /api/match/evaluate: OK (Ranked {len(match_result['results'])} candidates in {match_result['processing_time_ms']}ms)")
    print(f"  Top Candidate: {match_result['top_candidate_name']} ({match_result['results'][0]['overall_score']}%)")

    # 6. Export CSV
    res = client.post("/api/match/export-csv", json={
        "job_description": parsed_jd,
        "resumes": sample_resumes
    })
    assert res.status_code == 200, f"Export CSV failed: {res.text}"
    assert "Rank,Candidate Name" in res.text
    print(f"✓ POST /api/match/export-csv: OK ({len(res.text)} bytes generated)")

    print("\nAll API endpoints passed successfully!")

if __name__ == "__main__":
    test_endpoints()
