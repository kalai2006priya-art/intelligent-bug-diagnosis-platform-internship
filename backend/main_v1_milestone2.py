from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import os
import re

from backend.root_cause_agent import root_cause_agent
from backend.duplicate_detection_agent import duplicate_detection_agent
from backend.remediation_agent import remediation_agent


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Intelligent Bug Diagnosis Platform",
    description="AI-based multi-agent bug diagnosis and fix recommendation platform",
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# FILE PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

BUG_REPORTS_FILE = os.path.join(
    BASE_DIR,
    "bug_reports.json"
)


# =========================================================
# PYDANTIC MODELS
# =========================================================

class BugReport(BaseModel):
    title: str
    description: str
    stack_trace: Optional[str] = ""
    error_logs: Optional[str] = ""


class TriageResult(BaseModel):
    severity: str
    priority: str
    affected_component: str
    confidence_score: float
    reasoning: str


class LogAnalysisResult(BaseModel):
    exception_type: str
    error_message: str
    failure_point: str
    affected_code_path: str
    confidence_score: float


# =========================================================
# TRIAGE AGENT
# =========================================================

def triage_agent(bug: BugReport):

    text = (
        f"{bug.title} "
        f"{bug.description} "
        f"{bug.stack_trace} "
        f"{bug.error_logs}"
    ).lower()

    # -----------------------------------------------------
    # Severity Detection
    # -----------------------------------------------------

    critical_keywords = [
        "system crash",
        "data loss",
        "security breach",
        "production down",
        "server down",
        "database corruption"
    ]

    high_keywords = [
        "nullpointerexception",
        "outofmemoryerror",
        "fatal error",
        "service unavailable",
        "application crash",
        "crash"
    ]

    medium_keywords = [
        "exception",
        "error",
        "failed",
        "failure",
        "timeout",
        "incorrect"
    ]

    if any(keyword in text for keyword in critical_keywords):

        severity = "Critical"
        confidence = 0.95

    elif any(keyword in text for keyword in high_keywords):

        severity = "High"
        confidence = 0.90

    elif any(keyword in text for keyword in medium_keywords):

        severity = "Medium"
        confidence = 0.80

    else:

        severity = "Low"
        confidence = 0.60

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    priority = severity

    # -----------------------------------------------------
    # Component Detection
    # -----------------------------------------------------

    if any(
        keyword in text
        for keyword in [
            "login",
            "authentication",
            "authenticate",
            "password",
            "auth"
        ]
    ):

        affected_component = "Authentication/Login"

    elif any(
        keyword in text
        for keyword in [
            "database",
            "sql",
            "mysql",
            "postgresql",
            "mongodb",
            "query",
            "connection"
        ]
    ):

        affected_component = "Database"

    elif any(
        keyword in text
        for keyword in [
            "api",
            "endpoint",
            "request",
            "response",
            "backend",
            "server"
        ]
    ):

        affected_component = "API/Backend"

    elif any(
        keyword in text
        for keyword in [
            "file",
            "folder",
            "path",
            "config",
            "configuration",
            ".properties",
            ".xml",
            ".json",
            ".yaml",
            ".yml",
            "read file",
            "write file"
        ]
    ):

        affected_component = "File Handling"

    elif any(
        keyword in text
        for keyword in [
            "button",
            "screen",
            "page",
            "frontend",
            "ui",
            "user interface",
            "display"
        ]
    ):

        affected_component = "User Interface"

    else:

        affected_component = "Unknown"

    # -----------------------------------------------------
    # Reasoning
    # -----------------------------------------------------

    reasoning = (
        f"Severity '{severity}' was determined from the "
        f"keywords and error patterns present in the submitted bug. "
        f"The affected component was identified as "
        f"'{affected_component}'."
    )

    return TriageResult(
        severity=severity,
        priority=priority,
        affected_component=affected_component,
        confidence_score=confidence,
        reasoning=reasoning
    )


# =========================================================
# LOG ANALYSIS AGENT
# =========================================================

