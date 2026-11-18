# MatchPro AI — Technical Interview Preparation Guide (40 Q&A)

This document contains 40 interview questions and concise, natural answers grounded in the MatchPro AI codebase for an AI / Full-Stack Developer internship interview.

---

## Category 1: Project Architecture

### 1. Can you explain your project in 60 seconds?
> "MatchPro AI is an AI-powered resume matching and candidate ranking engine. Recruiters upload Job Descriptions and batch candidate resumes in PDF or DOCX format. The system extracts skills, work experience, and education, converts text into dense 384-dimensional semantic embeddings using Sentence-BERT, reconciles overlapping work timelines, and computes a multi-factor score. It outputs a ranked recruiter dashboard with Explainable AI reasoning that cites verbatim sentence snippets from the candidate's resume."

### 2. Why did you choose React and FastAPI?
> "FastAPI provides native asynchronous I/O, automatic Pydantic schema validation, and high performance for Python ML workflows. React 18 with Vite provides an instantaneous, reactive Single Page Application with dynamic filtering, candidate comparison, and state management without page refreshes."

### 3. What is the complete request lifecycle when a recruiter clicks 'Match & Rank'?
> "The React frontend sends a `POST /api/match/evaluate` request containing the parsed JD and an array of extracted resumes. FastAPI validates the request using Pydantic, generates Sentence-BERT embeddings on CPU, evaluates mandatory and preferred skill overlaps, merges experience intervals, computes deterministic weighted scores, generates Explainable AI evidence snippets, and returns a sorted array of candidate results in under 250 milliseconds."

### 4. Why did you choose a stateless in-memory architecture?
> "For a rapid-prototyping evaluation system processing 10 to 500 resumes, in-memory processing in RAM offers sub-second response times, zero database migration overhead, and superior candidate data privacy because resumes are not permanently stored on disk."

### 5. How do the frontend and backend communicate?
> "They communicate via standard JSON REST APIs. In production, FastAPI serves the compiled React production bundle from `frontend/dist` on the root `/` path, meaning both client and API run on the same origin domain, completely eliminating CORS latency and configuration issues."

---

## Category 2: AI and NLP

### 6. What is Sentence-BERT (SBERT)?
> "Sentence-BERT is a modification of the pretrained BERT network using siamese and triplet network structures to generate semantically meaningful sentence embeddings that can be compared using cosine similarity."

### 7. Why did you choose `all-MiniLM-L6-v2`?
> "It maps sentences into 384-dimensional dense vectors with a 5x speed advantage over base BERT and minimal loss in semantic quality. It runs efficiently on CPU without requiring an expensive GPU, with an average inference time of 3.2 milliseconds."

### 8. What are embeddings?
> "Embeddings are dense numerical vector representations of text where words or sentences with similar contextual meanings are positioned close to each other in high-dimensional vector space."

### 9. What is cosine similarity and how is it calculated?
> "Cosine similarity measures the angle between two non-zero vectors in multi-dimensional space. Because our SBERT embeddings are unit-normalized to length 1.0, cosine similarity is simply the dot product of the two vectors, ranging from -1.0 to 1.0."

### 10. Why not use only TF-IDF?
> "TF-IDF relies purely on lexical word frequency and cannot recognize synonyms or contextual meaning. If a JD says 'PostgreSQL' and a candidate writes 'Relational SQL database', TF-IDF sees zero overlap, whereas Sentence-BERT recognizes strong semantic alignment."

### 11. What is semantic similarity?
> "Semantic similarity evaluates whether two passages convey equivalent meaning despite using different vocabulary, sentence structures, or phrasing."

### 12. How do you prevent false-positive skill matching?
> "We implement a 5-tier classification system. Merely mentioning a keyword once in a resume is classified as 'Partial Match' or 'Insufficient Evidence'. A 'Strong Match' requires verified evidence inside employment history or technical projects with a verbatim sentence snippet or frequency $\ge 2$."

### 13. How do you extract contextual evidence?
> "Our `find_evidence_snippet` function uses boundary-aware regex to find where a skill was used, splits surrounding text into sentences, and extracts the exact 1–2 sentence snippet where the technology was applied."

---

## Category 3: Matching Algorithm

### 14. Explain the complete matching algorithm.
> "The algorithm combines four weighted components: Skill Match (40%), Semantic Similarity (35%), Experience Alignment (20%), and Education (5%). Component scores are strictly bounded between 0 and 100, and the final percentage is a deterministic linear combination."

### 15. How are mandatory and preferred skills handled?
> "Mandatory skills carry 85% of the base skill score, while preferred skills carry 15%. If a candidate matches zero mandatory skills, their skill score is strictly 0.0%, and versatility bonuses are withheld."

### 16. How is the final match percentage calculated?
> "Formula: $\text{Overall} = 0.40 \cdot \text{Skills} + 0.35 \cdot \text{Semantic} + 0.20 \cdot \text{Experience} + 0.05 \cdot \text{Education}$. The score is strictly clamped between 0.0 and 100.0."

### 17. How do you compare experience?
> "Experience score is calculated as $\min(100.0, \frac{\text{Candidate Years}}{\text{Required Years}} \times 100.0)$. Excess seniority is capped at 100% so that it does not distort missing technical skills."

