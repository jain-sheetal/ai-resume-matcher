# MatchPro AI — Matching Algorithm & Mathematical Formulation

This document provides a comprehensive technical and mathematical explanation of the candidate evaluation algorithms implemented in MatchPro AI.

---

## 1. Sentence-BERT Semantic Matching Engine

### Architecture & Model Choice
MatchPro AI uses the **`sentence-transformers/all-MiniLM-L6-v2`** model.
- **What is Sentence-BERT (SBERT)?** Traditional BERT requires passing sentence pairs $(S_A, S_B)$ simultaneously through cross-attention layers, making pairwise comparison over $N$ resumes $O(N^2)$ and computationally prohibitive. SBERT uses a siamese neural network architecture with mean-pooling to derive independent, dense vector embeddings for individual text passages.
- **Dimensionality:** Encodes variable-length text into fixed-size dense vectors in $\mathbb{R}^{384}$ (384 dimensions). This dimension represents a compressed, highly expressive balance between semantic expressiveness and ultra-fast CPU inference latency ($\approx 3.2\text{ ms}$ per call).
- **Unit Normalization:** All vectors are mapped to unit length ($\|v\|_2 = 1.0$), transforming cosine similarity into a direct vector dot product:
  $$\cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^{384} u_i v_i$$
- **Why Semantic Matching Surpasses Raw Keyword Overlap:**
  - *Synonym Recognition:* Automatically aligns "building REST APIs" with "RESTful web services" without manual rules.
  - *Context Sensitivity:* Evaluates whether a candidate uses a framework professionally or merely mentions it in passing.
  - *Cross-Section Alignment:* Evaluates candidate project descriptions (40%), employment history (40%), and skills summary (20%) separately against job description requirements.

---

## 2. Context-Aware Skill Matching & 5-Tier Classification

### Controlled Skill Equivalences
To prevent semantic drift while ensuring industry aliases match, the engine evaluates a controlled equivalence dictionary prior to cosine evaluation:
- `React` $\leftrightarrow$ `React.js`, `ReactJS`, `React framework`
- `PostgreSQL` $\leftrightarrow$ `Postgres`, `PgSQL`, `PostgreSQL Database`
- `FastAPI` $\leftrightarrow$ `FastAPI framework`, `Python REST API`
- `Docker` $\leftrightarrow$ `Containerization`, `Docker engine`
- `CI/CD` $\leftrightarrow$ `Continuous Integration`, `Continuous Deployment`, `GitHub Actions`

### 5-Tier Match Classification
For every requirement in the Job Description, the engine assigns one of five mutually exclusive tiers:

| Tier | Criteria | Weight Awarded |
|---|---|:---:|
| **Strong Match** | Exact canonical match demonstrated in experience/projects with verbatim snippet OR frequency $\ge 2$. | **1.00** |
| **Partial Match** | Exact canonical match found in skills list with only 1 brief mention. | **0.85** |
| **Related Skill** | Matched via controlled equivalence or semantic adjacent technology. | **0.75** |
| **Missing** | Technology absent from all resume sections. | **0.00** |
| **Insufficient Evidence** | Candidate mentions term in an ambiguous context without project proof. | **0.00** |

### Mandatory vs Preferred Skill Scoring Formulation
The raw skill score partitions requirements into mandatory (85% base) and preferred (15% base):

$$S_{\text{raw\_skill}} = 85.0 \times \left(\frac{\sum \text{Score}_{\text{mandatory}}}{N_{\text{mandatory}}}\right) + 15.0 \times \left(\frac{\sum \text{Score}_{\text{preferred}}}{N_{\text{preferred}}}\right)$$

### Gated Versatility Bonus
Candidates who possess additional valuable technologies outside the JD requirements earn a versatility bonus ($+0.5\%$ per extra skill, capped at $+5.0\%$).
$$\text{Bonus} = \min\left(5.0, 0.5 \times N_{\text{additional}}\right)$$
**Critical Rule:** The versatility bonus is **strictly gated on $\sum \text{Score}_{\text{mandatory}} > 0$**. If a candidate satisfies zero mandatory requirements, their skill score is strictly $0.0\%$, preventing irrelevant candidates from receiving unearned versatility points.

---

## 3. Experience Calculation & Overlapping Interval Merging

Traditional ATS tools calculate years of experience by either extracting single duration mentions or summing all dates mentioned in the resume. When a candidate lists concurrent part-time jobs, freelance consulting, or overlapping internships, naive addition inflates experience.

