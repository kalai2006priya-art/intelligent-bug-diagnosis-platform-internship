import hashlib
import logging
import math
from typing import List
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _model = None
    _use_fallback = False

    @classmethod
    def get_embedding_mode(cls) -> str:
        """
        Explicitly identifies the active embedding mechanism.
        Clearly differentiates between dense neural transformer embeddings and
        the lightweight lexical token-hash projection fallback.
        """
        if settings.LOW_MEMORY_MODE:
            return "lexical_hash_projection_fallback (low_memory_mode enabled)"
        if cls._use_fallback:
            return "lexical_hash_projection_fallback (transformer unavailable / memory fallback)"
        if cls._model is not None:
            return f"{settings.EMBEDDING_MODEL_NAME} (dense neural transformer loaded)"
        return f"{settings.EMBEDDING_MODEL_NAME} (lazy, uninitialized)"

    @classmethod
    def is_model_loaded(cls) -> bool:
        """Returns True only if the dense neural model is currently loaded in memory."""
        return cls._model is not None

    @classmethod
    def get_model(cls):
        """
        Lazily loads the SentenceTransformer model only when requested by an active feature.
        If LOW_MEMORY_MODE is set or memory is constrained, explicitly falls back to
        the lightweight lexical token-hash projection without crashing.
        """
        if settings.LOW_MEMORY_MODE:
            if not cls._use_fallback:
                logger.info(
                    "LOW_MEMORY_MODE is active. Using lightweight deterministic 384-d token-hash projection. "
                    "Note: This is a memory-saving lexical fallback (<512MB RAM) and is not equivalent to dense neural MiniLM embeddings."
                )
                cls._use_fallback = True
            return None

        if cls._model is None and not cls._use_fallback:
            try:
                try:
                    import torch
                    torch.set_num_threads(1)
                except Exception:
                    pass
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading dense neural embedding model: {settings.EMBEDDING_MODEL_NAME}")
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            except (MemoryError, Exception) as e:
                logger.warning(
                    f"Could not load SentenceTransformer ({e}). Falling back to lightweight lexical token-hash projection. "
                    "Note: Lexical token-hash projection is not equivalent to dense neural MiniLM embeddings."
                )
                cls._use_fallback = True
        return cls._model

    @classmethod
    def _fallback_embed(cls, text: str, dim: int = 384) -> List[float]:
        """
        Deterministic, zero-dependency 384-dimensional lexical token-hash projection vector.
        Designed for memory-constrained hosting environments (<512MB RAM).
        CRITICAL DISTINCTION: This generates normalized vectors reflecting lexical keyword
        and token overlap. It does NOT produce dense semantic representations and is NOT
        equivalent to the all-MiniLM-L6-v2 transformer model.
        """
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()

        for word in words:
            # Deterministic hash to dimension
            h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            idx = h % dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign

        # L2 Normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """Generate a 384-dimensional embedding vector for a single text."""
        model = cls.get_model()
        if model is not None and not cls._use_fallback:
            try:
                emb = model.encode(text, convert_to_numpy=True)
                return emb.tolist()
            except Exception as e:
                logger.warning(f"Error computing embedding with SentenceTransformer: {e}")
        return cls._fallback_embed(text)

    @classmethod
    def get_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """Batch embedding generation for efficient indexing."""
        model = cls.get_model()
        if model is not None and not cls._use_fallback:
            try:
                embs = model.encode(texts, convert_to_numpy=True)
                return embs.tolist()
            except Exception as e:
                logger.warning(f"Error in batch embeddings: {e}")
        return [cls._fallback_embed(t) for t in texts]
