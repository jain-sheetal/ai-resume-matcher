import unittest
import os
import io
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import (
    ParsedJobDescription, ExtractedResume, CandidateContact,
    CandidateEducation, CandidateExperience, ScoringWeights,
    ExtractionConfidence
)
from app.matcher.embedding_engine import embedding_engine, CONTROLLED_EQUIVALENCES
from app.matcher.skill_matcher import evaluate_skills_detailed
from app.matcher.experience_matcher import evaluate_experience
from app.matcher.scorer import calculate_overall_score, validate_and_normalize_weights
from app.extractor.experience_extractor import merge_intervals, extract_experience
from app.extractor.contact_extractor import extract_contact, extract_education
from app.extractor.jd_extractor import parse_job_description
from app.routes.resume_routes import process_single_resume

client = TestClient(app)

class TestResumeParsingAccuracy(unittest.TestCase):
    """A. Resume parsing tests covering diverse formats, layouts, and edge cases."""

    def test_standard_text_resume(self):
        text = """John Doe
john.doe@example.com | (555) 123-4567 | San Francisco, CA
linkedin.com/in/johndoe | github.com/johndoe

EDUCATION
Bachelor of Science in Computer Science, Stanford University (2020)

PROFESSIONAL EXPERIENCE
Senior Software Engineer | Acme Corp (2020 - Present)
- Engineered scalable microservices in Python and FastAPI.
- Maintained PostgreSQL relational database and Redis caching layer.

SKILLS
Python, FastAPI, Docker, PostgreSQL, Redis, Git, Linux
"""
        resume = process_single_resume("john_doe.txt", text.encode())
        self.assertEqual(resume.contact.name, "John Doe")
        self.assertEqual(resume.contact.email, "john.doe@example.com")
        self.assertIn("Python", resume.extracted_skills)
        self.assertIn("FastAPI", resume.extracted_skills)
        self.assertTrue(resume.experience.total_years >= 3.0)
        self.assertEqual(resume.education.highest_degree, "Bachelor's Degree")
        self.assertEqual(resume.confidence.overall, "High")

    def test_overlapping_employment_periods(self):
        """Verify non-overlapping timeline interval merging prevents double-counting."""
        # Job 1: 2020 to 2023 (3 years)
        # Job 2: 2021 to 2024 (overlapping, 3 years)
        # Total span: 2020 to 2024 (strictly 4.0 years, NOT 6.0 years!)
        intervals = [(2020.0, 2023.0), (2021.0, 2024.0)]
        merged_years = merge_intervals(intervals)
        self.assertEqual(merged_years, 4.0)

    def test_missing_education_does_not_invent_degree(self):
        """Resumes without education sections must NOT be defaulted to Bachelor's Degree."""
        text = """Alex Smith
alex.smith@email.com
Experience: 3 years building web apps.
Skills: JavaScript, Node.js, HTML, CSS
"""
        edu, conf = extract_education(text)
        self.assertEqual(edu.highest_degree, "Not Specified")
        self.assertFalse(edu.is_detected)
        self.assertEqual(conf, "Low")

    def test_missing_experience_does_not_invent_years(self):
        """Resumes with no dates or claims must report 0.0 years, not 1.0."""
        text = """Jordan Lee
jordan@email.com
Skills: Python, SQL
"""
        exp, conf = extract_experience(text)
        self.assertEqual(exp.total_years, 0.0)
        self.assertEqual(conf, "Low")

    def test_file_validation_rejects_legacy_doc(self):
        """Binary .doc format must be explicitly rejected with a clear explanation."""
        with self.assertRaises(ValueError) as ctx:
            process_single_resume("sample.doc", b"fake binary doc header")
        self.assertIn("Legacy binary .doc format is not supported", str(ctx.exception))

    def test_file_validation_rejects_unsupported_extensions(self):
        """Unsupported extensions (.exe, .zip, etc.) must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            process_single_resume("resume.exe", b"executable bytes")
        self.assertIn("Unsupported file format", str(ctx.exception))

    def test_scanned_pdf_detection(self):
        """Empty or text-less PDF files must be flagged as scanned/empty."""
        resume = process_single_resume("scanned_resume.pdf", b"%PDF-1.4 empty content")
        self.assertTrue(resume.is_scanned_or_empty)
        self.assertIn("Low", resume.confidence.overall)


class TestMatchingAlgorithmScenarios(unittest.TestCase):
    """B. Matching algorithm tests covering 10 distinct JD-resume scenarios."""

    def setUp(self):
        self.jd = parse_job_description("""Senior Backend Python Developer
