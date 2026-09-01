import csv
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

# Allow large CSV fields
csv.field_size_limit(10_000_000)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
OUTPUT_DIR = PROJECT_ROOT / "data" / "embeddings"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


def generate_embeddings(model, chunk_file):

    print("\n" + "=" * 70)
    print(f"Processing: {chunk_file.name}")
    print("=" * 70)

    output_file = OUTPUT_DIR / f"{chunk_file.stem}_embeddings.json"

    # Skip already processed chunks
    if output_file.exists():
        print("Already processed. Skipping.")
        return

    records = []

    try:

        with open(
            chunk_file,
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                text = row.get("text", "")

                if text is None:
                    continue

                text = text.strip()

                if not text:
                    continue

                records.append({
                    "bug_id": row.get("bug_id", ""),
                    "source": row.get("source", ""),
                    "text": text
                })

    except csv.Error as error:

        print(f"CSV ERROR in {chunk_file.name}: {error}")
        print("Skipping this chunk.")
        return

    if not records:

        print("No records found. Skipping.")
        return

    print(f"Records: {len(records)}")
    print("Generating embeddings...")

    texts = [record["text"] for record in records]

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    output_data = []

    for record, embedding in zip(records, embeddings):

        output_data.append({
            "bug_id": record["bug_id"],
            "source": record["source"],
            "text": record["text"],
            "embedding": embedding.tolist()
        })

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            ensure_ascii=False
        )

    print(f"Saved: {output_file}")


def main():

    print("=" * 80)
    print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
    print("M1.4 - EMBEDDING GENERATION")
    print("=" * 80)

    if not CHUNKS_DIR.exists():

        print(f"Chunks directory not found: {CHUNKS_DIR}")
        return

    chunk_files = sorted(
        CHUNKS_DIR.glob("*_chunk_*.csv")
    )

    print(f"Chunk files found: {len(chunk_files)}")

    if not chunk_files:

        print("No chunk files found.")
        return

    # Load model only once
    print(f"\nLoading model: {MODEL_NAME}")

    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")

    processed = 0
    skipped = 0

    for chunk_file in chunk_files:

        output_file = OUTPUT_DIR / f"{chunk_file.stem}_embeddings.json"

        if output_file.exists():

            print(f"Skipping already processed: {chunk_file.name}")
            skipped += 1

            continue

        generate_embeddings(model, chunk_file)

        if output_file.exists():
            processed += 1

    print("\n" + "=" * 80)
    print("Embedding generation completed.")
    print("=" * 80)

    print(f"New chunks processed: {processed}")
    print(f"Already processed/skipped: {skipped}")
    print(f"Embeddings saved to: {OUTPUT_DIR}")

    print("=" * 80)


if __name__ == "__main__":
    main()