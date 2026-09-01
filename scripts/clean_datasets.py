import csv
from pathlib import Path
csv.field_size_limit(10_000_000)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(value):
    if value is None:
        return ""

    value = str(value)
    value = value.replace("\r", " ")
    value = value.replace("\n", " ")
    value = " ".join(value.split())

    return value.strip()


def process_eclipse():
    input_file = PROJECT_ROOT / "data" / "eclipse" / "eclipse_bug_report_data.csv"
    output_file = OUTPUT_DIR / "eclipse_cleaned.csv"

    print("\nProcessing Eclipse...")

    with open(input_file, "r", encoding="utf-8", errors="replace", newline="") as infile:
        reader = csv.DictReader(infile)

        with open(output_file, "w", encoding="utf-8", newline="") as outfile:

            fields = [
                "bug_id",
                "source",
                "project",
                "component",
                "title",
                "description",
                "severity",
                "status",
                "resolution",
                "created_at",
                "resolved_at"
            ]

            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()

            count = 0

            for row in reader:

                title = clean_text(row.get("short_description"))
                description = clean_text(row.get("long_description"))

                if not title and not description:
                    continue

                writer.writerow({
                    "bug_id": clean_text(row.get("bug_id")),
                    "source": "Eclipse",
                    "project": clean_text(row.get("product_name")),
                    "component": clean_text(row.get("component_name")),
                    "title": title,
                    "description": description,
                    "severity": clean_text(row.get("severity_category")),
                    "status": clean_text(row.get("status_category")),
                    "resolution": clean_text(row.get("resolution_category")),
                    "created_at": clean_text(row.get("creation_date")),
                    "resolved_at": clean_text(row.get("resolution_date"))
                })

                count += 1

    print(f"Eclipse cleaned records: {count}")
    print(f"Saved: {output_file}")


def process_mozilla():
    input_file = PROJECT_ROOT / "data" / "mozilla" / "mozila_bug_report_data.csv"
    output_file = OUTPUT_DIR / "mozilla_cleaned.csv"

    print("\nProcessing Mozilla...")

    if not input_file.exists():
        print("Mozilla dataset not found. Skipping.")
        return

    with open(
        input_file,
        "r",
        encoding="utf-8",
        errors="replace",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        fields = [
            "bug_id",
            "source",
            "project",
            "component",
            "title",
            "description",
            "severity",
            "status",
            "resolution",
            "created_at",
            "resolved_at"
        ]

        with open(
            output_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as outfile:

            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()

            count = 0

            for row in reader:

                title = clean_text(row.get("short_description"))
                description = clean_text(row.get("long_description"))

                if not title and not description:
                    continue

                writer.writerow({
                    "bug_id": clean_text(row.get("bug_id")),
                    "source": "Mozilla",
                    "project": clean_text(row.get("product_name")),
                    "component": clean_text(row.get("component_name")),
                    "title": title,
                    "description": description,
                    "severity": clean_text(row.get("severity_category")),
                    "status": clean_text(row.get("status_category")),
                    "resolution": clean_text(row.get("resolution_category")),
                    "created_at": clean_text(row.get("creation_date")),
                    "resolved_at": clean_text(row.get("resolution_date"))
                })

                count += 1

    print(f"Mozilla cleaned records: {count}")
    print(f"Saved: {output_file}")
def process_apache_issues():
    input_file = PROJECT_ROOT / "data" / "apache" / "issues.csv"
    output_file = OUTPUT_DIR / "apache_issues_cleaned.csv"

    print("\nProcessing Apache Issues...")

    with open(input_file, "r", encoding="utf-8", errors="replace", newline="") as infile:
        reader = csv.DictReader(infile)

        fields = [
            "bug_id",
            "source",
            "project",
            "component",
            "title",
            "description",
            "priority",
            "status",
            "resolution",
            "created_at",
            "resolved_at"
        ]

        with open(output_file, "w", encoding="utf-8", newline="") as outfile:

            writer = csv.DictWriter(outfile, fieldnames=fields)
            writer.writeheader()

            count = 0

            for row in reader:

                title = clean_text(row.get("summary"))
                description = clean_text(row.get("description"))

                if not title and not description:
                    continue

                writer.writerow({
                    "bug_id": clean_text(row.get("key")),
                    "source": "Apache",
                    "project": clean_text(row.get("project.name")),
                    "component": "",
                    "title": title,
                    "description": description,
                    "priority": clean_text(row.get("priority.name")),
                    "status": clean_text(row.get("status.name")),
                    "resolution": clean_text(row.get("resolution.name")),
                    "created_at": clean_text(row.get("created")),
                    "resolved_at": clean_text(row.get("resolutiondate"))
                })

                count += 1

                # Progress for large dataset
                if count % 10000 == 0:
                    print(f"Apache issues processed: {count}")

    print(f"Apache cleaned records: {count}")
    print(f"Saved: {output_file}")


print("=" * 80)
print("INTELLIGENT BUG DIAGNOSIS PLATFORM")
print("M1.4 - DATA CLEANING & STANDARDIZATION")
print("=" * 80)

process_eclipse()
process_mozilla()
process_apache_issues()

print("\nCleaning completed.")
print(f"Processed files are stored in: {OUTPUT_DIR}")