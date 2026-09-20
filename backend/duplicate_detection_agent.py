import os
import json
import numpy as np
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

BUG_REPORTS_FILE = os.path.join(
    BASE_DIR,
    "bug_reports.json"
)


# =========================================================
# LOAD MODEL
# =========================================================

MODEL = SentenceTransformer("all-MiniLM-L6-v2")


# =========================================================
# LOAD HISTORICAL VECTOR STORE
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
        f"Warning: Could not load historical vector store: {e}"
    )


# =========================================================
# BUILD BUG TEXT
# =========================================================

def build_bug_text(bug):

    return " ".join(
        [
            str(bug.get("title", "")),
            str(bug.get("description", "")),
            str(bug.get("stack_trace", "")),
            str(bug.get("error_logs", ""))
        ]
    ).strip()


# =========================================================
# SIMILARITY CLASSIFICATION
# =========================================================

def classify_similarity(similarity):

    if similarity >= 0.75:

        return "Duplicate"

    elif similarity >= 0.55:

        return "Related"

    else:

        return "New-Unmatched"


# =========================================================
# EXTRACT RESOLUTION
# =========================================================

def extract_resolution(text):

    text = str(text)

    resolution_keywords = [
        "fixed",
        "resolved",
        "patch",
        "solution",
        "workaround",
        "corrected"
    ]

    for keyword in resolution_keywords:

        if keyword.lower() in text.lower():

            return text

    return "Resolution information not available"


# =========================================================
# DUPLICATE DETECTION AGENT
# =========================================================

def duplicate_detection_agent(
    bug,
    top_k=5
):

    query_text = build_bug_text(bug)

    if not query_text:

        return {
            "status": "New-Unmatched",
            "confidence_score": 0.0,
            "reasoning": "Insufficient bug information for duplicate detection.",
            "matching_bugs": [],
            "historical_matches": [],
            "previously_submitted_matches": [],
            "evidence_status": "Insufficient evidence"
        }

    # =====================================================
    # CREATE QUERY EMBEDDING
    # =====================================================

    query_embedding = MODEL.encode(
        [query_text],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    # =====================================================
    # SEARCH HISTORICAL BUGS
    # =====================================================

    historical_matches = []

    if index is not None and len(metadata) > 0:

        search_k = min(
            top_k,
            index.ntotal
        )

        similarities, indices = index.search(
            query_embedding,
            search_k
        )

        for similarity, idx in zip(
            similarities[0],
            indices[0]
        ):

            if idx < 0 or idx >= len(metadata):

                continue

            record = metadata[idx]

            similarity_score = float(
                similarity
            )

            classification = classify_similarity(
                similarity_score
            )

            record_text = record.get(
                "text",
                ""
            )

            historical_matches.append({

                "source": record.get(
                    "source",
                    "Historical Knowledge Base"
                ),

                "bug_id": record.get(
                    "bug_id",
                    "Unknown"
                ),

                "similarity_score": round(
                    similarity_score,
                    4
                ),

                "classification": classification,

                "summary": record_text[:500],

                "component": record.get(
                    "component",
                    "Unknown"
                ),

                "exception_or_error": record.get(
                    "exception_type",
                    record.get(
                        "error_type",
                        "Unknown"
                    )
                ),

                "root_cause": record.get(
                    "root_cause",
                    "Not available"
                ),

                "resolution": extract_resolution(
                    record_text
                ),

                "reason": (
                    "Historical bug retrieved using "
                    "semantic similarity from the "
                    "historical defect knowledge base."
                )
            })

    # =====================================================
    # LOAD PREVIOUSLY SUBMITTED BUGS
    # =====================================================

    previously_submitted_matches = []

    try:

        if os.path.exists(BUG_REPORTS_FILE):

            with open(
                BUG_REPORTS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                submitted_bugs = json.load(file)

        else:

            submitted_bugs = []

    except Exception:

        submitted_bugs = []

    # =====================================================
    # COMPARE WITH PREVIOUS SUBMISSIONS
    # =====================================================

    for submitted_bug in submitted_bugs:

        submitted_text = build_bug_text(
            submitted_bug.get(
                "bug",
                submitted_bug
            )
        )

        if not submitted_text:

            continue

        submitted_embedding = MODEL.encode(
            [submitted_text],
            normalize_embeddings=True
        )

        submitted_embedding = np.asarray(
            submitted_embedding,
            dtype="float32"
        )

        # -------------------------------------------------
        # CORRECT SIMILARITY CALCULATION
        # -------------------------------------------------

        similarity = float(
            (query_embedding @ submitted_embedding.T)[0][0]
        )

        classification = classify_similarity(
            similarity
        )

        previously_submitted_matches.append({

            "source": "Previously Submitted Bug",

            "bug_id": submitted_bug.get(
                "id",
                "Unknown"
            ),

            "similarity_score": round(
                similarity,
                4
            ),

            "classification": classification,

            "summary": submitted_text[:500],

            "component": submitted_bug.get(
                "triage",
                {}
            ).get(
                "affected_component",
                "Unknown"
            ),

            "exception_or_error": submitted_bug.get(
                "log_analysis",
                {}
            ).get(
                "exception_type",
                "Unknown"
            ),

            "root_cause": submitted_bug.get(
                "root_cause",
                {}
            ).get(
                "root_cause_hypothesis",
                "Not available"
            )
            if isinstance(
                submitted_bug.get("root_cause"),
                dict
            )
            else "Not available",

            "resolution": submitted_bug.get(
                "remediation",
                "Resolution not available"
            ),

            "reason": (
                "Previously submitted bug compared "
                "using the same semantic embedding strategy."
            )
        })

    # =====================================================
    # COMBINE ALL MATCHES
    # =====================================================

    all_matches = (
        historical_matches
        + previously_submitted_matches
    )

    all_matches.sort(
        key=lambda item: item.get(
            "similarity_score",
            0.0
        ),
        reverse=True
    )

    top_matches = all_matches[:top_k]

    # =====================================================
    # DETERMINE OVERALL STATUS
    # =====================================================

    if top_matches:

        best_match = top_matches[0]

        overall_status = best_match.get(
            "classification",
            "New-Unmatched"
        )

        overall_confidence = best_match.get(
            "similarity_score",
            0.0
        )

        reasoning = (
            f"Top semantic match has a similarity "
            f"score of {overall_confidence:.4f} "
            f"and is classified as "
            f"'{overall_status}'."
        )

    else:

        overall_status = "New-Unmatched"

        overall_confidence = 0.0

        reasoning = (
            "No sufficiently similar historical or "
            "previously submitted bug was found."
        )

    # =====================================================
    # EVIDENCE STATUS
    # =====================================================

    if top_matches:

        evidence_status = "Historical or previous submission evidence found"

    else:

        evidence_status = "Insufficient evidence"

    # =====================================================
    # FINAL STRUCTURED RESULT
    # =====================================================

    return {

        "status": overall_status,

        "confidence_score": round(
            float(overall_confidence),
            4
        ),

        "reasoning": reasoning,

        "matching_bugs": top_matches,

        "historical_matches": historical_matches,

        "previously_submitted_matches": (
            previously_submitted_matches
        ),

        "evidence_status": evidence_status
    }