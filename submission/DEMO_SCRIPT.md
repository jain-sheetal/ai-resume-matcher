# MatchPro AI — Live Demonstration Video Script (3–5 Minutes)

**Presenter:** Sheetal Jain  
**Live URL:** [https://ai-resume-matcher-xs5e.onrender.com/](https://ai-resume-matcher-xs5e.onrender.com/)  
**Target Duration:** 4 minutes 30 seconds  

---

## Timeline & Narration Breakdown

### [0:00 – 0:30] Problem Statement & Introduction
- **On Screen:** Browser opens to `https://ai-resume-matcher-xs5e.onrender.com/`. Clean navigation bar, hero banner *"AI-Based Resume Matching & Candidate Ranking"*, and dual-input panels visible.
- **Presenter Narration:**
  > *"Hello everyone! Today, recruiters spend only 6 to 8 seconds scanning a resume, often relying on legacy ATS tools that look for exact keyword matches. This leads to two major issues: keyword-stuffed resumes get false-positive high scores, while qualified candidates who write 'Postgres' instead of 'PostgreSQL' are unfairly rejected. To solve this, I built **MatchPro AI** — an intelligent, semantic resume matching and candidate ranking engine powered by Sentence-BERT and Explainable AI."*

### [0:30 – 1:00] Architecture & Technology Stack
- **On Screen:** Mouse points to the navbar status badge: `Embedding: all-MiniLM-L6-v2` and clicks the `Algorithm Docs` modal showing the 4 weighted pillars.
- **Presenter Narration:**
  > *"MatchPro AI uses a modern full-stack architecture. The backend is built with **FastAPI**, serving high-speed asynchronous REST endpoints and executing CPU-optimized **Sentence-BERT** embeddings using the `all-MiniLM-L6-v2` model. The frontend is a reactive **React 18** Single Page Application styled with Tailwind CSS. The entire application runs inside a multi-stage Docker container deployed live on Render."*

### [1:00 – 1:45] Entering the Job Description (Module 1)
- **On Screen:** In Module 1 ("Job Description Input"), click the **"Senior Full Stack Developer"** preset button (or paste a custom JD). Then click the blue **"Extract Requirements"** button. The card highlights:
  - Position: *Senior Full Stack Developer*
  - Min Experience: *4.0 Years*
  - Required Skills (19): *AWS, CI/CD, Docker, FastAPI, Python, React, PostgreSQL...*
- **Presenter Narration:**
  > *"Let's start by defining our Job Description. We can paste raw job text, upload a document, or click a pre-built benchmark. When I click 'Extract Requirements', the backend automatically segments the JD into mandatory technical skills, preferred qualifications, and minimum required experience tenure. Here we see 19 required skills and a 4-year minimum experience requirement."*

### [1:45 – 2:30] Batch Resume Upload (Module 2)
- **On Screen:** In Module 2 ("Batch Resume Upload"), click the button **"Load 12 Sample Resumes (PDF & DOCX)"** (or drag & drop candidate files). The grid populates with 12 candidate cards showing:
  - *Alex Rivera (PDF, 5.8 yrs exp, 16 skills)*
  - *Brenda Zhao (DOCX, 5.8 yrs exp, 13 skills)*
  - *Laura Chen (PDF, 0.5 yrs exp, 6 skills)*
  - Notice the bottom trigger turns green: *"Ready to execute AI semantic matching & candidate ranking!"*
- **Presenter Narration:**
  > *"Next, in Module 2, recruiters can upload resumes in bulk. The system supports multi-file PDF, DOCX, and TXT formats. I'll load our benchmark set of 12 candidate resumes. In milliseconds, our binary extraction pipeline parses each document, identifies candidate contact details with confidence ratings, and extracts their technical skills and employment timelines without storing sensitive data on disk."*

### [2:30 – 3:15] Executing Matching & Candidate Ranking Table
- **On Screen:** Click the vibrant blue/indigo button **"Match & Rank Candidates (12)"**. The page smoothly scrolls down to the candidate ranking table.
  - Candidate #1: *Alex Rivera (82.6%)*
  - Candidate #2: *Carlos Mendez (80.4%)*
  - Candidate #12: *Laura Chen (43.1%)*
  - Type *"React"* in the search bar — table filters down instantly.
  - Filter by experience: select *"3+ yrs"* — only experienced candidates appear.
- **Presenter Narration:**
  > *"Now, let's click 'Match & Rank Candidates'. In under 250 milliseconds, the engine executes semantic vector encoding, skill taxonomy mapping, and interval timeline merging. In our ranking table, Alex Rivera takes the #1 rank with an 82.6% composite match score, followed by Carlos Mendez. Recruiters can instantly filter by name, search for specific technologies, or filter by minimum years of experience."*

### [3:15 – 4:00] Deep Dive: Explainable AI & Evidence Citation
- **On Screen:** Click on **Alex Rivera**'s row. The **Candidate Detail Drawer** slides open from the right:
  - High Extraction Confidence badge.
  - Score Breakdown bars: Skills 78.6%, Semantic 76.8%, Experience 100.0%, Education 100.0%.
  - Verdict: *"Good Potential — Recommended for Screening"*.
  - Strengths list cites verbatim text: *"e.g. 'Architected and deployed 12+ scalable microservices using Python and FastAPI...' ".*
  - Requirements breakdown tabs: click *"Strong Match"* to see verified evidence; click *"Missing"* to see absent skills (*Django, MySQL*).
- **Presenter Narration:**
  > *"A key differentiator of MatchPro AI is Explainability. When I click on Alex Rivera, the detail drawer shows exactly why this candidate scored 82.6%. Notice our Explainable AI citing verbatim sentence snippets directly from Alex's resume: 'Architected and deployed 12+ scalable microservices using Python and FastAPI'. We don't just count keywords — we provide verifiable evidence of where and how the skill was demonstrated."*

### [4:00 – 4:30] Head-to-Head Comparison & CSV Export
- **On Screen:** Close the drawer. In the table, check the checkboxes for **Alex Rivera** and **Brenda Zhao**. Click the **"Compare (2)"** button.
  - The Head-to-Head Comparison Modal opens, showing side-by-side metric bars, skill overlap matrices, and experience comparisons.
  - Close the modal and click **"Export Ranking CSV"**. The CSV file downloads instantly.
- **Presenter Narration:**
  > *"When choosing between finalists, recruiters can select two candidates and click 'Compare'. This opens a side-by-side head-to-head evaluation comparing their skills, experience, and verdicts. Finally, with one click on 'Export CSV', recruiters can download a standardized report containing complete candidate records for their applicant tracking system."*

### [4:30 – 5:00] AI Methodology & Conclusion
- **On Screen:** Return to hero banner. Point to GitHub link and live Render deployment.
- **Presenter Narration:**
  > *"Under the hood, MatchPro AI merges overlapping employment dates to prevent tenure inflation, uses controlled equivalences for technologies like Postgres and React, and strictly bounds scores between 0 and 100%. With 23 automated tests passing in 0.18 seconds and a verified evaluation score of 93.5/100, MatchPro AI delivers a fast, transparent, and fair recruitment tool. Thank you!"*
