import csv
import json
from pathlib import Path

import faiss
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_DIR = PROJECT_ROOT / "data" / "embeddings"
VECTOR_DIR = PROJECT_ROOT / "data" / "vector_store"

VECTOR_DIR.mkdir(parents=True, exist_ok=True)

INDEX_FILE = VECTOR_DIR / "bug_index.faiss"
METADATA_FILE = VECTOR_DIR / "bug_metadata.json"

EMBEDDING_DIMENSION = 384


def load_embedding_file(file_path):

    print(f"Reading: {file_path.name}")

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    vectors = []
    metadata = []

    for record in data:

        embedding = record.get("embedding")

        if not embedding:
            continue

        vectors.append(embedding)

        metadata.append({
            "bug_id": record.get("bug_id", ""),
            "source": record.get("source", ""),
            "text": record.get("text", "")
        })

    return vectors, metadata


def main():

    print("=" * 80)
    print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
    print("M1.4 - FAISS VECTOR INDEX")
    print("=" * 80)

    if not EMBEDDINGS_DIR.exists():

        print(f"Embeddings directory not found: {EMBEDDINGS_DIR}")
        return

    embedding_files = sorted(
        EMBEDDINGS_DIR.glob("*_embeddings.json")
    )

    print(f"Embedding files found: {len(embedding_files)}")

    if not embedding_files:

        print("No embedding files found.")
        return

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    all_metadata = []

    processed_files = 0
    total_vectors = 0

    for file_path in embedding_files:

        try:

            vectors, metadata = load_embedding_file(file_path)

            if not vectors:
                print("No vectors found. Skipping.")
                continue

            vector_array = np.asarray(
                vectors,
                dtype="float32"
            )

            index.add(vector_array)

            all_metadata.extend(metadata)

            total_vectors += len(vectors)
            processed_files += 1

            print(
                f"Added {len(vectors)} vectors | "
                f"Total: {total_vectors}"
            )

        except Exception as error:

            print(f"ERROR processing {file_path.name}: {error}")
            print("Skipping this file.")

    print("\nSaving FAISS index...")

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    print(f"FAISS index saved: {INDEX_FILE}")

    print("\nSaving metadata...")

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_metadata,
            file,
            ensure_ascii=False
        )

    print(f"Metadata saved: {METADATA_FILE}")

    print("\n" + "=" * 80)
    print("VECTOR INDEXING COMPLETED")
    print("=" * 80)

    print(f"Files processed : {processed_files}")
    print(f"Total vectors   : {total_vectors}")
    print(f"Vector dimension: {EMBEDDING_DIMENSION}")
    print(f"Index           : {INDEX_FILE}")
    print(f"Metadata        : {METADATA_FILE}")

    print("=" * 80)


if __name__ == "__main__":
    main()