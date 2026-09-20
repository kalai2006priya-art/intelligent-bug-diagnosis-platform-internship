from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.historical_defect import HistoricalDefect
from app.schemas.knowledge_base import HistoricalDefectResponse, SemanticSearchRequest, SemanticSearchResponse
from app.rag.retriever import RAGRetriever
from app.rag.vector_store import VectorStore

router = APIRouter(prefix="/knowledge-base", tags=["Knowledge Base"])

@router.get("/defects", response_model=List[HistoricalDefectResponse])
def list_historical_defects(
    source: Optional[str] = Query(None, description="Filter by Mozilla, Apache, or Eclipse"),
    project: Optional[str] = Query(None, description="Filter by project name"),
    component: Optional[str] = Query(None, description="Filter by component"),
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieves indexed historical defect records with optional multi-source filtering."""
    query = db.query(HistoricalDefect)
    if source:
        query = query.filter(HistoricalDefect.dataset_source == source)
    if project:
        query = query.filter(HistoricalDefect.project.ilike(f"%{project}%"))
    if component:
        query = query.filter(HistoricalDefect.component.ilike(f"%{component}%"))

    return query.order_by(HistoricalDefect.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/search", response_model=SemanticSearchResponse)
def semantic_search_knowledge_base(
    req: SemanticSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Executes semantic vector similarity retrieval against the historical defect vector database.
    Used for verifying RAG retrieval and testing similarity metrics.
    """
    matches = RAGRetriever.retrieve_similar_defects(
        query=req.query,
        top_k=req.top_k,
        source_filter=req.source
    )

    results = []
    for m in matches:
        meta = m.get("metadata", {})
        bug_id = meta.get("bug_id", "")
        # Look up full record in SQLite if available, otherwise construct from chunk metadata
        db_rec = db.query(HistoricalDefect).filter(HistoricalDefect.bug_id == bug_id).first()
        if db_rec:
            res_item = HistoricalDefectResponse.model_validate(db_rec)
            res_item.similarity = m.get("similarity")
            results.append(res_item)
        else:
            results.append(HistoricalDefectResponse(
                id=m.get("chunk_id", ""),
                dataset_source=meta.get("source", "General"),
                project=meta.get("project", "General"),
                bug_id=bug_id,
                title=meta.get("title", ""),
                description=m.get("text", ""),
                component=meta.get("component"),
                resolution=meta.get("resolution"),
                similarity=m.get("similarity")
            ))

    return SemanticSearchResponse(
        query=req.query,
        total_results=len(results),
        results=results
    )

@router.get("/stats")
def get_knowledge_base_stats(db: Session = Depends(get_db)):
    """Provides counts of indexed historical defects per dataset source."""
    counts = db.query(
        HistoricalDefect.dataset_source,
        func.count(HistoricalDefect.id)
    ).group_by(HistoricalDefect.dataset_source).all()

    stats_dict = {source: count for source, count in counts}
    vector_count = VectorStore.count()

    return {
        "sources": {
            "Mozilla": stats_dict.get("Mozilla", 0),
            "Apache": stats_dict.get("Apache", 0),
            "Eclipse": stats_dict.get("Eclipse", 0)
        },
        "total_relational_records": sum(stats_dict.values()),
        "total_vector_chunks": vector_count
    }