def log_analysis_agent(bug: BugReport):

    combined_logs = (
        f"{bug.stack_trace}\n"
        f"{bug.error_logs}"
    ).strip()

    # -----------------------------------------------------
    # Exception / Error Type
    # -----------------------------------------------------

    exception_type = "Unknown"

    exception_match = re.search(
        r"\b[A-Za-z][A-Za-z0-9_]*(?:Exception|Error)\b",
        combined_logs
    )

    if exception_match:

        exception_type = exception_match.group(0)

    # -----------------------------------------------------
    # Error Message
    # -----------------------------------------------------

    error_message = "Unknown"

    message_patterns = [
        r"(?:ERROR|Error|error)\s*:\s*(.+)",
        r"(?:Exception|Error)\s*:\s*(.+)"
    ]

    for pattern in message_patterns:

        match = re.search(
            pattern,
            combined_logs
        )

        if match:

            error_message = match.group(1).strip()
            break

    # -----------------------------------------------------
    # Java Exception Message
    # -----------------------------------------------------

    if error_message == "Unknown":

        java_exception_match = re.search(
            r"(?:[A-Za-z][A-Za-z0-9_]*(?:Exception|Error)):\s*(.+)",
            combined_logs
        )

        if java_exception_match:

            error_message = java_exception_match.group(1).strip()

    # -----------------------------------------------------
    # Failure Point
    # -----------------------------------------------------

    failure_point = "Unknown"

    java_trace_match = re.search(
        r"at\s+([A-Za-z0-9_.$]+\([^)]*\))",
        combined_logs
    )

    if java_trace_match:

        failure_point = java_trace_match.group(1)

    elif error_message != "Unknown":

        failure_point = error_message

    # -----------------------------------------------------
    # Affected Code Path
    # -----------------------------------------------------

    affected_code_path = "Unknown"

    if java_trace_match:

        full_trace = java_trace_match.group(1)

        method_match = re.match(
            r"([A-Za-z0-9_.$]+)\(",
            full_trace
        )

        if method_match:

            affected_code_path = method_match.group(1)

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    if (
        exception_type != "Unknown"
        and error_message != "Unknown"
        and failure_point != "Unknown"
    ):

        confidence_score = 0.90

    elif (
        exception_type != "Unknown"
        or error_message != "Unknown"
    ):

        confidence_score = 0.70

    else:

        confidence_score = 0.50

    return LogAnalysisResult(
        exception_type=exception_type,
        error_message=error_message,
        failure_point=failure_point,
        affected_code_path=affected_code_path,
        confidence_score=confidence_score
    )


# =========================================================
# BUG REPORT STORAGE
# =========================================================

def load_bug_reports():

    if not os.path.exists(BUG_REPORTS_FILE):

        return []

    try:

        with open(
            BUG_REPORTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_bug_reports(reports):

    with open(
        BUG_REPORTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            reports,
            file,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "message": "Intelligent Bug Diagnosis Platform API is running"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# =========================================================
# CREATE BUG REPORT
# M2 + M3.1 + M3.2 + M3.3 ORCHESTRATION
# =========================================================

@app.post("/bugs")
def create_bug(bug: BugReport):

    # -----------------------------------------------------
    # Basic Validation
    # -----------------------------------------------------

    if not bug.title.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug.description.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug description is required"
        )

    # -----------------------------------------------------
    # M2 - Triage Agent
    # -----------------------------------------------------

    triage_result = triage_agent(bug)

    # -----------------------------------------------------
    # M2 - Log Analysis Agent
    # -----------------------------------------------------

    log_analysis_result = log_analysis_agent(bug)

    # -----------------------------------------------------
    # M3.1 - Root Cause Agent
    # -----------------------------------------------------

    root_cause_result = root_cause_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        },

        triage_result=triage_result.model_dump(),

        log_analysis_result=log_analysis_result.model_dump()
    )

    # -----------------------------------------------------
    # M3.2 - Duplicate Detection Agent
    # -----------------------------------------------------

    duplicate_result = duplicate_detection_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        }
    )

    # -----------------------------------------------------
    # M3.3 - Remediation Agent
    # -----------------------------------------------------

    remediation_result = remediation_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        },

        triage_result=triage_result.model_dump(),

        log_analysis_result=log_analysis_result.model_dump(),

        root_cause_result=root_cause_result,

        duplicate_result=duplicate_result
    )

    # -----------------------------------------------------
    # Load Existing Reports
    # -----------------------------------------------------

    reports = load_bug_reports()

    # -----------------------------------------------------
    # Generate ID
    # -----------------------------------------------------

    if reports:

        bug_id = max(
            report.get("id", 0)
            for report in reports
        ) + 1

    else:

        bug_id = 1

    # -----------------------------------------------------
    # Combined Diagnosis
    # -----------------------------------------------------

    diagnosis = {

        "id": bug_id,

        "bug": {

            "title": bug.title,

            "description": bug.description,

            "stack_trace": bug.stack_trace,

            "error_logs": bug.error_logs
        },

        "triage": triage_result.model_dump(),

        "log_analysis": log_analysis_result.model_dump(),

        "root_cause": root_cause_result,

        "duplicate_detection": duplicate_result,

        "remediation": remediation_result
    }

    # -----------------------------------------------------
    # Agent Context
    # -----------------------------------------------------

    diagnosis["agent_context"] = {

        "triage_completed": True,

        "log_analysis_completed": True,

        "root_cause_completed": True,

        "duplicate_detection_completed": True,

        "remediation_completed": True
    }

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    reports.append(diagnosis)

    save_bug_reports(reports)

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return diagnosis


