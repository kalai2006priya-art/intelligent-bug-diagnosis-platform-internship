import pytest
from app.rag.chunker import chunk_historical_bug, clean_text
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore
from app.rag.retriever import RAGRetriever

def test_chunker_structure():
    sample = {
        "bug_id": "TEST-100",
        "dataset_source": "Mozilla",
        "project": "Firefox",
        "title": "Sample test defect",
        "description": "Long description of how Firefox crashed during network streaming.",
        "stack_trace": "Crash [@ nsHttpChannel::OnStopRequest]",
        "comments": "Fixed by adding defensive null check.",
        "component": "Networking",
        "resolution": "FIXED"
    }
    chunks = chunk_historical_bug(sample)
    assert len(chunks) >= 2
    types = [c["metadata"]["chunk_type"] for c in chunks]
    assert "description" in types
    assert "stack_trace" in types

def test_embedding_generation():
    text = "NullPointerException in user authentication validator"
    emb = EmbeddingService.get_embedding(text)
    assert isinstance(emb, list)
    assert len(emb) == 384
    # Test batch
    embs = EmbeddingService.get_embeddings([text, "Another sample text"])
    assert len(embs) == 2
    assert len(embs[0]) == 384

def test_vector_store_retrieval():
    # Query for http channel crash (present in sample data)
    matches = RAGRetriever.retrieve_similar_defects("nsHttpChannel OnStopRequest crash", top_k=2)
    assert isinstance(matches, list)
    if matches:
        assert "similarity" in matches[0]
        assert "chunk_id" in matches[0]
        assert matches[0]["similarity"] >= 0.0

def test_rag_context_building():
    matches = [
        {
            "chunk_id": "c1",
            "similarity": 0.88,
            "text": "Fixed NullPointerException by guarding null listener.",
            "metadata": {"bug_id": "MOZ-104820", "source": "Mozilla", "title": "Crash in OnStopRequest", "resolution": "FIXED"}
        }
    ]
    context = RAGRetriever.build_rag_context_string(matches)
    assert "MOZ-104820" in context
    assert "Mozilla" in context
    assert "0.88" in context
