import os
from pydantic import BaseModel

class ScoringWeights(BaseModel):
    skills: float = 0.40       # 40% weight on technical/hard skill overlap
    semantic: float = 0.35     # 35% weight on contextual semantic embedding similarity
    experience: float = 0.20   # 20% weight on years of relevant experience
    education: float = 0.05    # 5% weight on academic degree qualification

    def validate_weights(self) -> bool:
        total = self.skills + self.semantic + self.experience + self.education
        return abs(total - 1.0) < 0.01

DEFAULT_WEIGHTS = ScoringWeights()
MODEL_NAME = "all-MiniLM-L6-v2"
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
