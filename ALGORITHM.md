# Technical Approach & AI Matching Methodology (MatchPro AI)

## 1. Overview & Architecture Philosophy
**MatchPro AI** implements a hybrid scoring engine designed for automated resume screening and candidate ranking. Rather than relying on naive substring search (which produces false positives like matching `"Go"` in `"Good"`) or slow, non-deterministic external LLM APIs, our architecture combines:
1. **Contextual Semantic Embeddings** via Sentence Transformers (`all-MiniLM-L6-v2`) on CPU.
2. **Controlled Skill-Equivalence Ontology (250+ canonical skills)** with boundary-aware regex assertions `(?<![a-zA-Z0-9])` and symbol safety (`C++`, `C#`, `.NET`).
3. **Context-Aware Evidence Classification**: Classifying requirements into *Strong Match*, *Partial Match*, *Related Skill*, *Missing*, and *Insufficient Evidence* linked directly to extracted resume sentences.
4. **Non-Overlapping Chronological Interval Merging** for verifiable candidate tenure.
5. **Multi-Factor Extraction Confidence Ratings** (High, Medium, Low) based on empirical document evidence.
6. **Transparent Explainable AI (XAI)** decision rationale.

---

## 2. Core Scoring Formula

The overall candidate matching score $S_{\text{overall}} \in [0.0, 100.0]$ is computed as a deterministic, weighted composite:

$$S_{\text{overall}} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{semantic}} \cdot S_{\text{semantic}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{edu}} \cdot S_{\text{edu}}$$

### Default Recruiter Weights
$$\sum_{i} w_i = 1.0, \quad w_i \ge 0$$

| Component | Default Weight ($w$) | Metric | Purpose |
| :--- | :---: | :--- | :--- |
| **Technical Skills** ($S_{\text{skill}}$) | **0.40** (40%) | Mandatory & preferred requirements with evidence | Evaluates technical prerequisite mastery |
| **Semantic AI** ($S_{\text{semantic}}$) | **0.35** (35%) | Sentence-BERT Cosine Similarity | Measures contextual & domain overlap |
| **Experience Tenure** ($S_{\text{exp}}$) | **0.20** (20%) | Candidate non-overlapping yrs vs JD min | Evaluates professional seniority |
| **Education Qualification** ($S_{\text{edu}}$) | **0.05** (5%) | Verified degree qualification baseline | Academic baseline evaluation |

---

## 3. Algorithmic Breakdown

### 3.1. Dense Contextual Embeddings ($S_{\text{semantic}}$)
Keyword search fails when candidate narratives use different phrasing than the job posting:
* *Example:* *"Engineered resilient microservices with asynchronous endpoints"* $\leftrightarrow$ *"Backend REST API developer"*.

**Sentence-BERT Pipeline:**
1. Text streams (Job Description context and Candidate project/work histories) are tokenized and processed through a 6-layer MiniLM transformer.
2. Mean pooling over token embeddings produces normalized 384-dimensional dense vectors $\mathbf{u}, \mathbf{v} \in \mathbb{R}^{384}$ such that $\|\mathbf{u}\|_2 = 1.0, \|\mathbf{v}\|_2 = 1.0$.
3. Cosine similarity is computed via dot product:
   $$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \sum_{i=1}^{384} u_i v_i$$
4. Clamped to $[0.0, 1.0]$ and scaled:
   $$S_{\text{semantic}} = \text{round}(\min(100.0, \max(0.0, \text{Cosine Similarity} \times 100.0)), 1)$$

**Engine Health & Fallback Transparency:**
The system caches `all-MiniLM-L6-v2` locally for offline execution. If the deep learning runtime is unavailable, it initializes a verified `TfidfVectorizer(ngram_range=(1,2))` with explicit diagnostics exposed at `GET /health` and `GET /api/match/diagnostics`. It **never silently presents TF-IDF results as semantic AI without flagging `is_fallback: True`**.

---

### 3.2. Context-Aware Skill Matching & Controlled Equivalences ($S_{\text{skill}}$)

#### A. Controlled Equivalence Mapping
To ensure semantic equivalence without false drift, the engine maintains controlled mappings:
* `React.js`, `ReactJS`, `React Frontend` $\leftrightarrow$ `React`
* `Postgres`, `PgSQL`, `PostgreSQL Database` $\leftrightarrow$ `PostgreSQL`
* `FastAPI Framework`, `Asynchronous Python API` $\leftrightarrow$ `FastAPI`
* `ML`, `Applied Machine Learning`, `Statistical Modeling` $\leftrightarrow$ `Machine Learning`
* `CI/CD`, `Continuous Integration`, `GitHub Actions`, `Jenkins` $\leftrightarrow$ `CI/CD`

