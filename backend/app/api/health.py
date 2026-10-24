from fastapi import APIRouter
from app.config import settings
from app.rag.vector_store import VectorStore
from app.rag.embeddings import EmbeddingService

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def health_check():
    """
    Lightweight health check endpoint.
    Strictly avoids initializing ChromaDB or loading the heavy embedding model into memory.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "vector_store_chunks": VectorStore.cached_count(),
        "vector_store_initialized": VectorStore.is_initialized(),
        "embedding_mode": EmbeddingService.get_embedding_mode(),
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
