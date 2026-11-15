"""
Synthetic Resume Generator
Generates 12 realistic synthetic resumes (both PDF and DOCX) with varied skills and experience levels.
No real personal identifiable data is used.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from docx import Document
from docx.shared import Inches, Pt, RGBColor

CANDIDATES = [
    {
        "filename": "Alex_Rivera_Senior_FullStack.pdf",
        "format": "pdf",
        "name": "Alex Rivera",
        "title": "Senior Full-Stack Engineer",
        "email": "alex.rivera.dev@example.com",
        "phone": "+1 (555) 234-5678",
        "linkedin": "alex-rivera-fullstack",
        "github": "arivera-dev",
        "experience_years": 5.2,
        "education": "B.S. in Computer Science, Stanford University, 2021",
        "skills": ["Python", "FastAPI", "React", "TypeScript", "PostgreSQL", "Docker", "AWS", "REST APIs", "Git", "CI/CD", "Redis", "Tailwind CSS"],
        "summary": "Results-oriented Senior Full-Stack Engineer with over 5 years of professional experience building high-throughput microservices and responsive frontends. Proven track record leading backend migrations to FastAPI and scaling PostgreSQL databases to handle millions of queries daily.",
        "experience": [
            ("Senior Software Engineer", "Apex Cloud Technologies", "2023 - Present", [
                "Architected and deployed 12+ scalable microservices using Python and FastAPI, serving over 2M active users.",
                "Redesigned the frontend customer portal in React.js and TypeScript, reducing client load times by 45%.",
                "Optimized complex PostgreSQL queries and implemented Redis caching, lowering average API latency from 280ms to 42ms.",
                "Configured Docker containers and orchestrated CI/CD automated deployments with GitHub Actions and AWS ECS."
            ]),
            ("Full Stack Developer", "DataWave Solutions", "2021 - 2023", [
                "Built full-stack web applications using React.js, Python, and RESTful APIs.",
                "Integrated third-party payment gateways and authentication using OAuth2 and JWT.",
                "Maintained 95%+ unit test coverage using PyTest and Jest."
            ])
        ]
    },
    {
        "filename": "Brenda_Zhao_Java_Backend.docx",
        "format": "docx",
        "name": "Brenda Zhao",
        "title": "Senior Java Backend Engineer",
        "email": "brenda.zhao.tech@example.com",
        "phone": "+1 (555) 345-6789",
        "linkedin": "brendazhao-eng",
        "github": "bzhao-code",
        "experience_years": 4.5,
        "education": "Master of Science in Software Engineering, Carnegie Mellon University, 2021",
        "skills": ["Java", "Spring Boot", "PostgreSQL", "Microservices", "Docker", "Kubernetes", "Redis", "SQL", "Git", "REST APIs", "AWS"],
        "summary": "Passionate Java Backend Specialist with 4.5 years of industry experience developing mission-critical enterprise applications. Deep mastery of Spring Boot, distributed microservices, and relational database optimization.",
        "experience": [
            ("Senior Backend Developer", "FinCore Systems", "2022 - Present", [
                "Engineered transactional payment processing microservices using Java 17 and Spring Boot.",
                "Designed relational schemas in PostgreSQL and MySQL, processing over 10M transactions daily.",
                "Containerized core services with Docker and deployed onto Kubernetes clusters on AWS.",
                "Implemented Redis distributed locks and caching layers to ensure 99.99% system availability."
            ]),
            ("Software Engineer", "Nexis Enterprise Labs", "2021 - 2022", [
                "Developed RESTful web services in Java and Spring Framework.",
                "Conducted code reviews, database indexing, and unit testing with JUnit and Mockito."
            ])
        ]
    },
    {
        "filename": "Carlos_Mendez_FullStack_Python.pdf",
        "format": "pdf",
        "name": "Carlos Mendez",
        "title": "Full Stack Python Developer",
        "email": "carlos.mendez.dev@example.com",
        "phone": "+1 (555) 456-7890",
        "linkedin": "carlos-mendez-py",
        "github": "cmendez-code",
        "experience_years": 3.5,
        "education": "B.Tech in Computer Science & Engineering, 2022",
        "skills": ["Python", "Django", "React", "JavaScript", "SQL", "MySQL", "REST APIs", "Git", "Docker", "HTML5", "CSS3"],
        "summary": "Full Stack Developer with 3.5 years of hands-on experience building web applications with Django and React. Experienced in relational database design, asynchronous task workers, and responsive UI interfaces.",
        "experience": [
            ("Full Stack Developer", "OmniWeb Innovations", "2022 - Present", [
                "Created responsive single-page web applications using React.js and modern JavaScript.",
                "Built resilient backend REST APIs using Python and Django REST Framework.",
                "Wrote performant SQL queries and handled migrations across MySQL databases.",
                "Collaborated with UX teams using Agile sprints and Git version control."
            ]),
            ("Junior Software Engineer", "ByteForge Studio", "2021 - 2022", [
                "Assisted in developing frontend components and writing integration test cases."
            ])
        ]
    },
    {
        "filename": "Diana_Patel_Frontend_Engineer.docx",
        "format": "docx",
        "name": "Diana Patel",
        "title": "Frontend Software Engineer",
        "email": "diana.patel.ui@example.com",
        "phone": "+1 (555) 567-8901",
        "linkedin": "dianapatel-ui",
        "github": "dianap-dev",
        "experience_years": 4.0,
        "education": "B.S. in Information Technology, University of Washington, 2022",
        "skills": ["React", "TypeScript", "JavaScript", "Next.js", "Redux", "Tailwind CSS", "HTML5", "CSS3", "Node.js", "Git", "REST APIs"],
        "summary": "Frontend specialist with 4 years of experience crafting pixel-perfect, accessible, and high-performance user interfaces. Expert in React.js, TypeScript, Next.js, and state management architectures.",
        "experience": [
            ("Lead Frontend Developer", "Verve Interactive", "2023 - Present", [
                "Led frontend architecture migration to Next.js and TypeScript, decreasing bounce rates by 22%.",
                "Created a unified React component library with Tailwind CSS used across 8 company applications.",
                "Integrated frontend clients with backend REST and GraphQL endpoints."
            ]),
            ("UI Developer", "PixelWorks Media", "2021 - 2023", [
                "Built responsive dashboards in React, Redux, and Chart.js."
            ])
        ]
    },
    {
        "filename": "Ethan_Walker_Cloud_DevOps.pdf",
        "format": "pdf",
        "name": "Ethan Walker",
        "title": "DevOps & Cloud Infrastructure Engineer",
        "email": "ethan.walker.ops@example.com",
        "phone": "+1 (555) 678-9012",
        "linkedin": "ethanwalker-cloud",
        "github": "ewalker-ops",
        "experience_years": 5.0,
        "education": "B.S. in Computer Systems, Purdue University, 2021",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD", "Linux", "Bash", "Python", "Git", "PostgreSQL"],
        "summary": "DevOps Engineer with 5 years experience managing scalable cloud infrastructure on AWS. Strong expertise in Docker containerization, Kubernetes cluster management, and Terraform infrastructure-as-code.",
        "experience": [
            ("Senior DevOps Engineer", "Stratosphere Cloud", "2023 - Present", [
                "Provisioned and managed multi-region AWS environments utilizing Terraform and CloudFormation.",
                "Constructed robust automated CI/CD pipelines in GitHub Actions and Jenkins.",
                "Administered production Kubernetes clusters maintaining 99.95% uptime."
            ]),
            ("Systems Administrator", "Prime Hosting", "2021 - 2023", [
                "Maintained Linux servers, bash automation scripts, and PostgreSQL database backups."
            ])
        ]
    },
    {
        "filename": "Fiona_Gallagher_AI_NLP.docx",
        "format": "docx",
        "name": "Fiona Gallagher",
        "title": "AI / Machine Learning Engineer (NLP)",
        "email": "fiona.gallagher.ai@example.com",
        "phone": "+1 (555) 789-0123",
        "linkedin": "fionagallagher-ai",
        "github": "fgallagher-nlp",
        "experience_years": 3.0,
        "education": "M.S. in Artificial Intelligence, University of Edinburgh, 2023",
        "skills": ["Python", "Machine Learning", "NLP", "spaCy", "Sentence Transformers", "PyTorch", "Scikit-Learn", "FastAPI", "Hugging Face", "LLMs", "Docker", "Git"],
        "summary": "AI Engineer with 3 years of specialized expertise in Natural Language Processing, text representation, and semantic search. Experienced in training transformer models and deploying production ML APIs with FastAPI.",
        "experience": [
            ("Machine Learning Engineer", "CognitiveAI Labs", "2023 - Present", [
                "Engineered semantic text matching and search pipelines utilizing Sentence Transformers and vector similarity.",
                "Built custom named entity recognition (NER) pipelines with spaCy for resume and contract parsing.",
                "Deployed real-time inference microservices with FastAPI and Docker on AWS EC2."
            ]),
            ("Data Science Intern", "Insight Analytics", "2022 - 2023", [
                "Trained classifier models using Scikit-Learn and PyTorch on unstructured text datasets."
            ])
        ]
    },
    {
        "filename": "George_Washington_Junior_Dev.pdf",
        "format": "pdf",
        "name": "George Washington",
        "title": "Junior Full Stack Developer",
        "email": "george.washington.dev@example.com",
        "phone": "+1 (555) 890-1234",
        "linkedin": "georgewashington-dev",
        "github": "gwashington-code",
        "experience_years": 1.2,
        "education": "B.S. in Computer Science, Georgia Tech, 2025",
        "skills": ["Python", "FastAPI", "React", "JavaScript", "SQL", "PostgreSQL", "Git", "HTML5", "CSS3"],
        "summary": "Motivated Junior Developer with 1.2 years of professional experience building web apps. Quick learner eager to contribute clean Python backend code and React components to high-impact teams.",
        "experience": [
            ("Associate Software Developer", "NovaTech Solutions", "2025 - Present", [
                "Developed REST endpoints in Python and FastAPI for customer analytics.",
                "Assisted in creating responsive UI components in React.js and CSS3.",
                "Collaborated with senior engineers on database queries and unit testing."
            ])
        ]
    },
    {
        "filename": "Hannah_Schmidt_Data_Analyst.docx",
        "format": "docx",
        "name": "Hannah Schmidt",
        "title": "Business Data Analyst",
        "email": "hannah.schmidt.data@example.com",
        "phone": "+1 (555) 901-2345",
        "linkedin": "hannahschmidt-analytics",
        "github": "hschmidt-data",
        "experience_years": 2.5,
        "education": "B.S. in Economics & Statistics, NYU, 2023",
        "skills": ["SQL", "Python", "Pandas", "NumPy", "PostgreSQL", "Git", "Problem Solving"],
        "summary": "Data Analyst with 2.5 years of experience querying relational databases, building automated dashboards, and extracting business intelligence insights using SQL and Python.",
        "experience": [
            ("Data Analyst", "Metrix Consulting", "2023 - Present", [
                "Wrote advanced SQL queries and stored procedures across PostgreSQL datasets.",
                "Processed large tabular datasets using Python, Pandas, and NumPy for executive KPI reporting."
            ])
        ]
    },
    {
        "filename": "Ian_Thorne_Mobile_Engineer.pdf",
        "format": "pdf",
        "name": "Ian Thorne",
        "title": "Mobile iOS / Android Developer",
        "email": "ian.thorne.apps@example.com",
        "phone": "+1 (555) 012-3456",
        "linkedin": "ianthorne-mobile",
        "github": "ithorne-apps",
        "experience_years": 3.5,
        "education": "B.S. in Software Engineering, UT Austin, 2022",
        "skills": ["Swift", "Kotlin", "Git", "REST APIs", "Unit Testing"],
        "summary": "Mobile application developer with 3.5 years of native iOS and Android application engineering experience. Proficient in Swift and Kotlin.",
        "experience": [
            ("Mobile Engineer", "AppVibe Mobile", "2022 - Present", [
                "Developed native iOS features using Swift and SwiftUI.",
                "Integrated backend REST APIs and handled client-side caching."
            ])
        ]
    },
    {
        "filename": "Jessica_Martinez_QA_Engineer.docx",
        "format": "docx",
        "name": "Jessica Martinez",
        "title": "QA Automation Engineer",
        "email": "jessica.martinez.qa@example.com",
        "phone": "+1 (555) 123-7890",
        "linkedin": "jessicamartinez-qa",
        "github": "jmartinez-test",
        "experience_years": 1.5,
        "education": "B.S. in Information Systems, 2024",
        "skills": ["Python", "Unit Testing", "Git", "Agile", "SQL"],
        "summary": "Detail-oriented QA Automation Engineer with 1.5 years experience designing automated test suites in Python and ensuring regression quality in Agile workflows.",
        "experience": [
            ("QA Engineer", "QualityFirst Labs", "2024 - Present", [
                "Authored automated regression test scripts using PyTest.",
                "Participated in Agile sprint planning and bug triage."
            ])
        ]
    },
    {
        "filename": "Kevin_OConnor_Staff_Systems.pdf",
        "format": "pdf",
        "name": "Kevin O'Connor",
        "title": "Staff Distributed Systems Architect",
        "email": "kevin.oconnor.arch@example.com",
        "phone": "+1 (555) 234-8901",
        "linkedin": "kevinoconnor-arch",
        "github": "koconnor-dist",
        "experience_years": 8.0,
        "education": "Master of Science in Computer Science, MIT, 2018",
        "skills": ["Go", "Kubernetes", "Microservices", "PostgreSQL", "Docker", "System Design", "AWS", "Redis", "Git", "REST APIs", "Python"],
        "summary": "Seasoned Distributed Systems Engineer with 8 years of technical leadership designing fault-tolerant, high-scale architectures in Go and Python. Extensive track record leading infrastructure transformations.",
        "experience": [
            ("Staff Systems Architect", "Titan Distributed Networks", "2021 - Present", [
                "Led engineering architecture for core multi-tenant microservices handling 50k RPS.",
                "Architected event-driven pipelines utilizing Kafka, Redis, and PostgreSQL clusters.",
                "Mentored 15+ engineers in distributed systems design, observability, and containerization."
            ]),
            ("Senior Backend Developer", "GlobalCloud Services", "2018 - 2021", [
                "Built microservices and scalable APIs deployed in Kubernetes clusters on AWS."
            ])
        ]
    },
    {
        "filename": "Laura_Chen_Software_Intern.pdf",
        "format": "pdf",
        "name": "Laura Chen",
        "title": "Software Engineering Intern",
        "email": "laura.chen.student@example.com",
        "phone": "+1 (555) 345-9012",
        "linkedin": "laurachen-tech",
        "github": "lchen-code",
        "experience_years": 0.5,
        "education": "B.S. in Computer Science Candidate, UC Berkeley, Class of 2027",
        "skills": ["Python", "JavaScript", "HTML5", "CSS3", "Git", "Problem Solving"],
        "summary": "Curious computer science undergraduate looking for software engineering internship opportunities. Strong foundations in data structures, algorithms, and web basics.",
        "experience": [
            ("Software Engineering Intern", "Campus Web Labs", "Summer 2026", [
                "Built interactive club directory web pages using JavaScript and HTML5.",
                "Created python scripts for student survey data processing."
            ])
        ]
    }
]

def generate_pdf(cand: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb')
    )
    contact_style = ParagraphStyle(
        'DocContact',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748b')
    )
    section_heading = ParagraphStyle(
        'DocSec',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        spaceBefore=2
    )

    story = []
    story.append(Paragraph(cand['name'], title_style))
    story.append(Paragraph(cand['title'], subtitle_style))
    contact_line = f"{cand['email']} | {cand['phone']} | linkedin.com/in/{cand['linkedin']} | github.com/{cand['github']}"
    story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=8))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_heading))
    story.append(Paragraph(cand['summary'], body_style))
    story.append(Spacer(1, 6))

    # Skills
    story.append(Paragraph("TECHNICAL SKILLS", section_heading))
    skills_text = "<b>Core Competencies:</b> " + ", ".join(cand['skills'])
    story.append(Paragraph(skills_text, body_style))
    story.append(Spacer(1, 6))

    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE", section_heading))
    for role, company, period, bullets in cand['experience']:
        role_line = f"<b>{role}</b> — <i>{company}</i> ({period})"
        story.append(Paragraph(role_line, body_style))
        for b in bullets:
            story.append(Paragraph(f"• {b}", bullet_style))
        story.append(Spacer(1, 4))

    # Education
    story.append(Paragraph("EDUCATION", section_heading))
    story.append(Paragraph(cand['education'], body_style))

    doc.build(story)

def generate_docx(cand: dict, output_path: str):
    doc = Document()

    # Title & Contact
    h1 = doc.add_paragraph()
    run = h1.add_run(cand['name'])
    run.font.name = 'Arial'
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)

    sub = doc.add_paragraph()
    s_run = sub.add_run(cand['title'])
    s_run.font.name = 'Arial'
    s_run.font.size = Pt(12)
    s_run.font.bold = True
    s_run.font.color.rgb = RGBColor(37, 99, 235)

    contact = doc.add_paragraph()
    c_run = contact.add_run(f"{cand['email']} | {cand['phone']} | linkedin.com/in/{cand['linkedin']} | github.com/{cand['github']}")
    c_run.font.name = 'Arial'
    c_run.font.size = Pt(9)
    c_run.font.color.rgb = RGBColor(100, 116, 139)

    # Summary
    doc.add_heading("PROFESSIONAL SUMMARY", level=2)
    p = doc.add_paragraph(cand['summary'])
    p.style.font.name = 'Arial'

    # Skills
    doc.add_heading("TECHNICAL SKILLS", level=2)
    sp = doc.add_paragraph()
    sp.add_run("Core Proficiencies: ").bold = True
    sp.add_run(", ".join(cand['skills']))

    # Experience
    doc.add_heading("PROFESSIONAL EXPERIENCE", level=2)
    for role, company, period, bullets in cand['experience']:
        rp = doc.add_paragraph()
        rp.add_run(f"{role} — {company} ").bold = True
        rp.add_run(f"({period})").italic = True
        for b in bullets:
            bp = doc.add_paragraph(b, style='List Bullet')
            bp.style.font.name = 'Arial'

    # Education
    doc.add_heading("EDUCATION", level=2)
    ep = doc.add_paragraph(cand['education'])
    ep.style.font.name = 'Arial'

    doc.save(output_path)

def main():
    target_dir = os.path.join(os.path.dirname(__file__), "resumes")
    os.makedirs(target_dir, exist_ok=True)
    print(f"Generating synthetic resumes in: {target_dir}")

    for cand in CANDIDATES:
        out_file = os.path.join(target_dir, cand['filename'])
        if cand['format'] == 'pdf':
            generate_pdf(cand, out_file)
            print(f"  [PDF] Generated: {cand['filename']}")
        else:
            generate_docx(cand, out_file)
            print(f"  [DOCX] Generated: {cand['filename']}")

    print(f"\nSuccessfully generated {len(CANDIDATES)} sample resumes (PDF & DOCX)!")

if __name__ == "__main__":
    main()
