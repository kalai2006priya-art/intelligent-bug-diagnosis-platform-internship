from .auth import router as auth_router
from .bugs import router as bugs_router
from .knowledge_base import router as knowledge_base_router
from .health import router as health_router

__all__ = ["auth_router", "bugs_router", "knowledge_base_router", "health_router"]
