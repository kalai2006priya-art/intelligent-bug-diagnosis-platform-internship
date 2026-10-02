import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database.session import SessionLocal
from app.database.init_db import init_db, seed_sample_defects_if_empty, seed_default_users_if_empty
from app.api.auth import router as auth_router
from app.api.bugs import router as bugs_router
from app.api.knowledge_base import router as knowledge_base_router
from app.api.health import router as health_router
from app.api.analytics import router as analytics_router
from app.api.kb_growth import router as kb_growth_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("bug_platform")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables and seed sample historical defects
    logger.info("Initializing database and knowledge base...")
    init_db()
    db = SessionLocal()
    try:
        seed_default_users_if_empty(db)
        seed_sample_defects_if_empty(db)
    finally:
        db.close()
    logger.info("Platform backend ready for requests.")
    yield
    # Shutdown
    logger.info("Platform backend shutting down.")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "An AI-assisted defect diagnosis platform leveraging historical defect repositories "
        "(Mozilla, Apache, Eclipse) and coordinated multi-agent analysis for automated triage, "
        "log parsing, root-cause isolation, duplicate detection, actionable remediation, "
        "defect pattern analytics, and continuous knowledge base growth."
    ),
    version="1.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred while processing the request."}
    )

# Include routers
# Health & root status
app.include_router(health_router)

# Authentication endpoints: /api/auth/*
app.include_router(auth_router, prefix="/api")

# Bugs endpoints mounted at /api and root / so both /bugs and /api/bugs work seamlessly
app.include_router(bugs_router, prefix="/api")
app.include_router(bugs_router)

# Knowledge base endpoints: /api/knowledge-base/*
app.include_router(knowledge_base_router, prefix="/api")

# Knowledge base growth endpoints: /api/knowledge-base/growth/*
app.include_router(kb_growth_router, prefix="/api")

# Analytics endpoints: /api/analytics/*
app.include_router(analytics_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
