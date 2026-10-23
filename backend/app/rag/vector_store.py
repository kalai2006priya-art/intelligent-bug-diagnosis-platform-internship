import os
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    _client = None
    _collection = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            try:
                import chromadb
                from chromadb.config import Settings as ChromaSettings
                cls._client = chromadb.PersistentClient(
                    path=settings.CHROMA_PERSIST_DIRECTORY,
                    settings=ChromaSettings(anonymized_telemetry=False)
                )
            except Exception as e:
                logger.warning(f"Error initializing PersistentClient ({e}). Falling back to EphemeralClient.")
                try:
                    import chromadb
                    cls._client = chromadb.EphemeralClient()
                except Exception as ex:
                    logger.error(f"Could not initialize ChromaDB client ({ex}).")
                    cls._client = None
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            cls._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        return cls._collection

    @classmethod
    def add_chunks(
        cls,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """Add or update chunks in the vector collection."""
        if not ids:
            return
        collection = cls.get_collection()
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    @classmethod
    def query(
        cls,
        query_embedding: List[float],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries the vector collection for nearest neighbors using cosine similarity.
        Converts Chroma cosine distances to similarity scores:
        Cosine Distance = 1.0 - Cosine Similarity
        Cosine Similarity = 1.0 - Cosine Distance
        """
        collection = cls.get_collection()
        count = collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": actual_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            results = collection.query(**kwargs)
        except Exception as e:
            logger.error(f"Error executing vector query: {e}")
            return []

        parsed_results = []
        if not results or not results.get("ids") or len(results["ids"]) == 0:
            return []

        ids = results["ids"][0]
        docs = results["documents"][0] if "documents" in results else [""] * len(ids)
        metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(ids)
        distances = results["distances"][0] if "distances" in results else [0.5] * len(ids)

        for chunk_id, doc, meta, dist in zip(ids, docs, metas, distances):
            # Chroma returns cosine distance d in [0, 2]
            # Similarity = max(0.0, 1.0 - d)
            similarity = max(0.0, min(1.0, 1.0 - float(dist)))
            parsed_results.append({
                "chunk_id": chunk_id,
                "text": doc,
                "metadata": meta,
                "similarity": round(similarity, 4),
                "distance": round(float(dist), 4)
            })

        return parsed_results

    @classmethod
    def count(cls) -> int:
        try:
            collection = cls.get_collection()
            return collection.count()
        except Exception:
            return 0
