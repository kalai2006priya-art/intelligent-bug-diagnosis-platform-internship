import csv
from pathlib import Path
from collections import Counter

# Increase CSV field size limit for very large Apache comment fields
csv.field_size_limit(10_000_000)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


DATASETS = {
    "Eclipse": PROJECT_ROOT / "data" / "eclipse" / "eclipse_bug_report_data.csv",
    "Mozilla": PROJECT_ROOT / "data" / "mozilla" / "mozila_bug_report_data.csv",
    "Apache Issues": PROJECT_ROOT / "data" / "apache" / "issues.csv",
    "Apache Comments": PROJECT_ROOT / "data" / "apache" / "comments.csv",
}


# Number of rows to inspect from each dataset
SAMPLE_ROWS = 5000


def analyze_csv(name, file_path):
    print("\n" + "=" * 80)
    print(f"{name} DATASET ANALYSIS")
    print("=" * 80)

    # Check whether the file exists
    if not file_path.exists():
        print(f"FILE NOT FOUND: {file_path}")
        return

    # Display file size
    size_mb = file_path.stat().st_size / (1024 * 1024)
    size_gb = size_mb / 1024

    print(f"File: {file_path}")

    if size_gb >= 1:
        print(f"File Size: {size_gb:.2f} GB")
    else:
        print(f"File Size: {size_mb:.2f} MB")

    try:
        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="replace",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                print("No columns found.")
                return

            columns = reader.fieldnames

            # Display columns
            print("\nNumber of columns:", len(columns))

            print("\nColumns:")

            for number, column in enumerate(columns, start=1):
                print(f"{number}. {column}")

            # Counters
            missing_values = Counter()
            value_counts = {}

            for column in columns:
                value_counts[column] = Counter()

            rows_checked = 0

            # Read only a sample of rows
            for row in reader:

                if rows_checked >= SAMPLE_ROWS:
                    break

                for column in columns:

                    value = row.get(column, "")

                    if value is None or value.strip() == "":
                        missing_values[column] += 1

                    # Count short categorical values
                    if value and len(value) < 100:
                        value_counts[column][value] += 1

                rows_checked += 1

            print(f"\nRows inspected: {rows_checked}")

            # Missing value analysis
            print("\nMissing values in inspected rows:")

            found_missing = False

            for column in columns:

                count = missing_values[column]

                if count > 0:
                    print(f"  {column}: {count}")
                    found_missing = True

            if not found_missing:
                print("  No missing values found in inspected rows.")

            # Categorical analysis
            print("\nSample categorical value analysis:")

            useful_columns = [
                "resolution",
                "resolution.name",
                "status",
                "status.name",
                "priority",
                "priority.name",
                "severity",
                "severity_category",
                "component",
                "component_name",
                "product",
                "product_name",
                "project",
                "project.name",
                "issuetype",
                "issuetype.name",
            ]

            for column in useful_columns:

                if column in value_counts and value_counts[column]:

                    print(f"\n{column}:")

                    for value, count in value_counts[column].most_common(10):
                        print(f"  {value}: {count}")

    except Exception as error:
        print(f"ERROR: {error}")


# Main program
print("\n" + "=" * 80)
print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
print("M1.4 - HISTORICAL DEFECT DATASET ANALYSIS")
print("=" * 80)


for dataset_name, dataset_path in DATASETS.items():
    analyze_csv(dataset_name, dataset_path)


print("\n" + "=" * 80)
print("Dataset analysis completed.")
print("=" * 80)