Required Skills: Python, FastAPI, PostgreSQL, Docker, Redis
Preferred Skills: Kubernetes, CI/CD, AWS
Experience: Minimum 4 years of experience.
Education: Bachelor's Degree in Computer Science
Key Responsibilities:
- Design and implement high-performance REST APIs using FastAPI and Python.
- Architect robust relational schemas in PostgreSQL.
- Containerize services with Docker.
""")

    def test_scenario_1_excellent_match(self):
        """Candidate has all mandatory skills, matching experience, and high semantic overlap."""
        skills = self.jd.required_skills + self.jd.preferred_skills
        matched, missing, _, evidences, skill_score = evaluate_skills_detailed(
            candidate_skills=skills,
            required_skills=self.jd.required_skills,
            preferred_skills=self.jd.preferred_skills
        )
        self.assertEqual(len(missing), 0)
        self.assertTrue(skill_score >= 95.0)

    def test_scenario_2_partial_technical_match(self):
        """Candidate has some mandatory skills but misses others."""
        skills = ["Python", "Docker"]
        matched, missing, _, _, skill_score = evaluate_skills_detailed(
            candidate_skills=skills,
            required_skills=self.jd.required_skills,
            preferred_skills=self.jd.preferred_skills
        )
        self.assertIn("Python", matched)
        self.assertIn("PostgreSQL", missing)
        self.assertTrue(25.0 <= skill_score <= 65.0)

    def test_scenario_3_missing_all_mandatory_skills(self):
        """Candidate only possesses unrelated frontend skills."""
        skills = ["Photoshop", "Figma", "UI Design", "Illustrator"]
        matched, missing, _, _, skill_score = evaluate_skills_detailed(
            candidate_skills=skills,
            required_skills=self.jd.required_skills,
            preferred_skills=self.jd.preferred_skills
        )
        self.assertEqual(len(matched), 0)
        self.assertEqual(skill_score, 0.0)

    def test_scenario_4_strong_skills_insufficient_experience(self):
        """Candidate meets all skills but has only 1.0 yr experience against 4.0 yrs required."""
        exp_score = evaluate_experience(candidate_years=1.0, required_years=4.0)
        # Power curve: (1.0 / 4.0)^0.85 * 100 = ~30.8%
        self.assertTrue(25.0 <= exp_score <= 35.0)

    def test_scenario_5_relevant_experience_missing_preferred(self):
        """Candidate meets all mandatory skills & experience, but lacks preferred skills."""
        skills = list(self.jd.required_skills)
        matched, missing, _, _, skill_score = evaluate_skills_detailed(
            candidate_skills=skills,
            required_skills=self.jd.required_skills,
            preferred_skills=self.jd.preferred_skills
        )
        self.assertEqual(len(missing), 0)
        # Scores well (>= 80%) because mandatory skills are all met
        self.assertTrue(skill_score >= 80.0)

    def test_scenario_6_similar_skills_controlled_equivalences(self):
        """Equivalent skills (e.g. Postgres vs PostgreSQL) must be recognized."""
        skills = ["Postgres", "Python3", "FastAPI Framework", "Docker Containers"]
        matched, _, _, evidences, _ = evaluate_skills_detailed(
            candidate_skills=skills,
            required_skills=self.jd.required_skills
        )
        # Matches recognized via controlled equivalences
        matched_str = " ".join(matched).lower()
        self.assertTrue("postgres" in matched_str)
        self.assertTrue("python" in matched_str)

    def test_scenario_7_irrelevant_keyword_mentions(self):
        """Searching for 'Go' must not match 'Good' or 'Google'."""
        from app.extractor.skill_extractor import extract_skills_from_text
        text = "I am a Good communicator who loves Google products."
        skills = extract_skills_from_text(text)
        self.assertNotIn("Go", skills)

    def test_scenario_8_candidate_with_project_experience_only(self):
        """Candidates with project experience but 0 yrs verified tenure are scored appropriately."""
        exp_score = evaluate_experience(candidate_years=0.5, required_years=4.0)
        self.assertTrue(exp_score < 20.0)

    def test_scenario_9_candidate_with_high_professional_experience(self):
        """Candidate with 8.0 yrs against 4.0 yrs receives maximum 100% experience score."""
        exp_score = evaluate_experience(candidate_years=8.0, required_years=4.0)
        self.assertEqual(exp_score, 100.0)

    def test_scenario_10_semantic_similarity_separation(self):
        """Semantically related text must score substantially higher than unrelated text."""
        related_text = "Architected asynchronous REST APIs in Python using FastAPI with PostgreSQL database storage."
        unrelated_text = "Designed floral centerpieces and organized flower arrangements for wedding ceremonies."
        jd_text = "Senior Backend Python Developer building FastAPI REST services and PostgreSQL schemas."

        sim_related = embedding_engine.calculate_similarity(jd_text, related_text)
        sim_unrelated = embedding_engine.calculate_similarity(jd_text, unrelated_text)

        self.assertTrue(sim_related > 0.60)
        self.assertTrue(sim_unrelated < 0.25)
        self.assertTrue(sim_related - sim_unrelated > 0.40)


class TestScoringAndWeights(unittest.TestCase):
    """C. Scoring tests: boundary verification, weight normalization, and determinism."""

    def test_score_boundaries(self):
        """Scores must strictly remain clamped within 0.0 and 100.0."""
        b1 = calculate_overall_score(150.0, 120.0, 200.0, 100.0)
        self.assertEqual(b1.overall_score, 100.0)

        b2 = calculate_overall_score(-50.0, -20.0, -10.0, 0.0)
        self.assertEqual(b2.overall_score, 0.0)

    def test_invalid_negative_weights_fallback(self):
        """Negative weights must be rejected and safely blocked by schema validation."""
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ScoringWeights(skills=-0.5, semantic=-0.5, experience=0.0, education=0.0)

        # Zero weights fallback to defaults
        zero_weights = ScoringWeights(skills=0.0, semantic=0.0, experience=0.0, education=0.0)
        normalized = validate_and_normalize_weights(zero_weights)
        self.assertEqual(normalized.skills, 0.40)
        self.assertEqual(normalized.semantic, 0.35)

    def test_deterministic_scoring(self):
        """Identical inputs must yield identical scores down to the exact decimal."""
        score_1 = calculate_overall_score(78.5, 82.0, 100.0, 85.0)
        score_2 = calculate_overall_score(78.5, 82.0, 100.0, 85.0)
        self.assertEqual(score_1.overall_score, score_2.overall_score)
        self.assertEqual(score_1.model_dump(), score_2.model_dump())


class TestAPIEndpoints(unittest.TestCase):
    """D. REST API endpoint tests: health, diagnostics, uploads, matching, and CSV."""

    def test_health_and_diagnostics_endpoint(self):
        res = client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("ai_engine", data)
        self.assertEqual(data["ai_engine"]["active_engine"], "sentence-transformers")

    def test_diagnostics_endpoint(self):
        res = client.get("/api/match/diagnostics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("active_engine", data)
        self.assertIn("is_fallback", data)

    def test_evaluate_rejects_empty_resumes(self):
        payload = {
            "job_description": {
                "title": "Software Engineer",
                "raw_text": "Sample JD",
                "required_skills": ["Python"],
                "preferred_skills": [],
                "min_experience_years": 2.0,
                "required_education": "Bachelor's Degree",
                "key_responsibilities": []
            },
            "resumes": []
        }
        res = client.post("/api/match/evaluate", json=payload)
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
