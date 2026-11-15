import os
import numpy as np
from typing import List, Union
from sklearn.metrics.pairwise import cosine_similarity
from app.config import MODEL_NAME

# Prevent HF hub from making online check calls if cached
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

class EmbeddingEngine:
    _instance = None
    _model = None
    _fallback_vectorizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading SentenceTransformer model: {MODEL_NAME} (offline cache)...")
            # First try loading with local_files_only=True
            try:
                self._model = SentenceTransformer(MODEL_NAME, local_files_only=True)
            except Exception:
                # If local_files_only argument is unsupported or needs network
                self._model = SentenceTransformer(MODEL_NAME)
            print("SentenceTransformer loaded successfully!")
        except Exception as e:
            print(f"Warning: Could not load SentenceTransformer ({e}). Falling back to TF-IDF.")
            self._model = None
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._fallback_vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')

    def encode(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate dense embeddings for a string or list of strings."""
        if isinstance(texts, str):
            texts = [texts]

        if self._model is not None:
            return self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        else:
            # Fallback to TF-IDF dense array
            if len(texts) == 1:
                return np.zeros((1, 384))
            tfidf = self._fallback_vectorizer.fit_transform(texts)
            return tfidf.toarray()

    def calculate_similarity(self, text_a: str, text_b: str) -> float:
        """Calculate cosine similarity between two texts (0.0 to 1.0)."""
        if not text_a.strip() or not text_b.strip():
            return 0.0

        if self._model is not None:
            embs = self._model.encode([text_a, text_b], convert_to_numpy=True)
            sim = cosine_similarity([embs[0]], [embs[1]])[0][0]
            # Rescale slightly if negative and clamp to [0, 1]
            return float(np.clip(sim, 0.0, 1.0))
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vec = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
            try:
                tfidf = vec.fit_transform([text_a, text_b])
                sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
                return float(np.clip(sim, 0.0, 1.0))
            except Exception:
                return 0.5

# Global singleton
embedding_engine = EmbeddingEngine()
