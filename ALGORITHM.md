# Technical Approach & AI Matching Methodology

## 1. Overview
The **MatchPro AI** matching engine uses a hybrid architecture combining:
1. **Contextual Semantic Embeddings** via Sentence Transformers (`all-MiniLM-L6-v2`)
2. **Canonical Skill Ontology & Alias Taxonomy** with boundary-aware phrase matching
3. **Chronological Experience Timeline & Duration Resolution**
4. **Transparent Explainable AI (XAI) Rationale Generation**

---

## 2. Core Scoring Formula

The overall candidate matching score $S_{\text{overall}} \in [0, 100]$ is computed as a weighted combination of four distinct criteria:

$$S_{\text{overall}} = w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{semantic}} \cdot S_{\text{semantic}} + w_{\text{exp}} \cdot S_{\text{exp}} + w_{\text{edu}} \cdot S_{\text{edu}}$$

Subject to:
$$\sum_{i} w_i = 1.0, \quad w_i \ge 0$$

### Default Recruiter Weights
| Component | Weight ($w$) | Metric | Purpose |
| :--- | :--- | :--- | :--- |
| **Technical Skill Overlap** ($S_{\text{skill}}$) | **0.40** (40%) | Canonical skill coverage & aliases | Evaluates core technical prerequisites |
| **Semantic Similarity** ($S_{\text{semantic}}$) | **0.35** (35%) | Sentence-BERT Cosine Similarity | Measures contextual & domain relevance |
| **Experience Tenure** ($S_{\text{exp}}$) | **0.20** (20%) | Candidate years vs JD minimum | Evaluates professional seniority |
| **Education Qualification** ($S_{\text{edu}}$) | **0.05** (5%) | Degree match (B.S., M.S., Ph.D.) | Academic baseline evaluation |

> *Note: Recruiters can dynamically adjust these weights in the UI according to hiring priorities (e.g. prioritizing experience for Senior roles or semantic versatility for Research roles).*

---

## 3. Algorithmic Breakdown

### 3.1. Contextual Semantic Similarity ($S_{\text{semantic}}$)
Keyword search fails when candidates describe their work with different phrasing than the job posting (e.g., *"Engineered resilient microservices with asynchronous endpoints"* vs *"Backend REST API developer"*).

To capture latent semantic meaning, we employ **Sentence-BERT (`all-MiniLM-L6-v2`)**:
1. Input texts (JD requirements context and Resume experience narratives) are tokenized and passed through a 6-layer MiniLM transformer.
2. Mean pooling over token embeddings produces a normalized 384-dimensional dense vector $\mathbf{u}, \mathbf{v} \in \mathbb{R}^{384}$.
3. Cosine similarity is computed:

$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^{384} u_i v_i}{\sqrt{\sum_{i=1}^{384} u_i^2} \sqrt{\sum_{i=1}^{384} v_i^2}}$$

4. The raw similarity $\in [0, 1]$ is scaled:
$$S_{\text{semantic}} = \min(100.0, \max(0.0, \text{Cosine Similarity} \times 100))$$

### 3.2. Skill Ontology & Alias Taxonomy ($S_{\text{skill}}$)
A naive substring search creates false positives (e.g., matching `"Go"` in `"Good"` or `"C"` in `"Cat"`). Our system addresses this through:
1. **Canonical Taxonomy**: Maps 250+ tech skills to canonical forms.
   - Example: `["react.js", "reactjs", "react"]` $\rightarrow$ `React`
   - Example: `["k8s", "kubernetes"]` $\rightarrow$ `Kubernetes`
   - Example: `["aws", "amazon web services"]` $\rightarrow$ `AWS`
2. **Boundary-Aware Regex Matching**:
   Using `(?<![a-zA-Z0-9])` and `(?![a-zA-Z0-9])` with custom handling for symbols (`C++`, `C#`, `.NET`).
3. **Overlap Computation**:
   $$\text{Base Score} = \frac{|\mathcal{S}_{\text{candidate}} \cap \mathcal{S}_{\text{required}}|}{|\mathcal{S}_{\text{required}}|} \times 100$$
4. **Additional Versatility Bonus**:
   Candidates possessing additional relevant skills receive up to $+5\%$ bonus:
   $$S_{\text{skill}} = \min\left(100.0, \text{Base Score} + \min(5.0, |\mathcal{S}_{\text{additional}}| \times 0.5)\right)$$

### 3.3. Experience Duration & Timeline Resolution ($S_{\text{exp}}$)
Accurately determining years of experience requires resolving both explicit claims and chronological work histories:
1. **Explicit Extraction**: Parses statements like *"5+ years of experience in software engineering"*.
2. **Chronological Interval Extraction**: Parses work dates (e.g., `Jan 2021 – Present`, `2018 – 2021`).
3. **Non-Overlapping Interval Merging**:
   Sorts intervals $[t_{\text{start}}^{(i)}, t_{\text{end}}^{(i)}]$ and merges overlapping ranges to avoid double-counting concurrent or overlapping positions:
   $$\Delta t_{\text{total}} = \sum_{k} (t_{\text{end}}^{(k)} - t_{\text{start}}^{(k)})$$
4. **Score Scaling**:
   - If $Y_{\text{candidate}} \ge Y_{\text{required}}$: Score $= 100.0$
   - If $Y_{\text{candidate}} < Y_{\text{required}}$:
     $$S_{\text{exp}} = \left(\frac{Y_{\text{candidate}}}{Y_{\text{required}}}\right)^{0.85} \times 100$$
   *(The progressive $0.85$ exponent avoids an overly punitive cliff for candidates just under the threshold while appropriately reflecting the seniority gap).*

---

## 4. Explainable AI (XAI) Architecture

For every candidate, the engine outputs an explainable decision structure:
- **Verdict**: Overall categorization (`Strong Match`, `Good Potential`, `Moderate Fit`, `Low Alignment`).
- **Strengths**: Specific positive drivers (e.g., *"Exceeds minimum tenure: 5.2 yrs vs 4.0 yrs required (+1.2 yrs buffer)"*, *"Possesses 14 of 19 core skills (74%)"*).
- **Gaps**: Explicitly identified missing requirements (e.g., *"Missing required skills: Kubernetes, AWS"*).
- **Semantic Narrative**: Contextual explanation of domain alignment.
