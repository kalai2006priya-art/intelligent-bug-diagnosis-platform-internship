import os
import json
import re
import faiss
from sentence_transformers import SentenceTransformer


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

VECTOR_STORE_DIR = os.path.join(
    BASE_DIR,
    "data",
    "vector_store"
)

FAISS_INDEX_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "bug_index.faiss"
)

METADATA_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "bug_metadata.json"
)


# =========================================================
# LOAD MODEL
# =========================================================

MODEL = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# =========================================================
# LOAD HISTORICAL KNOWLEDGE BASE
# =========================================================

index = None
metadata = []

try:

    index = faiss.read_index(
        FAISS_INDEX_FILE
    )

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

except Exception as e:

    print(
        f"Warning: Could not load remediation knowledge base: {e}"
    )


# =========================================================
# BUILD SEARCH TEXT
# =========================================================

def build_search_text(
    bug,
    triage_result,
    log_analysis_result,
    root_cause_result,
    duplicate_result
):

    parts = [

        str(bug.get("title", "")),

        str(bug.get("description", "")),

        str(bug.get("stack_trace", "")),

        str(bug.get("error_logs", "")),

        str(
            triage_result.get(
                "affected_component",
                ""
            )
        ),

        str(
            triage_result.get(
                "severity",
                ""
            )
        ),

        str(
            log_analysis_result.get(
                "exception_type",
                ""
            )
        ),

        str(
            log_analysis_result.get(
                "error_message",
                ""
            )
        ),

        str(
            log_analysis_result.get(
                "failure_point",
                ""
            )
        ),

        str(
            log_analysis_result.get(
                "affected_code_path",
                ""
            )
        ),

        str(
            root_cause_result.get(
                "root_cause_hypothesis",
                ""
            )
        ),

        str(
            duplicate_result.get(
                "status",
                ""
            )
        )
    ]

    return " ".join(parts).strip()


# =========================================================
# EXTRACT HISTORICAL RESOLUTION
# =========================================================

