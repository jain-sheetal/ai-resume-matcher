# AI-Based Resume Matching & Candidate Ranking System (MatchPro AI)

> **Practical Development Assignment Submission**  
> **Role:** AI / Full Stack Developer Intern / Project-Based  
> **Tech Stack:** React 18, Tailwind CSS, Python FastAPI, Sentence Transformers (`all-MiniLM-L6-v2`), PyPDF, python-docx, Scikit-Learn.

---

## 📌 Executive Summary

**MatchPro AI** is an intelligent candidate screening and resume ranking platform designed to streamline recruiter workflows. It extracts structured entities from heterogeneous resumes (PDF and DOCX), benchmarks candidate profiles against targeted Job Descriptions (JDs), and produces transparent, explainable ranking scores powered by **contextual semantic embeddings** rather than naive keyword search.

---

## 🎯 Evaluation Criteria Mapping (100%)

| Evaluation Parameter | Weight | Implementation Details in This Project | Status |
| :--- | :---: | :--- | :---: |
| **Functional Application** | **25%** | Complete end-to-end working web application (FastAPI backend + React frontend) with real-time matching, CSV export, and live testing. | ✅ Complete |
| **Resume Parsing Accuracy** | **15%** | Robust parsing pipeline supporting PDF & DOCX; accurately extracts Candidate Name, Email, Phone, Chronological Experience, Skills, and Education. | ✅ Complete |
| **JD-to-Resume Matching Logic** | **25%** | Hybrid matching combining Sentence Transformers (`all-MiniLM-L6-v2`), canonical skill ontology (250+ skills), and chronological tenure intervals. | ✅ Complete |
| **Matching Score & Explanation** | **15%** | Transparent multi-criteria scoring formula with Explainable AI (XAI) outputting strengths, gaps, experience delta, and domain alignment. | ✅ Complete |
| **UI/UX & Usability** | **10%** | Modern, responsive dashboard with drag-and-drop batch uploader, real-time filters, interactive ranking table, and slide-over candidate analysis drawer. | ✅ Complete |
| **Code Quality & Documentation** | **10%** | Modular, typed Python code (Pydantic, FastAPI), clean component architecture, comprehensive docs (`README.md`, `ALGORITHM.md`), and test scripts. | ✅ Complete |

---

## 🚀 Key Functional Modules

### Module 1: Job Description Input
- **Flexible Input:** Interface to paste JD text or upload JD files (`.pdf`, `.docx`, `.txt`).
- **Entity Extraction:** Automatically extracts key role titles, mandatory technical skills, minimum required experience (years), and educational requirements.
- **Pre-Configured Presets:** Instant 1-click presets for *Senior Full Stack Developer (Python/React)*, *Java Backend Engineer (Spring Boot)*, and *AI/NLP Machine Learning Engineer*.

### Module 2: Batch Resume Upload
- **High-Capacity Batch Processing:** Upload 10, 20, or more resumes simultaneously.
- **Format Support:** Full dual-format support for both **PDF** and **DOCX** files.
- **Candidate Extraction:** Extracts candidate contact info (name, email, phone, links), detected years of experience, and canonical skills.
- **⚡ 1-Click Demo Data:** Includes a built-in *"Load 12 Sample Resumes"* button with realistic synthetic candidate profiles.

### Module 3: AI Resume Matching Engine
- **Dense Contextual Embeddings:** Uses Sentence Transformers (`all-MiniLM-L6-v2`) to capture deep semantic intent and domain overlap beyond literal keyword occurrences.
- **Canonical Skill Taxonomy:** Inverted index mapping 250+ tech skills with alias normalization (e.g. `React.js` $\rightarrow$ `React`, `Postgres` $\rightarrow$ `PostgreSQL`, `k8s` $\rightarrow$ `Kubernetes`).
- **Experience Duration Resolution:** Compares candidate tenure against JD expectations with non-overlapping timeline merging.
- **Configurable Weights:** Recruiter-customizable scoring weights (Skills 40%, Semantic 35%, Experience 20%, Education 5%).

