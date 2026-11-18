import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes.jd_routes import router as jd_router
from app.routes.resume_routes import router as resume_router
from app.routes.match_routes import router as match_router

from app.matcher.embedding_engine import embedding_engine

app = FastAPI(
    title="MatchPro AI - Resume Matching & Candidate Ranking API",
    description="Enterprise-grade AI-powered resume parsing, semantic embedding matching, and candidate ranking system.",
    version="1.1.0"
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
    diagnostics = embedding_engine.get_diagnostics()
    return {
        "status": "healthy",
        "service": "MatchPro AI Engine",
        "version": "1.1.0",
        "ai_engine": diagnostics.model_dump()
    }

# Serve built frontend SPA if frontend/dist exists
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(dist_dir) and os.path.exists(os.path.join(dist_dir, "index.html")):
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Do not catch docs or openapi
        if full_path in ["docs", "redoc", "openapi.json"]:
            return None
        file_path = os.path.join(dist_dir, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "message": "AI-Based Resume Matching & Candidate Ranking System API",
            "docs_url": "/docs",
            "health_url": "/health"
        }
