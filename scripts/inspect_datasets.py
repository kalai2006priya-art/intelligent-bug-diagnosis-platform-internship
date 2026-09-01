import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASETS = {
    "Mozilla": PROJECT_ROOT / "data" / "mozilla" / "mozilla_bug_report_data.csv",
    "Eclipse": PROJECT_ROOT / "data" / "eclipse" / "eclipse_bug_report_data.csv",
    "Apache Issues": PROJECT_ROOT / "data" / "apache" / "issues.csv",
    "Apache Comments": PROJECT_ROOT / "data" / "apache" / "comments.csv",
}


def inspect_csv(name, file_path):
    print("\n" + "=" * 70)
    print(f"{name}")
    print("=" * 70)

    if not file_path.exists():
        print(f"FILE NOT FOUND: {file_path}")
        return

    size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"File: {file_path}")
    print(f"Size: {size_mb:.2f} MB")

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as file:

            reader = csv.reader(file)

            header = next(reader, None)

            if header:
                print("\nColumns:")
                for number, column in enumerate(header, start=1):
                    print(f"{number}. {column}")

            print("\nFirst 3 rows:")

            for number, row in enumerate(reader, start=1):
                print(f"\nRow {number}:")
                for column, value in zip(header, row):
                    print(f"  {column}: {value[:200]}")

                if number == 3:
                    break

    except Exception as error:
        print(f"ERROR: {error}")


print("\nINTELLIGENT BUG DIAGNOSIS PLATFORM")
print("Historical Defect Dataset Inspection")

for dataset_name, dataset_path in DATASETS.items():
    inspect_csv(dataset_name, dataset_path)

print("\n" + "=" * 70)
print("Inspection completed.")
print("=" * 70)