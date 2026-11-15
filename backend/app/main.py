from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.jd_routes import router as jd_router
from app.routes.resume_routes import router as resume_router
from app.routes.match_routes import router as match_router

app = FastAPI(
    title="MatchPro AI - Resume Matching & Candidate Ranking API",
    description="Enterprise-grade AI-powered resume parsing, semantic embedding matching, and candidate ranking system.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(jd_router)
app.include_router(resume_router)
app.include_router(match_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "MatchPro AI Engine",
        "version": "1.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "AI-Based Resume Matching & Candidate Ranking System API",
        "docs_url": "/docs",
        "health_url": "/health"
    }
