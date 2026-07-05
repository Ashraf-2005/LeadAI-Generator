"""
LeadAI Backend - FastAPI Application
Main entry point for the API server
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

import database
from routers import auth, leads

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LeadAI API",
    description="AI-Powered Sales Lead Qualification & Email Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup():
    """Initialize database on app startup."""
    logger.info("Starting LeadAI backend...")
    database.init_db()
    logger.info("✓ Backend initialized")


@app.on_event("shutdown")
async def shutdown():
    """Clean up on shutdown."""
    logger.info("Shutting down LeadAI backend...")


# ==============================================================================
# IMPORTANT: Register API routers FIRST (before any catch-all routes)
# ==============================================================================
app.include_router(auth.router, prefix="/api")
app.include_router(leads.router, prefix="/api")


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LeadAI API"}


# ==============================================================================
# Frontend serving - MUST come AFTER all API routes
# ==============================================================================
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(FRONTEND_DIR):
    # Mount static files
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")


# Serve index.html for root
@app.get("/", include_in_schema=False)
async def root():
    """Serve index.html as root."""
    if os.path.exists(FRONTEND_DIR):
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
    return {"message": "LeadAI API"}


# Catch-all for SPA routing - MUST be last
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    """Serve frontend files or fallback to index.html for SPA routing"""
    if not os.path.exists(FRONTEND_DIR):
        raise HTTPException(status_code=404)
    
    file_path = os.path.join(FRONTEND_DIR, full_path)
    
    # Serve actual files if they exist
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # For SPA routing, serve index.html (but not for /api/ paths)
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404)
    
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "development") == "development"
    )