### Timeline Interval Merging Algorithm
1. Date regex patterns extract all intervals:
   $$I = \{[s_1, e_1], [s_2, e_2], \dots, [s_k, e_k]\}$$
   Where `"Present"` or `"Current"` is converted to dynamic date fraction:
   $$\text{current\_fraction} = \text{year} + \frac{\text{month} - 1}{12.0}$$
2. Intervals are sorted chronologically by start date: $s_1 \le s_2 \le \dots \le s_k$.
3. Overlapping intervals are merged sequentially:
   $$\text{If } s_{i+1} \le e_i \implies \text{Merged} = [s_i, \max(e_i, e_{i+1})]$$
4. Total calendar tenure is the sum of merged interval lengths:
   $$\text{Total Years} = \sum_{j} (e_j - s_j)$$

### Experience Benchmark Comparison
$$\text{Score}_{\text{experience}} = \min\left(100.0, \frac{\text{Candidate Years}}{\text{Required Years}} \times 100.0\right)$$
Tenure exceeding the requirement is capped at 100.0% (preventing extreme seniority from distorting other evaluation criteria).

---

## 4. Overall Weighted Scoring Formula & Worked Example

### The Composite Scoring Formula
The overall match score is a deterministic weighted linear combination bounded strictly in $[0.0, 100.0]$:

$$S_{\text{overall}} = (w_{\text{skills}} \cdot S_{\text{skills}}) + (w_{\text{semantic}} \cdot S_{\text{semantic}}) + (w_{\text{experience}} \cdot S_{\text{experience}}) + (w_{\text{education}} \cdot S_{\text{education}})$$

**Default Normalized Weights:**
- $w_{\text{skills}} = 0.40$ (40% Weight)
- $w_{\text{semantic}} = 0.35$ (35% Weight)
- $w_{\text{experience}} = 0.20$ (20% Weight)
- $w_{\text{education}} = 0.05$ (5% Weight)
- $\sum w_i = 0.40 + 0.35 + 0.20 + 0.05 = 1.00$

---

### Worked Numerical Example

#### Candidate Profile: Alex Rivera
- **Applied Position:** Senior Full Stack Developer (Required Experience: 4.0 years, Bachelor's Degree required).
- **Mandatory Skills Required (4):** Python, FastAPI, PostgreSQL, Docker.
- **Preferred Skills Required (2):** Redis, AWS.

#### 1. Skill Score Calculation ($S_{\text{skills}}$)
- **Mandatory Skills:**
  - Python: Strong Match (1.0)
  - FastAPI: Strong Match (1.0)
  - PostgreSQL: Strong Match (1.0)
  - Docker: Strong Match (1.0)
  - Mandatory subtotal: $\frac{4.0}{4.0} \times 85.0 = 85.0\%$
- **Preferred Skills:**
  - Redis: Strong Match (1.0)
  - AWS: Missing (0.0)
  - Preferred subtotal: $\frac{1.0}{2.0} \times 15.0 = 7.5\%$
- **Additional Skills (2):** TypeScript, Git $\implies \text{Bonus} = \min(5.0, 2 \times 0.5) = +1.0\%$
- **Final Skill Score:**
  $$S_{\text{skills}} = \min(100.0, 85.0 + 7.5 + 1.0) = \mathbf{93.5\%}$$

#### 2. Semantic Similarity Score ($S_{\text{semantic}}$)
- Sentence-BERT cross-section cosine similarity between JD text and candidate experience/projects:
  $$\cos(\theta) = 0.768 \implies S_{\text{semantic}} = \mathbf{76.8\%}$$

#### 3. Experience Score ($S_{\text{experience}}$)
- Candidate possesses 5.8 calendar years vs 4.0 years required:
  $$S_{\text{experience}} = \min\left(100.0, \frac{5.8}{4.0} \times 100.0\right) = \min(100.0, 145.0) = \mathbf{100.0\%}$$

#### 4. Education Score ($S_{\text{education}}$)
- Candidate holds a verified B.S. in Computer Science (matches Bachelor's requirement):
  $$S_{\text{education}} = \mathbf{100.0\%}$$

#### 5. Composite Final Score
$$S_{\text{overall}} = (0.40 \times 93.5) + (0.35 \times 76.8) + (0.20 \times 100.0) + (0.05 \times 100.0)$$
$$S_{\text{overall}} = 37.40 + 26.88 + 20.00 + 5.00 = 89.28 \implies \mathbf{89.3\%}$$

**Result:** Alex Rivera receives an overall match score of **89.3%**, classified as *"Strong Match — Priority Candidate"*.
