from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="Intelligent Bug Diagnosis Platform",
    description="Backend API for bug submission and diagnosis",
    version="1.0.0"
)

BUG_FILE = Path("bug_reports.json")


class BugReport(BaseModel):
    title: str
    description: str
    stack_trace: str = ""
    error_logs: str = ""


def load_bug_reports():
    if not BUG_FILE.exists():
        return []

    with open(BUG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_bug_reports(reports):
    with open(BUG_FILE, "w", encoding="utf-8") as file:
        json.dump(reports, file, indent=4)


@app.get("/")
def root():
    return {
        "message": "Intelligent Bug Diagnosis Platform API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/bugs")
def submit_bug(bug: BugReport):

    reports = load_bug_reports()

    new_bug = {
        "id": len(reports) + 1,
        "title": bug.title,
        "description": bug.description,
        "stack_trace": bug.stack_trace,
        "error_logs": bug.error_logs,
        "created_at": datetime.now().isoformat()
    }

    reports.append(new_bug)

    save_bug_reports(reports)

    return {
        "message": "Bug report saved successfully",
        "bug": new_bug
    }


@app.get("/bugs")
def get_bugs():

    reports = load_bug_reports()

    return {
        "total_bugs": len(reports),
        "bugs": reports
    }


@app.post("/bugs/upload")
async def upload_bug_file(file: UploadFile = File(...)):

    allowed_extensions = [".txt", ".log"]

    filename = file.filename or ""
    file_extension = ""

    if "." in filename:
        file_extension = "." + filename.rsplit(".", 1)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only .txt and .log files are allowed."
        )

    file_content = await file.read()

    max_file_size = 2 * 1024 * 1024

    if len(file_content) > max_file_size:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 2 MB."
        )

    try:
        text_content = file_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must contain readable UTF-8 text."
        )

    return {
        "message": "Bug file uploaded successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "content": text_content
    }