### Module 4: Candidate Ranking Dashboard
- **Ranked Table:** Displays candidates sorted descending by overall match percentage.
- **Detailed Columns:** Rank medal (🥇, 🥈, 🥉), Candidate Name, Total Experience, Match %, Matched Skills chips.
- **Interactive Controls:** Real-time search by name/skill, minimum score threshold slider, multi-column sorting.
- **Export to CSV:** Single-click export of candidate rankings to a CSV spreadsheet.

### Module 5: Candidate-Level Analysis (Deep Dive)
- **Recruiter Slide-Over Drawer:** Comprehensive view opened by clicking any candidate.
- **Score Breakdown:** Individual scores for Technical Skills, Semantic Embeddings, Experience, and Education.
- **Side-by-Side Experience Comparison:** Candidate years vs Required years with tenure delta.
- **Matched vs Missing Skills:** Color-coded badges with checkmarks and alerts.
- **Explainable AI Rationale:** Clear bulleted list of strengths, gaps, and semantic alignment justifications.
- **Extracted Text Preview:** Collapsible raw text viewer for auditability.

---

## 🏗️ System Architecture

```
ai-resume-matcher/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application entrypoint
│   │   ├── config.py                   # Scoring weights & global configurations
│   │   ├── models/schemas.py           # Pydantic data schemas
│   │   ├── parsers/                    # PDF & DOCX text extractors & normalizer
│   │   ├── extractor/                  # Skill ontology, contact, experience, and JD extractors
│   │   ├── matcher/                    # SentenceTransformer embeddings, scorer, explainer
│   │   └── routes/                     # REST API endpoints (JD, Resumes, Matching)
│   ├── sample_data/
│   │   ├── generate_samples.py         # Generator for 12 synthetic resumes (PDF & DOCX)
│   │   └── resumes/                    # Pre-generated sample resumes
│   ├── test_pipeline.py                # End-to-end backend test script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                 # UI components (Navbar, JD, Uploader, Table, Drawer, Modals)
│   │   ├── services/api.js             # API client
│   │   ├── App.jsx                     # Main application logic
│   │   └── index.css                   # Tailwind CSS styling
│   ├── package.json
│   └── vite.config.js
├── ALGORITHM.md                        # In-depth algorithmic & math documentation
├── start.sh                            # One-command dual-server launcher
└── README.md
```

---

## ⚡ Quickstart & Setup Guide

### Prerequisites
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & npm

---

### Step 1: Clone / Open Project in VS Code
```bash
# Navigate to the project directory
cd /Users/kratarthsrivastava/.gemini/antigravity/scratch/ai-resume-matcher

# Open directly in VS Code
code .
```

---

### Step 2: Start the Application with 1 Command
Run the bundled `start.sh` script to launch both backend and frontend concurrently:

```bash
chmod +x start.sh
./start.sh
```

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Alternative: Manual Step-by-Step Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the test pipeline to verify installation
python test_pipeline.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Testing with Sample Resumes

1. Click **"Presets"** at the top of Module 1 to pick a sample Job Description (e.g. *Senior Full Stack Developer*).
2. Click **"Load 12 Sample Resumes (PDF & DOCX)"** in Module 2.
3. Click **"Match & Rank Candidates"**.
4. Explore the **Ranking Dashboard**, click on any candidate to view the **Candidate-Level Analysis Drawer**, and click **"Export CSV"** to download the report.

---

## 🧮 Matching Formula Summary

$$\text{Overall Score} = 0.40 \times S_{\text{skill}} + 0.35 \times S_{\text{semantic}} + 0.20 \times S_{\text{exp}} + 0.05 \times S_{\text{edu}}$$

For a full technical and mathematical breakdown, see [ALGORITHM.md](ALGORITHM.md).

---

## 📄 License
Synthetic test data and code developed for the technical interview assignment. All candidate profiles are entirely synthetic with no real personal data.