def extract_resolution(text):

    text = str(text)

    patterns = [

        r"(?:resolution|resolved|solution|fix|fixed|patch|workaround)\s*[:\-]\s*(.+)",

        r"(?:Resolution|Resolved|Solution|Fix|Fixed|Patch|Workaround)\s*[:\-]\s*(.+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1).strip()

    return "Historical resolution not explicitly available"


# =========================================================
# BEST PRACTICE RECOMMENDATIONS
# =========================================================

def generate_best_practice_recommendation(
    bug,
    triage_result,
    log_analysis_result,
    root_cause_result
):

    component = triage_result.get(
        "affected_component",
        "Unknown"
    )

    exception_type = log_analysis_result.get(
        "exception_type",
        "Unknown"
    )

    root_cause = root_cause_result.get(
        "root_cause_hypothesis",
        ""
    )

    recommendations = []

    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    if component == "Database" or exception_type == "SQLException":

        recommendations.append({

            "recommendation": (
                "Verify database connection configuration, "
                "credentials, database availability, and "
                "connection-pool settings."
            ),

            "implementation_guidance": (
                "Check the database URL, username, password, "
                "connection timeout, and connection-pool limits. "
                "Add proper connection error handling and retry "
                "logic where appropriate."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.80
        })

    # -----------------------------------------------------
    # NULL POINTER
    # -----------------------------------------------------

    elif exception_type == "NullPointerException":

        recommendations.append({

            "recommendation": (
                "Identify the null object at the reported "
                "failure point and validate it before use."
            ),

            "implementation_guidance": (
                "Add null checks or appropriate validation "
                "before accessing object properties or methods. "
                "Trace the object initialization path."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.85
        })

    # -----------------------------------------------------
    # OUT OF MEMORY
    # -----------------------------------------------------

    elif exception_type == "OutOfMemoryError":

        recommendations.append({

            "recommendation": (
                "Reduce excessive memory consumption and "
                "identify objects or operations causing "
                "memory pressure."
            ),

            "implementation_guidance": (
                "Check large collections, file processing, "
                "caching, and repeated object creation. "
                "Use streaming or batch processing where possible."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.85
        })

    # -----------------------------------------------------
    # IO EXCEPTION
    # -----------------------------------------------------

    elif exception_type == "IOException":

        recommendations.append({

            "recommendation": (
                "Verify file paths, file availability, "
                "permissions, and input/output handling."
            ),

            "implementation_guidance": (
                "Validate the file path before access, "
                "check file existence and permissions, and "
                "handle I/O failures using appropriate exception handling."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.82
        })

    # -----------------------------------------------------
    # SECURITY EXCEPTION
    # -----------------------------------------------------

    elif exception_type == "SecurityException":

        recommendations.append({

            "recommendation": (
                "Review authentication, authorization, "
                "permissions, and access-control configuration."
            ),

            "implementation_guidance": (
                "Verify user credentials and required permissions. "
                "Check access-control rules and ensure sensitive "
                "operations require proper authorization."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.82
        })

    # -----------------------------------------------------
    # UNKNOWN / GENERAL
    # -----------------------------------------------------

    else:

        recommendations.append({

            "recommendation": (
                "Inspect the reported failure point and "
                "validate the related component configuration "
                "and error-handling logic."
            ),

            "implementation_guidance": (
                "Review the stack trace and application logs, "
                "reproduce the issue, add appropriate validation "
                "and exception handling, and verify the fix "
                "with regression testing."
            ),

            "evidence_type": "Best Practice / Agent Reasoning",

            "confidence_score": 0.65
        })

    return recommendations


# =========================================================
# REMEDIATION AGENT
# =========================================================

def remediation_agent(
    bug,
    triage_result,
    log_analysis_result,
    root_cause_result,
    duplicate_result,
    top_k=5
):

    search_text = build_search_text(
        bug,
        triage_result,
        log_analysis_result,
        root_cause_result,
        duplicate_result
    )

    # =====================================================
    # HISTORICAL RETRIEVAL
    # =====================================================

    historical_evidence = []

    if (
        index is not None
        and len(metadata) > 0
        and search_text
    ):

        query_embedding = MODEL.encode(
            [search_text],
            normalize_embeddings=True
        )

        similarities, indices = index.search(
            query_embedding,
            min(top_k, index.ntotal)
        )

        for similarity, idx in zip(
            similarities[0],
            indices[0]
        ):

            if idx < 0 or idx >= len(metadata):

                continue

            record = metadata[idx]

            record_text = record.get(
                "text",
                ""
            )

            resolution = extract_resolution(
                record_text
            )

            historical_evidence.append({

                "source": record.get(
                    "source",
                    "Historical Knowledge Base"
                ),

                "bug_id": record.get(
                    "bug_id",
                    "Unknown"
                ),

                "similarity_score": round(
                    float(similarity),
                    4
                ),

                "historical_bug_summary": record_text[:500],

                "historical_resolution": resolution,

                "evidence_type": "Historical Evidence"
            })

    # =====================================================
    # BEST PRACTICE RECOMMENDATIONS
    # =====================================================

    recommendations = generate_best_practice_recommendation(
        bug,
        triage_result,
        log_analysis_result,
        root_cause_result
    )

    # =====================================================
    # ADD HISTORICAL RESOLUTION AS RECOMMENDATION
    # =====================================================

    for evidence in historical_evidence[:3]:

        resolution = evidence.get(
            "historical_resolution",
            ""
        )

        if (
            resolution
            and
            resolution != "Historical resolution not explicitly available"
        ):

            recommendations.append({

                "recommendation": (
                    f"Review the historical resolution "
                    f"from bug {evidence.get('bug_id', 'Unknown')}."
                ),

                "implementation_guidance": resolution,

                "evidence_type": "Historical Evidence",

                "reference_bug_id": evidence.get(
                    "bug_id",
                    "Unknown"
                ),

                "confidence_score": evidence.get(
                    "similarity_score",
                    0.0
                )
            })

    # =====================================================
    # DETERMINE CONFIDENCE
    # =====================================================

    if historical_evidence:

        best_similarity = historical_evidence[0].get(
            "similarity_score",
            0.0
        )

        if best_similarity >= 0.75:

            overall_confidence = 0.90

        elif best_similarity >= 0.60:

            overall_confidence = 0.75

        elif best_similarity >= 0.45:

            overall_confidence = 0.60

        else:

            overall_confidence = 0.40

    else:

        overall_confidence = 0.50

    # =====================================================
    # EVIDENCE STATUS
    # =====================================================

    if historical_evidence:

        evidence_status = (
            "Historical evidence and best-practice "
            "recommendations available"
        )

    else:

        evidence_status = (
            "Insufficient historical evidence; "
            "recommendation based on best practices"
        )

    # =====================================================
    # REASONING
    # =====================================================

    reasoning = (

        "Remediation recommendations were generated using "

        "the triage result, log analysis, root cause findings, "

        "duplicate detection context, and semantically retrieved "

        "historical defect information. Historical evidence is "

        "presented separately from best-practice reasoning. "

        "Recommendations should be validated before applying "

        "them to production systems."

    )

    # =====================================================
    # FINAL STRUCTURED RESULT
    # =====================================================

    return {

        "recommendations": recommendations,

        "historical_evidence": historical_evidence,

        "confidence_score": round(
            overall_confidence,
            4
        ),

        "reasoning": reasoning,

        "evidence_status": evidence_status
    }