# =========================================================
# GET ALL BUG REPORTS
# =========================================================

@app.get("/bugs")
def get_bugs():

    return load_bug_reports()


# =========================================================
# UPLOAD BUG LOG FILE
# =========================================================

@app.post("/bugs/upload")
async def upload_bug_file(
    file: UploadFile = File(...)
):

    # -----------------------------------------------------
    # File Extension Validation
    # -----------------------------------------------------

    filename = file.filename or ""

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in [".txt", ".log"]:

        raise HTTPException(
            status_code=400,
            detail="Only .txt and .log files are allowed"
        )

    # -----------------------------------------------------
    # Read File
    # -----------------------------------------------------

    content = await file.read()

    # -----------------------------------------------------
    # Maximum File Size = 2 MB
    # -----------------------------------------------------

    if len(content) > 2 * 1024 * 1024:

        raise HTTPException(
            status_code=400,
            detail="File size must be less than 2 MB"
        )

    # -----------------------------------------------------
    # Decode
    # -----------------------------------------------------

    try:

        text_content = content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded"
        )

    # -----------------------------------------------------
    # Return Uploaded Content
    # -----------------------------------------------------

    return {

        "filename": filename,

        "content": text_content
    }


# =========================================================
# TRIAGE ONLY
# =========================================================

@app.post("/bugs/triage")
def analyze_triage(bug: BugReport):

    if not bug.title.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug.description.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug description is required"
        )

    result = triage_agent(bug)

    return {

        "triage": result.model_dump()
    }


# =========================================================
# LOG ANALYSIS ONLY
# =========================================================

@app.post("/bugs/log-analysis")
def analyze_logs(bug: BugReport):

    result = log_analysis_agent(bug)

    return {

        "log_analysis": result.model_dump()
    }


# =========================================================
# ROOT CAUSE ANALYSIS ONLY
# M3.1
# =========================================================

@app.post("/bugs/root-cause")
def analyze_root_cause(bug: BugReport):

    if not bug.title.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug.description.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug description is required"
        )

    # -----------------------------------------------------
    # First run M2 agents
    # -----------------------------------------------------

    triage_result = triage_agent(bug)

    log_analysis_result = log_analysis_agent(bug)

    # -----------------------------------------------------
    # Run M3.1 Root Cause Agent
    # -----------------------------------------------------

    result = root_cause_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        },

        triage_result=triage_result.model_dump(),

        log_analysis_result=log_analysis_result.model_dump()
    )

    return {

        "triage": triage_result.model_dump(),

        "log_analysis": log_analysis_result.model_dump(),

        "root_cause": result
    }


# =========================================================
# DUPLICATE DETECTION
# M3.2
# =========================================================

@app.post("/bugs/duplicate-detection")
def detect_duplicates(bug: BugReport):

    if not bug.title.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug.description.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug description is required"
        )

    # -----------------------------------------------------
    # Run M3.2 Duplicate Detection Agent
    # -----------------------------------------------------

    result = duplicate_detection_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        }
    )

    return {

        "duplicate_detection": result
    }


# =========================================================
# REMEDIATION ANALYSIS
# M3.3
# =========================================================

@app.post("/bugs/remediation")
def analyze_remediation(bug: BugReport):

    if not bug.title.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug title is required"
        )

    if not bug.description.strip():

        raise HTTPException(
            status_code=400,
            detail="Bug description is required"
        )

    # -----------------------------------------------------
    # M2 - Triage
    # -----------------------------------------------------

    triage_result = triage_agent(bug)

    # -----------------------------------------------------
    # M2 - Log Analysis
    # -----------------------------------------------------

    log_analysis_result = log_analysis_agent(bug)

    # -----------------------------------------------------
    # M3.1 - Root Cause
    # -----------------------------------------------------

    root_cause_result = root_cause_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        },

        triage_result=triage_result.model_dump(),

        log_analysis_result=log_analysis_result.model_dump()
    )

    # -----------------------------------------------------
    # M3.2 - Duplicate Detection
    # -----------------------------------------------------

    duplicate_result = duplicate_detection_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        }
    )

    # -----------------------------------------------------
    # M3.3 - Remediation
    # -----------------------------------------------------

    result = remediation_agent(

        bug={
            "title": bug.title,
            "description": bug.description,
            "stack_trace": bug.stack_trace,
            "error_logs": bug.error_logs
        },

        triage_result=triage_result.model_dump(),

        log_analysis_result=log_analysis_result.model_dump(),

        root_cause_result=root_cause_result,

        duplicate_result=duplicate_result
    )

    return {

        "triage": triage_result.model_dump(),

        "log_analysis": log_analysis_result.model_dump(),

        "root_cause": root_cause_result,

        "duplicate_detection": duplicate_result,

        "remediation": result
    }