from typing import List, Dict, Any, Optional
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore

class RAGRetriever:
    @classmethod
    def retrieve_similar_defects(
        cls,
        query: str,
        top_k: int = 5,
        source_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Takes raw text / symptoms, encodes with the standardized embedding model,
        and retrieves top-K matching historical defect chunks from ChromaDB.
        """
        if not query or len(query.strip()) < 3:
            return []

        query_emb = EmbeddingService.get_embedding(query.strip())
        where_filter = {"source": source_filter} if source_filter else None
        
        matches = VectorStore.query(
            query_embedding=query_emb,
            top_k=top_k,
            where_filter=where_filter
        )
        return matches

    @classmethod
    def build_rag_context_string(cls, matches: List[Dict[str, Any]]) -> str:
        """
        Formats retrieved matches into a structured text context block
        for downstream Root Cause and Remediation agents.
        """
        if not matches:
            return "No matching historical defect records found in the knowledge base."

        context_lines = ["--- BEGIN RETRIEVED HISTORICAL EVIDENCE ---"]
        for idx, item in enumerate(matches, 1):
            meta = item.get("metadata", {})
            bug_id = meta.get("bug_id", "Unknown")
            source = meta.get("source", "General")
            title = meta.get("title", "")
            resolution = meta.get("resolution", "N/A")
            sim = item.get("similarity", 0.0)
            text_snippet = item.get("text", "")[:400]

            context_lines.append(
                f"[Evidence #{idx}] Source: {source} | Bug ID: {bug_id} | Similarity: {sim:.2f}\n"
                f"Title: {title}\n"
                f"Historical Resolution: {resolution}\n"
                f"Content Snippet: {text_snippet}\n"
            )
        context_lines.append("--- END RETRIEVED HISTORICAL EVIDENCE ---")
        return "\n".join(context_lines)
