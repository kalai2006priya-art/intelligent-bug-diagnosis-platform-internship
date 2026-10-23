import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Locate root directory of project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    APP_NAME: str = "Intelligent Bug Diagnosis Platform with Fix Recommendation Assistance"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # Security
    SECRET_KEY: str = "intelligent-bug-diagnosis-platform-dev-secret-key-change-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'bug_platform.db'}"

    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "historical_defects"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Thresholds for duplicate detection
    SIMILARITY_THRESHOLD_DUPLICATE: float = 0.85
    SIMILARITY_THRESHOLD_RELATED: float = 0.65

    # LLM Settings (Optional)
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "heuristic"

    # Data paths
    DATA_RAW_DIR: str = str(BASE_DIR / "data" / "raw")
    DATA_SAMPLE_DIR: str = str(BASE_DIR / "data" / "sample_data")
    DATA_PROCESSED_DIR: str = str(BASE_DIR / "data" / "processed")

    # Memory Optimization for Cloud Hosting (Render Free Tier)
    LOW_MEMORY_MODE: bool = False
    DEFER_VECTOR_INDEXING: bool = True

    class Config:
        env_file = str(ENV_PATH)
        extra = "ignore"

settings = Settings()
