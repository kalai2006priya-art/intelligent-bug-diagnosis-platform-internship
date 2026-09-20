import os
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import Base, engine, SessionLocal
from app.models.historical_defect import HistoricalDefect
from app.rag.chunker import chunk_historical_bug
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

def init_db():
    """Create all relational database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")

def seed_sample_defects_if_empty(db: Session):
    """
    Seeds bundled sample defects into SQLite and ChromaDB if historical_defects is empty,
    providing immediate RAG capabilities out of the box.
    """
    count = db.query(HistoricalDefect).count()
    if count > 0:
        return

    sample_dir = Path(settings.DATA_SAMPLE_DIR)
    if not sample_dir.exists():
        logger.warning(f"Sample data directory does not exist: {sample_dir}")
        return

    sample_files = [
        sample_dir / "mozilla_sample.json",
        sample_dir / "apache_sample.json",
        sample_dir / "eclipse_sample.json"
    ]

    all_records = []
    for s_file in sample_files:
        if s_file.exists():
            try:
                with open(s_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_records.extend(data)
            except Exception as e:
                logger.error(f"Error reading sample file {s_file}: {e}")

    if not all_records:
        return

    logger.info(f"Seeding {len(all_records)} sample historical defects into SQLite and ChromaDB...")

    chunk_ids = []
    documents = []
    metadatas = []

    for item in all_records:
        # 1. Insert into SQLite
        rec = HistoricalDefect(
            dataset_source=item.get("dataset_source", "General"),
            project=item.get("project", "General"),
            bug_id=str(item.get("bug_id")),
            title=item.get("title", ""),
            description=item.get("description", ""),
            stack_trace=item.get("stack_trace"),
            error_message=item.get("error_message"),
            component=item.get("component"),
            severity=item.get("severity"),
            priority=item.get("priority"),
            resolution=item.get("resolution"),
            status=item.get("status"),
            comments=item.get("comments"),
            source_reference=item.get("source_reference")
        )
        db.add(rec)

        # 2. Prepare chunks for ChromaDB
        chunks = chunk_historical_bug(item)
        for c in chunks:
            chunk_ids.append(c["chunk_id"])
            documents.append(c["text"])
            metadatas.append(c["metadata"])

    db.commit()

    # 3. Generate embeddings and add to ChromaDB
    if documents:
        try:
            embeddings = EmbeddingService.get_embeddings(documents)
            VectorStore.add_chunks(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"Successfully indexed {len(chunk_ids)} chunks into ChromaDB.")
        except Exception as e:
            logger.error(f"Error indexing chunks in ChromaDB: {e}")
