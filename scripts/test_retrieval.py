import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parent.parent

VECTOR_DIR = PROJECT_ROOT / "data" / "vector_store"

INDEX_FILE = VECTOR_DIR / "bug_index.faiss"
METADATA_FILE = VECTOR_DIR / "bug_metadata.json"

MODEL_NAME = "all-MiniLM-L6-v2"

TOP_K = 5


def main():

    print("=" * 80)
    print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
    print("M1.4 - RAG RETRIEVAL TEST")
    print("=" * 80)

    # ---------------------------------------------------------
    # Check vector store files
    # ---------------------------------------------------------

    if not INDEX_FILE.exists():

        print(f"FAISS index not found: {INDEX_FILE}")
        return

    if not METADATA_FILE.exists():

        print(f"Metadata file not found: {METADATA_FILE}")
        return

    # ---------------------------------------------------------
    # Load FAISS index
    # ---------------------------------------------------------

    print("\nLoading FAISS index...")

    index = faiss.read_index(
        str(INDEX_FILE)
    )

    print("FAISS index loaded successfully.")

    print(f"Total vectors: {index.ntotal}")
    print(f"Vector dimension: {index.d}")

    # ---------------------------------------------------------
    # Load metadata
    # ---------------------------------------------------------

    print("\nLoading metadata...")

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    print("Metadata loaded successfully.")
    print(f"Metadata records: {len(metadata)}")

    # ---------------------------------------------------------
    # Load embedding model
    # ---------------------------------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Embedding model loaded successfully.")

    # ---------------------------------------------------------
    # Test bug report
    # ---------------------------------------------------------

    test_bug = """
    NullPointerException occurs when opening the application.
    The error happens while processing a user request.
    The application crashes unexpectedly and the stack trace
    indicates a problem inside the core processing module.
    """

    print("\n" + "=" * 80)
    print("TEST BUG REPORT")
    print("=" * 80)

    print(test_bug.strip())

    # ---------------------------------------------------------
    # Generate query embedding
    # ---------------------------------------------------------

    print("\nGenerating query embedding...")

    query_embedding = model.encode(
        [test_bug],
        normalize_embeddings=True
    )

    # ---------------------------------------------------------
    # Search FAISS
    # ---------------------------------------------------------

    print("Searching historical defect knowledge base...")

    scores, indices = index.search(
        query_embedding,
        TOP_K
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print(f"TOP {TOP_K} SIMILAR HISTORICAL BUGS")
    print("=" * 80)

    for rank, (score, index_id) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        if index_id < 0:
            continue

        if index_id >= len(metadata):
            continue

        record = metadata[index_id]

        print(f"\n--- Result {rank} ---")

        print(f"Similarity Score : {score:.4f}")

        print(f"Bug ID           : {record.get('bug_id', '')}")

        print(f"Source           : {record.get('source', '')}")

        print(
            f"Description      : "
            f"{record.get('text', '')[:500]}"
        )

    print("\n" + "=" * 80)
    print("RAG RETRIEVAL TEST COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()