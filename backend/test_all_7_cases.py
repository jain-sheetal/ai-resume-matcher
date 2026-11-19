import sys
from datetime import datetime
from app.extractor.experience_extractor import calculate_professional_experience
from app.matcher.explainer import calculate_experience_gap

def test_all_cases():
    print("=" * 60)
    print("VERIFYING ALL 7 TARGET CASES FOR PROFESSIONAL EXPERIENCE")
    print("=" * 60)

    # Case 1: B.Tech (2021-2025) + 9-month internship (Jan 2025 - Sep 2025)
    r1 = """
    Aarav Sharma
    aarav@example.com
    
    EDUCATION
    Bachelor of Technology in Computer Science (2021 - 2025)
    XYZ Institute of Technology
    
    INTERNSHIPS & EXPERIENCE
    Software Engineering Intern
    Alpha AI Labs
    Jan 2025 - Sep 2025
    - Developed machine learning models
    """
    exp1, _ = calculate_professional_experience(r1)
    print(f"Case 1: {exp1.formatted_experience} | {exp1.years_months} | Status: {exp1.experience_status} | Edu: {exp1.education_duration}")
    print(f"        total_months: {exp1.total_months}, total_years: {exp1.total_years}")
    assert exp1.total_months in [8, 9], f"Expected 8 or 9 months, got {exp1.total_months}"
    assert "9 months" in exp1.formatted_experience or "0.75" in exp1.formatted_experience, f"Unexpected format {exp1.formatted_experience}"
    assert exp1.education_duration == "Excluded"
    assert exp1.total_years < 1.0, f"Must NOT count 4-year B.Tech! Got {exp1.total_years}"

    # Case 2: B.Tech (2021-2025) + No employment history
    r2 = """
    Priya Patel
    priya@example.com
    
    EDUCATION
    Bachelor of Technology (B.Tech) in Information Technology
    ABC University, 2021 - 2025
    CGPA: 8.9/10
    
    PROJECTS
    Online Book Store (Academic Project)
    - Built using React and Node.js
    """
    exp2, _ = calculate_professional_experience(r2)
    print(f"Case 2: {exp2.formatted_experience} | {exp2.years_months} | Status: {exp2.experience_status} | Edu: {exp2.education_duration}")
    print(f"        total_months: {exp2.total_months}, total_years: {exp2.total_years}")
    assert exp2.total_months == 0, f"Expected 0 months, got {exp2.total_months}"
    assert exp2.total_years == 0.0
    assert exp2.experience_status == "Fresher"
    assert exp2.education_duration == "Excluded"

    # Case 3: B.Tech + 1-year internship
    r3 = """
    Rohan Verma
    
    EDUCATION
    B.Tech Computer Science (2020 - 2024)
    
    WORK EXPERIENCE
    AI Research Intern
    Google DeepMind
    Jan 2023 - Jan 2024
    """
    exp3, _ = calculate_professional_experience(r3)
    print(f"Case 3: {exp3.formatted_experience} | {exp3.years_months} | Status: {exp3.experience_status} | Edu: {exp3.education_duration}")
    print(f"        total_months: {exp3.total_months}, total_years: {exp3.total_years}")
    assert exp3.total_months == 12, f"Expected 12 months, got {exp3.total_months}"
    assert "1 year" in exp3.formatted_experience or "12 months" in exp3.formatted_experience
    assert exp3.experience_status == "Experienced"

    # Case 4: B.Tech + 2-year job
    r4 = """
    Sneha Gupta
    
    EDUCATION
    B.Tech (2018 - 2022)
    
    EXPERIENCE
    Software Engineer
    Microsoft
    Jan 2022 - Jan 2024
    """
    exp4, _ = calculate_professional_experience(r4)
    print(f"Case 4: {exp4.formatted_experience} | {exp4.years_months} | Status: {exp4.experience_status} | Edu: {exp4.education_duration}")
    print(f"        total_months: {exp4.total_months}, total_years: {exp4.total_years}")
    assert exp4.total_months == 24, f"Expected 24 months, got {exp4.total_months}"
    assert "2 years" in exp4.formatted_experience or "24 months" in exp4.formatted_experience
    assert exp4.experience_status == "Experienced"

    # Case 5: B.Tech + 6-month internship + 1-year job
    r5 = """
    Vikram Malhotra
    
    EDUCATION
    B.Tech (2019 - 2023)
    
    PROFESSIONAL EXPERIENCE
    Machine Learning Engineer
    Tech Corp
    Jan 2023 - Jan 2024
    
    Data Science Intern
    Data Dynamics
    Jul 2022 - Jan 2023
    """
    exp5, _ = calculate_professional_experience(r5)
    print(f"Case 5: {exp5.formatted_experience} | {exp5.years_months} | Status: {exp5.experience_status} | Edu: {exp5.education_duration}")
    print(f"        total_months: {exp5.total_months}, total_years: {exp5.total_years}")
    assert exp5.total_months == 18, f"Expected 18 months, got {exp5.total_months}"
    assert "18 months" in exp5.formatted_experience or "1.5" in exp5.formatted_experience
    assert exp5.experience_status == "Experienced"

    # Case 6: Overlapping jobs - count overlapping months only once
    r6 = """
    Kunal Shah
    
    EDUCATION
    B.Tech Computer Science (2018 - 2022)
    
    WORK EXPERIENCE
    Software Engineer
    Alpha Inc
    Jan 2022 - Dec 2023
    
    Technical Consultant (Part-time)
    Beta LLC
    Jun 2022 - Jun 2023
    """
    exp6, _ = calculate_professional_experience(r6)
    print(f"Case 6: {exp6.formatted_experience} | {exp6.years_months} | Status: {exp6.experience_status} | Edu: {exp6.education_duration}")
    print(f"        total_months: {exp6.total_months}, total_years: {exp6.total_years}")
    # Jan 2022 to Dec 2023 is 23 or 24 months. Jun 2022 to Jun 2023 is completely within it!
    # Overlap merged => exactly 23 or 24 months, NOT 24 + 12 = 36 months!
    assert exp6.total_months in [23, 24], f"Expected 23-24 months due to deduplication, got {exp6.total_months}"

    # Case 7: Candidate with 9 months experience applied for JD requiring 2 years -> shortfall: 1 year and 3 months (15 months)
    gap_months, formatted_gap = calculate_experience_gap(candidate_months=9, required_years=2.0)
    print(f"Case 7: Gap for 9 months vs 2.0 yrs JD: gap_months={gap_months}, formatted='{formatted_gap}'")
    assert gap_months == 15, f"Expected 15 months gap, got {gap_months}"
    assert formatted_gap == "1 year and 3 months", f"Expected '1 year and 3 months', got '{formatted_gap}'"

    print("\nALL 7 TARGET CASES PASSED PERFECTLY!")

if __name__ == "__main__":
    test_all_cases()
