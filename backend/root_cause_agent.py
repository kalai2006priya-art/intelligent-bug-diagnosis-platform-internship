import json
import os
import re
import faiss
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_PATH = os.path.join(
    BASE_DIR,
    "data",
    "vector_store",
    "bug_index.faiss"
)

METADATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "vector_store",
    "bug_metadata.json"
)


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# Load FAISS index
# ---------------------------------------------------------

index = faiss.read_index(INDEX_PATH)


# ---------------------------------------------------------
# Load historical bug metadata
# ---------------------------------------------------------

with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# ---------------------------------------------------------
# Root Cause Agent
# ---------------------------------------------------------

def root_cause_agent(
    bug,
    triage_result,
    log_analysis_result,
    top_k=5
):
    """
    Determines probable root cause using:
    - Bug description
    - Triage result
    - Log analysis result
    - Historical defect knowledge base
    """

    description = bug.get("description", "")
    title = bug.get("title", "")

    exception_type = log_analysis_result.get(
        "exception_type", "Unknown"
    )

    error_message = log_analysis_result.get(
        "error_message", "Unknown"
    )

    failure_point = log_analysis_result.get(
        "failure_point", "Unknown"
    )

    affected_code_path = log_analysis_result.get(
        "affected_code_path", "Unknown"
    )

    component = triage_result.get(
        "affected_component", "Unknown"
    )

    severity = triage_result.get(
        "severity", "Unknown"
    )

    # -----------------------------------------------------
    # Build search query
    # -----------------------------------------------------

    search_text = f"""
    Title: {title}
    Description: {description}
    Component: {component}
    Severity: {severity}
    Exception: {exception_type}
    Error Message: {error_message}
    Failure Point: {failure_point}
    Code Path: {affected_code_path}
    """

    # -----------------------------------------------------
    # Generate embedding
    # -----------------------------------------------------

    query_embedding = model.encode(
        [search_text],
        normalize_embeddings=True
    )

    # -----------------------------------------------------
    # Search historical defects
    # -----------------------------------------------------

    distances, indices = index.search(
        query_embedding,
        top_k
    )

    retrieved_defects = []

    for distance, idx in zip(distances[0], indices[0]):

        if idx < 0 or idx >= len(metadata):
            continue

        record = metadata[idx]

        similarity = float(distance)

        retrieved_defects.append({
            "rank": len(retrieved_defects) + 1,
            "similarity_score": round(similarity, 4),
            "historical_bug": record
        })

    # -----------------------------------------------------
    # Root cause hypothesis
    # -----------------------------------------------------

    hypothesis = generate_root_cause_hypothesis(
        component,
        exception_type,
        error_message,
        failure_point,
        retrieved_defects
    )

    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    if retrieved_defects:
        best_similarity = retrieved_defects[0]["similarity_score"]

        if best_similarity >= 0.75:
            confidence = 0.90
        elif best_similarity >= 0.60:
            confidence = 0.75
        elif best_similarity >= 0.45:
            confidence = 0.60
        else:
            confidence = 0.40
    else:
        confidence = 0.20

    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    evidence = []

    for item in retrieved_defects[:3]:

        historical_bug = item["historical_bug"]

        evidence.append({
            "similarity_score": item["similarity_score"],
            "historical_record": historical_bug
        })

    # -----------------------------------------------------
    # Final structured result
    # -----------------------------------------------------

    return {
        "root_cause_hypothesis": hypothesis,
        "confidence_score": confidence,
        "evidence": evidence,
        "retrieved_historical_defects": retrieved_defects,
        "evidence_status": (
            "Historical evidence found"
            if retrieved_defects
            else "Insufficient historical evidence"
        )
    }


# ---------------------------------------------------------
# Root Cause Hypothesis Generator
# ---------------------------------------------------------

def generate_root_cause_hypothesis(
    component,
    exception_type,
    error_message,
    failure_point,
    retrieved_defects
):

    # -----------------------------------------------------
    # Strong exception-based reasoning
    # -----------------------------------------------------

    if exception_type == "NullPointerException":

        return (
            "Probable root cause is an attempt to access "
            "an object or reference that has not been initialized "
            "or contains a null value."
        )

    if exception_type == "OutOfMemoryError":

        return (
            "Probable root cause is excessive memory consumption, "
            "such as loading a large amount of data into memory "
            "or an unreleased object/resource."
        )

    if exception_type == "SQLException":

        return (
            "Probable root cause is a database connectivity or "
            "database operation failure, potentially caused by "
            "connection configuration, unavailable database service, "
            "credentials, or query execution."
        )

    if exception_type == "IOException":

        return (
            "Probable root cause is a file or input/output operation "
            "failure, potentially caused by a missing file, invalid "
            "path, unavailable resource, or access problem."
        )

    if exception_type == "SecurityException":

        return (
            "Probable root cause is an authentication, authorization, "
            "or security permission failure."
        )

    # -----------------------------------------------------
    # Historical evidence based reasoning
    # -----------------------------------------------------

    if retrieved_defects:

        return (
            "Probable root cause is related to the same technical "
            "failure pattern observed in similar historical defects. "
            "The retrieved historical records provide supporting "
            "evidence, but the root cause is not confirmed."
        )

    # -----------------------------------------------------
    # Insufficient evidence
    # -----------------------------------------------------

    return (
        "Insufficient evidence to determine a reliable root cause. "
        "Additional logs, stack trace information, or historical "
        "defect evidence is required."
    )