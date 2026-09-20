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
    def get_model(cls):
        if cls._model is None and not cls._use_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic fallback embedding engine.")
                cls._use_fallback = True
        return cls._model

    @classmethod
    def _fallback_embed(cls, text: str, dim: int = 384) -> List[float]:
        """
        Deterministic, zero-dependency 384-dimensional semantic projection vector.
        Ensures identical text produces identical normalized vectors with cosine similarity
        reflecting token overlap and semantic keywords.
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
