import os
import numpy as np
from typing import List, Union, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from app.config import MODEL_NAME
from app.models.schemas import EngineDiagnostics

# Prevent HF hub from making blocking online calls if cached locally
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Controlled Skill & Term Equivalence Mapping for Semantic Expansion
CONTROLLED_EQUIVALENCES: Dict[str, List[str]] = {
    "react": ["react.js", "reactjs", "react framework", "react frontend"],
    "fastapi": ["fastapi framework", "asynchronous python api", "python rest api"],
    "django": ["django framework", "django rest framework", "drf"],
    "postgresql": ["postgres", "pgsql", "postgresql database", "relational postgres"],
    "docker": ["docker containers", "containerization", "dockerized deployments"],
    "kubernetes": ["k8s", "container orchestration", "k8s clusters"],
    "aws": ["amazon web services", "aws cloud", "ec2 s3 lambda"],
    "ci/cd": ["continuous integration", "continuous deployment", "github actions", "gitlab ci", "jenkins"],
    "machine learning": ["ml", "applied machine learning", "ml algorithms", "statistical modeling"],
    "deep learning": ["dl", "deep neural networks", "neural networks", "artificial neural networks"],
    "cnn": ["convolutional neural networks", "convolutional neural network", "convnet", "convnets", "cnns"],
    "nlp": ["natural language processing", "text processing", "computational linguistics", "text analytics"],
    "computer vision": ["cv", "opencv", "image processing", "object detection"],
    "pytorch": ["torch", "pytorch framework", "libtorch"],
    "tensorflow": ["tf", "keras", "tensorflow 2", "tf.keras"],
    "scikit-learn": ["sklearn", "scikit learn", "scikit"],
    "generative ai": ["genai", "gen-ai", "generative-ai"],
    "llms": ["llm", "large language models", "large language model"],
    "rag": ["retrieval augmented generation", "retrieval-augmented generation", "rag pipeline"],
    "prompt engineering": ["prompt design", "few-shot prompting", "chain-of-thought"],
    "rest apis": ["restful api development", "rest api endpoints", "restful web services", "api design"],
    "sql": ["structured query language", "relational database queries", "rdbms"],
    "microservices": ["distributed microservices", "service-oriented architecture", "event-driven architecture"],
    "python": ["python programming", "python3", "python backend", "py"],
    "javascript": ["js", "es6", "vanilla javascript"],
    "typescript": ["ts", "typed javascript"],
    "node.js": ["nodejs", "node", "node runtime"],
    "redis": ["redis cache", "in-memory caching", "redis kv store"]
}

class EmbeddingEngine:
    _instance = None
    _model = None
    _fallback_vectorizer = None
    _is_fallback = False
    _error_message = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize SentenceTransformer model with safe offline and fallback mechanisms."""
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading SentenceTransformer model: {MODEL_NAME}...")
            # First try loading with local_files_only=True to prevent network blockages
            try:
                self._model = SentenceTransformer(MODEL_NAME, local_files_only=True)
            except Exception:
                # If cache is in alternate location or needs first-time download
                os.environ.pop("HF_HUB_OFFLINE", None)
                os.environ.pop("TRANSFORMERS_OFFLINE", None)
                self._model = SentenceTransformer(MODEL_NAME)
            
            # Put model in eval mode for fast CPU inference
            if hasattr(self._model, "eval"):
                self._model.eval()
            self._is_fallback = False
            self._error_message = None
            print("SentenceTransformer loaded successfully!")
        except Exception as e:
            self._error_message = str(e)
            self._is_fallback = True
            self._model = None
            print(f"Warning: SentenceTransformer unavailable ({e}). Initializing verified TF-IDF Fallback Engine.")
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')

    def get_diagnostics(self) -> EngineDiagnostics:
        """Expose active engine status, model details, and fallback state for diagnostics."""
        if self._model is not None and not self._is_fallback:
            return EngineDiagnostics(
                active_engine="sentence-transformers",
                model_name=MODEL_NAME,
                is_fallback=False,
                device="cpu",
                status="healthy (operational)"
            )
        else:
            return EngineDiagnostics(
                active_engine="tfidf-fallback",
                model_name="scikit-learn TfidfVectorizer(ngram_range=(1,2))",
                is_fallback=True,
                device="cpu",
                status=f"degraded (fallback active: {self._error_message or 'model not cached'})"
            )

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate dense embeddings for a string or list of strings."""
        if isinstance(texts, str):
            texts = [texts]

        if not texts or all(not t.strip() for t in texts):
            return np.zeros((len(texts), 384))

        if self._model is not None and not self._is_fallback:
            try:
                return self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False, normalize_embeddings=True)
            except Exception as e:
                print(f"Inference error with SentenceTransformer: {e}")

        # Fallback to TF-IDF
        if self._fallback_vectorizer is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
        
        try:
            tfidf = self._fallback_vectorizer.fit_transform(texts)
            arr = tfidf.toarray()
            # Pad or truncate to 384 dimensions for schema consistency
            if arr.shape[1] < 384:
                padded = np.zeros((arr.shape[0], 384))
                padded[:, :arr.shape[1]] = arr
                return padded
            return arr[:, :384]
        except Exception:
            return np.zeros((len(texts), 384))

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate cosine similarity between two texts (0.0 to 1.0)."""
        if not text_a or not text_b or not text_a.strip() or not text_b.strip():
            return 0.0

        if self._model is not None and not self._is_fallback:
            try:
                embs = self._model.encode([text_a, text_b], convert_to_numpy=True, normalize_embeddings=True)
                sim = float(np.dot(embs[0], embs[1]))
                return float(np.clip(sim, 0.0, 1.0))
            except Exception as e:
                print(f"Error in embedding similarity: {e}")

        # Verified TF-IDF cosine similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            tfidf = vec.fit_transform([text_a, text_b])
            sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
            return float(np.clip(sim, 0.0, 1.0))
        except Exception:
            return 0.0

    def calculate_cross_section_similarity(
        self,
        jd_requirements: List[str],
        candidate_sections: Dict[str, str]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Compare JD technical requirements and responsibilities against candidate's
        specific resume sections (skills, projects, work experience).
        Returns overall semantic similarity and section-by-section breakdown.
        """
        if not jd_requirements or not candidate_sections:
            return 0.0, {}

        jd_text = "\n".join(jd_requirements)
        section_scores: Dict[str, float] = {}

        for sec_name, sec_text in candidate_sections.items():
            if sec_text and sec_text.strip():
                sim = self.calculate_similarity(jd_text, sec_text)
                section_scores[sec_name] = round(sim * 100.0, 1)

        if not section_scores:
            return 0.0, {}

        # Weighted combination across sections:
        # Projects (40%), Experience (40%), Skills summary (20%)
        weights = {"projects": 0.40, "experience": 0.40, "skills": 0.20}
        total_w = 0.0
        weighted_sum = 0.0

        for sec, score in section_scores.items():
            w = weights.get(sec, 0.33)
            weighted_sum += (score * w)
            total_w += w

        overall = (weighted_sum / total_w) if total_w > 0 else 0.0
        return round(overall, 1), section_scores

# Global singleton
embedding_engine = EmbeddingEngine()