### 18. How do you handle overlapping employment dates?
> "We use an interval-merging algorithm (`merge_intervals`). Date spans are converted into decimal years, sorted chronologically, and merged whenever an end date overlaps a start date, calculating true calendar tenure."

### 19. How do you handle missing information?
> "Missing information is never fabricated. Missing education is marked as 'Not Specified' with an education score of 0.0% and flagged with low extraction confidence."

### 20. How do you ensure deterministic scoring?
> "All embedding vectors are generated with deterministic model weights, floating-point rounding is clamped to 1 decimal place, and ties in skills are broken with consistent alphabetical sorting."

---

## Category 4: Backend

### 21. Why FastAPI over Flask or Django?
> "FastAPI is built on Starlette and Pydantic, providing automatic OpenAPI documentation, asynchronous route handling, and type safety out of the box."

### 22. How do you handle PDF and DOCX parsing?
> "We use `pypdf` for direct binary PDF extraction and `python-docx` for Word documents, including paragraph and table cell extraction, without relying on third-party cloud conversion services."

### 23. How does batch upload work?
> "The `/api/resumes/upload` endpoint accepts `List[UploadFile]`, processing each file in memory, validating extension and size ($\le 10\text{ MB}$), and parsing up to 30 files concurrently."

### 24. How are API errors handled?
> "All endpoints use structured FastAPI `HTTPException` handlers with descriptive error messages, and parser exceptions return graceful fallbacks without terminating the worker."

### 25. How would you handle large files or streaming?
> "Files exceeding 10MB are rejected upfront. In production, we would use chunked streaming with `aiofiles` and offload extraction to background Celery workers."

---

## Category 5: Frontend

### 26. Explain the React component architecture.
> "The app has a single-page architecture: `Navbar`, `JobDescriptionInput` (Module 1), `ResumeUploader` (Module 2), `CandidateRankingTable` (Module 3), `CandidateDetailDrawer`, and `CandidateComparisonModal`."

### 27. How does the candidate ranking dashboard work?
> "It renders candidates sorted by match score with real-time text search, tenure filters (`1+`, `3+`, `5+`), category tier filters (`Strong`, `Good`, `Moderate`), and comparison checkboxes."

### 28. How does candidate comparison work?
> "Recruiters select two candidates via checkboxes and click 'Compare (2)'. A modal opens displaying side-by-side metric bars, skill overlap matrices, and verdicts."

### 29. How do you manage application state?
> "We use React's built-in `useState` and `useEffect` hooks lifted to `App.jsx`, ensuring predictable unidirectional data flow without the overhead of Redux."

---

## Category 6: Deployment

### 30. Explain Docker multi-stage builds.
> "Stage 1 uses Node 18 to build the React frontend into static assets in `dist/`. Stage 2 uses `python:3.11-slim`, copies the built frontend, installs CPU-only PyTorch, and runs Uvicorn, keeping image size minimal."

### 31. How is the model loaded in production?
> "We use a singleton pattern with lazy loading. The model loads on first request or startup and stays cached in memory for subsequent inference calls."

### 32. How would you scale this to 100,000 resumes?
> "We would introduce an Approximate Nearest Neighbor (ANN) vector database like Qdrant or Milvus, pre-compute embeddings via background Celery queues, and perform sub-10ms similarity searches."

### 33. Why is there no database in this submission?
> "This assignment is an interactive prototype evaluation. A stateless in-memory architecture delivers instantaneous ranking (<250ms), zero cloud DB costs, and protects candidate privacy."

### 34. What are the current limitations?
> "Image-only scanned PDFs require OCR (e.g., Tesseract). Memory scales with concurrent batch size, which a vector DB and disk caching would address."

---

## Category 7: Practical Engineering & Behavioral

### 35. What was the most difficult bug you encountered and how did you resolve it?
> "The disabled 'Match & Rank' button defect. In `App.jsx`, `canMatch` wasn't passed down properly to `ResumeUploader`. We wired `canMatch={Boolean(parsedJd && resumes.length > 0)}` and verified the fix across automated tests and live deployment."

### 36. What would you improve with another week of development?
> "I would add Tesseract OCR for scanned PDF support, an interactive weights slider for custom hiring criteria, and unit test CI workflows with GitHub Actions."

### 37. What would you do differently in an enterprise production environment?
> "I would add OAuth2 JWT authentication, PostgreSQL with pgvector for persistent search, Celery/Redis background task queues, and Prometheus/Grafana monitoring."

### 38. How would you evaluate the actual ranking accuracy in production?
> "We would measure Normalized Discounted Cumulative Gain (NDCG@10) and Mean Reciprocal Rank (MRR) by comparing system rankings against human recruiter hiring decisions."

### 39. How do you prevent bias in recruitment ranking?
> "Our extraction pipeline scrubs personal identifiers (name, gender, age, email) before semantic embedding comparison. Embeddings evaluate strictly technical skills, project descriptions, and verified experience."

### 40. Why should we select you for this internship?
> "I deliver complete, mathematically sound engineering solutions. Within this five-day assignment, I built a working full-stack system with Sentence-BERT, interval timeline merging, 23 automated tests, and live Docker deployment on Render, achieving a verified 93.5/100 evaluation score."