#### B. Requirement Match Classification Tiers
For every JD requirement, the engine evaluates evidence from the resume text:
1. **Strong Match (1.0 weight):** Skill is demonstrated in experience or project narratives with concrete sentence context (frequency $\ge 2$ or descriptive sentence snippet $>40$ chars).
2. **Partial Match (0.85 weight):** Mentioned in skills section or single brief mention.
3. **Related Skill (0.75 weight):** Matched via controlled semantic equivalence.
4. **Missing (0.0 weight):** No verifiable mention found in document.
5. **Insufficient Evidence (0.0 weight):** Ambiguous token in unrelated context.

#### C. Mandatory vs. Preferred Weighting
* **Mandatory Requirements:** Account for **85%** of the raw skill score.
* **Preferred / Nice-to-Have Skills:** Account for **15%** of the raw skill score.
* **Versatility Bonus:** Candidates meeting mandatory skills receive up to $+5\%$ bonus for additional relevant tech proficiencies. If mandatory requirements score $0.0$, the versatility bonus is strictly zero.

---

### 3.3. Chronological Tenure & Non-Overlapping Interval Merging ($S_{\text{exp}}$)

1. **Dynamic Temporal Calculation:**
   Current year and month fractions are determined dynamically using `datetime.now()` (e.g. `2026.85`), eliminating hardcoded current-year assumptions.
2. **Interval Extraction:**
   Dates are parsed into start and end floats: $t = \text{year} + \frac{\text{month} - 1}{12}$.
3. **Non-Overlapping Interval Merging:**
   Intervals $[t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)}]$ are sorted chronologically. Overlapping concurrent tenures (e.g., freelancing during full-time employment) are merged:
   $$\Delta t_{\text{total}} = \sum_{k} (t_{\text{end}}^{(k)} - t_{\text{start}}^{(k)})$$
4. **Tenure Curve:**
   * If $Y_{\text{cand}} \ge Y_{\text{req}}$: $S_{\text{exp}} = 100.0$
   * If $Y_{\text{cand}} < Y_{\text{req}}$:
     $$S_{\text{exp}} = \left(\frac{Y_{\text{cand}}}{Y_{\text{req}}}\right)^{0.85} \times 100.0$$
   *(The $0.85$ power exponent penalizes seniority gaps gracefully without an unrealistic cliff for candidates just under the threshold).*

---

### 3.4. Education Matching ($S_{\text{edu}}$)

The engine evaluates degree level without assuming unearned qualifications:
* Ph.D. $\rightarrow 1.0$ (100%)
* Master's Degree (M.S., M.Tech, MBA, MCA) $\rightarrow 0.95$ (95%)
* Bachelor's Degree (B.S., B.Tech, B.E., BCA) $\rightarrow 0.85$ (85%)
* Associate / Diploma $\rightarrow 0.70$ (70%)
* If no education is mentioned: explicitly flagged as **`Not Specified`** ($S_{\text{edu}} = 50.0\%$, Extraction Confidence: `Low`).

---

## 4. Multi-Factor Extraction Confidence Model

To ensure recruiters know when an extraction is solid vs ambiguous, every resume receives empirical confidence ratings:

| Dimension | High Confidence Criteria | Medium Confidence Criteria | Low Confidence Criteria |
| :--- | :--- | :--- | :--- |
| **Name** | 2–4 title-cased words at top of document | Extracted from filename with clean tokens | Fallback to generic "Candidate" |
| **Contact** | Verified Email AND verified Phone (10–15 digits) | Email OR Phone verified | Neither found |
| **Experience** | Chronological intervals AND explicit tenure match | Dates found OR explicit tenure found | No dates; entry-level keywords only |
| **Education** | Degree level AND institution name verified | Degree level verified | Not specified |
| **Skills** | $\ge 5$ verified canonical skills | 2–4 verified skills | $<2$ skills found |
| **Overall** | $\ge 4$ High dimensions, text stream verified | $\ge 2$ High dimensions | Scanned/empty PDF or low evidence |

---

## 5. Explainable AI (XAI) Output

For every evaluated candidate, the engine outputs:
1. **Verdict:** Categorization (`Strong Match`, `Good Potential`, `Moderate Fit`, `Low Alignment`).
2. **Requirement Evidence Table:** Table showing every JD skill, category (Mandatory/Preferred), match result (Strong/Partial/Related/Missing), and the verbatim resume sentence snippet.
3. **Key Strengths:** Explicit positive drivers (e.g. tenure buffer, strongly demonstrated frameworks).
4. **Score Deductions / Gaps:** Missing mandatory requirements and experience shortfalls.
5. **Domain Context:** Semantic alignment narrative.
