"""
=============================================================================
Universal Historical Defect Dataset Ingestion & Processing Pipeline
Supports: Mozilla, Apache, Eclipse Kaggle Datasets (.csv, .tsv, .json)
=============================================================================
Usage:
    python scripts/process_datasets.py            # Processes Kaggle files in data/raw/
    python scripts/process_datasets.py --sample   # Indexes sample datasets in data/sample_data/
=============================================================================
"""

import os
import sys
import json
import csv
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add backend directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database.session import SessionLocal, Base, engine
from app.models.historical_defect import HistoricalDefect
from app.rag.chunker import clean_text, chunk_historical_bug
from app.rag.embeddings import EmbeddingService
from app.rag.vector_store import VectorStore

# Column variant lookup mappings for heterogeneous Kaggle datasets
COLUMN_MAPPINGS = {
    "bug_id": ["bug_id", "id", "issue_id", "issue_key", "bug id", "key", "number"],
    "title": ["summary", "title", "short_desc", "short description", "headline", "subject"],
    "description": ["description", "body", "long_desc", "long description", "details", "content"],
    "component": ["component", "component/s", "module", "subsystem", "category", "product_component"],
    "severity": ["severity", "bug_severity", "priority", "issue type", "impact"],
    "priority": ["priority", "bug_priority", "urgency"],
    "resolution": ["resolution", "status", "outcome", "fix_status"],
    "comments": ["comments", "comment", "resolution_notes", "discussion"],
    "stack_trace": ["stack_trace", "stacktrace", "trace", "crash_log"]
}

def detect_field_name(headers: List[str], target_field: str) -> Optional[str]:
    """Finds the actual CSV header that maps to the target standard field."""
    lower_headers = {h.lower().strip(): h for h in headers}
    candidates = COLUMN_MAPPINGS.get(target_field, [target_field])
    for cand in candidates:
        if cand in lower_headers:
            return lower_headers[cand]
    return None

def read_file_records(file_path: Path, dataset_source: str) -> List[Dict[str, Any]]:
    """Parses a CSV, TSV, or JSON file, adapting to varying schemas."""
    records = []
    ext = file_path.suffix.lower()

    if ext == ".json":
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            if isinstance(data, list):
                for d in data:
                    d["dataset_source"] = d.get("dataset_source") or dataset_source
                    d["project"] = d.get("project") or file_path.stem
                    records.append(d)
        return records

    if ext in [".csv", ".tsv"]:
        delimiter = "\t" if ext == ".tsv" else ","
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            # Detect delimiter if possible
            first_line = f.readline()
            f.seek(0)
            if "\t" in first_line and ext != ".tsv":
                delimiter = "\t"

            reader = csv.DictReader(f, delimiter=delimiter)
            fieldnames = reader.fieldnames or []
            
            id_col = detect_field_name(fieldnames, "bug_id")
            title_col = detect_field_name(fieldnames, "title")
            desc_col = detect_field_name(fieldnames, "description")
            comp_col = detect_field_name(fieldnames, "component")
            sev_col = detect_field_name(fieldnames, "severity")
            prio_col = detect_field_name(fieldnames, "priority")
            res_col = detect_field_name(fieldnames, "resolution")
            comm_col = detect_field_name(fieldnames, "comments")
            trace_col = detect_field_name(fieldnames, "stack_trace")

            for row_idx, row in enumerate(reader):
                title = clean_text(row.get(title_col, "")) if title_col else ""
                desc = clean_text(row.get(desc_col, "")) if desc_col else ""
                if not title and not desc:
                    continue  # Skip empty defect rows

                bug_id = str(row.get(id_col) or f"{dataset_source.upper()}-{row_idx+1}")
                records.append({
                    "dataset_source": dataset_source,
                    "project": file_path.stem,
                    "bug_id": bug_id,
                    "title": title or "Untitled defect",
                    "description": desc or title,
                    "component": row.get(comp_col) if comp_col else "General",
                    "severity": row.get(sev_col) if sev_col else "Medium",
                    "priority": row.get(prio_col) if prio_col else "Medium",
                    "resolution": row.get(res_col) if res_col else "CLOSED",
                    "comments": row.get(comm_col) if comm_col else None,
                    "stack_trace": row.get(trace_col) if trace_col else None,
                    "source_reference": f"Kaggle import from {file_path.name}"
                })

    return records

