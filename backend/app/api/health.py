from fastapi import APIRouter
from app.config import settings
from app.rag.vector_store import VectorStore

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def health_check():
    """System health check endpoint."""
    chunks = 0
    try:
        chunks = VectorStore.count()
    except Exception:
        chunks = 0
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "vector_store_chunks": chunks,
        "memory_mode": "low_memory" if settings.LOW_MEMORY_MODE else "standard"
    }

@router.get("/")
def root_endpoint():
    """Root platform information endpoint."""
    return {
        "title": settings.APP_NAME,
        "status": "online",
        "api_documentation": "/docs",
        "version": "1.0.0",
        "description": "AI-assisted software bug diagnosis platform with historical defect retrieval and fix recommendation assistance."
    }
