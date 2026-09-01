import csv
from pathlib import Path

csv.field_size_limit(10_000_000)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "chunks"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 500


def clean_text(value):
    if not value:
        return ""

    return " ".join(str(value).replace("\n", " ").replace("\r", " ").split())


def create_chunks(input_file, output_file):
    print(f"\nProcessing: {input_file.name}")

    if not input_file.exists():
        print("File not found. Skipping.")
        return

    chunk_number = 0
    record_count = 0
    buffer = []

    with open(
        input_file,
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        for row in reader:

            text = " ".join([
                clean_text(row.get("title")),
                clean_text(row.get("description")),
                clean_text(row.get("project")),
                clean_text(row.get("component")),
                clean_text(row.get("severity")),
                clean_text(row.get("priority")),
                clean_text(row.get("resolution"))
            ]).strip()

            if not text:
                continue

            buffer.append({
                "bug_id": clean_text(row.get("bug_id")),
                "source": clean_text(row.get("source")),
                "text": text
            })

            record_count += 1

            if len(buffer) >= CHUNK_SIZE:

                chunk_number += 1

                chunk_file = OUTPUT_DIR / (
                    f"{output_file.stem}_chunk_{chunk_number}.csv"
                )

                write_chunk(chunk_file, buffer)

                buffer = []

                print(f"  Created chunk {chunk_number}")

    if buffer:
        chunk_number += 1

        chunk_file = OUTPUT_DIR / (
            f"{output_file.stem}_chunk_{chunk_number}.csv"
        )

        write_chunk(chunk_file, buffer)

        print(f"  Created chunk {chunk_number}")

    print(f"Total records processed: {record_count}")
    print(f"Total chunks created: {chunk_number}")


def write_chunk(file_path, rows):

    with open(
        file_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=["bug_id", "source", "text"]
        )

        writer.writeheader()
        writer.writerows(rows)


print("=" * 80)
print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
print("M1.4 - DATA CHUNKING")
print("=" * 80)

create_chunks(
    INPUT_DIR / "eclipse_cleaned.csv",
    INPUT_DIR / "eclipse_cleaned.csv"
)

create_chunks(
    INPUT_DIR / "mozilla_cleaned.csv",
    INPUT_DIR / "mozilla_cleaned.csv"
)

create_chunks(
    INPUT_DIR / "apache_issues_cleaned.csv",
    INPUT_DIR / "apache_issues_cleaned.csv"
)

print("\n" + "=" * 80)
print("Chunking completed.")
print(f"Chunks saved to: {OUTPUT_DIR}")
print("=" * 80)