def process_and_index(records: List[Dict[str, Any]]):
    """Saves standardized records to SQLite and indexes chunks into ChromaDB."""
    if not records:
        print("No records found to process.")
        return

    print(f"\n[+] Total records loaded: {len(records)}")
    print("[+] Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    chunk_ids = []
    documents = []
    metadatas = []
    inserted_db_count = 0

    try:
        print("[+] Standardizing, cleaning and persisting records...")
        for r in records:
            # Check duplicate in SQLite
            existing = db.query(HistoricalDefect).filter(
                HistoricalDefect.dataset_source == r["dataset_source"],
                HistoricalDefect.bug_id == str(r["bug_id"])
            ).first()

            if not existing:
                db_record = HistoricalDefect(
                    dataset_source=r["dataset_source"],
                    project=r.get("project", "General"),
                    bug_id=str(r["bug_id"]),
                    title=r["title"][:255],
                    description=r["description"],
                    stack_trace=r.get("stack_trace"),
                    error_message=r.get("error_message"),
                    component=r.get("component"),
                    severity=r.get("severity"),
                    priority=r.get("priority"),
                    resolution=r.get("resolution"),
                    status=r.get("status", "CLOSED"),
                    comments=r.get("comments"),
                    source_reference=r.get("source_reference")
                )
                db.add(db_record)
                inserted_db_count += 1

            # Chunk record for ChromaDB
            chunks = chunk_historical_bug(r)
            for c in chunks:
                chunk_ids.append(c["chunk_id"])
                documents.append(c["text"])
                metadatas.append(c["metadata"])

        db.commit()
        print(f"[+] Persisted {inserted_db_count} new records into SQLite historical_defects table.")

        if documents:
            print(f"[+] Generating 384-d embeddings for {len(documents)} text chunks...")
            embeddings = EmbeddingService.get_embeddings(documents)
            print("[+] Inserting vectors into ChromaDB...")
            VectorStore.add_chunks(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            print(f"[+] Successfully indexed {len(chunk_ids)} chunks into ChromaDB.")

        print(f"\n[SUCCESS] Knowledge Base update complete. Total vectors in store: {VectorStore.count()}")

    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Ingest and process historical bug datasets.")
    parser.add_argument("--sample", action="store_true", help="Index verified bundled sample datasets.")
    args = parser.parse_args()

    all_records = []

    if args.sample:
        sample_dir = PROJECT_DIR / "data" / "sample_data"
        print(f"[+] Scanning sample directory: {sample_dir}")
        for s_file in sample_dir.glob("*.json"):
            source = "Mozilla" if "mozilla" in s_file.stem.lower() else "Apache" if "apache" in s_file.stem.lower() else "Eclipse"
            print(f"  -> Loading {s_file.name} (Source: {source})")
            recs = read_file_records(s_file, source)
            all_records.extend(recs)
    else:
        raw_dir = PROJECT_DIR / "data" / "raw"
        sources = ["mozilla", "apache", "eclipse"]
        print(f"[+] Scanning raw Kaggle datasets in: {raw_dir}")
        found_any = False
        for s in sources:
            source_dir = raw_dir / s
            if source_dir.exists():
                files = list(source_dir.glob("*.csv")) + list(source_dir.glob("*.tsv")) + list(source_dir.glob("*.json"))
                source_label = s.capitalize()
                for f in files:
                    found_any = True
                    print(f"  -> Found {source_label} dataset file: {f.name}")
                    recs = read_file_records(f, source_label)
                    all_records.extend(recs)

        if not found_any:
            print("[!] No Kaggle dataset files found in data/raw/{mozilla,apache,eclipse}/.")
            print("[!] Automatically falling back to index bundled sample datasets from data/sample_data/...")
            sample_dir = PROJECT_DIR / "data" / "sample_data"
            for s_file in sample_dir.glob("*.json"):
                source = "Mozilla" if "mozilla" in s_file.stem.lower() else "Apache" if "apache" in s_file.stem.lower() else "Eclipse"
                recs = read_file_records(s_file, source)
                all_records.extend(recs)

    process_and_index(all_records)

if __name__ == "__main__":
    main()
