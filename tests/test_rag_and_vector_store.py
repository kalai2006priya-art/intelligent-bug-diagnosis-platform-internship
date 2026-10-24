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

def test_lightweight_health_check_does_not_initialize_chroma_or_model(client):
    """
    Requirement 1: Verify /health endpoint is strictly lightweight and does not
    force-initialize ChromaDB or load heavy neural models into memory.
    """
    # Temporarily reset in-memory handles to test whether /health forces initialization
    original_client = VectorStore._client
    original_collection = VectorStore._collection
    VectorStore._client = None
    VectorStore._collection = None

    try:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "embedding_mode" in data
        # ChromaDB client MUST remain None after hitting /health
        assert VectorStore._client is None
        assert VectorStore.is_initialized() is False
    finally:
        VectorStore._client = original_client
        VectorStore._collection = original_collection

def test_explicit_fallback_mode_distinction():
    """
    Requirement 3: Verify the fallback mode explicitly identifies as a lexical
    token-hash projection and never claims to be equivalent to dense MiniLM embeddings.
    """
    mode = EmbeddingService.get_embedding_mode()
    assert isinstance(mode, str)
    # The mode string must be descriptive and explicit
    if "fallback" in mode:
        assert "lexical_hash_projection_fallback" in mode
        # Must not claim to be dense MiniLM
        assert "dense neural transformer loaded" not in mode

def test_retrieval_failure_returns_empty_and_does_not_fake_data(monkeypatch):
    """
    Requirement 4: When vector store queries encounter an exception,
    log the error and return an empty list without inventing fake matches.
    """
    def mock_query_failure(*args, **kwargs):
        raise RuntimeError("Simulated ChromaDB disk read failure")

    monkeypatch.setattr(VectorStore, "query", mock_query_failure)
    matches = RAGRetriever.retrieve_similar_defects("Critical database deadlock exception", top_k=3)
    assert matches == []
    # Verify downstream context string honestly states no records found
    context_str = RAGRetriever.build_rag_context_string(matches)
    assert "No matching historical defect records found" in context_str

def test_avoid_reembedding_when_already_seeded(monkeypatch):
    """
    Requirement 6: Avoid re-embedding sample defects if the vector store already has records.
    """
    from app.database.init_db import ensure_vector_store_seeded

    # Mock count to indicate records are already indexed
    monkeypatch.setattr(VectorStore, "count", lambda: 49)

    add_chunks_called = False
    def mock_add_chunks(*args, **kwargs):
        nonlocal add_chunks_called
        add_chunks_called = True

    monkeypatch.setattr(VectorStore, "add_chunks", mock_add_chunks)
    ensure_vector_store_seeded()
    assert add_chunks_called is False, "ensure_vector_store_seeded must not re-embed when count > 0"
