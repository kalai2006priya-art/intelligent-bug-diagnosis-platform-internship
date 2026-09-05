from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
from datetime import datetime
import re


app = FastAPI(
    title="Intelligent Bug Diagnosis Platform",
    description="Backend API for bug submission and diagnosis",
    version="1.0.0"
)


BUG_FILE = Path("bug_reports.json")


# =========================
# BUG REPORT MODEL
# =========================

class BugReport(BaseModel):
    title: str
    description: str
    stack_trace: str = ""
    error_logs: str = ""


# =========================
# TRIAGE RESULT MODEL
# =========================

class TriageResult(BaseModel):
    severity: str
    priority: str
    affected_component: str
    confidence_score: float
    reasoning: str


# =========================
# LOG ANALYSIS RESULT MODEL
# =========================

class LogAnalysisResult(BaseModel):
    exception_type: str
    failure_point: str
    affected_code_path: str


# =========================
# LOAD BUG REPORTS
# =========================

def load_bug_reports():
    if not BUG_FILE.exists():
        return []

    with open(BUG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# =========================
# SAVE BUG REPORTS
# =========================

def save_bug_reports(reports):
    with open(BUG_FILE, "w", encoding="utf-8") as file:
        json.dump(reports, file, indent=4)


# =========================
# ROOT ENDPOINT
# =========================

@app.get("/")
def root():
    return {
        "message": "Intelligent Bug Diagnosis Platform API is running"
    }


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================
# TRIAGE AGENT
# =========================

def triage_agent(bug: BugReport):

    text = (
        bug.title + " " +
        bug.description + " " +
        bug.stack_trace + " " +
        bug.error_logs
    ).lower()

    severity = "Low"
    priority = "Low"
    affected_component = "Unknown"
    confidence_score = 0.60

    reasoning = (
        "The bug information indicates a low-impact issue."
    )

    # Critical bugs
    if any(keyword in text for keyword in [
        "system crash",
        "data loss",
        "security breach",
        "production down",
        "server down",
        "database corruption"
    ]):

        severity = "Critical"
        priority = "High"
        confidence_score = 0.95

        reasoning = (
            "The bug contains indicators of critical system impact "
            "such as system failure, data loss, or production outage."
        )

    # High severity bugs
    elif any(keyword in text for keyword in [
        "nullpointerexception",
        "outofmemoryerror",
        "fatal error",
        "service unavailable",
        "application crash",
        "crash"
    ]):

        severity = "High"
        priority = "High"
        confidence_score = 0.90

        reasoning = (
            "The bug contains an error or failure condition that can "
            "significantly affect application execution."
        )

    # Medium severity bugs
    elif any(keyword in text for keyword in [
        "exception",
        "error",
        "failed",
        "failure",
        "timeout",
        "incorrect"
    ]):

        severity = "Medium"
        priority = "Medium"
        confidence_score = 0.80

        reasoning = (
            "The bug contains an error or failure indication that "
            "may affect a specific functionality."
        )

    # Component detection
    if any(keyword in text for keyword in [
        "login",
        "authentication",
        "password",
        "signin",
        "sign in"
    ]):

        affected_component = "Authentication / Login"

    elif any(keyword in text for keyword in [
        "database",
        "sql",
        "query",
        "postgresql",
        "mysql"
    ]):

        affected_component = "Database"

    elif any(keyword in text for keyword in [
        "api",
        "endpoint",
        "http",
        "request",
        "response"
    ]):

        affected_component = "API / Backend"

    elif any(keyword in text for keyword in [
        "ui",
        "button",
        "screen",
        "frontend",
        "display"
    ]):

        affected_component = "User Interface"

    elif any(keyword in text for keyword in [
        "file",
        "upload",
        "download"
    ]):

        affected_component = "File Handling"

    return TriageResult(
        severity=severity,
        priority=priority,
        affected_component=affected_component,
        confidence_score=confidence_score,
        reasoning=reasoning
    )


# =========================
# LOG ANALYSIS AGENT
# =========================

def log_analysis_agent(bug: BugReport):

    log_text = (
        bug.stack_trace + "\n" +
        bug.error_logs + "\n" +
        bug.description
    )

    exception_type = "Unknown"
    failure_point = "Unable to determine"
    affected_code_path = "Unable to determine"

    # Detect exception type
    exception_patterns = [
        r"([A-Za-z]+Exception)",
        r"([A-Za-z]+Error)"
    ]

    for pattern in exception_patterns:

        match = re.search(pattern, log_text)

        if match:
            exception_type = match.group(1)
            break

    # Detect failure point
    line_pattern = r"at\s+([A-Za-z0-9_.$]+)\(([^)]*)\)"

    match = re.search(line_pattern, log_text)

    if match:

        method_name = match.group(1)
        location = match.group(2)

        failure_point = f"{method_name}({location})"
        affected_code_path = method_name

    else:

        # Alternative Java stack trace format
        alternative_pattern = r"at\s+([A-Za-z0-9_.$]+):(\d+)"

        match = re.search(
            alternative_pattern,
            log_text
        )

        if match:

            method_name = match.group(1)
            line_number = match.group(2)

            failure_point = (
                f"{method_name}: line {line_number}"
            )

            affected_code_path = method_name

        else:

            text = log_text.lower()

            if "login" in text:

                affected_code_path = (
                    "Authentication / Login flow"
                )

            elif "database" in text or "sql" in text:

                affected_code_path = (
                    "Database access flow"
                )

            elif "api" in text or "endpoint" in text:

                affected_code_path = (
                    "API / Backend request flow"
                )

            elif "file" in text or "upload" in text:

                affected_code_path = (
                    "File handling flow"
                )

    return LogAnalysisResult(
        exception_type=exception_type,
        failure_point=failure_point,
        affected_code_path=affected_code_path
    )


# =========================
# SUBMIT BUG + MULTI-AGENT ORCHESTRATION
# =========================

@app.post("/bugs")
def submit_bug(bug: BugReport):

    reports = load_bug_reports()

    # Create bug record
    new_bug = {
        "id": len(reports) + 1,
        "title": bug.title,
        "description": bug.description,
        "stack_trace": bug.stack_trace,
        "error_logs": bug.error_logs,
        "created_at": datetime.now().isoformat()
    }

    # -------------------------
    # STEP 1: RUN TRIAGE AGENT
    # -------------------------

    triage_result = triage_agent(bug)

    # -------------------------
    # STEP 2: RUN LOG ANALYSIS AGENT
    # -------------------------

    log_analysis_result = log_analysis_agent(bug)

    # -------------------------
    # STEP 3: COMBINE AGENT OUTPUTS
    # -------------------------

    combined_context = {
        "triage": triage_result.model_dump(),
        "log_analysis": log_analysis_result.model_dump()
    }

    # Store combined context
    new_bug["agent_context"] = combined_context

    # Save bug
    reports.append(new_bug)
    save_bug_reports(reports)

    # Return result
    return {
        "message": "Bug submitted and analyzed successfully",
        "bug": new_bug,
        "agent_context": combined_context
    }


# =========================
# GET ALL BUGS
# =========================

@app.get("/bugs")
def get_bugs():

    reports = load_bug_reports()

    return {
        "total_bugs": len(reports),
        "bugs": reports
    }


# =========================
# FILE UPLOAD
# =========================

@app.post("/bugs/upload")
async def upload_bug_file(
    file: UploadFile = File(...)
):

    allowed_extensions = [".txt", ".log"]

    filename = file.filename or ""

    file_extension = ""

    if "." in filename:

        file_extension = (
            "." +
            filename.rsplit(".", 1)[1].lower()
        )

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


# =========================
# TRIAGE API ENDPOINT
# =========================

@app.post(
    "/bugs/triage",
    response_model=TriageResult
)
def analyze_bug_triage(bug: BugReport):

    result = triage_agent(bug)

    return result


# =========================
# LOG ANALYSIS API ENDPOINT
# =========================

@app.post(
    "/bugs/log-analysis",
    response_model=LogAnalysisResult
)
def analyze_bug_logs(bug: BugReport):

    result = log_analysis_agent(bug)

    return result