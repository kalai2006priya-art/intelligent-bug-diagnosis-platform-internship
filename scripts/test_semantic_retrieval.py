"""
=============================================================================
Semantic Retrieval Testing Script
Tests vector similarity search against the ChromaDB historical defect knowledge base.
=============================================================================
Usage:
    python scripts/test_semantic_retrieval.py
    python scripts/test_semantic_retrieval.py --query "NullPointerException in authentication session"
=============================================================================
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.retriever import RAGRetriever
from app.rag.vector_store import VectorStore

DEFAULT_TEST_QUERIES = [
    "Null pointer crash in HTTP network request callback when cancelled",
    "Timeout waiting for connection from pool under heavy load",
    "Invalid thread access when updating UI dialog progress bar from background thread",
    "IndexedDB transaction aborted with UnknownError during eviction"
]

def run_retrieval_test(query: str, top_k: int = 3, source: str = None):
    print(f"\n=============================================================================")
    print(f"QUERY: '{query}'")
    if source:
        print(f"SOURCE FILTER: {source}")
    print(f"TOTAL CHUNKS IN VECTOR STORE: {VectorStore.count()}")
    print(f"=============================================================================")

    matches = RAGRetriever.retrieve_similar_defects(query, top_k=top_k, source_filter=source)

    if not matches:
        print("[-] No matching historical defect records found. Make sure to run `python scripts/process_datasets.py --sample` first.")
        return

    print(f"[+] Found {len(matches)} matching historical defect chunks:\n")
    for idx, m in enumerate(matches, 1):
        meta = m.get("metadata", {})
        sim = m.get("similarity", 0.0)
        dist = m.get("distance", 0.0)
        print(f"  Result #{idx}:")
        print(f"    - Bug ID:            {meta.get('bug_id')}")
        print(f"    - Source Repository: {meta.get('source')} ({meta.get('project')})")
        print(f"    - Similarity Score:  {sim:.4f} (Cosine Distance: {dist:.4f})")
        print(f"    - Component:         {meta.get('component')}")
        print(f"    - Defect Title:      {meta.get('title')}")
        print(f"    - Resolution:        {meta.get('resolution')}")
        print(f"    - Relevant Snippet:  {m.get('text', '')[:160]}...")
        print("-" * 65)

def main():
    parser = argparse.ArgumentParser(description="Test semantic retrieval against defect knowledge base.")
    parser.add_argument("--query", type=str, default=None, help="Bug symptoms or error description to query")
    parser.add_argument("--top_k", type=int, default=3, help="Number of results to retrieve")
    parser.add_argument("--source", type=str, default=None, help="Filter by Mozilla, Apache, or Eclipse")
    args = parser.parse_args()

    if args.query:
        run_retrieval_test(args.query, top_k=args.top_k, source=args.source)
    else:
        print("[+] Running suite of standard semantic retrieval test queries...")
        for q in DEFAULT_TEST_QUERIES:
            run_retrieval_test(q, top_k=args.top_k)

if __name__ == "__main__":
    main()
