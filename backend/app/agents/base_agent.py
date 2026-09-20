import abc
import logging
from typing import Dict, Any, Optional
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class BaseAgent(abc.ABC):
    """
    Abstract Base Class for all diagnosis agents.
    Provides automated fallbacks between external LLMs and internal deterministic heuristic analyzers.
    """
    agent_name: str = "BaseAgent"

    @abc.abstractmethod
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def heuristic_analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """Deterministic heuristic fallback when LLM is unavailable or offline."""
        pass
